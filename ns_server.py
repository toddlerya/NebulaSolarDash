#!/usr/bin/env python
# coding: utf-8
# author: qguo

import time
import json
from lib.bottle import request, Bottle, view, run, static_file
from lib.common_lib import re_joint_dir_by_os, get_conf_pat
from init_db import NSDb


class NSConf:
    def __init__(self):
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")
        self.server_port = get_conf_pat(ns_conf, "server", "port")
        self.debug = get_conf_pat(ns_conf, "server", "debug")
        self.mem_yellow = get_conf_pat(ns_conf, "server", "mem_yellow")
        self.mem_red = get_conf_pat(ns_conf, "server", "mem_red")
        self.cpu_yellow = get_conf_pat(ns_conf, "server", "cpu_yellow")
        self.cpu_red = get_conf_pat(ns_conf, "server", "cpu_red")

db = NSDb()
app = Bottle()

# 初始化数据库，建表
db.run_all_init_func()


@app.post('/update/')
def update():
    data = request.json
    ns_base_sql = "INSERT OR REPLACE INTO " \
                  "ns_base (hostname, ip, capturetime, cpu, mem, swap, osname, kernel, uptime) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') " % \
                  (data['hostname'], data['ip'], data['capturetime'], data['cpus'], data['mem']['total'], data['mem']['swap_total'], data['platform']['osname'], data['platform']['kernel'], data['uptime'])
    ns_cpu_sql = "INSERT INTO " \
                  "ns_cpu (hostname, ip, capturetime, user_cpu, nice_cpu, system_cpu, iowait_cpu, idle_cpu, usage_cpu, load_avg) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') " % \
                  (data['hostname'], data['ip'], data['capturetime'], data['cpu_usage']['user_cpu'], data['cpu_usage']['nice_cpu'], data['cpu_usage']['system_cpu'], data['cpu_usage']['iowait_cpu'], data['cpu_usage']['idle_cpu'], data['cpu_usage']['usage_cpu'], data['load'])
    ns_mem_sql = "INSERT INTO " \
                 "ns_mem (hostname, ip, capturetime, mem_total, mem_usage, mem_free, swap_total, swap_used, swap_free, mem_percent) " \
                 "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') " % \
                 (data['hostname'], data['ip'], data['capturetime'], data['mem']['total'], data['mem']['usage'], data['mem']['free'], data['mem']['swap_total'], data['mem']['swap_used'], data['mem']['swap_free'], data['mem']['percent'])
    # 注意：list类型插入数据库需要先序列化为json类型
    ns_disk_sql = "INSERT INTO " \
                 "ns_disk (hostname, ip, capturetime, disk, disk_io) " \
                 "VALUES ('%s', '%s', '%s', '%s', '%s') " % \
                 (data['hostname'], data['ip'], data['capturetime'], json.dumps(data['disk']), json.dumps(data['disk_rw']))
    ns_net_sql = "INSERT INTO " \
                  "ns_net (hostname, ip, capturetime, interface, traffic_in, traffic_out, sockets) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s') " % \
                  (data['hostname'], data['ip'], data['capturetime'], data['traffic'][0]['interface'], data['traffic'][0]['traffic_in'], data['traffic'][0]['traffic_out'], json.dumps(data['sockets']))
    all_sql = [ns_base_sql, ns_cpu_sql, ns_mem_sql, ns_disk_sql, ns_net_sql]
    # 暂时取消网络流量采集
    # all_sql = [ns_base_sql, ns_cpu_sql, ns_mem_sql, ns_disk_sql]
    for sql in all_sql:
        # print "[exec_sql--->] {SQL} \n".format(SQL=sql)
        try:
            db.cur.execute(sql)
        except Exception as err:
            print err
    try:
        db.conn.commit()
    except Exception as err:
        print err


@app.route("/assets/<static_filename:re:.*\.css|.*\.js|.*\.png|.*\.jpg|.*\.gif>")
def server_assets(static_filename):
    """
    加载js、css、图片等资源
    """
    assets_path = "./assets"
    return static_file(filename=static_filename, root=assets_path)


@app.route('/', method="GET")
@view("agent_info")
def agent():
    try:
        query_all_agent = """
        SELECT ns_base.hostname, ns_base.ip, ns_mem.mem_percent, ns_cpu.usage_cpu, max(ns_base.capturetime)
                FROM ns_base, ns_mem, ns_cpu where
                ns_base.capturetime=ns_mem.capturetime and
                ns_base.ip=ns_mem.ip and
                ns_base.capturetime=ns_cpu.capturetime and
                ns_base.ip=ns_cpu.ip group by ns_base.hostname, ns_base.ip order by ns_base.ip
        """
        db.cur.execute(query_all_agent)
        query_all_agent_res = db.cur.fetchall()
        server_data = [ns.server_ip, int(ns.server_port)]
        warn_color = map((lambda v: int(v)), [ns.mem_yellow, ns.mem_red, ns.cpu_yellow, ns.cpu_red])
        trans_all_agent_data = [server_data, query_all_agent_res, warn_color]
        all_agent_data = {"result": trans_all_agent_data}
        return all_agent_data
    except Exception as e:
        print e


