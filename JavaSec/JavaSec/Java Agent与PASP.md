# Java Agent与PASP

## 概念

Java 代理 (agent) 是在你的main方法前的一个拦截器 (interceptor)，也就是在main方法执行之前，执行agent的代码。

agent 的代码与你的main方法在同一个JVM中运行，并被同一个system classloader装载，被同一的安全策略 (security policy) 和上下文 (context) 所管理。

Java Agent 这个技术，对于大多数同学来说都比较陌生，但是多多少少又接触过，实际上，我们平时用的很多工具，都是基于Java Agent实现的，例如常见的热部署JRebel，各种线上诊断工具（btrace, greys），还有阿里开源的线上诊断工具 arthas。

其实Java Agent一点都不神秘，也是一个Jar包，只是启动方式和普通Jar包有所不同，对于普通的Jar包，通过指定类的main函数进行启动，但是Java Agent并不能单独启动，必须依附在一个Java应用程序运行，有点像寄生虫的感觉。

## 基本配置和工作流程

在 META-INF 目录下创建MANIFEST.MF 文件，在MANIFEST.MF 文件指定Agent的启动类

```xml
Manifest-Version: 1.0
Archiver-Version: Plexus Archiver
Built-By: jack
#静态 agent 类
Premain-Class: org.example.App
#动态 agent 类
Agent-Class: org.example.App
是否允许重复装载
Can-Redefine-Classes: true
Can-Retransform-Classes: true
Created-By: Apache Maven 3.2.5
Build-Jdk: 1.8.0_40
```

**Agent-Class&Premain-Class**

指定这两个值是因为在加载Java Agent之后，会找到 Agent-Class 或者 Premain-Class 指定的类，并运行对应的 agentmain 或者 premain 方法。

> MANIFEST.MF 文件，也可以通过Maven配置，在打包的时候自动生成
> 


## RASP技术

原理图


RASP进程是直接嵌入到APP执行流程中去，这一点和WAF有本质的不同。正是由于这一点，RASP可以避免WAF规则被各种奇异的编码绕过的痛点，因为Agent进程最终获取的参数正是各个层面编码转换完成后真正执行的参数。并且RASP不像WAF那样需要拦截每个请求去check是否命中了攻击的规则，而是当HOOK住的危险函数被调用之后，才会触发检测逻辑。

### 实现方法

我们可以在Transform类中注册很多CodeFileVisitor，比如每个漏洞类型编写一个Visitor，其实这里asm提供的这个Visitor是个基于事件模型的处理类，编写起代码来和XML的事件解析差不多。在这些Visitor中我们就可以只监控我们关心的一些危险函数，比如JDBC的execSQL函数，利用asm编程获取到调用这个函数时的具体参数，然后编写我们的规则来判定是否存在漏洞，如果存在漏洞就根据配置进行上报、阻断动作

<aside>
💡 Rasp技术的本质就是如何实现这样一个HOOK动作的agent。各个语言的实现都不同，比如PHP和Java的机制就不同，PHP是通过编写PHP扩展的形式进行HOOK与漏洞判断、上报。但是漏洞判定规则是通用的，因此这部分完全可以做成通用的服务运行。

</aside>