# 技术体系结构
## 总体技术体系
- 单一架构
	一个项目，一个工程，导出为一个war包，在一个Tomcat上运行。也叫all in one。
	
![](attachments/Pasted%20image%2020231009080328.png)

>单一架构，项目主要应用技术框架为：Spring , SpringMVC , Mybatis

- 分布式架构
一个项目（对应 IDEA 中的一个 project），拆分成很多个模块，每个模块是一个 IDEA 中的一个 module。每一个工程都是运行在自己的 Tomcat 上。模块之间可以互相调用。每一个模块内部可以看成是一个单一架构的应用。

![](attachments/Pasted%20image%2020231009080508.png)

>分布式架构，项目主要应用技术框架：SpringBoot (SSM), SpringCloud , 中间件等

## 框架概念和理解
框架( Framework )是一个集成了基本结构、规范、设计模式、编程语言和程序库等基础组件的软件系统，它可以用来构建更高级别的应用程序。框架的设计和实现旨在解决特定领域中的常见问题，帮助开发人员更高效、更稳定地实现软件开发目标。

站在文件结构的角度理解框架，可以将框架总结：**框架 = jar包+配置文件**

![](attachments/Pasted%20image%2020231009080821.png)

# SpringFramework 介绍