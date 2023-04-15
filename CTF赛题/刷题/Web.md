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
