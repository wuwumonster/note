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
在上面的目录穿越中我们提到了`open_basedir`的相关设置，那么这样的设置是否就无法绕过呢，当然是可以的，是可以通过`反射+glob://`伪协议或者其他的一些Trick来完成绕过的，在这里先引入php伪协议在文件包含中的应用
[PHP伪协议](../PHPTrike/PHP伪协议.md)
### file://
`file://`伪协议本身是对本地的文件系统进行访问
