Web Scan Demo
Author: idhyt  
Mail: idhyt@hotmail.com

web 扫描器 xss & sql & 网站目录

编写环境： Python_2.75_32 & PyChram

目录结构：

```
webscan
│  
│  webscan.py                                             ----启动模块
│  webscan.bat                                            ----启动脚本
│  
├─config
│      
│      config.py                                          ----配置文件
│      
├─lib
│  │  
│  ├─core                                                 ----核心代码
│  │  │  
│  │  ├─sitedir                                           ----网站目录扫描
│  │  │  │  site_dir_scan.py
│  │  │  │ 
│  │  │  ├─dict
│  │  │  │      cgi.txt
│  │  │  │      cgi1.txt
│  │  │  │      
│  │  │  └─exts
│  │  │          status_code.json
│  │  │          
│  │  ├─sqlinject                                         ----sql注入模块
│  │  │      sql_payloads.json
│  │  │      sql_scan.py
│  │  │      
│  │  ├─webkit
│  │  │      webkit.py                                    ----webkit模块(暂未使用)
│  │  │      
│  │  └─xss                                               ----xss扫描模块
│  │          xss_payloads.json
│  │          xss_scan.py
│  │          
│  ├─parse                                                ----解析模块包
│  │      data.py
│  │      url.py
│  │      web.py
│  │      
│  └─scan                                                 ----扫描方式及任务分发
│          urlscan.py
│          urlsscan.py
├─proxy                                                   ----socket5代理
│      plink.exe
│      plink_init.bat
│      proxy_switch.py
│      socks.py
│      
├─public
│  │  
│  ├─log                                                  ----日志模块
│  │  │  log.py
│  │  │  
│  │  └─logger
│  │          Logger.py
│  │          
│  └─publish                                              ----结果发布模块
│          result2html.py
│          
├─sql                                                     ----数据库操作模块
│      databases.py
│      mysql.py
│      
└─thirdparty                                              ----第三方库
    │  
    └─requests
        │  

```

用法:

对于单个url：
webscan.py -u "http://127.0.0.1/xss.php?x" -c cookies.txt
其中 cookies.txt 为你访问目标站点时的cookies

多url,默认从数据库读取
webscan.py -m 3 -s 1

-m 扫描模式 01 xss; 10 sql; 11 both
-s urls来源 01 数据库; 其他保留,可自动添加

扫描完毕后，会在目录下生结果文件，文件名为当前日期，如2015-01-11-21-23-27

