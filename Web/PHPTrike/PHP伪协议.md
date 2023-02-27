# PHP伪协议种类
- file:// — 访问本地文件系统 
- http:// — 访问 HTTP(s) 网址 
- ftp:// — 访问 FTP(s) URLs 
- php:// — 访问各个输入/输出流（I/O streams） 
- zlib:// — 压缩流 data:// — 数据（RFC 2397） 
- glob:// — 查找匹配的文件路径模式 
- phar:// — PHP 归档 
- ssh2:// — Secure Shell 2 
- rar:// — RAR ogg:// — 音频流 
- expect:// — 处理交互式的流

# php://filter

-   php://filter可以获取指定文件源码。当与包含文件结合时，php://filter流会当中php文件执行
| 名称                  | 描述                                                                 |
| --------------------- | -------------------------------------------------------------------- |
| resource=<数据流>     | 必要参数                                                             |
| read=<读链的筛选列表> | 该参数可选。可以设定一个或多个过滤器名称，以管道符`|`分隔        |
| write=<写链的筛选列表>|该参数可选。可以设定一个或多个过滤器名称，以管道符`|`分隔     |
| <; 两个链的筛选列表>  | 任何没有以 `read=` 或 `write=` 作前缀 的筛选器列表会视情况应用于读或写链 |

resource=<数据流>

必要参数

read=<读链的筛选列表>

该参数可选。可以设定一个或多个过滤器名称，以管道符（

write=<写链的筛选列表>

该参数可选。可以设定一个或多个过滤器名称，以管道符（

<; 两个链的筛选列表>

任何没有以 read= 或 write= 作前缀 的筛选器列表会视情况应用于读或写链。

# 过滤器

-   字符串过滤器
    -   string.rot13
    -   string.toupper 将所有字符转换为大写
    -   string.tolower 将所有字符转换为小写
    -   string.strip_tags 用来处理读入的所有标签
-   转换过滤器
    -   convert.base64-encode & convert.base64-decode base64加解密
    -   convert.quoted-printable-encode & convert.quoted-printable-decode 可以翻译为可打印字符引用编码，使用可以打印的ASCLL编码的字符表示各种编码形式下的字符
-   压缩过滤器
    -   zlib.deflate 压缩→php://filter/zlib.deflate/resource=flag.php ps: 此时输出为压缩后信息外带信息往往与解压配合使用
    -   zlib.inflate 解压 外带→php://filter/zlib.deflate|zlib.inflate/resource=flag.php
    -   bzip2.compress 解压
    -   bzip2.decompress 压缩
-   加密过滤器→PHP 7.7.0后已废弃
    -   mcrypt.* 对称加密
    -   mdecrypt.* 对称解密

# php://input

-   写入木马
-   命令执行
# data://伪协议

相当于执行了php语句

# phar://伪协议

无论后缀是什么都会当作压缩包来解压

用法：?file=phar://压缩包/内部文件 phar://xxx.png/shell.php 注意： PHP > =5.3.0 压缩包需要是zip协议压缩，rar不行，将木马文件压缩后，改为其他任意格式的文件都可以正常使用。 步骤： 写一个一句话木马文件shell.php，然后用zip协议压缩为shell.zip，然后将后缀改为png等其他格式

# zip://伪协议

用法：?file=zip://[压缩文件绝对路径]#[压缩文件内的子文件名] zip://xxx.png#shell.php

条件： PHP > =5.3.0，注意在windows下测试要5.3.0<PHP<5.4 才可以 #在浏览器中要编码为%23，否则浏览器默认不会传输特殊字符。

# zlib:// 和 bzip://与zip://为相同类型