#!/usr/bin/env python
# coding: utf-8
# author: qguo
# date：20170407


from lib.common_lib import re_joint_dir_by_os, get_conf_pat, ColorPrint
import os


class APMConf:
    def __init__(self):
        apm_conf = re_joint_dir_by_os("conf|ns.ini")
        self.all_agent_ip = get_conf_pat(apm_conf, "all_agent_ip", "ips")
        self.install_path = get_conf_pat(apm_conf, "agent", "install_path")


def install_to_each_node(_ips):
    """
    :param _ips pf_ip.ini配置的解析结果，及所有客户端的IP
    """
    try:
        _ip_list = _ips.split(",")
        ColorPrint.log_normal("此次安装的节点共计 %s 个" % (len(_ip_list)))
    except Exception as e:
        ColorPrint.log_fail("解析配置文件失败")
        raise e
    for _ip in _ip_list:
        try:
            os.system("sh install_app.sh {IP}".format(IP=_ip))
        except OSError:
            ColorPrint.log_fail("ERROR: 执行 --> sh install_app.sh {IP} <-- 失败".format(IP=_ip))
            raise OSError


def start_server():
    start_server_cmd = "nohup python ns_server.py &"
    try:
        os.system(start_server_cmd)
        ColorPrint.log_high("启动服务端成功")
    except BaseException as e:
        ColorPrint.log_fail('启动服务端失败: {C}'.format(C=start_server_cmd))
        raise e


def clean_history_data():
    del_old_database = "rm -rf ns.db"
    try:
        os.system(del_old_database)
        ColorPrint.log_high("删除历史数据成功")
    except BaseException as e:
        ColorPrint.log_fail('删除历史数据失败: {D}'.format(D=del_old_database))
        print e


def alert_install_path():
    pwd_path = os.getcwd()
    alert_cmd = """find {PWD} -name "*.sh" | xargs sed -ri 's|INSTALL_PATH=.*|INSTALL_PATH="{INSTALL_PATH_ARGS}"|g'""".format(PWD=pwd_path, INSTALL_PATH_ARGS=apm.install_path)
    try:
        os.system(alert_cmd)
        ColorPrint.log_high("设置安装目录成功: {INSTALL_PATH_ARGS}".format(INSTALL_PATH_ARGS=apm.install_path))
    except Exception as e:
        ColorPrint.log_fail("设置安装目录失败")
        print e


apm = APMConf()


def main():
    alert_install_path()
    clean_history_data()
    start_server()
    install_to_each_node(apm.all_agent_ip)


if __name__ == '__main__':
    main()
