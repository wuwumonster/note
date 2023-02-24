dict 协议是一个字典服务器协议，通常用于让客户端使用过程中能够访问更多的字典源，能用来探测端口的指纹信息

协议格式：`dict://<host>:<port>/<dict-path>`
一般为：`dict://<host>:<port>/info` 探测端口应用信息  
执行命令：`dict://<host>:<port>/命令:参数` 冒号相当于空格，在 redis 利用中，只能利用未授权访问的 redis