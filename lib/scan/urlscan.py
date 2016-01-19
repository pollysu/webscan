#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月19日
@description:
"""

from public.log import log
from lib.core.sqlinject import sql_scan
from lib.core.xss import xss_scan
from lib.core.sitedir import site_dir_scan
from lib.parse import url as urlparse
from lib.parse import data


class UrlScan(object):
    def __init__(self, url, scan_mode, cookie_file, is_proxy=0):
        self.url = url
        self.scan_mode = scan_mode
        self.cookie_file = cookie_file
        self.is_proxy = is_proxy
        self.proxy = None
        
        self.data_parse = data.DataParse()
        self.url_parse = urlparse.UrlParse()
        
        self.url_scan_go()
        
    def scan_url(self, cookies):

        if self.scan_mode & 1:
            log.output_log("[*] test xss...")
            xss = xss_scan.XssScan(self.url, cookies, self.proxy)
            if len(xss.result) > 0:
                pass
            
        if self.scan_mode & 2:
            log.output_log("[*] test sql inject...")
            sql = sql_scan.SqlScan(self.url, self.proxy)
            if len(sql.result) > 0:
                pass
    
        if self.scan_mode & 4:
            log.output_log("[*] test site dir...")
            site_dir = site_dir_scan.SiteDirScan(self.url, self.proxy)
            if len(site_dir.result) > 0:
                pass

    def url_scan_go(self):
        if self.url_parse.is_param_url(self.url) is False:
            log.output_log("[*] url need params %s" % self.url)
            return False

        cookies = self.data_parse.get_cookies(self.cookie_file) if self.cookie_file is not None else None
        # set proxy
        if self.is_proxy == 1:
            from proxy import proxy_switch
            self.proxy = proxy_switch.Proxy()
            proxy_switch.link_proxy(self.proxy)

        self.scan_url(cookies)