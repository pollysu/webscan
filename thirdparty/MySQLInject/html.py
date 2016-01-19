#!/usr/bin/env python
# encoding: utf-8
"""
@author:     HHH
@description:
"""

import contextlib
import re
from __builtin__ import str
from xml.sax import parse
from StringIO import StringIO
from xml.sax.handler import ContentHandler
#from package import MyBrowserBase
    
class HTMLHandler(ContentHandler):
    """
    This class defines methods to parse the input HTML page to
    fingerprint the back-end database management system
    """

    def __init__(self, page):
        ContentHandler.__init__(self)

        self._dbms = None
        self._page = page

        self.dbms = None


    def startElement(self, name, attrs):
        try:
            if name == "dbms":
                self._dbms = attrs.get("value")
    
            elif name == "error":
                if re.search(attrs.get("regexp"), self._page, re.I):
                    self.dbms = self._dbms
        except Exception,e:
            pass
        

def readCachedFileContent(FileName):
    Data = ''
    try:
        with open(FileName,'r') as File:
            Data = File.read()
            
    except Exception,e:
        print str(e)
    finally:
        return Data
    
def htmlParser(page,XMLFileData):
    """
    This function calls a class that parses the input HTML page to
    fingerprint the back-end database management system
    """
    
    handler = HTMLHandler(page)

    parseXmlFile(XMLFileData, handler)
    
    return handler.dbms


def parseXmlFile(XMLFileData, handler):
    """
    Parses XML file by a given handler
    """
    try:
        with contextlib.closing(StringIO(XMLFileData)) as stream:
            parse(stream, handler)
    except Exception,e:
        print str(e)
        
def main():
    try:
        pass
    except Exception,e:
        print str(e)
    finally:
        pass
    
if __name__ == '__main__': 
    main()