#!/usr/bin/env python
# coding: utf-8
# author: qguo
# date：20170407


from lib.common_lib import re_joint_dir_by_os, get_conf_pat
import os


class APMConf:
    def __init__(self):
        apm_conf = re_joint_dir_by_os("conf|ns.ini")
        self.all_agent_ip = get_conf_pat(apm_conf, "all_agent_ip", "ips")


def uninstall_to_each_node(_ips):
    """
    :param _ips pf_ip.ini配置的解析结果，及所有客户端的IP
    """
    try:
        _ip_list = _ips.split(",")
        print "此次卸载的节点共计 %s 个" % (len(_ip_list))
    except Exception as e:
        raise e
    for _ip in _ip_list:
        try:
            os.system("sh uninstall_app.sh {IP}".format(IP=_ip))
        except OSError:
            print OSError
            print "ERROR: 执行 --> sh uninstall_app.sh {IP} <-- 失败".format(IP=_ip)


def stop_server():
    stop_server_cmd = """ps aux | grep "ns_server.py" | grep -v grep | awk -F " " '{print $2}' | xargs kill -9"""
    try:
        os.system(stop_server_cmd)
        print "停止服务端成功"
    except BaseException as e:
        print e
        print '停止服务端失败: %s' % stop_server_cmd


def main():
    apm = APMConf()
    stop_server()
    uninstall_to_each_node(apm.all_agent_ip)


if __name__ == '__main__':
    main()