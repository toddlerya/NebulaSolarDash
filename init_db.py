#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: toddler
# date: 20170430

import sqlite3
import inspect


class NSDb:
    def __init__(self):
        self.db_name = "ns.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

    def init_ns_base_tb(self):
        init_sql = ('\n'
                    '        CREATE TABLE IF NOT EXISTS ns_base (\n'
                    '          ID INTEGER PRIMARY KEY AUTOINCREMENT,\n'
                    '          HOSTNAME TEXT NOT NULL,\n'
                    '          IP TEXT NOT NULL,\n'
                    '          CAPTURETIME INTEGER NOT NULL,\n'
                    '          CPU TEXT NOT NULL,\n'
                    '          MEM TEXT NOT NULL,\n'
                    '          OSNAME TEXT NOT NULL,\n'
                    '          KERNEL TEXT NOT NULL,\n'
                    '          UPTIME TEXT NOT NULL\n'
                    '        )\n'
                    '        ')
        creat_base_index_sql = "CREATE UNIQUE INDEX [BASE_INDEX] ON [ns_base] ([HOSTNAME], [IP]);"
        self.cur.execute(init_sql)
        try:
            self.cur.execute(creat_base_index_sql)
        except Exception as err:
            print err
        self.conn.commit()

    def init_ns_cpu_tb(self):
        init_sql = ('\n'
                    '        CREATE TABLE IF NOT EXISTS ns_cpu (\n'
                    '          ID INTEGER PRIMARY KEY AUTOINCREMENT,\n'
                    '          HOSTNAME TEXT NOT NULL,\n'
                    '          IP TEXT NOT NULL,\n'
                    '          CAPTURETIME INTEGER NOT NULL,\n'
                    '          CPU_USAGE INTEGER NOT NULL,\n'
                    '          LOAD_AVG INTEGER NOT NULL\n'
                    '        )\n'
                    '        ')
        self.cur.execute(init_sql)
        self.conn.commit()

    def init_ns_mem_tb(self):
        init_sql = ('\n'
                    '        CREATE TABLE IF NOT EXISTS ns_mem (\n'
                    '          ID INTEGER PRIMARY KEY AUTOINCREMENT,\n'
                    '          HOSTNAME TEXT NOT NULL,\n'
                    '          IP TEXT NOT NULL,\n'
                    '          CAPTURETIME INTEGER NOT NULL,\n'
                    '          MEM_ALL INTEGER NOT NULL,\n'
                    '          MEM_USAGE INTEGER NOT NULL,\n'
                    '          MEM_FREE INTEGER NOT NULL,\n'
                    '          MEM_CACHED INTEGER NOT NULL,\n'
                    '          MEM_BUFFERS INTEGER NOT NULL,\n'
                    '          MEM_PERCENT INTEGER NOT NULL\n'
                    '        )\n'
                    '        ')
        self.cur.execute(init_sql)
        self.conn.commit()

    def init_ns_disk_tb(self):
        init_sql = ('\n'
                    '        CREATE TABLE IF NOT EXISTS ns_disk (\n'
                    '          ID INTEGER PRIMARY KEY AUTOINCREMENT,\n'
                    '          HOSTNAME TEXT NOT NULL,\n'
                    '          IP TEXT NOT NULL,\n'
                    '          CAPTURETIME INTEGER NOT NULL,\n'
                    '          DISK TEXT NOT NULL,\n'
                    '          DISK_IO TEXT NOT NULL,\n'
                    '          DISK_READ INTEGER NOT NULL,\n'
                    '          DISK_WRITE INTEGER NOT NULL\n'
                    '        )\n'
                    '        ')
        self.cur.execute(init_sql)
        self.conn.commit()

    def init_ns_net_tb(self):
        init_sql = ('\n'
                    '        CREATE TABLE IF NOT EXISTS ns_net (\n'
                    '          ID INTEGER PRIMARY KEY AUTOINCREMENT,\n'
                    '          HOSTNAME TEXT NOT NULL,\n'
                    '          IP TEXT NOT NULL,\n'
                    '          CAPTURETIME INTEGER NOT NULL,\n'
                    '          INTERFACE TEXT NOT NULL,\n'
                    '          TRAFFIC_IN INTEGER NOT NULL,\n'
                    '          TRAFFIC_OUT INTEGER NOT NULL,\n'
                    '          SOCKETS TEXT NOT NULL\n'
                    '        )\n'
                    '        ')
        self.cur.execute(init_sql)
        self.conn.commit()

    def run_all_init_func(self):
        """
        自动获取NSDb类里的所有init_ns_xxx方法，依次执行建表
        """
        for func in inspect.getmembers(self, predicate=inspect.ismethod):
            if func[0][:7] == 'init_ns':
                func[1]()
