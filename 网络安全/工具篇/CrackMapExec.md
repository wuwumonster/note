## 简介
[CrackMapExec（CME）](https://github.com/byt3bl33d3r/CrackMapExec)是一款后渗透利用工具，可帮助自动化大型活动目录(AD)网络安全评估任务。其缔造者[@byt3bl33d3r](https://twitter.com/byt3bl33d3r)称，该工具的生存概念是，“利用AD内置功能/协议达成其功能，并规避大多数终端防护/IDS/IPS解决方案。”
apt-get install crackmapexec

## 帮助
```SHELL
usage: crackmapexec [-h] [-t THREADS] [--timeout TIMEOUT] [--jitter INTERVAL] [--darrell] [--verbose] {ftp,ssh,smb,winrm,ldap,rdp,mssql} ...

      ______ .______           ___        ______  __  ___ .___  ___.      ___      .______    _______ ___   ___  _______   ______
     /      ||   _  \         /   \      /      ||  |/  / |   \/   |     /   \     |   _  \  |   ____|\  \ /  / |   ____| /      |
    |  ,----'|  |_)  |       /  ^  \    |  ,----'|  '  /  |  \  /  |    /  ^  \    |  |_)  | |  |__    \  V  /  |  |__   |  ,----'
    |  |     |      /       /  /_\  \   |  |     |    <   |  |\/|  |   /  /_\  \   |   ___/  |   __|    >   <   |   __|  |  |
    |  `----.|  |\  \----. /  _____  \  |  `----.|  .  \  |  |  |  |  /  _____  \  |  |      |  |____  /  .  \  |  |____ |  `----.
     \______|| _| `._____|/__/     \__\  \______||__|\__\ |__|  |__| /__/     \__\ | _|      |_______|/__/ \__\ |_______| \______|

                                                A swiss army knife for pentesting networks
                                    Forged by @byt3bl33d3r and @mpgn_x64 using the powah of dank memes

                                           Exclusive release for Porchetta Industries users
                                                       https://porchetta.industries/

                                                   Version : 5.4.0
                                                   Codename: Indestructible G0thm0g

options:
  -h, --help            show this help message and exit
  -t THREADS            set how many concurrent threads to use (default: 100)
  --timeout TIMEOUT     max timeout in seconds of each thread (default: None)
  --jitter INTERVAL     sets a random delay between each connection (default: None)
  --darrell             give Darrell a hand
  --verbose             enable verbose output

protocols:
  available protocols

  {ftp,ssh,smb,winrm,ldap,rdp,mssql}
    ftp                 own stuff using FTP
    ssh                 own stuff using SSH
    smb                 own stuff using SMB
    winrm               own stuff using WINRM
    ldap                own stuff using LDAP
    rdp                 own stuff using RDP
    mssql               own stuff using MSSQL

```