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

在找unserliaze的时候发现大多都写死了序列化内容，没有写死的不是很复杂就是变量不可控，现在来考虑能够触发phar的函数