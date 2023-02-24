## 简述
RESP协议是redis服务之间数据传输的通信协议，redis客户端和redis服务端之间通信会采取RESP协议因此我们后续构造payload时也需要转换成RESP协议的格式。
## 协议说明
RESP协议是应该支持一下数据类型的序列化协议：
- 简单字符串
- 错误类型
- 整数
- 批量字符串
- 数组
RESP在Redis中的请求-响应协议方式
- 客户端将命令作为Blk Strings的RESP数组发送到Redis服务器
- 服务器根据命令实现回复一种RESP类型
  在RESP中某些数据类型取决于第一个字节
- `+`代表简单字符串Simple Strings
- `:`代表整数
- `-`代表错误类型
- `$` 代表Bulk Strings
- `*`代表数组