#!/usr/bin/env python
# encoding: utf-8
"""
@author:     HHH
@date:       2015年04月01日
@description:
"""

import Queue, threading, sys
from threading import Thread
import time
import os

class MyWork(Thread):
    def __init__(self,WorkQueue,ResQueue,ID,timeout = 5):
        threading.Thread.__init__(self)
        self.Id         = ID
        self.WorkQueue  = WorkQueue
        self.ResQueue   = ResQueue
        self.TimeOut    = timeout
        self.start()
        
    def run(self):
        try:
            while self.ResQueue.empty():
                callable, args = self.WorkQueue.get(timeout=self.TimeOut)
                Res = callable(*args)
                if Res is not None:
                    self.ResQueue.put(Res)
                    break
                
        except Queue.Empty:
            pass
        except Exception,e:
            print 'MyThread Error%s' % str(e)
        finally:
            pass
    
    def Myexit(self):
        try:
            self.exit()
        except Exception,e:
            print str(e)
        finally:
            pass
        
class WorkMag():
    def __init__(self):
        self.WorkQueue  = Queue.Queue()
        self.ResQueue   = Queue.Queue()
        self.Works      = []
        
    def Start(self,ThreadNum):
        try:
            for nCount in range(ThreadNum):
                Worker = MyWork(WorkQueue = self.WorkQueue,ResQueue = self.ResQueue,ID = nCount)
                self.Works.append(Worker)
            
        except Exception,e:
            pass
        finally:
            pass
        
    def Add_Work(self,callback,arg):
        try:
            self.WorkQueue.put((callback, arg))
        except Exception,e:
            print str(e)
        finally:
            pass
        
    def WaitForComlete(self):
        try:
            for Worker in self.Works:
                if self.ResQueue.empty() is True and Worker.isAlive():
                    Worker.join()
                else:
                    pass
        except Exception,e:
            print str(e)
        finally:
            pass
        
    def Get_Result(self):
        try:
            Res = None
            if self.ResQueue.empty() is False:
                Res = self.ResQueue.get()
        except Exception,e:
            print str(e)
        finally:
            return Res
            pass
        
        
def CallBackTest(I):
    print I
    
def main():
    try:
        WM = WorkMag()
        for nCount in range(10):
            WM.Add_Work(CallBackTest, nCount)
        
        WM.Start(10)
        WM.WaitForComlete()
    except Exception,e:
        print str(e)
    finally:
        pass
    
if __name__ == '__main__':
    main()
    os.system('pause')
    pass