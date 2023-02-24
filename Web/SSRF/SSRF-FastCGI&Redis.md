# FastCGI
[(70条消息) SSRF漏洞之FastCGI利用篇_F4ke12138的博客-CSDN博客_fastcgi漏洞](https://blog.csdn.net/weixin_39664643/article/details/114977217)

[FastCGI](../协议/FastCGI.md)
SSRF打FastCGI，基于Gopher协议，向9000端口发送伪造的信息流，由于9000端口的监听就是PHP-FPM在解析到对应的信息后进行命令执行
## FPM脚本 + urlencode
监听本机的9000端口并将对应流量写入文件，用fpm,py的脚本执行后对应文件就获得了打9000端口的数据报文，然后进行两次url编码就可以用gopher协议来传入
## Gopherus
![](attachment/Pasted%20image%2020230222083822.png)

# Redis
## 绝对路径写shell
## 写ssh公钥
## crontab 写定时任务反弹shell