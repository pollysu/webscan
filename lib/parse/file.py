#!/usr/bin/env python
# encoding: utf-8
"""
@author:     idhyt
@date:       2015年4月13日
@description:
"""
import os


class FileParse(object):

    # travel
    def travel_files_by_suffix(self, dir_path, suffix):
        try:
            match_files = []
            for root, dirs, files in os.walk(dir_path):
                # print("Root = ", root, "\ndirs = ", dirs, "\nfiles = ", files)
                for file_ in files:
                    if suffix in file_.split(".")[-1]:
                        file_full_path = "".join([root, "\\", file_])
                        match_files.append(file_full_path)

            return match_files
        except Exception, e:
            print str(e)