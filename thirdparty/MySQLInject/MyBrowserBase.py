#!/usr/bin/env python
# encoding: utf-8
"""
@author:     HHH
@date:       2015年04月01日
@description:
"""

import socket
import urllib2
import cookielib
import random

class BrowserBase(object): 

    def __init__(self):
        socket.setdefaulttimeout(20)

    def GetPageSource(self,url,timeout = 30):
        
        Data        = {}
        ReadData    = ''
        cookie_support= urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.opener = urllib2.build_opener(cookie_support,urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)
        user_agents = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36 LBBROWSER"] 
       
        agent = random.choice(user_agents)
        self.opener.addheaders = [("User-agent",agent),("Accept","*/*"),('Referer','http://www.google.com.hk')]
        socket.setdefaulttimeout(timeout)
        
        try:
            res = self.opener.open(url)
            ReadData =  res.read()
            Data.setdefault('GetRes','200')
        except urllib2.HTTPError, e:
            try:
                if hasattr(e, 'code'):
                    if e.code == 500:
                        ReadData = e.read()
                        Data.setdefault('GetRes','200')
                    else:
                        Data.setdefault('GetRes','timeout')
            except socket.timeout:
                Data.setdefault('GetRes','timeout')
                pass
            except Exception,e:
                if 'Error 503' in str(e):
                    Data.setdefault('GetRes','503')
                else:
                    Data.setdefault('GetRes','timeout')
        except Exception,e:
            if hasattr(e, 'code'):
                Data.setdefault('GetRes',str(e.code))
            else:
                if 'Error 503' in str(e):
                    Data.setdefault('GetRes','503')
                else:
                    Data.setdefault('GetRes','timeout')
                
        finally:
            Data.setdefault('PageData',ReadData)
            return Data
        
def main():
    Test = BrowserBase()
    print Test.GetPageSource('http://www.baidu.com')
    
if __name__ == '__main__':
    main()
    pass