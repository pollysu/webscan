#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
Created on 2011-7-29

@author: Administrator
'''
import datetime
import time
import os
import threading

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../log/"))

def thread_safe(func):
    '''函数线程安全装饰器'''
    mutex = threading.Lock() # 新建锁
        
    def dec(*args, **kwargs):
        '''装饰函数'''
        mutex.acquire() # 请求获得锁
        try:
            result = func(*args, **kwargs) # call 原函数
        finally:
            mutex.release() # 释放锁
        return result
    return dec

class Logger(object):
    '''
    logger.
    '''
    @classmethod
    @thread_safe
    def Write(cls, msg):
        try:
            if not os.path.exists(LOG_DIR):
                os.mkdir(LOG_DIR)
            try:
                log_path = os.path.join(LOG_DIR + str(datetime.date.today()) + '.py.log')
                log_file = open(log_path, 'a')
                msg_l = '[%s]%s\n' % (time.ctime(time.time()), msg)
                if isinstance(msg_l, unicode):
                    print msg_l.encode('gbk')
                else:
                    print unicode(msg_l, 'utf-8').encode('gbk')
                log_file.write(msg_l)
                log_file.close()
            except Exception, ex:
                print '[%s][Logger] Error: cannot write log!' % (time.ctime(time.time())), ex
        except Exception, ex:
            print '[%s][Logger] Error: cannot create log path!' % (time.ctime(time.time())), ex
            
    @classmethod
    @thread_safe
    def WriteLogOnly(cls, msg):
        try:
            if not os.path.exists(LOG_DIR):
                os.mkdir(LOG_DIR)
            try:
                log_path = os.path.join(LOG_DIR + str(datetime.date.today()) + '.py.log')
                log_file = open(log_path, 'a')
                msg_l = '[%s]%s\n' % (time.ctime(time.time()), msg)
                log_file.write(msg_l)
                log_file.close()
            except Exception, ex:
                print '[%s][Logger] Error: cannot write log!' % (time.ctime(time.time())), ex
        except Exception, ex:
            print '[%s][Logger] Error: cannot create log path!' % (time.ctime(time.time())), ex
            
    @classmethod
    @thread_safe
    def WriteEx(cls, md5, msg):
        try:
            if not os.path.exists(LOG_DIR):
                os.mkdir(LOG_DIR)
            try:
                log_path = os.path.join(LOG_DIR + str(datetime.date.today()) + '.py.log')
                log_file = open(log_path, 'a')
                msg_l = '[%s][%s]%s\n' % (time.ctime(time.time()), md5, msg)
                if isinstance(msg_l, unicode):
                    print msg_l.encode('gbk')
                else:
                    print unicode(msg_l, 'utf-8').encode('gbk')
                log_file.write(msg_l)
                log_file.close()
            except Exception, ex:
                print '[%s][Logger] Error: cannot write log!' % (time.ctime(time.time())), ex
        except Exception, ex:
            print '[%s][Logger] Error: cannot create log path!' % (time.ctime(time.time())), ex
            
if __name__ == '__main__':
    str1 = '测试'
    Logger.Write(str1)