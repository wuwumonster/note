IP: 10.10.11.57
### 扫描
```
fscan -h 10.10.11.57

   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.3
start infoscan
10.10.11.57:22 open
10.10.11.57:80 open
[*] alive ports len is: 2
start vulscan
[*] WebTitle http://10.10.11.57        code:302 len:154    title:302 Found 跳转url: http://cypher.htb/
已完成 1/2 [-] ssh 10.10.11.57:22 root 1 ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
已完成 1/2 [-] ssh 10.10.11.57:22 root root@111 ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
已完成 1/2 [-] ssh 10.10.11.57:22 root 123456789 ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
已完成 1/2 [-] ssh 10.10.11.57:22 root abc123456 ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
已完成 1/2 [-] ssh 10.10.11.57:22 root sysadmin ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
已完成 1/2 [-] ssh 10.10.11.57:22 admin admin ssh: handshake failed: ssh: unable to authenticate, attempted methods [none password], no supported methods remain
已完成 2/2
```

配置hosts文件






