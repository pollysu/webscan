#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月30日
@description:
"""

import os
import json
from thirdparty import requests
from proxy import proxy_switch

import threading
from public.log import log
from lib.parse import data

# 多线程开关
_IS_MULTI_THREAD = False
# 线程数
_THREAD_COUNT = 10
# 线程锁
_MUTEX = threading.Lock()


class Thread(threading.Thread):
    def __init__(self, func, args):
        super(Thread, self).__init__()
        self.func = func
        self.args = args
        
        if _IS_MULTI_THREAD is True:
            self.func(*self.args)
            
    def run(self):
        self.func(*self.args)


class SiteDirScan(object):
    def __init__(self, url, proxy):
        self.payloads = open("".join([os.path.split(os.path.realpath(__file__))[0], "\\dict\\cgi.txt"])).readlines()
        self.status_codes = json.load(open(
            "".join([os.path.split(os.path.realpath(__file__))[0], "\\exts\\status_code.json"])
        ))
        self.url = url
        self.proxy = proxy
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                      "Chrome/28.0.1500.71 Safari/537.36"}
        
        self.result = []

        self.data_parse = data.DataParse()
        self.site_dir_go()

    def get_payload(self, timeout=1):
        if _MUTEX.acquire(timeout):
            payload = self.payloads.pop(0) if len(self.payloads) > 0 else None
            _MUTEX.release()
            return payload

    def result_dispose(self, str_result, timeout=1):
        if _MUTEX.acquire(timeout):
            self.result.append(str_result)
            _MUTEX.release()
            log.output_log(str_result, True)
    
    def switch_proxy(self, timeout=1):
        if _MUTEX.acquire(timeout):
            proxy_switch.link_proxy(self.proxy)
            _MUTEX.release()
            
    # function : scan site dir
    # return : None
    def check_site_dir(self, site_root):
        while True:
            test_dir = self.get_payload()
            if test_dir is None:
                break
            test_url = site_root + test_dir
            try:
                req = requests.get(test_url, headers=self.headers, cookies=None, timeout=3)
                status_code = req.status_code
                status = self.status_codes[str(status_code)][0] \
                    if str(status_code) in self.status_codes else "Undefined"
                self.result_dispose("[site_dir][%d][%s]%s" % (status_code, str(status), test_url))

            except Exception, e:
                log.output_log("".join(["[error] ", str(e)]), True)
                pass

    # function : sql inject test begin
    # return : None
    def site_dir_go(self):
        # get site root dir
        ret_list = self.data_parse.get_data_by_regex(self.url, "(http://[\w.:]{0,62})/?")
        if len(ret_list) == 0:
            return
        site_root = ret_list[0]
        
        # ---------------------- 多线程切换 -----------------------------------------
        if _IS_MULTI_THREAD is True:
            threads = [Thread(self.check_site_dir, (site_root,)) for i in range(_THREAD_COUNT)]
            for i in threads:
                i.start()
            for i in threads:
                i.join()
        else:
            Thread(self.check_site_dir, (site_root,))


def site_dir_scan(url):
    site_dir = SiteDirScan(url, None)
    if len(site_dir.result) > 0:
        pass
#         data.output_result(site_dir.result)
    
if __name__ == '__main__':
    site_dir_scan("http://tchjbh.gotoip3.com/news_display.php?id=148")
    pass
