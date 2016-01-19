#!/usr/bin/env python
# encoding: utf-8
"""
@author:     HHH
@description:

"""
import os

from xml.etree import ElementTree as et
from datatype import AttribDict


def cleanupVals(text, tag):
    if tag in ("clause", "where"):
        text = text.split(',')

    if isinstance(text, basestring):
        text = int(text) if text.isdigit() else str(text)

    elif isinstance(text, list):
        count = 0

        for _ in text:
            text[count] = int(_) if _.isdigit() else str(_)
            count += 1

        if len(text) == 1 and tag not in ("clause", "where"):
            text = text[0]

    return text

def parseXmlNode(node):
    BRet = []
    try:
        for element in node.getiterator('boundary'):
            boundary = AttribDict()
            
            for child in element.getchildren():
                if child.text:
                    values = cleanupVals(child.text, child.tag)
                    boundary[child.tag] = values
                else:
                    boundary[child.tag] = None
            
            BRet.append(boundary)
        
        for element in node.getiterator('test'):
            test = AttribDict()
            
            for child in element.getchildren():
                if child.text and child.text.strip():
                    values = cleanupVals(child.text, child.tag)
                    test[child.tag] = values
                else:
                    if len(child.getchildren()) == 0:
                        test[child.tag] = None
                        continue
                    else:
                        test[child.tag] = AttribDict()
                
                    for gchild in child.getchildren():
                        if gchild.tag in test[child.tag]:
                            prevtext = test[child.tag][gchild.tag]
                            test[child.tag][gchild.tag] = [prevtext, gchild.text]
                        else:
                            test[child.tag][gchild.tag] = gchild.text
            
            BRet.append(test)
            
    except Exception,e:
        print str(e)
    finally:
        return BRet

def loadXML(PathsList):
    payloadFiles = PathsList
    PayLoads     = []
    Item         = 0
    
    for Path in payloadFiles:
        payloadFilePath = os.path.join("".join([os.path.split(os.path.realpath(__file__))[0], "\\payloads"]), Path)

        #logger.debug("Parsing payloads from file '%s'" % payloadFile)

        try:
            doc = et.parse(payloadFilePath)
            root = doc.getroot()
            PayLoads += parseXmlNode(root)
            
        except Exception, e:
            ErrMsg = 'LoadPayloads Fail! FileName:%s,Error:%s' % payloadFiles[Item],str(e)
            print ErrMsg
        finally:
            pass
        
    return PayLoads
