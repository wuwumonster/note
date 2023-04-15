## `[MRCTF2020]`你传你🐎呢 #文件上传
文件上传发现被过滤

![](attachments/Pasted%20image%2020230415111247.png)

修改content-type 为image/jpeg和后缀名后上传成功

![](attachments/Pasted%20image%2020230415111607.png)

/var/www/html/upload/ebe5b85736548ba0a494c533dec573bc/shell.jpg

这里写.htaccess文件更改解析

```
AddType application/x-httpd-php .jpg
```