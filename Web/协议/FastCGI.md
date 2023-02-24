# 简述
FastCGI是一个通讯协议，HTTP是浏览器和服务器中间件进行数据交换的协议，而FastCGI是服务器中间件与某个语言后端进行数据交换的协议。与HTTP协议相同有着自己的格式，FastCGI协议由多个record组成，record==header==和==body==部分，服务器中间件将这二者按照fastcgi的规则封装好发给语言后端，语言后端解码后拿到具体数据，进行指定操作，并将结果返回给服务器中间件
结构如下
```c++
typedef struct {
  /* Header */
  unsigned char version; // 版本
  unsigned char type; // 本次record的类型
  unsigned char requestIdB1; // 本次record对应的请求id
  unsigned char requestIdB0;
  unsigned char contentLengthB1; // body体的大小
  unsigned char contentLengthB0;
  unsigned char paddingLength; // 额外块大小
  unsigned char reserved; 
 
  /* Body */
  unsigned char contentData[contentLength];
  unsigned char paddingData[paddingLength];
} FCGI_Record;
```
各个部分的作用在这里就不细说
在与PHP交互时就会涉及到一个应用程序`PHP-FPM(FastCGI进程管理器)` FPM是一个fastcgi的协议解析器，服务器中间件就负责将用户的请求按照fastcgi协议将TCP流解析为真正的数据

# 脚本链接
[Fastcgi PHP-FPM Client && Code Execution (github.com)](https://gist.github.com/phith0n/9615e2420f31048f7e30f3937356cf75)
# 参考链接
[Fastcgi协议分析 && PHP-FPM未授权访问漏洞 && Exp编写 | 离别歌 (leavesongs.com)](https://www.leavesongs.com/PENETRATION/fastcgi-and-php-fpm.html)