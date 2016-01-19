#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月24日
@description:
"""
import os
import time
import subprocess
import socket
import socks
from config import config
from public.log import log


class Proxy(object):
    def __init__(self):
        self.proxy_info = config.ProxyInfo(os.path.split(os.path.realpath(__file__))[0])
        self.proxy_count = self.proxy_info.count
        self.index = 0
    
    # function :  get a proxy
    # return : proxy info / { }
    def get_proxy_info(self):
        if self.index > self.proxy_count - 1:
            self.index = 0
        return self.proxy_info.proxy[self.index]
    
    # function :  start proxy by plink.exe ssh
    # return : None
    # plink.exe server_ip -N -ssh -2 -P 22 -l user_name -D client_ip:port -pw pwd
    def start_proxy(self, proxy_info):
        try:
            command = "%s %s -N -ssh -2 -P 22 -l %s -D %s:%d -pw %s" % (
                self.proxy_info.plink_path,
                proxy_info["server_ip"],
                proxy_info["user_name"],
                proxy_info["client_ip"],
                proxy_info["port"],
                proxy_info["pwd"])
            subprocess.Popen(command)
            log.output_log("[proxy] start proxy success!")
            self.set_proxy(proxy_info["client_ip"], proxy_info["port"])
        except Exception, e:
            log.output_log("[error] start proxy false!", True)
            log.output_log("".join(["[error] ", str(e)]), True)
            
    # function : switch proxy by socket5
    # return : True / False
    def set_proxy(self, ip_address, port):
        try:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip_address, port)
            socket.socket = socks.socksocket
            log.output_log("[proxy] switch proxy success! port %d" % port)
            return True
        
        except Exception, e:
            log.output_log("[error] switch proxy false!", True)
            log.output_log("".join(["[error] ", str(e)]), True)
            return False
    
    # function : check proxy by get ip address
    # return : True / False
    def get_addr(self):
        try:
            import urllib2
            response = urllib2.urlopen("http://int.dpool.sina.com.cn/iplookup/iplookup.php")
            html = response.read()
            print html.decode('gb2312')
            return True
        
        except Exception, e:
            print str(e)
            return False
        
        
def link_proxy(proxy):
    proxy_info = proxy.get_proxy_info()
    log.output_log("[proxy] switch server: %s" % proxy_info["server_ip"], True)
    proxy.index += 1
    proxy.start_proxy(proxy_info)
    while proxy.get_addr() is False:
        proxy.start_proxy(proxy_info)
        time.sleep(5)
        
    
if __name__ == '__main__':
    proxy = Proxy()
    for i in range(10):
        link_proxy(proxy)

    pass



