:: -s 1 数据库取数据
:: -m 1 xss 2 sql
:: -p 1 挂代理

:: xss
start python webscan.py -s 1 -m 1 -p 1

:: sql
start python webscan.py -s 1 -m 2 -p 1

pause