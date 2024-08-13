## MSF安装指北——Windows环境
在kali中已经自带这里只对windows的安装进行说明
[Directory Tree (metasploit.com)](https://windows.metasploit.com/)

在直接使用msi安装的时候发现安装后应用中存在msf但是在安装路径无法找到对应文件夹，如安

### Ruby环境安装
安装地址[RubyInstaller for Windows](https://rubyinstaller.org/)

安装流程 ->[Windows环境下安装Ruby教程_ruby.exe-CSDN博客](https://blog.csdn.net/Alive_tree/article/details/103043158)
>这里使用的powershell脚本安装安装后如果没有对应的依赖环境无法启动

![](attachments/Pasted%20image%2020240812174627.png)


### MSF安装
```POWERSHELL
[CmdletBinding()]
Param(
    $DownloadURL = "https://windows.metasploit.com/metasploitframework-latest.msi",
    $DownloadLocation = "$env:APPDATA/Metasploit",
    $InstallLocation = "D:\web\DomainAttack\framework\msf",
    $LogLocation = "$DownloadLocation/install.log"
)

If(! (Test-Path $DownloadLocation) ){
    New-Item -Path $DownloadLocation -ItemType Directory
}

If(! (Test-Path $InstallLocation) ){
    New-Item -Path $InstallLocation -ItemType Directory
}

$Installer = "$DownloadLocation/metasploit.msi"

Invoke-WebRequest -UseBasicParsing -Uri $DownloadURL -OutFile $Installer

& $Installer /q /log $LogLocation INSTALLLOCATION="$InstallLocation"
```

安装后设置环境变量`D:\web\DomainAttack\framework\msf\metasploit-framework\bin`