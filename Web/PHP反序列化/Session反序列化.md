`PHP session`的存储机制是由`session.serialize_handler`来定义引擎的，默认是以文件的方式存储，且存储的文件是由`sess_sessionid`来决定文件名的
文件的内容始终是session值的序列化之后的内容
`session.serialize_handler`定义的引擎

|处理器名称|存储格式|
|---|---|
|php|键名 + 竖线 + 经过`serialize()`函数序列化处理的值|
|php_binary|键名的长度对应的 ASCII 字符 + 键名 + 经过`serialize()`函数序列化处理的值|
|php_serialize|经过serialize()函数序列化处理的**数组**|

>**注：自 PHP 5.5.4 起可以使用 _php_serialize_**

`php_serialize`在内部简单地直接使用 `serialize/unserialize`函数，并且不会有`php`和 `php_binary`所具有的限制。 使用较旧的序列化处理器导致`$_SESSION` 的索引既不能是数字也不能包含特殊字符(`|` 和 `!`) 。

### php 处理器
 ```php
 <?php
error_reporting(0);
ini_set('session.serialize_handler','php');
session_start();
$_SESSION['session'] = $_GET['session'];
?>
```

`session` 为`$_SESSION['session']`的键名，`|`后为传入 GET 参数经过序列化后的值
![](attachments/Pasted%20image%2020240218131855.png)
### php_binary
```php
<?php
error_reporting(0);
ini_set('session.serialize_handler','php_binary');
session_start();
$_SESSION['sessionsessionsessionsessionsession'] = $_GET['session'];
?>
```
![](attachments/Pasted%20image%2020240218131933.png)

`#`为键名长度对应的 ASCII 的值，`sessionsessionsessionsessionsessions`为键名，`s:7:"xianzhi";`为传入 GET 参数经过序列化后的值

### php_serialize
```php
<?php
error_reporting(0);
ini_set('session.serialize_handler','php_serialize');
session_start();
$_SESSION['session'] = $_GET['session'];
?>
```

![](attachments/Pasted%20image%2020240218132003.png)

`a:1`表示`$_SESSION`数组中有 1 个元素，花括号里面的内容即为传入 GET 参数经过序列化后的值