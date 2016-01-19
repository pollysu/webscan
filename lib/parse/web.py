#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年4月2日
@description:
"""

import re
from thirdparty import requests
from proxy import proxy_switch
from public.log import log


class WebSite(object):
    def __init__(self, proxy):
        self.proxy = proxy
        self.timeout = 3

    # function : get page source and charset
    # return : [html, encoding] / None
    def get_page_source_info(self, url, headers, cookies, times=0):
        if times < 3:
            try:
                # test proxy
                # proxy_switch.link_proxy(self.proxy)
                req = requests.get(url, headers=headers, cookies=cookies, timeout=self.timeout)
                if req.status_code == 200:
                    # 获取网页编码
                    encoding = None
                    try:
                        encoding = req.apparent_encoding
                        if encoding is not None:
                            encoding = encoding.lower()
                            encoding = encoding if 'utf' in encoding or 'gbk' in encoding else None
                    except Exception, e:
                        log.output_log("".join(["[error] ", str(e)]), True)

                    encoding = self.get_page_charset(req.content) if encoding is None else encoding
                    req.encoding = "utf-8" if encoding is None else encoding
                    html = req.text
                    req.close()
                    return [html, encoding]
                
                if req.status_code == 403:
                    times += 1
                    log.output_log("[error] 403 and try to connet %d" % times, True)
                    proxy_switch.link_proxy(self.proxy)
                    self.get_page_source_info(url, headers, cookies, times)
                return None
            
            except Exception, e:
                log.output_log("".join(["[error] ", str(e)]), True)
                return None
            
    # 获取文本编码
    def get_page_charset(self, page_source):
        try:
            coding = None
            data_lines = page_source.split('\n')
    #         '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
    #         '<meta charset="utf-8">
            regex = re.compile(r'<meta[\S\s]+charset *= *["\']?([a-zA-Z-0-9]+)["\']?', re.IGNORECASE)
            for line in data_lines:
                # 分块进行检测
                pattern = regex.search(line)
                if pattern:
                    coding = pattern.group(1)
            return coding 
        except Exception, e:
            log.output_log("".join(["[error] ", str(e)]), True)
    
    # function : get server info
    # return : dict
    def get_server_info(self, url):
        server_info = {}
        try:
            req = requests.get(url, timeout=self.timeout)
            status_code, server_type, web_type = req.status_code, req.headers['server'], req.headers["x-powered-by"]
            server_info.setdefault("status_code", status_code)
            server_info.setdefault("server", server_type)
            server_info.setdefault("x-powered-by", web_type)
        except Exception, e:
            print str(e)
        finally:
            server_info.setdefault("status_code", "unknow")
            server_info.setdefault("server", "unknow")
            server_info.setdefault("x-powered-by", "unknow")
            return server_info
    
    # function : get page size
    # return : page_size
    def get_page_size(self, url):
        try:
            req = requests.get(url, timeout=self.timeout)
            # 有时候没有content-length这个键
            page_size = int(req.headers["content-length"]) if "content-length" in req.headers else len(req.content)
            return page_size
        except Exception, e:
            log.output_log("".join(["[error] ", str(e)]), True)
            return 0

    # function : get page source only
    # return : html without charset
    def get_page_source(self, url, headers, cookies, times=0):
        if times < 3:
            try:
                req = requests.get(url, headers=headers, cookies=cookies, timeout=self.timeout)
                if req.status_code == 200:
                    html = req.text
                    req.close()
                    return html

                if req.status_code == 403:
                    times += 1
                    log.output_log("[error] 403 and try to connet %d" % times, True)
                    proxy_switch.link_proxy(self.proxy)
                    self.get_page_source_info(url, headers, cookies, times)
                return None

            except Exception, e:
                log.output_log("".join(["[error] ", str(e)]), True)
                return None

    # function : get lines from content
    # return : list
    def content_2_lines(self, page_source):
        try:
            res_lines = []
            data_lines = page_source.split('\n')
            if len(data_lines) > 1:
                for sub_str in data_lines:
                    res_lines += self.ExtractTextTagContent(sub_str)
            return res_lines
        except Exception, e:
            log.output_log("".join(["[error] ", str(e)]), True)
