#!/usr/bin/env python
# coding: utf-8
# author: qguo
# date: 20170508


from lib.common_lib import re_joint_dir_by_os, get_conf_pat, ColorPrint
import os
import argparse
import sys
import subprocess
import shlex


class APMConf:
    def __init__(self):
        apm_conf = re_joint_dir_by_os("conf|ns.ini")
        self.all_agent_ip = get_conf_pat(apm_conf, "all_agent_ip", "ips")
        self.install_path = get_conf_pat(apm_conf, "agent", "install_path")


def install_start_each_node(_ips, do_type):
    """
    :param _ips pf_ip.ini配置的解析结果，及所有客户端的IP
    :param do_type 执行类型: install-安装, start-启动
    """
    try:
        _ip_list = _ips.split(",")
        ColorPrint.log_normal("[+] 此次安装的节点共计 %s 个" % (len(_ip_list)))
    except Exception as e:
        ColorPrint.log_fail("[-] 解析配置文件失败")
        raise e
    for _ip in _ip_list:
        try:
            os.system("sh start_insall_app.sh {IP} {DO_TYPE}".format(IP=_ip, DO_TYPE=do_type))
        except OSError:
            ColorPrint.log_fail("ERROR: 执行 --> sh start_insall_app.sh {IP} {DO_TYPE} <-- 失败".format(IP=_ip, DO_TYPE=do_type))
            raise OSError


def uninstall_stop_each_node(_ips, do_type):
    """
    :param _ips pf_ip.ini配置的解析结果，及所有客户端的IP
    :param do_type 执行类型: uninstall-卸载, stop-停止
    """
    try:
        _ip_list = _ips.split(",")
        ColorPrint.log_normal("[+] 此次卸载的节点共计 %s 个" % (len(_ip_list)))
    except Exception as e:
        raise e
    for _ip in _ip_list:
        try:
            os.system("sh stop_uninstall_app.sh {IP} {DO_TYPE}".format(IP=_ip, DO_TYPE=do_type))
        except OSError:
            ColorPrint.log_fail("ERROR: 执行 --> sh stop_uninstall_app.sh {IP} {DO_TYPE} <-- 失败".format(IP=_ip, DO_TYPE=do_type))
            print OSError


def start_server():
    """
    启动服务端
    """
    start_server_cmd = "nohup python ns_server.py > log_of_ns_server 2>&1 &"
    try:
        os.system(start_server_cmd)
        ColorPrint.log_high("[+] 启动服务端成功")
    except BaseException as e:
        ColorPrint.log_fail('[-] 启动服务端失败: {C}'.format(C=start_server_cmd))
        raise e


def stop_server():
    """
    停止服务端
    """
    get_pid_server_cmd = """ps aux | grep "ns_server.py" | grep -v grep | awk -F " " '{print $2}'"""
    try:
        server_pid_out = os.popen(get_pid_server_cmd).readlines()
        if len(server_pid_out) == 0:
            ColorPrint.log_normal("[+] 没有需要停止的服务端")
        elif len(server_pid_out) == 1:
            server_pid = server_pid_out[0].strip()
            kill_server_cmd = "kill -9 %s" % server_pid
            try:
                os.system(kill_server_cmd)
                ColorPrint.log_high("[+] 停止服务端成功")
            except BaseException as e:
                ColorPrint.log_fail("[-] 停止服务端失败: %s" % kill_server_cmd)
                print e
    except BaseException as e:
        ColorPrint.log_fail("[-] 获取服务端进程号失败: %s" % get_pid_server_cmd)
        print e


def clean_history_data():
    """
    清理历史数据
    """
    del_old_database = "rm -rf ns.db"
    del_old_run_log = "rm -rf log_of_ns_server"
    try:
        os.system(del_old_database)
        os.system(del_old_run_log)
        ColorPrint.log_high("[+] 删除历史数据成功")
    except BaseException as e:
        ColorPrint.log_fail('[-] 删除历史数据失败: {D}'.format(D=del_old_database))
        print e


def alert_install_path():
    pwd_path = os.getcwd()
    alert_cmd = """find {PWD} -name "*.sh" | xargs sed -ri 's|INSTALL_PATH=.*|INSTALL_PATH="{INSTALL_PATH_ARGS}"|g'""".format(PWD=pwd_path, INSTALL_PATH_ARGS=apm.install_path)
    try:
        os.system(alert_cmd)
        ColorPrint.log_high("[+] 设置安装目录成功: {INSTALL_PATH_ARGS}".format(INSTALL_PATH_ARGS=apm.install_path))
    except Exception as e:
        ColorPrint.log_fail("[-] 设置安装目录失败")
        print e


apm = APMConf()


def installation():
    ColorPrint.log_normal('[+] 开始安装客户端到各个节点并自动启动客户端以及服务端')
    alert_install_path()
    clean_history_data()
    start_server()
    install_start_each_node(apm.all_agent_ip, do_type="install")


def uninstallation():
    ColorPrint.log_normal('[+] 开始停止各个节点的客户端并停止程序清理安装文件，同时停止服务端')
    stop_server()
    uninstall_stop_each_node(apm.all_agent_ip, do_type="uninstall")


def start_all():
    ColorPrint.log_normal('[+] 启动各个节点的客户端并设置crond守护')
    install_start_each_node(apm.all_agent_ip, do_type="start")


def stop_all():
    ColorPrint.log_normal('[+] 停止各个节点的客户端并去除crond守护')
    uninstall_stop_each_node(apm.all_agent_ip, do_type="stop")


def start_one(one_ip):
    ColorPrint.log_normal("[+] 停止%s节点客户端并去除crond守护" % one_ip)
    install_start_each_node(one_ip, do_type="start")


def stop_one(one_ip):
    ColorPrint.log_normal("[+] 启动%s节点客户端并设置crond守护" % one_ip)
    uninstall_stop_each_node(one_ip, do_type="stop")


def main():
    parser = argparse.ArgumentParser(description="Manager Tool")
    parser.add_argument('-install', action='store_true', help='安装客户端到各个节点并自动启动客户端以及服务端')
    parser.add_argument('-uninstall', action='store_true', help='停止各个节点的客户端并停止程序清理安装文件，同时停止服务端')
    parser.add_argument('-startall', action='store_true', help='启动各个节点的客户端并设置crond守护')
    parser.add_argument('-stopall', action='store_true', help='停止各个节点的客户端并去除crond守护')
    parser.add_argument('-start', dest='start_one', action='store', help='启动一个指定节点的客户端并设置crond守护')
    parser.add_argument('-stop', dest='stop_one', action='store', help='停止一个指定节点的客户端并去除crond守护')
    args = parser.parse_args()
    if args.install:
        installation()
    elif args.uninstall:
        uninstallation()
    elif args.startall:
        start_all()
    elif args.stopall:
        stop_all()
    elif args.start_one:
        start_one(args.start_one)
    elif args.stop_one:
        stop_one(args.stop_one)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        ColorPrint.log_normal("==== 请输入-h参数查看帮助说明 ====")
    main()