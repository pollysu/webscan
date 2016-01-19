# encoding = utf-8
"""
Created on 2015.02.02

@author: idhyt
"""

'''
Usage:
    clouddb = ('127.0.0.1', 'username', 'password', 'db_name')
    sql = MySQL( *clouddb )
    sql.....
'''
import MySQLdb
from public.log import log
from time import sleep


SLEEP_TIME = 5


class MySQL():
    def __init__(self, host, user, psd, db, port=3306):
        self.host = host
        self.user = user
        self.psd = psd
        self.db = db
        self.port = port
        self.db_msg = 'host:%s, user:%s, psd:%s, db:%s, port:%s' % (host, user, psd, db, port)
        self._connect()
        
    def __del__(self):
        self.close()
        
    def _connect(self):
        count = 0
        while count < 5:
            try:
                self.conn = MySQLdb.Connect(self.host, self.user, self.psd,
                                            self.db, self.port, charset='utf8')
                self.cur = self.conn.cursor()
                self.cur.execute('set names utf8')
                break            
            except Exception, e:
                error_string = '(%s) connect fail, error: %s' % (self.db_msg, e)
                self._error_log(error_string)
                sleep(SLEEP_TIME)
            count += 1
    
    def _error_log(self, error_string):
        log.output_log("".join(["[error] ", error_string]), True)
    
    def get_value(self, sql_string, argv_list=None):
        count = 0
        while count < 5:
            try:
                self.conn.commit()
                if argv_list is None:
                    self.cur.execute(sql_string)
                else:
                    self.cur.execute(sql_string, argv_list)
                    
                result = self.cur.fetchone()
                break
            except Exception, e:
                if argv_list is None:
                    error_string = '(%s) execute fail, error: %s' % (sql_string, e)
                    self._error_log(error_string)
                else:
                    error_string = '(%s) execute fail, argvlist: %s error: %s' % (sql_string, argv_list, e)
                    self._error_log(error_string)
                    
                if e[0] == 1062:
                    break
                sleep(SLEEP_TIME)
                self.close()
                self._connect()
            count += 1
        return result

    def get_values(self, sql_string, argv_list=None):
        count = 0
        while count < 5:
            try:
                self.conn.commit()
                if argv_list is None:
                    self.cur.execute(sql_string)
                else:
                    self.cur.execute(sql_string, argv_list)
                result = self.cur.fetchall()
                break
            except Exception, e:
                if argv_list is None:
                    error_string = '(%s) execute fail, error: %s' % (sql_string, e)
                    self._error_log(error_string)
                else:
                    error_string = '(%s) execute fail, argvlist: %s error: %s' % (sql_string, argv_list, e)
                    self._error_log(error_string)
                
                if e[0] == 1062:
                    break
                sleep(SLEEP_TIME)
                self.close()
                self._connect()
            count += 1
        return result
        
    def insert_value(self, sql_string, argv_list=None):
        count = 0
        while count < 5:
            try:
                if argv_list is None:
                    self.cur.execute(sql_string)
                else:
                    self.cur.execute(sql_string, argv_list)
                self.conn.commit()
                break
            except MySQLdb.IntegrityError, e:
                if argv_list is None:
                    error_string = '(%s) execute fail, error: %s' % (sql_string, e)
                    self._error_log(error_string)
                else:
                    error_string = '(%s) execute fail, argvlist: %s error: %s' % (sql_string, argv_list, e)
                    self._error_log(error_string)
                
                if e.args[0] == 1062:
                    break
                else:
                    sleep(SLEEP_TIME)
                    self.close()
                    self._connect()
            except MySQLdb.OperationalError, e:
                if argv_list is None:
                    error_string = '(%s) execute fail, error: %s' % (sql_string, e)
                    self._error_log(error_string)
                else:
                    error_string = '(%s) execute fail, argvlist: %s error: %s' % (sql_string, argv_list, e)
                    self._error_log(error_string)
                
                # ----idhyt----
                if e[0] == 1366:
                    sql_string = sql_string.decode('gbk', 'ignore')
                # -------------
                if e.args[0] == 1050:
                    break
                else:
                    sleep(SLEEP_TIME)
                    self.close()
                    self._connect()
            except Exception, e:
                error_string = '(%s) execute fail, error: %s' % (sql_string, e)
                self._error_log(error_string)
                sleep(SLEEP_TIME)
                self.close()
                self._connect()
            count += 1
            
    # insert but do don't commit
    def insert_value_not_commit(self, sql_string, argv_list=None):
        count = 0
        while count < 5:
            try:
                if argv_list is None:
                    self.cur.execute(sql_string)
                else:
                    self.cur.execute(sql_string, argv_list)
                break
            except MySQLdb.IntegrityError, e:
                if argv_list is None:
                    error_string = '(%s) execute fail, error: %s' % (sql_string, e)
                    self._error_log(error_string)
                else:
                    error_string = '(%s) execute fail, argvlist: %s error: %s' % (sql_string, argv_list, e)
                    self._error_log(error_string)
                
                if e.args[0] == 1062:
                    break
                else:
                    sleep(SLEEP_TIME)
                    self.close()
                    self._connect()
            except MySQLdb.OperationalError, e:
                if argv_list is None:
                    error_string = '(%s) execute fail, error: %s' % (sql_string, e)
                    self._error_log(error_string)
                else:
                    error_string = '(%s) execute fail, argvlist: %s error: %s' % (sql_string, argv_list, e)
                    self._error_log(error_string)
                
                # ----idhyt----
                if e[0] == 1366:
                    sql_string = sql_string.decode('gbk','ignore')
                # -------------
                if e.args[0] == 1050:
                    break
                else:
                    sleep(SLEEP_TIME)
                    self.close()
                    self._connect()
            except Exception, e:
                error_string = '(%s) execute fail, error: %s' % (sql_string, e)
                self._error_log(error_string)
                sleep(SLEEP_TIME)
                self.close()
                self._connect()
            count += 1

    def commit(self):   
        try:
            self.conn.commit()
        except Exception, e:
            print str(e)
            return False
        return True
      
    def close(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception, e:
            print str(e)