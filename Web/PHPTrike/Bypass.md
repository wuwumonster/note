# MD5
## 0e绕过
#PHP-弱比较绕过
**绕过原理**：PHP在处理字符串时会出现缺陷，如果字符串为’5e2’，本来只是一个正常字符串，但PHP会认为这是科学计数法里的e，那么PHP进行比较时会将这个字符串按照科学计数法计算，即`5e2=5*10^2=500`，由此0e100被认为和0相等。md5加密后的哈希值是一串16进制数，因此需要哈希值第一位为0，第二位为e即可，后面不论是什么都认为和0相等
**md5h后0e开头：**
- QNKCDZO
- 240610708
- s878926199a
- s155964671a
- s1091221200a
- s1665632922a
**经过md5函数加密一次和两次后均以’0e’开头：**
- 7r4lGXCH2Ksu2JNT3BYM
- CbDLytmyGm2xQyaLNhWn
- 770hQgrBOjrcqftrlaZk
MD5值与原值都是0e开头
- 0e215962017
## 数组绕过
#PHP-强比较绕过 #PHP-弱比较绕过 
**绕过原理**：无论是PHP弱比较还是强比较，md5()函数无法处理数组，如果传入的是数组，会返回NULL，两个数组经过加密后返回值均为NULL，形成相等。
```php
?a[]=1&b[]=2
```

## MD5碰撞绕过
#MD5碰撞-Fastcoll
可以碰撞出结果相同的文件
GET
```
a=%4d%c9%68%ff%0e%e3%5c%20%95%72%d4%77%7b%72%15%87%d3%6f%a7%b2%1b%dc%56%b7%4a%3d%c0%78%3e%7b%95%18%af%bf%a2%00%a8%28%4b%f3%6e%8e%4b%55%b3%5f%42%75%93%d8%49%67%6d%a0%d1%55%5d%83%60%fb%5f%07%fe%a2&b=%4d%c9%68%ff%0e%e3%5c%20%95%72%d4%77%7b%72%15%87%d3%6f%a7%b2%1b%dc%56%b7%4a%3d%c0%78%3e%7b%95%18%af%bf%a2%02%a8%28%4b%f3%6e%8e%4b%55%b3%5f%42%75%93%d8%49%67%6d%a0%d1%d5%5d%83%60%fb%5f%07%fe%a2
```
POST 传参时需要再次url编码
```
a%3D%254d%25c9%2568%25ff%250e%25e3%255c%2520%2595%2572%25d4%2577%257b%2572%2515%2587%25d3%256f%25a7%25b2%251b%25dc%2556%25b7%254a%253d%25c0%2578%253e%257b%2595%2518%25af%25bf%25a2%2500%25a8%2528%254b%25f3%256e%258e%254b%2555%25b3%255f%2542%2575%2593%25d8%2549%2567%256d%25a0%25d1%2555%255d%2583%2560%25fb%255f%2507%25fe%25a2%26b%3D%254d%25c9%2568%25ff%250e%25e3%255c%2520%2595%2572%25d4%2577%257b%2572%2515%2587%25d3%256f%25a7%25b2%251b%25dc%2556%25b7%254a%253d%25c0%2578%253e%257b%2595%2518%25af%25bf%25a2%2502%25a8%2528%254b%25f3%256e%258e%254b%2555%25b3%255f%2542%2575%2593%25d8%2549%2567%256d%25a0%25d1%25d5%255d%2583%2560%25fb%255f%2507%25fe%25a2
```
## MD5截断比较
#MD5脚本爆破
```php
<?php 
$a=$_GET['a']; 
if(substr(md5($str), 0, 6) === "edef"){ 
	echo 'success!'; 
}
```

