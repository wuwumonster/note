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
上面这段代码是一个


这是一个看似安全的代码，对路径的前缀，和文件名后缀的控制了
```php
<?php
$file=$_GET['file'];
include('/var/www/html/upload/'.$file.'.jpg');
?>
```
