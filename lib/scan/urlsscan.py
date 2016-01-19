#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月19日
@description:
"""
import time

from public.log import log
from sql import vul_info_db
from config import config

from lib.core.xss import xss_scan
from lib.core.sitedir import site_dir_scan
from lib.parse import url as urlparse
from lib.parse import data

from thirdparty.MySQLInject import MySQLInject


class UrlsScan(object):
    def __init__(self, cookie_file, url_src, scan_mode=1, is_proxy=0):
        
        self.scan_mode = scan_mode
        self.cookie_file = cookie_file
        self.url_src = url_src
        self.is_proxy = is_proxy
        self.proxy = None
        
        self.data_parse = data.DataParse()
        self.url_parse = urlparse.UrlParse()
        
        self.urls_scan_go()

    def scan_db_urls(self, cookies):
        # xss and sql
        # 存储类方法初始化
        vul_db_cfg = config.VulInfoDB()
        vul_db_op = vul_info_db.ScanInfo(vul_db_cfg)
        
        # 扫描类方法初始化
        scan_db_cfg = config.ScanInfoDB()
        scan_db_op = vul_info_db.ScanInfo(scan_db_cfg)

        # 开始扫描
        # 获取扫描链接
        while True:
            # xss scan
            if self.scan_mode & 1:
                scan_info_tuple = scan_db_op.get_scan_url(1)
                if scan_info_tuple is None:
                    log.output_log("[*] no url need xss scan in db, please wait...")
                    time.sleep(2*60*60)
                    continue

                url, insert_info = scan_info_tuple[2], scan_info_tuple[:-1]
                if self.url_parse.is_param_url(url) is False:
                    log.output_log("".join(["[xss] valid url, begin get next url..."]))
                    continue

                log.output_log("".join(["[xss] begin scan url ", url]), True)

                # begin scan
                xss = xss_scan.XssScan(url, cookies, self.proxy)
                if len(xss.result) > 0:
                    # # 打印，存文件
                    # parse.output_result(xss.result)
                    xss_info_list = self.data_parse.format_vul_info(xss.result, insert_info)
                    # 漏洞存数据库
                    vul_db_op.save_vul_info_s(xss_info_list)
                else:
                    log.output_log("[xss] not found xss")
      
            # sql scan
            if self.scan_mode & 2:
                scan_info_tuple = scan_db_op.get_scan_url(2)
                if scan_info_tuple is None:
                    log.output_log("[*] no url need sql scan in db, please wait......")
                    time.sleep(2*60*60)
                    continue

                url, insert_info = scan_info_tuple[2], scan_info_tuple[:-1]
                if self.url_parse.is_param_url(url) is False:
                    log.output_log("".join(["[sqlinject] valid url, begin get next url..."]))
                    continue

                log.output_log("".join(["[sqlinject] begin scan url ", url]), True)
                """
                # begin scan #
                sql = sql_scan.SqlScan(url, self.proxy)
                if len(sql.result) > 0:
                    # # 打印，存文件
                    # parse.output_result(sql.result)
                    sql_info_list = self.data_parse.format_vul_info(sql.result, insert_info)
                    # 漏洞存数据库
                    vul_db_op.save_vul_info_s(sql_info_list)
                else:
                    log.output_log("[sql] not found inject")
                """
                # begin scan by
                # update 2015.04.30 by huanghenghui
                sql = MySQLInject.MySQLInject()
                # sql_result = sql.CheckSQLInject("http://special.hi-chic.com/?cat_id=47")
                sql_result = sql.CheckSQLInject(url)
                if sql_result["is_sql_inject"] is not None:
                    vul_info = insert_info + (sql_result["vul_type"], sql_result["vul_detail"], sql_result["vul_url"])
                    # 漏洞存数据库
                    vul_db_op.save_vul_info(vul_info)
                else:
                    log.output_log("[sql] not found inject")

            # site dir scan
            if self.scan_mode & 4:
                log.output_log("[*] test site dir...")
                site_dir = site_dir_scan.SiteDirScan(url, self.proxy)
                if len(site_dir.result) > 0:
                    pass

    def urls_scan_go(self):

        # init
        cookies = self.data_parse.get_cookies(self.cookie_file) if self.cookie_file is not None else None

        # set proxy
        if self.is_proxy == 1:
            from proxy import proxy_switch
            self.proxy = proxy_switch.Proxy()
            proxy_switch.link_proxy(self.proxy)

        if self.url_src == 1:
            self.scan_db_urls(cookies)