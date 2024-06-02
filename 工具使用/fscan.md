## 常用指令
### 存活主机探测
```SHELL
fscan -h 10.0.2.0/24 -nobr -nopoc -hn 10.0.2.2  
# 注意扫描端口开闭是自动的
#-hn 本机IP 跳过本机
```

### 全模块扫描
```SHELL
fscan -h 10.0.2.15
```

### 指定端口扫描
```SHELL
fscan -h 10.0.2.5 -p 80
```

### SSH爆破
```SHELL
fscan -h 10.0.2.5 -m ssh -userf users.txt -pwdf pass.txt  
# m选项用于选择扫描模式，默认为all

```
## help

```
Usage of fscan:
  -br int
        Brute threads (default 1)
  -c string
        exec command (ssh|wmiexec)
  -cookie string
        set poc cookie,-cookie rememberMe=login
  -debug int
        every time to LogErr (default 60)
  -dns
        using dnslog poc
  -domain string
        smb domain
  -full
        poc full scan,as: shiro 100 key
  -h string
        IP address of the host you want to scan,for example: 192.168.11.11 | 192.168.11.11-255 | 192.168.11.11,192.168.11.12
  -hash string
        hash
  -hf string
        host file, -hf ip.txt
  -hn string
        the hosts no scan,as: -hn 192.168.1.1/24
  -json
        json output
  -m string
        Select scan type ,as: -m ssh (default "all")
  -no
        not to save output log
  -nobr
        not to Brute password
  -nocolor
        no color
  -nopoc
        not to scan web vul
  -noredis
        no redis sec test
  -np
        not to ping
  -num int
        poc rate (default 20)
  -o string
        Outputfile (default "result.txt")
  -p string
        Select a port,for example: 22 | 1-65535 | 22,80,3306 (default "21,22,80,81,135,139,443,445,1433,1521,3306,5432,6379,7001,8000,8080,8089,9000,9200,11211,27017")
  -pa string
        add port base DefaultPorts,-pa 3389
  -path string
        fcgi、smb romote file path
  -ping
        using ping replace icmp
  -pn string
        the ports no scan,as: -pn 445
  -pocname string
        use the pocs these contain pocname, -pocname weblogic
  -pocpath string
        poc file path
  -portf string
        Port File
  -proxy string
        set poc proxy, -proxy http://127.0.0.1:8080
  -pwd string
        password
  -pwda string
        add a password base DefaultPasses,-pwda password
  -pwdf string
        password file
  -rf string
        redis file to write sshkey file (as: -rf id_rsa.pub)
  -rs string
        redis shell to write cron file (as: -rs 192.168.1.1:6666)
  -sc string
        ms17 shellcode,as -sc add
  -silent
        silent scan
  -socks5 string
        set socks5 proxy, will be used in tcp connection, timeout setting will not work
  -sshkey string
        sshkey file (id_rsa)
  -t int
        Thread nums (default 600)
  -time int
        Set timeout (default 3)
  -top int
        show live len top (default 10)
  -u string
        url
  -uf string
        urlfile
  -user string
        username
  -usera string
        add a user base DefaultUsers,-usera user
  -userf string
        username file
  -wmi
        start wmi
  -wt int
        Set web timeout (default 5)
```

### 中文参数解释
```SHELL
  -c string
        ssh命令执行
  -cookie string
        设置cookie
  -debug int
        多久没响应,就打印当前进度(default 60)
  -domain string
        smb爆破模块时,设置域名
  -h string
        目标ip: 192.168.11.11 | 192.168.11.11-255 | 192.168.11.11,192.168.11.12
  -hf string
        读取文件中的目标
  -hn string
        扫描时,要跳过的ip: -hn 192.168.1.1/24
  -m string
        设置扫描模式: -m ssh (default "all")
  -no
        扫描结果不保存到文件中
  -nobr
        跳过sql、ftp、ssh等的密码爆破
  -nopoc
        跳过web poc扫描
  -np
        跳过存活探测
  -num int
        web poc 发包速率  (default 20)
  -o string
        扫描结果保存到哪 (default "result.txt")
  -p string
        设置扫描的端口: 22 | 1-65535 | 22,80,3306 (default "21,22,80,81,135,139,443,445,1433,3306,5432,6379,7001,8000,8080,8089,9000,9200,11211,27017")
  -pa string
        新增需要扫描的端口,-pa 3389 (会在原有端口列表基础上,新增该端口)
  -path string
        fcgi、smb romote file path
  -ping
        使用ping代替icmp进行存活探测
  -pn string
        扫描时要跳过的端口,as: -pn 445
  -pocname string
        指定web poc的模糊名字, -pocname weblogic
  -proxy string
        设置代理, -proxy http://127.0.0.1:8080
  -user string
        指定爆破时的用户名
  -userf string
        指定爆破时的用户名文件
  -pwd string
        指定爆破时的密码
  -pwdf string
        指定爆破时的密码文件
  -rf string
        指定redis写公钥用模块的文件 (as: -rf id_rsa.pub)
  -rs string
        redis计划任务反弹shell的ip端口 (as: -rs 192.168.1.1:6666)
  -silent
        静默扫描,适合cs扫描时不回显
  -sshkey string
        ssh连接时,指定ssh私钥
  -t int
        扫描线程 (default 600)
  -time int
        端口扫描超时时间 (default 3)
  -u string
        指定Url扫描
  -uf string
        指定Url文件扫描
  -wt int
        web访问超时时间 (default 5)
  -pocpath string
        指定poc路径
  -usera string
        在原有用户字典基础上,新增新用户
  -pwda string
        在原有密码字典基础上,增加新密码
  -socks5
        指定socks5代理 (as: -socks5  socks5://127.0.0.1:1080)
  -sc 
        指定ms17010利用模块shellcode,内置添加用户等功能 (as: -sc add)

```