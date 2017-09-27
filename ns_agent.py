#!/usr/bin/env python
# coding: utf-8
# author: qguo

import inspect
import socket
import time
import os
import json
import urllib2
import multiprocessing
import platform
from datetime import timedelta
from lib.common_lib import re_joint_dir_by_os, get_conf_pat


class NSConf:
    def __init__(self):
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")
        self.server_port = get_conf_pat(ns_conf, "server", "port")
        self.agent_interval = get_conf_pat(ns_conf, "agent", "interval")


class InfoGather:
    """
    进程采集
    """

    def __init__(self):
        """
        初始化信息采集类的一些公用信息
        """
        self.agent_data = dict()
        self.now_capture_time = int(time.time())
        self.hostname = socket.gethostname()
        # ------------------------ b1gw00d ------------------------------
        # fix: b1gw00d --> https://github.com/toddlerya/NebulaSolarDash/issues/8
        try:
            csock =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            csock.connect(('8.8.8.8',80))
            (addr,port)=csock.getsockname()
            csock.close()
            self.ip = addr
        except socket.error:
            self.ip = '127.0.0.1'
        # ------------------------ b1gw00d ------------------------------
        # self.ip = socket.gethostbyname(self.hostname)
        self.agent_data['hostname'] = self.hostname
        self.agent_data['ip'] = self.ip
        self.agent_data['capturetime'] = self.now_capture_time

    # ----------------start: 获取服务器操作系统信息-----------------

    def get_platform(self):
        """
        Get the OS name, hostname and kernel
        """
        try:
            osname = " ".join(platform.linux_distribution())
            uname = platform.uname()

            if osname == ' ':
                osname = uname[0]

            data = {'osname': osname, 'hostname': uname[1], 'kernel': uname[2]}

        except Exception as err:
            print err
            data = str(err)

        return data

    # ----------------end: 获取服务器操作系统信息-----------------

    # ----------------start: 获取服务器运行时长以及负载信息-----------------

    def get_uptime(self):
        """
        获取服务器运行时间信息
        """
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_time = str(timedelta(seconds=uptime_seconds))
                data = uptime_time.split('.', 1)[0]

        except Exception as err:
            print err
            data = str(err)

        return data

    def get_load(self):
        """
        获取系统平均负载信息
        """
        try:
            data = os.getloadavg()[0]
        except Exception as err:
            print err
            data = str(err)

        return data

    # ----------------end: 获取服务器运行时长以及负载信息-----------------

    # ----------------start: 获取CPU相关信息-----------------

    def get_cpus(self):
        """
        获取CPU型号等相关硬件信息
        """
        try:
            pipe = os.popen("cat /proc/cpuinfo |" + "grep 'model name'")
            data = pipe.read().strip().split(':')[-1]
            pipe.close()

            if not data:
                pipe = os.popen("cat /proc/cpuinfo |" + "grep 'Processor'")
                data = pipe.read().strip().split(':')[-1]
                pipe.close()

            cpus = multiprocessing.cpu_count()

            data = "{CPUS} x {CPU_TYPE}".format(CPUS=cpus, CPU_TYPE=data)

        except Exception as err:
            print err
            data = str(err)

        return data

    def get_cpu_usage(self):
        """
        获取CPU使用率
        """
        try:
            cpu_pipe = os.popen("iostat").readlines()
            cpu_res = [line.strip("\n").split() for line in cpu_pipe]
            cpu_data = cpu_res[3]
            user_cpu = float(cpu_data[0])
            nice_cpu = float(cpu_data[1])
            system_cpu = float(cpu_data[2])
            iowait_cpu = float(cpu_data[3])
            steal_cpu = float(cpu_data[4])
            idle_cpu = float(cpu_data[5])

            usage_cpu = 100.0 - idle_cpu

            cpu_usage_data = {
                'user_cpu': user_cpu,
                'nice_cpu': nice_cpu,
                'system_cpu': system_cpu,
                'iowait_cpu': iowait_cpu,
                'steal_cpu': steal_cpu,
                'idle_cpu': idle_cpu,
                'usage_cpu': usage_cpu
            }

            data = cpu_usage_data

        except Exception as err:
            print err
            data = str(err)

        return data

    # ----------------end: 获取CPU相关信息-----------------

    # ----------------start: 获取网络相关信息-----------------

    def get_traffic(self):
        """
        获取网卡流量信息
        """

        def net_io(interface_name):
            """
            获取某个网卡的流量信息
            :param interface_name 网卡的名字
            """
            try:
                net_data = os.popen("cat /proc/net/dev |" + "grep " + interface_name + "| awk '{print $1, $9}'")
                net_io_data = net_data.read().strip().split(':', 1)[-1]
                net_data.close()

                if not net_io_data[0].isdigit():
                    net_data = os.popen("cat /proc/net/dev |" + "grep " + interface_name + "| awk '{print $2, $10}'")
                    net_io_data = net_data.read().strip().split(':', 1)[-1]
                    net_data.close()

                net_io_data = net_io_data.split()
                traffic_in = int(net_io_data[0]) / 1024
                traffic_out = int(net_io_data[1]) / 1024

                all_traffic = {'interface': interface_name, 'traffic_in': traffic_in, 'traffic_out': traffic_out}

                interface_data = all_traffic

            except Exception as err:
                print err
                interface_data = str(err)

            return interface_data

        net_data = list()

        try:
            eth = os.popen("ip addr | grep LOWER_UP | awk '{print $2}'")
            iface = eth.read().strip().replace(':', '').split('\n')
            eth.close()
            del iface[0]

            for i in iface:
                pipe = os.popen("ip addr show " + i + "| awk '{if ($2 == \"forever\"){!$2} else {print $2}}'")
                data1 = pipe.read().strip().split('\n')
                pipe.close()
                if len(data1) == 2:
                    data1.append('unavailable')
                if len(data1) == 3:
                    data1.append('unavailable')
                data1[0] = i
                net_data.append(data1)

            all_iface_data = list()

            for net in net_data:
                net_card_ip = net[2].strip().split("/")[0]
                if self.ip == net_card_ip:
                    all_iface_data.append(net_io(net[0]))

        except Exception as err:
            print err
            all_iface_data = str(err)

        return all_iface_data

    def get_sockets(self):
        """
        获取端口号和应用
        """
        try:
            pipe = os.popen(
                "ss -tnp | grep ESTAB | awk '{print $4, $5}'| sed 's/::ffff://g' | awk -F: '{print $1, $2}' "
                "| awk 'NF > 0' | sort -n | uniq -c")
            data = pipe.read().strip().split('\n')
            pipe.close()

            data = [i.split(None, 4) for i in data]

        except Exception as err:
            print err
            data = str(err)

        return data

    # ----------------end: 获取网络相关信息-----------------

    # ----------------start: 获取硬盘相关信息-----------------

    def get_disk(self):
        """
        获取硬盘使用量
        """
        try:
            pipe = os.popen("df -Ph | " + "grep -v Filesystem | " + "awk '{print $1, $2, $3, $4, $5, $6}'")
            data = pipe.read().strip().split('\n')
            pipe.close()

            data = [i.split(None, 6) for i in data]

        except Exception as err:
            print err
            data = str(err)

        return data

    def get_disk_rw(self):
        """
        通过/proc/diskstats获取硬盘的读写速度
        第4个域：读花费的毫秒数，这是所有读操作所花费的毫秒数；//基准
        第8个域：写花费的毫秒数，这是所有写操作所花费的毫秒数；//基准
        """
        try:
            # disk_io_dict = dict()
            disk_io_pipe = os.popen("iostat -kx").readlines()
            disk_io_res = [line.strip("\n").split() for line in disk_io_pipe]
            disk_io_data = disk_io_res[6:-1]
            # for each_device in disk_io_data:
            #     disk_io_device = str(each_device[0])
            #     each_device_value = {
            #     'disk_io_rrqm_s': float(each_device[1]),
            #     'disk_io_wrqm_s': float(each_device[2]),
            #     'disk_io_r_s': float(each_device[3]),
            #     'disk_io_w_s': float(each_device[4]),
            #     'disk_io_rkb_s': float(each_device[5]),
            #     'disk_io_wkb_s': float(each_device[6]),
            #     'disk_io_avgrq_sz': float(each_device[7]),
            #     'disk_io_avgqu_sz': float(each_device[8]),
            #     'disk_io_await': float(each_device[9]),
            #     'disk_io_util': float(each_device[10])
            #     }
            #     disk_io_dict[disk_io_device] = each_device_value
            """
            ================================disk_io_data数据示例==========================
            数据的每一列题头：
            ['Device:',  'rrqm/s',  'wrqm/s',  'r/s',  'w/s',  'rkB/s',  'wkB/s',  'avgrq-sz',  'avgqu-sz',  'await',  'svctm',  '%util']
            实际的disk_io_data数据
            [
             ['sda',  '0.00',  '33.75',  '0.11',  '5.63',  '1.01',  '157.55',  '55.25',  '0.02',  '4.02',  '0.38',  '0.22'],
             ['sdb',  '0.00',  '2.30',  '0.02',  '1.13',  '0.57',  '13.69',  '24.84',  '0.00',  '0.78',  '0.32',  '0.04'],
             ['sdc',  '0.00',  '2.36',  '0.01',  '1.20',  '0.21',  '14.22',  '23.88',  '0.00',  '0.40',  '0.17',  '0.02']
            ]

            """
            data = disk_io_data

        except Exception as err:
            print err
            data = str(err)

        return data

    # ----------------end: 获取硬盘相关信息-----------------

    # ----------------start: 获取内存相关信息-----------------

    def get_mem(self):
        """
        获取内存使用量信息
        """
        try:
            mem_pipe = os.popen("free -m").readlines()
            # 有名没有swap分区就看这里了,
            if len(mem_pipe) == 3:
                # 没有swap分区
                mem_res = [line.strip("\n").split() for line in mem_pipe]
                total_mem = int(mem_res[1][1])
                total_used = int(mem_res[2][2])
                total_free = int(mem_res[2][3])
                swap_total = 0
                swap_used = 0
                swap_free = 0
                percent = (100 - ((total_free * 100) / total_mem))
            elif len(mem_pipe) == 4:
                # 有swap分区
                mem_res = [line.strip("\n").split() for line in mem_pipe]
                total_mem = int(mem_res[1][1])
                total_used = int(mem_res[2][2])
                total_free = int(mem_res[2][3])
                swap_total = int(mem_res[3][1])
                swap_used = int(mem_res[3][2])
                swap_free = int(mem_res[3][3])
                percent = (100 - ((total_free * 100) / total_mem))
            else:
                # 出错了, 未知情况
                total_mem = 0
                total_used = 0
                total_free = 0
                swap_total = 0
                swap_used = 0
                swap_free = 0
                percent = 0

            mem_usage = {'total': total_mem,
                         'usage': total_used,
                         'free': total_free,
                         'swap_total': swap_total,
                         'swap_used': swap_used,
                         'swap_free': swap_free,
                         'percent': percent}

            # print 'mem_usage-->', mem_usage

            data = mem_usage

        except Exception as err:
            print err
            data = str(err)

        return data

    # ----------------end: 获取内存相关信息-----------------

    def run_all_get_func(self):
        """
        自动获取InfoGather类里的所有get_xxx方法，用xxx作为key，get_xxx()的返回值作为value，构造字典
        """
        for func in inspect.getmembers(self, predicate=inspect.ismethod):
            if func[0][:3] == 'get':
                self.agent_data[func[0][4:]] = func[1]()
        return self.agent_data


def gather_agent(ip, port, interval=60):
    """
    :param ip 服务端ip
    :param port 服务端端口号
    :param interval 间隔时间, 单位s
    """
    while True:
        ig = InfoGather()
        info_data = ig.run_all_get_func()
        # print "<----{IP}-info_data-->".format(IP=ig.ip), info_data
        try:
            req = urllib2.Request("http://{IP}:{PORT}/update/".format(IP=ip, PORT=port), json.dumps(info_data), {'Content-Type': 'application/json'})
            f = urllib2.urlopen(req)
            response = f.read()
            print response
            f.close()
        except Exception as e:
            print e
        time.sleep(int(interval))


def main():
    apm = NSConf()
    gather_agent(ip=apm.server_ip, port=int(apm.server_port), interval=apm.agent_interval)


if __name__ == '__main__':
    main()