```php
from multiprocessing.dummy import Pool as tp import hashlib knownMd5 = '666666' #已知的md5明文 
def md5(text): 
	return hashlib.md5(str(text).encode('utf-8')).hexdigest() 
def findCode(code): 
	key = code.split(':') 
	start = int(key[0]) 
	end = int(key[1]) 
	for code in range(start, end): 
		if md5(code)[0:6] == knownMd5: 
			print(code) 
list=[] 
for i in range(1): 
# 这里的range(number)指爆破出多少结果停止 
	list.append(str(10000000*i) + ':' + str(10000000*(i+1))) 
	pool = tp() # 使用多线程加快爆破速度 
	pool.map(findCode, list) 
	pool.close() 
	pool.join()
```

## MD5万能密码
- `ffifdyop`
**绕过原理**：利用ffifdyop这个字符串md5函数处理后哈希值为276f722736c95d99e921722cf9ed621c，[Mysql](https://cloud.tencent.com/product/cdb?from_column=20065&from=20065)刚好会把hex转化成字符串，恰好这个哈希值转化后是’or’6<乱码> 即 `'or'66�]��!r,��b`，这样就构成了一个万能密码。除了这个字符串之外，129581926211651571912466741651878684928也有同样的效果

## NAN和INF

```php
<?php $a = NAN; $b = NAN; if($a != $b && md5($a) == md5($b)){ echo 'success!'; }
```

**绕过原理**：NAN和INF，分别为非数字和无穷大，但是var_dump一下它们的数据类型却是double，那么在md5函数处理它们的时候，是将其直接转换为字符串”NAN”和字符串”INF”使用的，但是它们拥有特殊的性质，它们与任何数据类型（除了true）做强类型或弱类型比较均为false，甚至NAN=NAN都是false，但md5(‘NAN’)=md5(‘NAN’)为true。（我试了试发现NAN雀实可以，但INF没成功不知道为啥，不解…）

# SHA1
## 数组绕过
sha1函数同样无法处理数组，如果传入数组会返回NULL，可以绕过强弱比较
## sha1碰撞
这是两个SHA1值相同而不一样(SHA256的值不同)的pdf文件
```
a=%25PDF-1.3%0A%25%E2%E3%CF%D3%0A%0A%0A1%200%20obj%0A%3C%3C/Width%202%200%20R/Height%203%200%20R/Type%204%200%20R/Subtype%205%200%20R/Filter%206%200%20R/ColorSpace%207%200%20R/Length%208%200%20R/BitsPerComponent%208%3E%3E%0Astream%0A%FF%D8%FF%FE%00%24SHA-1%20is%20dead%21%21%21%21%21%85/%EC%09%239u%9C9%B1%A1%C6%3CL%97%E1%FF%FE%01%7FF%DC%93%A6%B6%7E%01%3B%02%9A%AA%1D%B2V%0BE%CAg%D6%88%C7%F8K%8CLy%1F%E0%2B%3D%F6%14%F8m%B1i%09%01%C5kE%C1S%0A%FE%DF%B7%608%E9rr/%E7%ADr%8F%0EI%04%E0F%C20W%0F%E9%D4%13%98%AB%E1.%F5%BC%94%2B%E35B%A4%80-%98%B5%D7%0F%2A3.%C3%7F%AC5%14%E7M%DC%0F%2C%C1%A8t%CD%0Cx0Z%21Vda0%97%89%60k%D0%BF%3F%98%CD%A8%04F%29%A1 
b=%25PDF-1.3%0A%25%E2%E3%CF%D3%0A%0A%0A1%200%20obj%0A%3C%3C/Width%202%200%20R/Height%203%200%20R/Type%204%200%20R/Subtype%205%200%20R/Filter%206%200%20R/ColorSpace%207%200%20R/Length%208%200%20R/BitsPerComponent%208%3E%3E%0Astream%0A%FF%D8%FF%FE%00%24SHA-1%20is%20dead%21%21%21%21%21%85/%EC%09%239u%9C9%B1%A1%C6%3CL%97%E1%FF%FE%01sF%DC%91f%B6%7E%11%8F%02%9A%B6%21%B2V%0F%F9%CAg%CC%A8%C7%F8%5B%A8Ly%03%0C%2B%3D%E2%18%F8m%B3%A9%09%01%D5%DFE%C1O%26%FE%DF%B3%DC8%E9j%C2/%E7%BDr%8F%0EE%BC%E0F%D2%3CW%0F%EB%14%13%98%BBU.%F5%A0%A8%2B%E31%FE%A4%807%B8%B5%D7%1F%0E3.%DF%93%AC5%00%EBM%DC%0D%EC%C1%A8dy%0Cx%2Cv%21V%60%DD0%97%91%D0k%D0%AF%3F%98%CD%A4%BCF%29%B1
```

# 空格过滤
## Linux
### $IFS
```SHELL
cat${IFS}flag 
cat$IFS$9flag 
cat$IFS$1flag
```

### < <> {,} %09 %20
```SHELL
cat<flag 
cat<>flag 
{cat,flag} 
cat%09flag 
cat%20flag
```
< 或<>与通配符一起使用时没有回显，使用不能同时使用
用逗号实现空格功能，需要用{}括起来
在PHP环境下可以使用%09(tab)绕过空格
# is_numeric()
如果指定的变量是数字和数字字符串则返回 TRUE，否则返回 FALSE，注意浮点型返回空值，即 FALSE。
is_numeric函数对于空字符%00，无论是%00放在前后都可以判断为非数值，而%20空格字符只能放在数值后。

```
?what=1'
?what=1,
?what=1%00
# 都可以绕过
```
# strcmp函数绕过
利用strcmp函数将数组或者对象类型与字符串进行比较会返回-1，但是从5.3开始，会返回0当传入`?id[]=1`时即可bypass

# array_search（）、in_array()绕过
array_search() 函数在数组中搜索某个键值，并返回对应的键名。in_array() 函数搜索数组中是否存在指定的值。基本功能是相同的，也就是说绕过姿势也相同。利用函数接入到了不符合的类型返回“0”这个特性，直接绕过检测。所以payload：`?test[]=0`。
# switch()绕过
如果switch是数字类型的case的判断时，switch会将其中的参数转换为int类型
```php
<?php $i ="3name"; 
switch ($i) { 
case 0: 
case 1: 
case 2: 
	echo "this is two";
	break; 
case 3: 
	echo "flag"; 
	break; 
} 
?>
```
# 布尔类型 True 与非零非 NULL 变量比较都会是 True
在PHP中任何类型的值, 与bool比较都会被转化成bool比较当转换为 bool 时，以下值被认为是 **`false`**：
- 布尔值 **`false`** 本身
- 整型值 `0`（零）
- 浮点型值 `0.0`（零）`-0.0`（零）
- 空字符串 `""`，以及字符串 `"0"`
- 不包括任何元素的数组
- 单位类型 NULL（包括尚未赋值的变量）
- 内部对象的强制转换行为重载为 bool。例如：由不带属性的空元素创建的 SimpleXML 对象。

所有其它值都被认为是 **`true`**（包括 资源 和 **`NAN`**）。

# 字符串过滤
## mb_strtolower
![](attachments/Pasted%20image%2020240401094610.png)


# 变量覆盖
## extract()
`extract($_POST)`和`extract($_GET)`将传入的get和post参数的参数名作为php的参数名，值作为参数的值，如果当前代码中已经有对应的参数名，会将其覆盖
##  `$$`导致的变量覆盖
```PHP
$flag=id
$$flag = $id
```

## 全局变量覆盖
register_globals

## parse_str()
这个函数把查询字符串解析到变量中,如果为多个变量则是放入数组
```PHP
parse_str('a=1');
# $a=1
parse_str('b=2&c=3',$array);
# $array = Aarry([b] => 2,[c]=> 3)
```

## import_request_variables
import_request_variables 函数可以在 register_global = off 时，把 GET/POST/Cookie 变量导入全局作用域中。
```PHP
import_request_variables('G');
# G为get传参
import_request_variables('P');
# P为post传参
# 开启后例如 http://example.com?id=a 就直接拿到 $id=a
```

# 科学计数法
```PHP
<?php
var_dump('==10e2' == '1e3');
# bool(true)
```
# 弱比较
## 空格无视
```PHP
var_dump('0xABCdef'       == '     0xABCdef');
# true (Output for hhvm-3.18.5 - 3.22.0, 7.0.0 - 7.2.0rc4: false)
```

## 字符串转换
若一个数字和一个字符串进行比较或者进行运算时，PHP会把字符串转换成数字再进行比较。若字符串以数字开头，则取开头数字作为转换结果，不能转换为数字的字符串（例如"aaa"是不能转换为数字的字符串，而"123"或"123aa"就是可以转换为数字的字符串）或null，则转换为0；

布尔值true和任意字符串都弱相等

当字符串被当作一个数值来处理时，如果该字符串没有包含’.’,‘e’,'E’并且其数值在整形的范围之内，该字符串作为int来取值，其他所有情况下都被作为float来取值，并且字符串开始部分决定它的取值，开始部分为数字，则其值就是开始的数字，否则，其值为0
```PHP
'123aaa123' == 123 // true
'aaa' == 0 // true
'aaa' == True // true
'0x01' == 1 // true PHP7.0 后十六进制字符串不再作为数字
'' == 0 == false == NULL // true
```

## 运算规则
```PHP
$a = 'a';
var_dump(++$a);
// string(1) "b"
var_dump($a+1);
// int(1)
```

# overflow
- 32位
	- int(2147483647)
- 64位
	- int(9223372036854775807)
# 浮点数
```PHP
var_dump(1.000000000000001 == 1); // bool(false)
var_dump(1.0000000000000001 == 1); // bool(true)
```

```PHP
$a = 0.1 * 0.1;
var_dump($a); // double(0.01)
var_dump($a == 0.01); // bool(false)
```
# 函数

## trim
去除字符前空白
未设置第二参数，去除：
- `" "` (0x20)
- `"\t"` (0x09)
- `"\n"` (0x0A)
- `"\x0B"` (0x0B)
- `"\r"` (0x0D)
- `"\0"` (0x00)
>不包括 `\f` 0x0C
>is_numeric() 允许`\f`在开头

```PHP
var_dump(is_numeric(" \f\t\n\0123")); //bool(true)
```

## preg_replace
- 第一個參數用 `/e` 修飾符，`$replacement` 會被當成 PHP code 執行
    - 必須有匹配到才會執行
    - PHP 5.5.0 起，會產生 `E_DEPRECATED` 錯誤
    - PHP 7.0.0 不再支援，用 `preg_replace_callback()` 代替


## sprintf / vprintf
- 對格式化字串的類型沒檢查
- 格式化字串中 % 後面的字元(除了 % 之外)會被當成字串類型吃掉
    - 例如 `%\`、`%'`、`%1$\'`
    - 在某些 SQLi 過濾狀況下，`%' and 1=1#` 中的單引號會被轉義成 `\'`，`%\` 又會被吃掉，`'` 成功逃逸
    - 原理：sprintf 實作是用 switch...case...
        - 碰到未知類型，`default` 不處理
## file_put_contents
第二个参数如果是数组，会被拼接为字符串
```PHP
<?php
$test = $_GET['txt'];
if(preg_match('[<>?]', $test)) die('bye');
file_put_contents('output', $test);
```
可以直接`?txt[]=<?php phpinfo(); ?>`写入
## ereg
`ereg` 和 `eregi` 在 PHP 7.0.0 已經被移除

## intval
四舍五入
```PHP
var_dump(intval(012)); // int(10)
var_dump(intval("012")); // int(12)
```
## chr()
- 大于256会mod 256
- 小于0会加上256的倍数直到大于0
# 通配符
- `"` => `.`
    - `a"php`
- `>` => `?`
    - `a.p>p`
    - `a.>>>`
- `<` => `*`
    - `a.<`

# PCRE回溯次数
- `pcre.backtrack_limit`
- 预设回溯次数为`1000000`
- 超过后`preg_match()`返回`false`

# ??? 
```PHP
$a="9D9"; 
var_dump(++$a);
// string(3) "9E0"
$a="9E0"; 
var_dump(++$a);
// double(10)
```