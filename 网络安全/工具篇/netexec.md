NetExec（nxc）是一个强大的网络服务利用工具，旨在自动化评估大型网络的安全性。它是 CrackMapExec 的继任者，支持多种协议（SMB、LDAP、WinRM、MSSQL、RDP、FTP 等），并通过模块化设计提供枚举、凭据测试、漏洞扫描和后渗透功能。

## 目标协议
```
smb
ssh
ldap
ftp
wmi
winrm
rdp
vnc
mssql
nfs
```

## 格式
每个协议都支持通过 CIDR 表示法、IP 地址、IP 范围、主机名、包含目标列表的文件或所有目标的组合来支持目标
```SHELL
nxc <protocol> poudlard.wizard
nxc <protocol> 192.168.1.0 192.168.0.2
nxc <protocol> 192.168.1.0 192.168.0.2
nxc <protocol> 192.168.1.0-28 10.0.0.1
nxc <protocol> 192.168.1.0-28 10.0.0.1-67
```