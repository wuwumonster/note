## Machine Information
As is common in real life Windows pentests, you will start the Fluffy box with credentials for the following account: j.fleischman / J0elTHEM4n1990!
## attack
nmap端口扫描

![](attachments/Pasted%20image%2020250906125355.png)

配置hosts文件,尝试登录

```SHELL
evil-winrm -u j.fleischman -p J0elTHEM4n1990! -i 10.10.11.69
```

无法登录,smb枚举目录
```SHELL
crackmapexec smb 10.10.11.69 -u j.fleischman -p J0elTHEM4n1990! --share
```
![](attachments/Pasted%20image%2020250906130655.png)

SMB枚举用户

```SHELL
crackmapexec smb 10.10.11.69 -u j.fleischman -p J0elTHEM4n1990! --rid-brute
```

![](attachments/Pasted%20image%2020250906131052.png)

