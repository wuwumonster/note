# 大小写绕过

针对于在关键字匹配中只针对了大写或小写，而代码在执行时本身对大小写不敏感


# 关键字的构造和替代
在某些时候无法通过大小写来躲过WAF的匹配机制，但WAF对关键字的处理本身有缺陷，比如删除，替换为“”

## 双写绕过
比如WAF将对应关键字删去，例如CTFHUB中文件上传双写后缀
```php
$name = basename($_FILES['file']['name']);
$blacklist = array("php", "php5", "php4", "php3", "phtml", "pht", "jsp", "jspa", "jspx", "jsw", "jsv", "jspf", "jtml", "asp", "aspx", "asa", "asax", "ascx", "ashx", "asmx", "cer", "swf", "htaccess", "ini");
$name = str_ireplace($blacklist, "", $name);
```
在上传webshell后发现后缀被删除了
![](attachment/Pasted%20image%2020230225202904.png)

于是双写后缀，成功上传
![](attachment/Pasted%20image%2020230225203009.png)

## 同效关键字，函数替换
- 比如最常见和花样最多的空格=>`${IFS}`,单双引号来达到同样的间隔效果,`%20`,`%09`,`%0a`,`%0b`,`%0c`,`%0d`,`%a0`,`/**/`等
- 以及sql中的各类函数平替
- linux中读文件cat,more,tac等


## 字符拼接
在python的SSTI中比较常见，用引号等方式来隔开原本被ban的关键字，但是又不影响代码执行，mysql函数中`+`有相同的效果

## 编码绕过

编码绕过广泛的存在于需要对输入进行解析的地方，利用于数据传输两端支持的编码差异的情况，常用的有
- URL编码
- 十六进制编码
- Unicode编码
- base64编码
更广泛的说，有些时候在对文件内部内容进行检测识别时，可以通过gzip等方式将文件打包传输，而此时内部进行解析时又支持这类的格式
这里提一下在2022补天白帽大会的一个议题《Java Webshell攻防下的黑魔法》
![](attachment/Pasted%20image%2020230225205133.png)

## 注释
- 在PHP中使用注释来规避空格，或者sql语句中来结束语句的查询
- 在mysql中存在内联注释`/*!注释内容*/`当后面所接的数据库版本号时，当实际的版本等于或是高于那个字符串，应用程序就会将注释内容解释为SQL，否则就会当做注释来处理。默认的，当没有接版本号时，是会执行里面的内容的


## 参数污染
当对一个参数传入两个值时，不同的服务器又不同的处理方法`wumonster.cn?key=value1&key=value2`
| 服务器           | 处理                    |
| ---------------- | ----------------------- |
| PHP/Apache       | 取最后一个值 key=value2 |
| Flask            | 取第一个值   key=value1 |
| JSP/Tomcat       | 取第一个值   key=value1 |
| Perl(CGI)/Apache | 取第一个值   key=value1 |
| ASP/IIS          |     key=value1,value2                    |
| Python/Apache                 | 取全部(List)                        |

## 缓冲区溢出
在编写waf的语言自身没有缓冲区保护机制时，当输入超出其缓冲区长度，就会引发bug而形成绕过，有一些栈溢出的感觉

##  分块数据包
在post传参中通过在最后两行空白行来形成空白块，加上Transfer-Encoding:chunked

# Bypass进阶

[基于HTTP协议特性绕WAF](基于HTTP协议特性绕WAF.md)