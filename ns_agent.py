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
        self.ip = socket.gethostbyname(self.hostname)
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

            if osname == '  ':
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
        获取CPU使用率和正在运行的进程
        """
        try:
            pipe = os.popen("ps aux --sort -%cpu,-rss")
            data = pipe.read().strip().split('\n')
            pipe.close()

            usage = [i.split(None, 10) for i in data]
            del usage[0]

            total_usage = []

            for element in usage:
                usage_cpu = element[2]
                total_usage.append(usage_cpu)

            total_usage = sum(float(i) for i in total_usage)

            data = total_usage

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
                net_data1 = os.popen("cat /proc/net/dev |" + "grep " + interface_name + "| awk '{print $1, $9}'")
                net_io_data = net_data1.read().strip().split(':', 1)[-1]
                net_data1.close()

                if not net_io_data[0].isdigit():
                    net_data2 = os.popen("cat /proc/net/dev |" + "grep " + interface_name + "| awk '{print $2, $10}'")
                    net_io_data = net_data2.read().strip().split(':', 1)[-1]
                    net_data2.close()

                net_io_data = net_io_data.split()

                traffic_in = int(net_io_data[0])
                traffic_out = int(net_io_data[1])

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

    def get_netstat(self):
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
            pipe = os.popen("cat /proc/partitions | grep -v 'major' | awk '{print $4}'")
            data = pipe.read().strip().split('\n')
            pipe.close()

            rws = []
            for i in data:
                if i.isalpha():
                    pipe = os.popen("cat /proc/diskstats | grep -w '" + i + "'|awk '{print $4, $8}'")
                    rw = pipe.read().strip().split()
                    pipe.close()

                    rws.append([i, rw[0], rw[1]])

            if not rws:
                pipe = os.popen("cat /proc/diskstats | grep -w '" + data[0] + "'|awk '{print $4, $8}'")
                rw = pipe.read().strip().split()
                pipe.close()

                rws.append([data[0], rw[0], rw[1]])

            data = rws

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
            pipe = os.popen(
                "free -tmo | " + "grep 'Mem' | " + "awk '{print $2,$4,$6,$7}'")
            data = pipe.read().strip().split()
            pipe.close()

            allmem = int(data[0])
            freemem = int(data[1])
            buffers = int(data[2])
            cachedmem = int(data[3])

            # Memory in buffers + cached is actually available, so we count it
            # as free. See http://www.linuxatemyram.com/ for details
            freemem += buffers + cachedmem

            percent = (100 - ((freemem * 100) / allmem))
            usage = (allmem - freemem)

            mem_usage = {'usage': usage,
                         'buffers': buffers,
                         'cached': cachedmem,
                         'free': freemem,
                         'all': allmem,
                         'percent': percent}

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
        print "<----{IP}-info_data-->".format(IP=ig.ip), info_data
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
