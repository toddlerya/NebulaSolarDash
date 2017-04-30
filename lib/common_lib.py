#!/usr/bin/env python
# coding: utf-8
# author: guoqun
# date: 20170103

"""
各种常用类库
"""
import logging
import logging.handlers
from ConfigParser import ConfigParser
from collections import namedtuple
import os
import shutil
import glob
import sys
import time
import datetime
import urllib2


class ColorPrint:
    """
    进行高亮输出运行信息
    """

    def __init__(self):
        pass

    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARING = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    @staticmethod
    def log_normal(info):
        print ColorPrint.OKBLUE + info + ColorPrint.ENDC

    @staticmethod
    def log_high(info):
        print ColorPrint.OKGREEN + info + ColorPrint.ENDC

    @staticmethod
    def log_warn(info):
        print ColorPrint.WARING + info + ColorPrint.ENDC

    @staticmethod
    def log_fail(info):
        print ColorPrint.FAIL + info + ColorPrint.ENDC


class LoadConf(object):
    def __init__(self):
        """
        初始化cfg
        """
        self.cfg = ConfigParser()

    def read_conf(self, ini_file):
        self.cfg.read(ini_file)

    def get_all_sections(self):
        try:
            sec_res = self.cfg.sections()
            return sec_res
        except BaseException, e:
            raise e

    def get_conf_item(self, cm='conf_module', ci='conf_item'):
        try:
            return self.cfg.get(cm, ci)
        except BaseException, e:
            raise e


def get_conf_pat(ini_file, module, ci='conf_item'):
    try:
        lc = LoadConf()
        lc.read_conf(ini_file)
        return lc.get_conf_item(module, ci)
    except Exception, e:
        raise e


def get_all_section(ini_file):
    try:
        lc = LoadConf()
        lc.read_conf(ini_file)
        return lc.get_all_sections()
    except Exception, e:
        raise e


class WriteLog():
    def __init__(self, log_filename):
        # 记录程序运行日志到日志文件
        self.LOG = logging.getLogger('log')
        loghdlr_wl = logging.handlers.RotatingFileHandler(log_filename, "a", 0, 1)
        log_format_wl = logging.Formatter("%(levelname)s:%(asctime)s:%(message)s")
        loghdlr_wl.setFormatter(log_format_wl)
        self.LOG.addHandler(loghdlr_wl)
        self.LOG.setLevel(logging.INFO)

    def wl_info(self, msg, *args, **kwargs):
        if self.LOG is not None:
            self.LOG.info(msg)

    def wl_error(self, msg, *args, **kwargs):
        if self.LOG is not None:
            self.LOG.error(msg)


class SaveRes():
    def __init__(self, res_filename):
        # 记录结果到结果文件
        self.RES = logging.getLogger('res')
        loghdlr_sr = logging.handlers.RotatingFileHandler(res_filename, "w", 0, 1)
        log_format_sr = logging.Formatter("%(message)s")
        loghdlr_sr.setFormatter(log_format_sr)
        self.RES.addHandler(loghdlr_sr)
        self.RES.setLevel(logging.INFO)

    def sr_save(self, msg, *args, **kwargs):
        if self.RES is not None:
            self.RES.info(msg)


def re_joint_dir_by_os(input_path):
    """
    根据系统来判断文件夹的分隔符来拼接目录的路径
    :param input_path 为需要拼接的目录参数；example: .|dir_a|dir_b|...|dir_n
    :return jointed_dir 根据系统判断后拼接后的目录
            example: linux: ./dir_a/dir_b/.../dir_n
                     windows: .\dir_a\dir_b\...\dir_n
    """
    try:
        splited_dir = input_path.split('|')
        jointed_dir = os.path.sep.join(splited_dir)
        return jointed_dir
    except BaseException, e:
        raise e


def clean(del_path=""):
    # 删除del_path, 若不存在则跳过重新创建（包括上层父目录）
    try:
        if os.path.exists(del_path):
            shutil.rmtree(del_path)
        else:
            pass
    except BaseException, e:
        ColorPrint.log_fail("删除{D}失败".format(D=del_path))
        sys.exit()
    time.sleep(0.5)
    try:
        os.makedirs(del_path)
    except BaseException, e:
        ColorPrint.log_fail("创建{D}失败".format(D=del_path))
        sys.exit()


def get_files_path(path, suffix):
    """
    模块作用：获取当前路径下所有指定后缀文件的绝对路径, 返回一个列表
    :param path 待获取文件的绝对目录
    :param suffix 待获取文件的后缀, 例如：txt
    """
    try:
        files = glob.glob("{P}/*.{S}".format(P=path, S=suffix))
        return files
    except Exception, e:
        ColorPrint.log_fail("获取{P}路径下以{S}为后缀的文件失败".format(P=path, S=suffix))
        raise e


