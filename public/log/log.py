#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年3月17日
@description:
"""

import time
from logger.Logger import Logger
import inspect
import re


def output_log(out_info, is_write_log=False):
    clog = CLog()
    call_model = clog.get_call_model_name()

    if is_write_log is True:
        Logger.Write("[%s]%s" % (call_model, out_info))
    else:
        date = time.ctime(time.time())
        print '[%s][%s]%s' % (str(date), call_model, out_info)


class CLog(object):
    def __init__(self):
        pass
    
    def get_file_name_in_full_path(self, file_path):
        return file_path.split('\\')[-1]

    def get_class_from_frame(self, fr):
        args, _, _, value_dict = inspect.getargvalues(fr)
        if len(args) and args[0] == 'self':
            instance = value_dict.get('self', None)
            if instance:
                return getattr(instance, '__class__', None)
        return None

    def get_call_model_name(self):
        frames = inspect.stack()
        chain_list = []
        for i in range(0, len(frames)):
            _, file_path, _, _, _, _ = frames[i]
            file_name = self.get_file_name_in_full_path(file_path)
            current_chain = '%s' % file_name
            chain_list.append(current_chain)
        return chain_list[2]
    
    def get_meta_data(self):
        frames = inspect.stack()
        chain_list = []
        for i in range(0, len(frames)):
            _, file_path, _, func_name, _, _ = frames[i]
            file_name = self.get_file_name_in_full_path(file_path)
            try:
                args = re.findall('\((.*)\)', frames[i][-2][0])[0]
            except IndexError:
                func_name = self.get_class_from_frame(frames[2][0]).__name__
                args = ''
            except:
                pass
            current_chain = '%s:%s(%s)' % (file_name, func_name, args)
            chain_list.append(current_chain)
        chain_list.reverse()
        return ' --> '.join(chain_list[:-2])