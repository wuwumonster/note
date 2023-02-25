# pipline 隧道传输绕过
## 原理
HTTP 协议是由 TCP 协议封装而来，当浏览器发起一个 HTTP 请求时，浏览器先和服务器建立起连接 TCP 连接，然后发送 HTTP 数据包（即我们用burpsuite 截获的数据），其中包含了一个 Connection 字段，一般值为 close，Apache 等 WEB 容器根据这个字段决定是保持该 TCP 连接或是断开。当发送的内容太大，超过一个 HTTP 包容量，需要分多次发送时，值会变成 keep-alive，即本次发起的 HTTP 请求所建立的 TCP 连接不断开，直到所发送内容结束 Connection 为 close 为止。
## 操作
- 关闭 burp 中 Repeater 模块的 Content-Length 自动更新
- 将下一份数据包直接加在上一份参数的后面

# chunked分块绕过
# Content-Type协议未覆盖绕过
# Content-Type协议未覆盖绕过+chunked分块绕过组合技
# 协议未覆盖绕过进阶技——fliename 混淆伪装绕过