#!/usr/bin/env python
# coding: utf-8
# author: qguo

from lib.bottle import request, Bottle, view, run, static_file
from lib.common_lib import re_joint_dir_by_os, get_conf_pat
import sqlite3
import time


class APMConf:
    def __init__(self):
        apm_conf = re_joint_dir_by_os("conf|pf_apm.ini")
        self.server_ip = get_conf_pat(apm_conf, "server", "ip")
        self.server_port = get_conf_pat(apm_conf, "server", "port")
        self.debug = get_conf_pat(apm_conf, "server", "debug")


class ApmDB:
    # todo 其实应该分两张表：一张静态节点信息表，一张动态信息表
    def __init__(self):
        self.db_name = "pf_apm.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()
        init_sql = """
        CREATE TABLE IF NOT EXISTS platform_apm (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          HOSTNAME TEXT NOT NULL,
          IP TEXT NOT NULL,
          CAPTURETIME INTEGER NOT NULL,
          CPU TEXT NOT NULL,
          CPU_USAGE FLOAT NOT NULL,
          LOAD TEXT NOT NULL,
          TRAFFIC TEXT NOT NULL,
          NETSTAT TEXT NOT NULL,
          MEM TEXT NOT NULL,
          DISK TEXT NOT NULL,
          DISK_RW TEXT NOT NULL,
          PLATFORM TEXT NOT NULL,
          UPTIME TEXT NOT NULL
        )
        """
        self.cur.execute(init_sql)
        self.conn.commit()


adb = ApmDB()
app = Bottle()


@app.post('/update/')
def update():
    insert_sql = ""
    insert_data = request.json
    print insert_data
    try:
        insert_sql = """
        INSERT INTO
        platform_apm (HOSTNAME, IP, CAPTURETIME, CPU, CPU_USAGE, LOAD, TRAFFIC, MEM_TOTAL, MEM_USE, MEM_FREE)
        VALUES
        ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")""" \
        % (insert_data['hostname'], insert_data['ip'], insert_data['capturetime'], insert_data['cpu_info'], insert_data['CPU_USAGE'],
           insert_data['load'], insert_data['traffic'], insert_data['mem_total'], insert_data['mem_use'], insert_data['mem_free'])
        adb.cur.execute(insert_sql)
        adb.conn.commit()
    except sqlite3.IntegrityError as e:
        print e


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
        query_all_agent = """SELECT DISTINCT (ip), hostname FROM platform_apm;"""
        adb.cur.execute(query_all_agent)
        query_all_agent_res = adb.cur.fetchall()
        # print query_all_agent_res
        server_data = [apm.server_ip, int(apm.server_port)]
        trans_all_agent_data = [server_data, query_all_agent_res]
        all_agent_data = {"result": trans_all_agent_data}
        return all_agent_data
    except sqlite3.IntegrityError as e:
        print e


@app.route('/agent/<ip_hostname>', method="GET")
# @view("each_agent_detail")
@view("ubuntu")
def show_agent(ip_hostname):
    try:
        # 初始化存储返回信息的字典
        once_agent_res = dict()

        # 采集此节点的静态信息
        show_agent_info = """SELECT hostname, ip, cpu, LOAD, mem_total, MAX(capturetime) FROM platform_apm WHERE ip = "{IP_H}" or hostname = "{IP_H}" GROUP BY ip;""".format(IP_H=ip_hostname)
        # print "exec show_agent_info ---> ", show_agent_info
        adb.cur.execute(show_agent_info)
        show_agent_info_res = adb.cur.fetchall()
        # print "show_agent_info_res", show_agent_info_res
        now_time = str(time.strftime("%Y%m%d-%H:%M:%S", time.localtime(show_agent_info_res[0][-1])))
        show_agent_info_res = list(show_agent_info_res[0])
        show_agent_info_res[-1] = now_time
        once_agent_res['agent_static'] = show_agent_info_res

        # 采集此节点的所有内存信息
        show_agent_mem_use = """SELECT capturetime, mem_use FROM platform_apm WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        # print "exec show_agent_mem_usage ---> ", show_agent_mem_usage
        adb.cur.execute(show_agent_mem_use)
        show_agent_mem_use_temp = adb.cur.fetchall()
        # print "show_agent_mem_use_temp--> ", show_agent_mem_use_temp
        # 通过zip逆转采集时间和内存使用量的对应关系:
        # [(1493087620, u'6186'), (1493087625, u'6186')] ---> [(1493087620, 1493087625), (u'6186', u'6186')]
        unzip_mem_use = zip(*show_agent_mem_use_temp)
        # print 'show_agent_mem_use -->', show_agent_mem_use
        show_agent_mem_use_res = ["", ""]
        # 将绝对秒转为年月日时分秒
        # show_agent_mem_usage_res[0] = map((lambda t: (time.strftime("%Y%m%d-%H:%M:%S", time.localtime(t)))), list(unzip_mem_usage[0]))
        # show_agent_mem_usage_res[0] = ["20170426-16:52:48", "20170426-16:52:53", "20170426-16:52:59"]
        show_agent_mem_use_res[0] = list(unzip_mem_use[0])
        show_agent_mem_use_res[1] = list(unzip_mem_use[1])
        once_agent_res['agent_mem_use'] = show_agent_mem_use_res

        # 采集此节点的CPU信息
        show_agent_CPU_USAGE = """SELECT capturetime, CPU_USAGE FROM platform_apm WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        adb.cur.execute(show_agent_CPU_USAGE)
        show_agent_CPU_USAGE_temp = adb.cur.fetchall()
        unzip_CPU_USAGE = zip(*show_agent_CPU_USAGE_temp)
        show_agent_CPU_USAGE_res = ["", ""]
        show_agent_CPU_USAGE_res[0] = list(unzip_CPU_USAGE[0])
        show_agent_CPU_USAGE_res[1] = list(unzip_CPU_USAGE[1])
        once_agent_res['agent_CPU_USAGE'] = show_agent_CPU_USAGE_res

        # 采集此节点的网卡信息
        show_agent_net = """SELECT capturetime, net FROM platform_apm WHERE ip = "{IP_H}" or hostname = "{IP_H}"  ORDER BY capturetime;""".format(IP_H=ip_hostname)
        adb.cur.execute(show_agent_net)
        show_agent_net_temp = adb.cur.fetchall()
        unzip_net = zip(*show_agent_net_temp)
        show_agent_net_res = ["", ""]
        show_agent_net_res[0] = list(unzip_net[0])
        show_agent_net_res[1] = list(unzip_net[1])
        show_agent_net_split_detail = map((lambda x: x.split("--")), show_agent_net_res[1])
        show_agent_net_res[1] = show_agent_net_split_detail
        print "show_agent_net_res-->", show_agent_net_res
        once_agent_res['agent_net_use'] = show_agent_net_res

        print "once_agent_res--->", once_agent_res
        all_agent_data = {"result": once_agent_res}

        return all_agent_data
    except BaseException as e:
        print e


if __name__ == '__main__':
    apm = APMConf()
    run(app, host="0.0.0.0", port=int(apm.server_port), debug=apm.debug)
