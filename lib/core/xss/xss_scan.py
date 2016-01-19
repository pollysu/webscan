#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月13日
@description:
"""

import os
import re
import bs4
from bs4 import BeautifulSoup
import json
import threading
import urllib2

from public.log import log
from lib.parse import url as urlparse
from lib.parse import web

# 多线程开关
_IS_MULTI_THREAD = False
# 线程锁
_MUTEX = threading.Lock()
# 漏洞标志位
_VUL_SIGN = 0
# _DORK_PAYLOAD = "ADC22F"
_DORK_PAYLOAD = "572F4D"


# function :  thread lock for check vul_sign
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


class XssScan(object):
    def __init__(self, url, cookies, proxy):
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/28.0.1500.71 Safari/537.36"}
        self.cookies = cookies
        self.proxy = proxy
        self.enc = "utf-8"
        self.urls = []
        self.payloads = json.load(open("".join([os.path.split(os.path.realpath(__file__))[0], "\\xss_payloads.json"])))
        self.test_urls = {
            "betweenCommonTag": [],
            "betweenTitle": [],
            "betweenTextarea": [],
            "betweenXmp": [],
            "betweenIframe": [],
            "betweenNoscript": [],
            "betweenNoframes": [],
            "betweenPlaintext": [],
            "betweenScript": [],
            "betweenStyle": [],
            "utf-7": [],
            "inSrcHrefAction": [],
            "inScript": [],
            "inStyle": [],
            "inCommonAttr": [],
            "inMetaRefresh": []
        }
        self.result = []
        self.url_parse = urlparse.UrlParse()
        self.web_site = web.WebSite(self.proxy)
        
        self.xss_go()

    # function : check xss possible first
    # return : no ret
    def judge_out(self, url, keyword, list_):
        page_source_info = self.web_site.get_page_source_info(url, self.headers, self.cookies)
        if page_source_info is not None and keyword in page_source_info[0]:
            list_.append(url)
            
    # function :  遍历获取子标签列表
    # return : no ret
    def get_children_tags(self, tag, tag_list):
        for i in tag.children:
            if type(i) == bs4.element.Tag:
                tag_list.append(i)
                self.get_children_tags(i, tag_list)
    
    # function :  判断payload出现位置
    # return : value
    def judge_location(self, url):
        try:
            page_source_info = self.web_site.get_page_source_info(url, self.headers, self.cookies)
            if page_source_info is None:
                return None
            page_source = page_source_info[0]
            soup = BeautifulSoup(page_source)
            tag_list = []
            self.get_children_tags(soup, tag_list)

            re_key = re.compile(_DORK_PAYLOAD)
            if soup.findAll(text=re_key):
                for i in soup.findAll(text=re_key):
                    if i.findParent("title"):
                        self.test_urls["betweenTitle"].append(url)
                    elif i.findParent("textarea"):
                        self.test_urls["betweenTextarea"].append(url)
                    elif i.findParent("xmp"):
                        self.test_urls["betweenXmp"].append(url)
                    elif i.findParent("iframe"):
                        self.test_urls["betweenIframe"].append(url)
                    elif i.findParent("noscript"):
                        self.test_urls["betweenNoscript"].append(url)
                    elif i.findParent("noframes"):
                        self.test_urls["betweenNoframes"].append(url)
                    elif i.findParent("plaintext"):
                        self.test_urls["betweenPlaintext"].append(url)
                    elif i.findParent("script"):
                        self.test_urls["betweenScript"].append(url)
                    elif i.findParent("style"):
                        self.test_urls["betweenStyle"].append(url)
                    else:
                        self.test_urls["betweenCommonTag"].append(url)
            
            if soup.findAll(name="meta", attrs={"http-equiv": "Refresh", "content": re.compile(_DORK_PAYLOAD)}):
                self.test_urls["inMetaRefresh"].append(url)
            
            if page_source.startswith(_DORK_PAYLOAD):
                self.test_urls["utf-7"].append(url)
    
            for i in tag_list:
                for j in i.attrs:
                    if _DORK_PAYLOAD in i.attrs[j]:
                        self.test_urls["inCommonAttr"].append(url)
    
                        if j in ["src", "href", "action"] and i.attrs[j].startswith(_DORK_PAYLOAD):
                            self.test_urls["inSrcHrefAction"].append(url)
                        elif (j.startswith("on") or (j in ["src", "href", "action"]
                                                     and i.attrs[j].startswith("javascript:"))):
                            self.test_urls["inScript"].append(url)
                        elif j == "style":
                            self.test_urls["inStyle"].append(url)
        except Exception, e:
            print str(e)

    def confirm_parent_tag(self, soup):
        for i in soup.findAll("x55test"):
            for j in i.parents:
                if j.name in (
                        "title",
                        "textarea",
                        "xmp",
                        "iframe",
                        "noscript",
                        "noframes",
                        "plaintext"
                ):
                    return False
        return True

    def confirm_in_script(self, soup, payload):
        tag_list = []
        self.get_children_tags(soup, tag_list)
        for i in tag_list:
            for j in i.attrs:
                if j.startswith("on") and payload in i.attrs[j]:
                    return True
        return False
    
    def result_dispose(self, str_result):
        if set_vul_sign(1) is True:
            self.result.append(str_result)
            log.output_log(str_result, True)
        
    def test_single_payload(self, url, location, payload):
        # if one thread found vul, other thread don't found with other payload test again
        if check_vul_sign() is True:
            return
        # test payloads
        test_url = url.replace(_DORK_PAYLOAD, urllib2.quote(payload))
        log.output_log("[test] %s" % test_url)
        page_source_info = self.web_site.get_page_source_info(test_url, self.headers, self.cookies)
        if page_source_info is None:
            return None
        page_source, self.enc = page_source_info[0], page_source_info[1]
        soup = BeautifulSoup(page_source)
        if (location in ("betweenCommonTag",
                         "betweenTitle",
                         "betweenTextarea",
                         "betweenXmp",
                         "betweenIframe",
                         "betweenNoscript",
                         "betweenNoframes",
                         "betweenPlaintext"
                         )and
                soup.findAll("x55test") and self.confirm_parent_tag(soup)):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))
            
        if (location == "betweenScript" and (soup.findAll("x55test")
                                             or soup.findAll(name="script", text=re.compile(r"[^\\]%s" % payload.replace("(", "\(").replace(")", "\)"))))):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))
            
        if (location == "betweenScript" and self.enc == "gbk" and
                soup.findAll(name="script", text=re.compile(r"\\%s" % payload.replace("(", "\(").replace(")", "\)")))):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))
            
        if (location == "betweenStyle" and (soup.findAll("x55test") or 
            soup.findAll(name="style",
                         text=re.compile("%s" % payload.replace(".", "\.").replace("(", "\(").replace(")", "\)"))))):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))

        if (location == "inMetaRefresh" and soup.findAll(
                name="meta", attrs={"http-equiv": "Refresh", "content": re.compile(payload)})):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))

        if location == "utf-7" and page_source.startswith("+/v8 +ADw-x55test+AD4-"):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))

        if (location == "inCommonAttr" and (soup.findAll("x55test")
                                            or soup.findAll(attrs={"x55test": re.compile("x55")}))):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))

        if (location == "inSrcHrefAction"
            and (soup.findAll(attrs={"src": re.compile("^(%s)" % payload)})
                 or soup.findAll(attrs={"href": re.compile("^(%s)" % payload)})
                 or soup.findAll(attrs={"action": re.compile("^(%s)" % payload)}))):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))

        if (location == "inScript" and
                self.confirm_in_script(soup, payload)):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))

        if (location == "inStyle" and
                soup.findAll(attrs={"style": re.compile("%s" % payload.replace(".", "\.").replace("(", "\(").replace(")", "\)"))})):
            self.result_dispose("[xss] [%s] [%s] %s" % (location, payload, test_url))

    def test_xss(self, url, location):
        if _IS_MULTI_THREAD is True:
            threads = []
            for i in self.payloads[location]:
                threads.append(Thread(self.test_single_payload, (url, location, i)))
            for i in threads:
                i.start()
            for i in threads:
                i.join()
            
        else:
            for i in self.payloads[location]:
                self.test_single_payload(url, location, i)

    def xss_go(self):
        log.output_log("".join(["[xss] test url ", self.url]), True)
        test_params = self.url_parse.get_params(self.url, _DORK_PAYLOAD)
        
# ---------------------- 多线程切换 -----------------------------------------
        if _IS_MULTI_THREAD is True:
            threads = [Thread(self.judge_out,
                       (self.url.replace(i, test_params[i]),
                        _DORK_PAYLOAD, self.urls)) for i in test_params]
            for i in threads:
                i.start()
            for i in threads:
                i.join()
        else:
            for param in test_params:
                url = self.url.replace(param, test_params[param])
                Thread(self.judge_out, (url, _DORK_PAYLOAD, self.urls))
                
#        self.enc = get_charset(self.url)

        if _IS_MULTI_THREAD is True:
            threads = [Thread(self.judge_location, (i,)) for i in self.urls]
            for i in threads:
                i.start()
            for i in threads:
                i.join()
        else:
            for i in self.urls:
                Thread(self.judge_location, (i,))
        # 去重
        for i in self.test_urls:
            if self.test_urls[i]:
                self.test_urls[i] = list(set(self.test_urls[i]))
                
        if _IS_MULTI_THREAD is True:
            threads = [Thread(self.test_xss, (j, i)) for i in self.test_urls for j in self.test_urls[i]]
            for i in threads:
                i.start()
            for i in threads:
                i.join()
            
        else:
            for i in self.test_urls:
                for j in self.test_urls[i]:
                    Thread(self.test_xss, (j, i))
# -------------------------------------------------------------------------

'''
def xss_scan(url, cookie_file):
    cookies = parse.get_cookies(cookie_file) if cookie_file is not None else None
    xss = XssScan(url, cookies)
    if len(xss.result) > 0 : parse.output_result(xss.result)
    
if __name__ == '__main__':
    xss_scan("", "cookie.txt")
'''