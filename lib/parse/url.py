#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年4月2日
@description:
"""
import urllib2
import re
import urlparse
import hashlib


class UrlParse(object):
    def __init__(self):
        self.payload_of_xss = "=ADC22F"
        self.regex_of_param = r"http://[\w./]*\?[\w-]*="
        self.regex_of_valid = r'[0-9a-zA-Z._/\?:=&@]*\.(jpg|swf|gif|cer|png|doc|xls|ppt|pptx|docs|rar|zip|pdf|chm|apk)'
        self.hash_size = 10000000
        pass
    
    def get_params(self, url, payload=None):
        payload = self.payload_of_xss if payload is None else payload
        query = urllib2.urlparse.urlparse(url).query
        params = query.split("&")
        test_params = {}
        
        for i in params:
            if i == params[0]:
                if "=" not in i:
                    test_params["?"+i] = "?" + i + payload
                elif i.endswith("="):
                    test_params["?"+i] = "?" + i + payload
                else:
                    # test_params["?"+i] = "?" + i.replace(i[i.rindex("=")+1:], payload)
                    test_params["?"+i] = "?" + i + payload
            else:
                if "=" not in i:
                    test_params["&"+i] = "&" + i + payload
                elif i.endswith("="):
                    test_params["&"+i] = "&" + i + payload
                else:
                    # test_params["&"+i] = "&"+ i.replace(i[i.rindex("=")+1:], payload)
                    test_params["&"+i] = "&" + i + payload
        return test_params
    
    def is_param_url(self, url, regex=None):
        # pattern = re.compile(r'http://[0-9a-zA-Z._/]*\?[a-zA-Z_]*=[0-9a-zA-Z_]*[0-9a-zA-Z._/=&]*')
        regex = self.regex_of_param if regex is None else regex
        pattern = re.compile(regex, re.IGNORECASE)
        match = pattern.match(url)
        if match:
            return True
        else:
            return False

    # 判断是否有无法解析的url，比如一些doc文档。增加判断，url大于512字节认为不可靠，过滤掉
    def is_valid_url(self, url, regex=None):
        regex = self.regex_of_valid if regex is None else regex
        if len(url) >= 512:
            return False
        pat = re.compile(regex, re.IGNORECASE)
        match = pat.match(url)
        if match:
            return False
        else:
            return True

    # URL相似度判断
    # 主要取4个值
    # 1,netloc的hash值
    # 2,path字符串拆解成列表的列表长度
    # 3,path中字符串的长度
    # 4,query参数名hash    a=1&b=2&c=3 : hash('abc')
    def url_similar(self, url, hash_size=None):

        hash_size = self.hash_size if hash_size is None else hash_size
        netloc_value = 0
        path_value = 0
        query_value = 0
        url_value = 0

        try:
            tmp = urlparse.urlparse(url)
            netloc = tmp[1]
            path = tmp[2][1:]
            query = tmp[4]

            if len(netloc) > 0:
                netloc = netloc.lower()
                netloc_value = hash(hashlib.new("md5", netloc).hexdigest()) % (hash_size-1)

            if len(path) > 0:
                # hash path
                path = path.lower()
                path_list = path.split('/')[:-1]
                # path = 'a/b/c/d.html'
                if len(path.split('/')[-1].split('.')) > 1:
                    tail = path.split('/')[-1].split('.')[:-1][0]
                # path = ''
                elif len(path.split('/')) == 1:
                    tail = path
                # path = 'a/'
                else:
                    tail = '1'
                path_list.append(tail)
                path_length = len(path_list)
                for i in range(path_length):
                    i_length = len(path_list[i]) * (10**(i+1))
                    path_value += i_length
                path_value = hash(hashlib.new("md5", str(path_value)).hexdigest()) % (hash_size-1)

            # hash query (参数名串hash运算)
            if len(query) > 0:
                str_key_names = ''
                query = query.lower()
                query_list = query.split('&')
                query_length = len(query_list)  # 2 1
                for i in range(query_length):
                    key_name = query_list[i].split('=')[0]
                    str_key_names += key_name
                query_value = hash(hashlib.new("md5", str_key_names).hexdigest()) % (hash_size-1)

            url_value = hash(hashlib.new("md5",
                                         str(netloc_value + path_value + query_value)).hexdigest()) % (hash_size-1)
    #             return url_value
        except Exception, e:
            print str(e)

        finally:
            return url_value
