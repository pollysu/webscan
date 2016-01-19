#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月17日
@description:
"""
import os
import json
import urllib2
import threading
from public.log import log
from lib.parse import web
from lib.parse import url as urlparse

# 多线程开关
_IS_MULTI_THREAD = True
# 线程锁
_MUTEX = threading.Lock()
# 漏洞标志位
_VUL_SIGN = 0
# 相似度
_UPPER_RATIO_BOUND = 0.95
_LOWER_RATIO_BOUND = 0.5


# function : thread lock for check vul_sign
# return : vul_sign = 1 True ; vul_sign = 0 False
def check_vul_sign(timeout=1):
    global _VUL_SIGN
    if _MUTEX.acquire(timeout):
        if _VUL_SIGN == 0:
            _MUTEX.release()
            return False
        if _VUL_SIGN == 1:
            _MUTEX.release()
            return True


# function : set vul_sign = 1 after found vul
# return : 0 -> 1 True; 1 -> 1 False
def set_vul_sign(sign, timeout=1):
    global _VUL_SIGN
    if _MUTEX.acquire(timeout):
        if _VUL_SIGN == 0:
            _VUL_SIGN = sign
            _MUTEX.release()
            return True
        elif _VUL_SIGN == sign:
            _MUTEX.release()
            return False


class Thread(threading.Thread):
    def __init__(self, func, args):
        super(Thread, self).__init__()
        self.func = func
        self.args = args
        
        if _IS_MULTI_THREAD is not True:
            self.func(*self.args)
            
    def run(self):
        self.func(*self.args)


# sql inject
class SqlScan(object):
    def __init__(self, url, proxy):
        self.payloads = json.load(open("".join([os.path.split(os.path.realpath(__file__))[0], "\\sql_payloads.json"])))
        self.url = url
        self.proxy = proxy
        self.inject_1_equ_1 = self.payloads["equ_1_1"][0]
        self.inject_1_equ_2 = self.payloads["equ_1_2"][0]
        
        self.url_parse = urlparse.UrlParse()
        self.web_site = web.WebSite(self.proxy)
        
        self.result = []
        self.server_info = {}
        self.sql_go()

    # function : get target server info
    # return : None
    def get_server_info(self):
        log.output_log("".join(["[inject url] ", self.url]), True)
        self.server_info = self.web_site.get_server_info(self.url)
        log.output_log("".join(["[*] the type of server is : ", self.server_info["server"]]))
        log.output_log("".join(["[*] the type of web powered by ", self.server_info["x-powered-by"]]))
        log.output_log("[*] please wait......")
    
    # function : test sql inject by ret page size
    # return : None
    def test_page_size(self, inject_url1, inject_url2):
        log.output_log("".join(["[test] inject url 1=1 ", inject_url1]))
        log.output_log("".join(["[test] inject url 1=2 ", inject_url2]))
        url_ret_page_size = self.web_site.get_page_size(self.url)
        url_ret_page_size_1 = self.web_site.get_page_size(inject_url1)
        url_ret_page_size_2 = self.web_site.get_page_size(inject_url2)
        if url_ret_page_size == url_ret_page_size_1 and url_ret_page_size != url_ret_page_size_2:
            return True

    # function : check sql inject by page similar
    # return : None
    def test_page_similar(self, inject_url1, inject_url2):
        page_source_original = self.web_site.get_page_source(self.url, None, None)
        page_source_1 = self.web_site.get_page_source(inject_url1, None, None)
        page_source_2 = self.web_site.get_page_source(inject_url2, None, None)
        context_original = self.web_site.content_2_lines(page_source_original)
        context_1 = self.web_site.content_2_lines(page_source_1)
        context_2 = self.web_site.content_2_lines(page_source_2)
        if self.comparison(context_original, context_1) is True \
                and self.comparison(context_original, context_2) is False:
            return True

    def comparison(self, context_1, context_2):
        index, match, ratio = 0, 0, 0
        try:
            while index < min(len(context_1), len(context_2)):
                if context_1[index] == context_2[index]:
                    match += 1
                else:
                    break
                index += 1
            ratio = 2.0 * match / (len(context_1) + len(context_2))
            # 相似度如果超过0.95则判断为同一页面
            if ratio >= _UPPER_RATIO_BOUND:
                return True
            elif ratio <= _LOWER_RATIO_BOUND:
                return False
            else:
                return None

        except Exception, e:
            log.output_log("".join(["[error] ", str(e)]), True)

    def result_dispose(self, str_result):
        if set_vul_sign(1) is True:
            self.result.append(str_result)
            log.output_log(str_result, True)

    def test_sql_inject(self, inject_url1, inject_url2):
        if check_vul_sign() is True:
            return
        # if self.test_page_size(inject_url1, inject_url2) is True
        #     or self.test_page_similar(inject_url1, inject_url2) is True:
        if self.test_page_size(inject_url1, inject_url2) is True:
            self.get_server_info()
            self.result_dispose("[%s] [%s] [server:%s + web:%s] %s" % (
                                "sqlinject", self.inject_1_equ_2,
                                self.server_info["server"], self.server_info["x-powered-by"],
                                inject_url2))

    # function : sql inject test begin
    # return : None
    def sql_go(self):
        # self.get_server_info()
        # 对于http://www.xxx.com/?id=1&name=str&title=22每个参数进行测试
        test_params_1 = self.url_parse.get_params(self.url, urllib2.quote(self.inject_1_equ_1))
        test_params_2 = self.url_parse.get_params(self.url, urllib2.quote(self.inject_1_equ_2))
        
        # ---------------------- 多线程切换 -----------------------------------------
        if _IS_MULTI_THREAD is True:
            threads = [Thread(
                self.test_sql_inject,
                (self.url.replace(i, test_params_1[i]),
                 self.url.replace(i, test_params_2[i]))) for i in test_params_1]
            for i in threads:
                i.start()
            for i in threads:
                i.join()
        else:
            for i in test_params_1:
                inject_url1, inject_url2 = self.url.replace(i, test_params_1[i]), self.url.replace(i, test_params_2[i])
                Thread(self.test_sql_inject, (inject_url1, inject_url2))

'''
def sql_scan(url):
    sql = SqlScan(url)
    if len(sql.result) > 0 : parse.output_result(sql.result)
    
if __name__ == '__main__':
    sql_scan("http://tchjbh.gotoip3.com/news_display.php?id=148")
    pass
'''
