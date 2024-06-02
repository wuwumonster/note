# 什么是SSRF
SSRF(Server-Side Request Forgery:服务端请求伪造),是一种由攻击者构造形成由服务端发起请求的一个安全漏洞。一般情况下，SSRF攻击的目标是从外网无法访问的内部系统。（正是因为它是由服务端发起的，所以它能够请求到与它相连而与外网隔离的内部系统）
SSRF 形成的原因大都是由于服务端提供了从其他服务器应用获取数据的功能且没有对目标地址做过滤与限制。比如从指定URL地址获取网页文本内容，加载指定地址的图片，下载等等。
![](attachments/Pasted%20image%2020240225125529.png)
## URL结构
![](attachments/Pasted%20image%2020240401142236.png)

![](attachments/Pasted%20image%2020240401142335.png)

![](attachments/Pasted%20image%2020240401142344.png)

# 漏洞函数
## PHP
- file_get_contents()
- fsockopen()
	- `fsockopen($hostname,$port,$errno,$errstr,$timeout)
	- 打开一个网络连接或者一个 Unix 套接字连接，初始化一个套接字连接到指定主机（hostname），实现对用户指定 url 数据的获取。该函数会使用 socket 跟服务器建立 tcp 连接，进行传输原始数据。 fsockopen() 将返回一个文件句柄，之后可以被其他文件类函数调用`（例如：fgets()，fgetss()，fwrite()，fclose()还有feof()）`如果调用失败，将返回false` ```
```php
// ssrf.php 
<?php $host=$_GET['url']; 
$fp = fsockopen($host, 80, $errno, $errstr, 30); 
if (!$fp) { 
	echo "$errstr ($errno)<br />\n"; 
} else { 
	$out = "GET / HTTP/1.1\r\n"; 
	$out .= "Host: $host\r\n"; 
	$out .= "Connection: Close\r\n\r\n"; 
	fwrite($fp, $out); 
	while (!feof($fp)) { 
		echo fgets($fp, 128); 
	} 
fclose($fp); 
} 
?>
```
- curl()
- SoapClient
# 利用方式
- gopher
- dict
	- 一个字典服务器协议,`A Dictionary Server Protocol`，允许客户端在使用过程中访问更多字典并且该协议约定服务器端侦听端口号:`2628`
- file
- http/https
## 内网服务
- Apache Hadoop远程命令执行
- axis2-admin部署Server命令执行
- Confluence SSRF
- counchdb WEB API远程命令执行
- dict
- docker API远程命令执行
- Elasticsearch引擎Groovy脚本命令执行
- ftp / ftps（FTP爆破）
- glassfish任意文件读取和war文件部署间接命令执行
- gopher
- HFS远程命令执行
- http、https
- imap/imaps/pop3/pop3s/smtp/smtps（爆破邮件用户名密码）
- Java调试接口命令执行
- JBOSS远程Invoker war命令执行
- Jenkins Scripts接口命令执行
- ldap
- mongodb
- php_fpm/fastcgi 命令执行
- rtsp - smb/smbs（连接SMB）
- sftp
- ShellShock 命令执行
- Struts2 命令执行
- telnet
- tftp（UDP协议扩展）
- tomcat命令执行
- WebDav PUT上传任意文件
- WebSphere Admin可部署war间接命令执行
- zentoPMS远程命令执行
## Redis利用
- 写ssh公钥
- 写crontab
- 写WebShell
- Windows写启动项
- 主从复制加载 .so 文件
- 主从复制写无损文件
## 访问内网&伪协议读取文件
# 攻击应用
- FastCGI
- MySQL
- Redis
	- `redis`服务是在`6379`端口开启的
	- 利用`dict`协议，`dict://127.0.0.1:6379/info`可获取本地`redis`服务配置信息
	- 利用`dict://127.0.0.1:6379/KEYS *`获取 `redis` 存储的内容
# 绕过
- URL解析规则
- IP地址转换
- 302跳转
- DNS重绑定
- IPv6
	- 使用IPv6的本地IP如 `[::]` `0000::1` 或IPv6的内网域名来绕过过滤
- IDN
	- 部分字符会在访问时做一个等价转换，例如 `ⓔⓧⓐⓜⓟⓛⓔ.ⓒⓞⓜ` 和 `example.com` 等同。利用这种方式，可以用 `① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩` 等字符绕过内网限制
# 常见内网网段
```
C类：192.168.0.0 - 192.168.255.255 

B类：172.16.0.0 - 172.31.255.255 

A类：10.0.0.0 - 10.255.255.255
```