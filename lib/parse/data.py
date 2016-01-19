#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月13日
@description:
"""
import re
import time
from public.log import log


class DataParse(object):
    def output_result(self, result, tag=0):
        # for i in result:
        #     print i
        date = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        if tag == 1:
            self.lines_to_file(date, result)

    # writelines 
    def lines_to_file(self, filename, lines):
        try:
            f = open(filename, "w")
            for line in lines:
                f.write(line + '\n')
            f.close()
        except Exception, e:
            log.output_log("".join(["[error] ", str(e)]), True)
    
    # function :  format xss info to [(id, file_name, vul_type, vul_detail, vul_uri),...]
    # return : list
    def format_vul_info(self, info_list, insert_scan_info, regex=r"\[(\w*)\] *(\[.*\] *\[.*\]) *(.*)"):
        vul_info_list = []
        pattern = re.compile(regex, re.IGNORECASE)
        for info in info_list:
            vul_info_list.append(insert_scan_info + pattern.findall(info)[0])
        return vul_info_list

    # function : get data by regex
    # return : data_list / None
    def get_data_by_regex(self, source, regex):
        pattern = re.compile(regex, re.IGNORECASE)
        result = pattern.findall(source)
        if len(result) > 0:
            return result
        else:
            return None
    
    # get cookies from cookie file
    def get_cookies(self, cookie_file):
        cookies = {}
        cookies_text = open(cookie_file).read().split("; ")
        for i in cookies_text:
            cookies[i.split("=")[0]] = i.split("=")[1]
        return cookies
