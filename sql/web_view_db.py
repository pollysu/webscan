#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年4月20日
@description:
"""
import mysql
from public.log import log


class WebView(object):
    def __init__(self, db_info):
        self.cloud_db = (db_info.db_host, db_info.db_user, db_info.db_pwd, db_info.db_name)
        self.db_table = db_info.db_table

    # function : get value from db (数据库信息, 保留)
    # return : (value1, value2, value3...)
    def select_info(self, tag=1):
        try:
            sql = mysql.MySQL(*self.cloud_db)
            if tag == 1:
                sql_string = "SELECT id, apk_name, url" + \
                             " FROM " + self.db_table + \
                             " WHERE webview_state = 0 LIMIT 1"

            ret_tuple = sql.get_value(sql_string)
            if ret_tuple is not None:
                if tag == 1:
                    sql_string = "UPDATE " + self.db_table + \
                                 " SET webview_state = 1" + \
                                 " WHERE id = " + str(ret_tuple[0])

                sql.insert_value(sql_string)
                return ret_tuple
            return None
        except Exception, e:
            log.output_log("".join(["[error] ", str(e)]), True)
            return None

    def insert_info_s(self, insert_info_list, tag=1):
        try:
            sql = mysql.MySQL(*self.cloud_db)
            if tag == 1:
                for insert_info in insert_info_list:
                    vul_code = insert_info["code"].replace("'", "\\'")
                    sql_string = "INSERT INTO " + self.db_table + "(apk_name, vul_activity, vul_method, vul_code) values('" + \
                                 insert_info["apk_name"] + "', '" + \
                                 insert_info["activity"] + "', '" + \
                                 insert_info["method"] + "', '" + \
                                 vul_code + "')"

                    sql.insert_value_not_commit(sql_string)
                sql.commit()

            elif tag == 2:
                sql_string = ''
                sql.insert_value(sql_string)
            return True

        except Exception, e:
            log.output_log("".join(["[error] ", str(e)]), True)
            return False

    def get_scan_file(self):
        return self.select_info()

    # (apk_name, vul_activity, vul_method, vul_code)
    def save_vul_info(self, insert_info):
        self.insert_info(insert_info)