Token = namedtuple('Token', ['type', 'value'])


def generate_tokens(pat, text):
    try:
        scanner = pat.scanner(text)
        for m in iter(scanner.match, None):
            yield Token(m.lastgroup, m.group())
    except Exception, e:
        raise e


def read_log(log_path):
    try:
        with open(log_path.decode('utf8').encode('gbk'), 'r') as lf:
            log_content = []
            for item in lf:
                if item == '\n':
                    pass
                else:
                    log_content.append(item.strip())
        return log_content
    except Exception, e:
        raise e


def get_all_files(cur_path):
    """
    获取module对应的log_path路径下所有的log日志,返回一个文件绝对路径的列表
    """
    logs_list = []
    for root, dirs, files in os.walk(cur_path.decode("utf-8")):
        for item_file in files:
            log_file = os.path.join(root, item_file)
            logs_list.append(log_file)
    return logs_list


def assert_check_point(wl, left_exception, right_exception, msg):
    # 断言检查点是否测试通过, 否则提示错误信息
    try:
        assert left_exception == right_exception
        return True
    except:
        ColorPrint.log_fail(msg)
        wl.wl_info(msg)
        return False


def localtime():
    """
    返回系统当前系统时间的绝对秒数，返回类型int
    example
    print localtime()
    1372323607
    :return:返回绝对秒数，int类型
    """
    return int(time.time())


def timetoint(*args):
    """
    #接受时间参数返回绝对秒数
    :param args:表示指定时间数字，如下例子所示
    :return:返回绝对秒数，int类型
    #使用示例
    #print timetoint(2013,1,5) ---1357315200
    #print timetoint(2013,01,5) ---1357315200
    #print timetoint(2013,01,5,9,50) ---1357350600
    #print timetoint(2013,01,5,9,01,50) ---1357347710
    """
    return int(time.mktime(datetime.datetime(*args).timetuple()))


def today_time(day=0):
    """
    #返回与当前日志相隔day的日期，返回类型str 如“20140909”,
    #day=正数表示未来几天的那天，负数过去几天的那天，0表示今天
    :param day:与当前日期相隔天数
    :return:返回日期，str类型
    """
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=int(day) * (-1))
    n_days = now - delta
    return n_days.strftime('%Y%m%d')


def daytimetoint(day=None, times=None):
    """
    #表示与当前时间相隔day天的time的时间转化成绝对秒数，返回格式int类型
    :param day:与当前日期相隔天数，数据类型int或者str
    :param time:需要转化的具体时间，如“112230” 表示11点22分30s，数据类型str
    :return:返回绝对秒数，int类型
    """
    day1time = int(time.mktime(time.strptime(today_time(int(day)) + times, "%Y%m%d%H%M%S")))
    return day1time


def today_start_time(offset=0):
    """
    返回当天日期的最早时间绝对秒数
    :param offset 日期偏移量, int或者str, 正整数为未来时间, 负整数为过去时间
    :return 返回绝对秒数，int类型
    """
    return daytimetoint(day=offset, times='000000')


def today_cur_time(offset=0):
    """
    返回当前时间的绝对秒数
    :param offset 日期偏移量, int或者str, 正整数为未来时间, 负整数为过去时间
    :return 返回绝对秒数，int类型
    """
    today_tuple = datetime.datetime.today()
    h = str(today_tuple.hour).zfill(2)
    m = str(today_tuple.minute).zfill(2)
    s = str(today_tuple.second).zfill(2)
    the_times = "%2s%2s%2s" % (h, m, s)
    return daytimetoint(day=offset, times=the_times)


def today_last_time(offset=0):
    """
    返回当天日期的最晚时间绝对秒数
    :param offset 日期偏移量, int或者str, 正整数为未来时间, 负整数为过去时间
    :return 返回绝对秒数，int类型
    """
    return daytimetoint(day=offset, times='235959')


def div_list(a_list, part):
    """
    均分一个列表
    :param a_list 待分割的列表 list 类型
    :param part 需要分割为几部分 int 类型
    """
    if not isinstance(a_list, list) or not isinstance(part, int):
        return []
    len_list = len(a_list)
    if part <= 0 or 0 == len_list:
        return []
    if part > len_list:
        return []
    elif part == len_list:
        return [[i] for i in a_list]
    else:
        j = len_list / part
        k = len_list % part
        # j,j,j,...(前面有n-1个j),j+k
        # 步长j,次数n-1
        split_res_list = []
        for i in xrange(0, (part-1) * j, j):
            split_res_list.append(a_list[i:i+j])
        # 算上末尾的j+k
        split_res_list.append(a_list[(part-1)*j:])
        return split_res_list


