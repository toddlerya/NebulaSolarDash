#!/usr/bin/env python
# coding: utf-8
# author: qguo

import time
import json
from lib.bottle import request, Bottle, view, run, static_file
from lib.common_lib import re_joint_dir_by_os, get_conf_pat
from init_db import NSDb


class APMConf:
    def __init__(self):
        apm_conf = re_joint_dir_by_os("conf|pf_apm.ini")
        self.server_ip = get_conf_pat(apm_conf, "server", "ip")
        self.server_port = get_conf_pat(apm_conf, "server", "port")
        self.debug = get_conf_pat(apm_conf, "server", "debug")


db = NSDb()
app = Bottle()

# 初始化数据库，建表
db.run_all_init_func()


@app.post('/update/')
def update():
    data = request.json
    print data
    ns_base_sql = "INSERT INTO " \
                  "ns_base (hostname, ip, capturetime, cpu, mem, osname, kernel, uptime) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') " % \
                  (data['hostname'], data['ip'], data['capturetime'], data['cpus'], data['mem']['all'], data['platform']['osname'], data['platform']['kernel'], data['uptime'])
    ns_cpu_sql = "INSERT INTO " \
                  "ns_cpu (hostname, ip, capturetime, cpu_usage, load_avg) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%s') " % \
                  (data['hostname'], data['ip'], data['capturetime'], data['cpu_usage'], data['load'])
    ns_mem_sql = "INSERT INTO " \
                 "ns_mem (hostname, ip, capturetime, mem_all, mem_usage, mem_free, mem_cached, mem_buffers, mem_percent) " \
                 "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') " % \
                 (data['hostname'], data['ip'], data['capturetime'], data['mem']['all'], data['mem']['usage'], data['mem']['free'], data['mem']['cached'], data['mem']['buffers'], data['mem']['percent'])
    # 注意：list类型插入数据库需要先序列化为json类型
    ns_disk_sql = "INSERT INTO " \
                 "ns_disk (hostname, ip, capturetime, disk, disk_read, disk_write) " \
                 "VALUES ('%s', '%s', '%s', '%s', '%s', '%s') " % \
                 (data['hostname'], data['ip'], data['capturetime'], json.dumps(data['disk']), data['disk_rw'][0][1], data['disk_rw'][0][2])
    ns_net_sql = "INSERT INTO " \
                  "ns_net (hostname, ip, capturetime, interface, traffic_in, traffic_out, netstat) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s') " % \
                  (data['hostname'], data['ip'], data['capturetime'], data['traffic'][0]['interface'], data['traffic'][0]['traffic_in'], data['traffic'][0]['traffic_out'], json.dumps(data['netstat']))
    all_sql = [ns_base_sql, ns_cpu_sql, ns_mem_sql, ns_disk_sql, ns_net_sql]
    for sql in all_sql:
        print sql
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
        query_all_agent = """SELECT DISTINCT (ip), hostname FROM ns_base;"""
        db.cur.execute(query_all_agent)
        query_all_agent_res = db.cur.fetchall()
        # print query_all_agent_res
        server_data = [apm.server_ip, int(apm.server_port)]
        trans_all_agent_data = [server_data, query_all_agent_res]
        all_agent_data = {"result": trans_all_agent_data}
        return all_agent_data
    except Exception as e:
        print e


@app.route('/agent/<ip_hostname>', method="GET")
@view("each_agent_detail")
# @view("ubuntu")
def show_agent(ip_hostname):
    try:
        # 初始化存储返回信息的字典
        once_agent_res = dict()

        # ---------------------------start: 采集此节点的静态信息-------------------------------------

        show_agent_info = """
            SELECT hostname, ip, cpu, mem, osname, kernel, uptime, MAX(capturetime)
            FROM ns_base
            WHERE ip = "{IP_H}" or hostname = "{IP_H}"
            GROUP BY ip;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_info)
        # 将查询的结果由元组转为列表
        show_agent_info_res = list(db.cur.fetchall()[0])

        # 将此条数据时间由绝对秒转为yyyymmdd-HH:MM:ss
        now_time = str(time.strftime("%Y%m%d-%H:%M:%S", time.localtime(show_agent_info_res[-1])))
        show_agent_info_res[-1] = now_time

        print "show_agent_info_res--->", show_agent_info_res
        once_agent_res['agent_static'] = show_agent_info_res

        # ---------------------------start: 采集此节点的所有内存信息-------------------------------------
        show_agent_mem = """
            SELECT capturetime, mem_all, mem_usage, mem_free, mem_cached, mem_buffers
            FROM ns_mem
            WHERE ip = "{IP_H}" or hostname = "{IP_H}"
            ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_mem)
        show_agent_mem_temp = db.cur.fetchall()
        print "show_agent_mem_temp--> ", show_agent_mem_temp
        # 通过zip逆转采集时间和内存使用量的对应关系:
        # [(1493087620, u'6186'), (1493087625, u'6186')] ---> [(1493087620, 1493087625), (u'6186', u'6186')]
        unzip_mem = zip(*show_agent_mem_temp)
        print unzip_mem
        once_agent_res['agent_mem'] = unzip_mem

        # 采集此节点的CPU信息
        show_agent_cpu_usage = """SELECT capturetime, cpu_usage
            FROM ns_cpu WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_cpu_usage)
        show_agent_cpu_usage_temp = db.cur.fetchall()
        unzip_cpu_usage = zip(*show_agent_cpu_usage_temp)
        show_agent_cpu_usage_res = ["", ""]
        show_agent_cpu_usage_res[0] = list(unzip_cpu_usage[0])
        show_agent_cpu_usage_res[1] = list(unzip_cpu_usage[1])
        once_agent_res['agent_cpu'] = show_agent_cpu_usage_res

        # 采集此节点的负载信息
        show_agent_load= """SELECT capturetime, load_avg
            FROM ns_cpu WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        db.cur.execute(show_agent_load)
        show_agent_load_temp = db.cur.fetchall()
        unzip_load = zip(*show_agent_load_temp)
        # 时间坐标轴复用CPU信息
        show_agent_load_res = list(unzip_load[1])
        once_agent_res['agent_load'] = show_agent_load_res

        # 采集此节点的网卡信息
        show_agent_net = """SELECT capturetime, interface, traffic_in, traffic_out
            FROM ns_net WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        # db.cur.execute(show_agent_net)
        # show_agent_net_temp = db.cur.fetchall()
        # unzip_net = zip(*show_agent_net_temp)
        # show_agent_net_res = ["", ""]
        # show_agent_net_res[0] = list(unzip_net[0])
        # show_agent_net_res[1] = list(unzip_net[1])
        # show_agent_net_split_detail = map((lambda x: x.split("--")), show_agent_net_res[1])
        # show_agent_net_res[1] = show_agent_net_split_detail
        # print "show_agent_net_res-->", show_agent_net_res
        # once_agent_res['agent_net_use'] = show_agent_net_res

        # print "once_agent_res--->", once_agent_res
        all_agent_data = {"result": once_agent_res}

        return all_agent_data
    except BaseException as e:
        print e


if __name__ == '__main__':
    apm = APMConf()
    run(app, host="0.0.0.0", port=int(apm.server_port), debug=apm.debug)