@app.route('/agent/<ip_hostname>', method="GET")
@view("each_agent_detail")
def show_agent(ip_hostname):
    try:
        # 初始化存储返回信息的字典
        once_agent_res = dict()

        # ---------------------------start: 采集此节点的静态信息-------------------------------------

        show_agent_info = """
            SELECT hostname, ip, cpu, mem, swap, osname, kernel, uptime, max(capturetime)
            FROM ns_base
            WHERE ip = "{IP_H}" or hostname = "{IP_H}"
            GROUP BY ip;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_info)
        # 将查询的结果由元组转为列表
        show_agent_info_res = list(db.cur.fetchall()[0])
        # 将此条数据时间由绝对秒转为yyyymmdd-HH:MM:ss
        now_time = str(time.strftime("%Y%m%d-%H:%M:%S", time.localtime(show_agent_info_res[-1])))
        show_agent_info_res[-1] = now_time
        once_agent_res['agent_static'] = show_agent_info_res

        # ---------------------------start: 采集此节点的所有内存信息-------------------------------------
        show_agent_mem = """
            SELECT capturetime, mem_total, mem_usage, mem_free, swap_total, swap_used, swap_free
            FROM ns_mem
            WHERE ip = "{IP_H}" or hostname = "{IP_H}"
            ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_mem)
        show_agent_mem_temp = db.cur.fetchall()
        # 通过zip逆转采集时间和内存使用量的对应关系:
        unzip_mem = zip(*show_agent_mem_temp)
        once_agent_res['agent_mem'] = unzip_mem

        # ---------------------------start: 采集此节点的CPU信息-------------------------------------

        show_agent_cpu_usage = """SELECT capturetime, usage_cpu, user_cpu, nice_cpu, system_cpu, iowait_cpu
            FROM ns_cpu WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_cpu_usage)
        show_agent_cpu_usage_temp = db.cur.fetchall()
        unzip_cpu_usage = zip(*show_agent_cpu_usage_temp)
        once_agent_res['agent_cpu'] = unzip_cpu_usage

        # ---------------------------start: 采集此节点的负载信息-------------------------------------

        show_agent_load= """SELECT capturetime, load_avg
            FROM ns_cpu WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_load)
        show_agent_load_temp = db.cur.fetchall()
        unzip_load = zip(*show_agent_load_temp)
        # 时间坐标轴复用CPU信息
        show_agent_load_res = list(unzip_load[1])
        once_agent_res['agent_load'] = show_agent_load_res

        # ---------------------------start: 采集此节点的网卡流量信息-------------------------------------

        # show_agent_traffic = """SELECT capturetime, interface, traffic_in, traffic_out
        #     FROM ns_net WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        # db.cur.execute(show_agent_traffic)
        # show_agent_traffic_temp = db.cur.fetchall()
        # unzip_traffic = zip(*show_agent_traffic_temp)
        # once_agent_res['agent_traffic'] = unzip_traffic

        # ---------------------------start: 采集此节点的硬盘读写速度信息-------------------------------------
        show_agent_diskio = """SELECT capturetime, disk_io
            FROM ns_disk WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_diskio)
        show_agent_diskio_temp = db.cur.fetchall()
        unzip_diskio = zip(*show_agent_diskio_temp)
        once_agent_res['agent_diskio'] = unzip_diskio

        # ---------------------------start: 采集此节点的硬盘存储信息-------------------------------------
        show_agent_disk = """SELECT max(capturetime), disk
            FROM ns_disk WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_disk)
        show_agent_disk_temp = db.cur.fetchall()
        show_agent_disk_json = json.loads(show_agent_disk_temp[0][1])
        once_agent_res['agent_disk'] = show_agent_disk_json

        # ---------------------------start: 采集此节点的sockets连接信息-------------------------------------
        show_agent_sockets = """SELECT max(capturetime), sockets
            FROM ns_net WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_sockets)
        show_agent_sockets_temp = db.cur.fetchall()
        show_agent_sockets_json = json.loads(show_agent_sockets_temp[0][1])
        # 因为是表格，不需要时间列，所以直接取[1]
        once_agent_res['agent_sockets'] = show_agent_sockets_json

        all_agent_data = {"result": once_agent_res}

        return all_agent_data
    except BaseException as e:
        print e


if __name__ == '__main__':
    ns = NSConf()
    run(app, host="0.0.0.0", port=int(ns.server_port), debug=ns.debug)
