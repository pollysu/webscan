#!/usr/local/bin/python2.7
# encoding: utf-8
"""
@author:     idhyt
@date:    2015.03.04
"""
# 配置文件


class ScanInfoDB:
    def __init__(self):
        self.db_host = ''
        self.db_user = ''
        self.db_pwd = ''
        self.db_name = ''
        self.db_port = 3306
        self.db_table = ''


class VulInfoDB:
    def __init__(self):
        self.db_host = ''
        self.db_user = ''
        self.db_pwd = ''
        self.db_name = ''
        self.db_port = 3306
        self.db_table = ''


class ProxyInfo:
    def __init__(self, current_path):
        # self.count = 3
        self.proxy = [{'server_ip': '', 'client_ip': '127.0.0.1', 'user_name': '', 'pwd': '', 'port': 8010},
                      {'server_ip': '', 'client_ip': '127.0.0.1', 'user_name': '', 'pwd': '', 'port': 8020},
                      {'server_ip': '', 'client_ip': '127.0.0.1', 'user_name': '', 'pwd': '', 'port': 8030}]
        self.count = len(self.proxy)
        self.plink_path = current_path + "\\plink.exe"

