#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月13日
@description:
"""

import argparse
from lib.scan import urlscan
from lib.scan import urlsscan


def get_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-m', '--mode', help="MODE to scan; -m 1 (1-xss 2-sql 3-both)")
    parser.add_argument('-u', '--url', help="URL to scan; -u http://example.com?xss=")
    parser.add_argument('-s', '--source', help="scan URL source; -s http://example.com?xss= -c cookies.txt")
    parser.add_argument('-c', '--cookie', help="URL to scan with cookie; -u http://example.com?xss= -c cookies.txt")
    parser.add_argument('-p', '--proxy', help="URL to scan with proxy; -u http://example.com?xss= -p 1")
    args = parser.parse_args()
    return args


def web_scan():

    args = get_args()
#     -m mode
#     01: xss scan  eg: -m 1
#     10: sql inject eg: -m 2
#     100 site dir scan eg: -m 4
#     111: both eg: -m 7 

#     -s source
#     01: url source from db
#     10: reserve
    
#     -p proxy
#     00: not set proxy
#     01: set proxy
    is_proxy = int(args.proxy) if args.proxy else 0

    if args.source and args.mode:
        urlsscan.UrlsScan(args.cookie, int(args.source), int(args.mode), is_proxy)
        
    if args.url and args.mode:
        urlscan.UrlScan(args.url, int(args.mode), args.cookie, is_proxy)

if __name__ == "__main__":
    web_scan()
