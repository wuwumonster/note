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
简单讲一个jar包它可以通过配置文件来适用一个功能那么他就是框架

>例如dbutils 数据可简化技术 log4j 日志输出，log4j就是框架

![](attachments/Pasted%20image%2020231009080821.png)

# SpringFramework 介绍
## Spring和SpringFramework概念
- 广义的 Spring：Spring 技术栈（全家桶）
	广义上的 Spring 泛指以 Spring Framework 为基础的 Spring 技术栈。
	经过十多年的发展，Spring 已经不再是一个单纯的应用框架，而是逐渐发展成为一个由多个不同子项目（模块）组成的成熟技术，例如 Spring Framework、Spring MVC、SpringBoot、Spring Cloud、Spring Data、Spring Security 等，其中 Spring Framework 是其他子项目的基础。
	这些子项目涵盖了从企业级应用开发到云计算等各方面的内容，能够帮助开发人员解决软件发展过程中不断产生的各种实际问题，给开发人员带来了更好的开发体验。
- 狭义的 Spring：Spring Framework（基础框架）
	狭义的 Spring 特指 Spring Framework，通常我们将它称为 Spring 框架。
	Spring Framework（Spring框架）是一个开源的应用程序框架，由SpringSource公司开发，最初是为了解决企业级开发中各种常见问题而创建的。它提供了很多功能，例如：依赖注入（Dependency Injection）、面向切面编程（AOP）、声明式事务管理（TX）等。其主要目标是使企业级应用程序的开发变得更加简单和快速，并且Spring框架被广泛应用于Java企业开发领域。
	Spring全家桶的其他框架都是以SpringFramework框架为基础！

## SpringFramework 主要功能模块
SpringFramework框架结构图：
![](attachments/Pasted%20image%2020231009082809.png)

| 功能模块       | 功能介绍                                                    |
| -------------- | ----------------------------------------------------------- |
| Core Container | 核心容器，在 Spring 环境下使用任何功能都必须基于 IOC 容器。 |
| AOP&Aspects    | 面向切面编程                                                |
| TX             | 声明式事务管理。                                            |
| Spring MVC     | 提供了面向Web应用程序的集成功能。                           |

# Spring IoC 容器和核心概念
## 组件和组件管理概念
### 什么是组件
回顾常规的三层架构处理请求流程：
![](attachments/Pasted%20image%2020231009083706.png)
整个项目就是由各种组件搭建而成的：
![](attachments/Pasted%20image%2020231009083720.png)

### Spring - 组件管理（IoC）
组件可以完全交给Spring 框架进行管理，Spring框架替代了程序员原有的new对象和对象属性赋值动作等
我们只需要编写元数据（配置文件）告知Spring 管理哪些类组件和他们的关系即可
>注意：组件是映射到应用程序中所有可重用组件的Java对象，应该是可复用的功能对象！

- 组件一定是对象
- 对象不一定是组件

综上所述，Spring 充当一个组件容器，创建、管理、存储组件，减少编码压力

### Spring管理优势
1. 降低了组件之间的耦合性：Spring IoC容器通过依赖注入机制，将组件之间的依赖关系削弱，减少了程序组件之间的耦合性，使得组件更加松散地耦合。
2. 提高了代码的可重用性和可维护性：将组件的实例化过程、依赖关系的管理等功能交给Spring IoC容器处理，使得组件代码更加模块化、可重用、更易于维护。
3. 方便了配置和管理：Spring IoC容器通过XML文件或者注解，轻松的对组件进行配置和管理，使得组件的切换、替换等操作更加的方便和快捷。
4. 交给Spring管理的对象（组件），方可享受Spring框架的其他功能（AOP,声明事务管理）等

## Spring IoC 容器和容器实现
### 程序中的普通容器&复杂容器
**普通容器**
- 数组
- 集合：List
- 集合：Set
**复杂容器**
Servlet 容器能够管理 Servlet(init,service,destroy)、Filter、Listener 这样的组件的一生，所以它是一个复杂容器。

|名称|时机|次数|
|---|---|---|
|创建对象|默认情况：接收到第一次请求 修改启动顺序后：Web应用启动过程中|一次|
|初始化操作|创建对象之后|一次|
|处理请求|接收到请求|多次|
|销毁操作|Web应用卸载之前|一次|

SpringIoC 容器也是一个复杂容器。它们不仅要负责创建组件的对象、存储组件的对象，还要负责调用组件的方法让它们工作，最终在特定情况下销毁组件。
>Spring管理组件的容器，就是一个复杂容器，不仅存储组件，也可以管理组件之间依赖关系，并且创建和销毁组件等

### SpringIoC 容器介绍
Spring IoC 容器，负责实例化、配置和组装 bean（组件）。容器通过读取配置元数据来获取有关要实例化、配置和组装组件的指令。配置元数据以 XML、Java 注解或 Java 代码形式表现。它允许表达组成应用程序的组件以及这些组件之间丰富的相互依赖关系。
![](attachments/Pasted%20image%2020231009084939.png)
Spring IoC 容器，负责实例化、配置和组装 bean（组件）。容器通过读取配置元数据来获取有关要实例化、配置和组

### SpringIoC 容器具体接口和实现类
**SpringIoC容器接口：**
`BeanFactory` 接口提供了一种高级配置机制，能够管理任何类型的对象，它是SpringIoC容器标准化超接口！
`ApplicationContext` 是 `BeanFactory` 的子接口。它扩展了以下功能：
- 更容易与 Spring 的 AOP 功能集成
- 消息资源处理（用于国际化）
- 特定于应用程序给予此接口实现，例如Web 应用程序的 `WebApplicationContext`

>简而言之， `BeanFactory` 提供了配置框架和基本功能，而 `ApplicationContext` 添加了更多特定于企业的功能。 `ApplicationContext` 是 `BeanFactory` 的完整超集

**ApplicationContext容器实现类：**

| 类型名                             | 简介                                                                                     |
| ---------------------------------- | ------------------------------------------------------------------------------------------- |
| ClassPathXmlApplicationContext     | 通过读取类路径下的 XML 格式的配置文件创建 IOC 容器对象                                      | 
| FileSystemXmlApplicationContext    | 通过文件系统路径读取 XML 格式的配置文件创建 IOC 容器对象                                    |
| AnnotationConfigApplicationContext | 通过读取Java配置类创建 IOC 容器对象                                                         |
| WebApplicationContext              | 专门为 Web 应用准备，基于 Web 环境创建 IOC 容器对象，并将对象引入存入 ServletContext 域中。 |  

### SpringIoC 容器管理配置方式
Spring框架提供了多种配置方式：XML配置方式、注解方式和Java配置类方式
1. XML配置方式：是Spring框架最早的配置方式之一，通过在XML文件中定义Bean及其依赖关系、Bean的作用域等信息，让Spring IoC容器来管理Bean之间的依赖关系。该方式从Spring框架的第一版开始提供支持。
2. 注解方式：从Spring 2.5版本开始提供支持，可以通过在Bean类上使用注解来代替XML配置文件中的配置信息。通过在Bean类上加上相应的注解（如@Component, @Service, @Autowired等），将Bean注册到Spring IoC容器中，这样Spring IoC容器就可以管理这些Bean之间的依赖关系。
3. **Java配置类**方式：从Spring 3.0版本开始提供支持，通过Java类来定义Bean、Bean之间的依赖关系和配置信息，从而代替XML配置文件的方式。Java配置类是一种使用Java编写配置信息的方式，通过@Configuration、@Bean等注解来实现Bean和依赖关系的配置。
### Spring IoC / DI 概念总结
#### IoC 容器
Spring IoC 容器，负责实例化、配置和组装 bean（组件）核心容器。容器通过读取配置元数据来获取有关要实例化、配置和组装组件的指令。
#### IoC (Inversion of Contral)控制反转
IoC 主要是针对对象的创建和调用控制而言的，也就是说，当应用程序需要使用一个对象时，不再是应用程序直接创建该对象，而是由 IoC 容器来创建和管理，即控制权由应用程序转移到 IoC 容器中，也就是“反转”了控制权。这种方式基本上是通过依赖查找的方式来实现的，即 IoC 容器维护着构成应用程序的对象，并负责创建这些对象。
#### DI (Dependency Injection)依赖注入
DI 是指在组件之间传递依赖关系的过程中，将依赖关系在容器内部进行处理，这样就不必在应用程序代码中硬编码对象之间的依赖关系，实现了对象之间的解耦合。在 Spring 中，DI 是通过 XML 配置文件或注解的方式实现的。它提供了三种形式的依赖注入：构造函数注入、Setter 方法注入和接口注入。

# Spring IoC 实践和应用
## Spring IoC / DI 实现步骤
1. 配置元数据（配置）
   配置元数据，既是编写交给SpringIoC容器管理组件的信息，配置方式有三种。
   基于 XML 的配置元数据的基本结构：
```XML
	<?xml version="1.0" encoding="UTF-8"?>
<!-- 此处要添加一些约束，配置文件的标签并不是随意命名 -->
<beans xmlns="http://www.springframework.org/schema/beans"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.springframework.org/schema/beans
    https://www.springframework.org/schema/beans/spring-beans.xsd">

  <bean id="..." [1] class="..." [2]>  
    <!-- collaborators and configuration for this bean go here -->
  </bean>

  <bean id="..." class="...">
    <!-- collaborators and configuration for this bean go here -->
  </bean>
  <!-- more bean definitions go here -->
</beans>
```
- `id`属性是标识单个Bean定义的字符串
- `class`属性定义Bean的类型并使用完全限定的类名
2. 实例化IoC容器
   ApplicationContext 是一个高级工厂的接口，能够维护不同 bean 及其依赖项的注册表。通过使用方法 T getBean(String name, Class requiredType) ，您可以检索 bean 的实例。
   允许读取 Bean 定义并访问它们，如以下示例所示：
```java
//创建ioc容器对象，指定配置文件，ioc也开始实例组件对象
ApplicationContext context = new ClassPathXmlApplicationContext("services.xml", "daos.xml");
//获取ioc容器的组件对象
PetStoreService service = context.getBean("petStore", PetStoreService.class);
//使用组件对象
List<String> userList = service.getUsernameList();
```
3. 获取Bean（组件）
`ApplicationContext` 是一个高级工厂的接口，能够维护不同 bean 及其依赖项的注册表。通过使用方法 `T getBean(String name, Class<T> requiredType)` ，您可以检索 bean 的实例。
允许读取 Bean 定义并访问它们，如以下示例所示：
```java
//创建ioc容器对象，指定配置文件，ioc也开始实例组件对象
ApplicationContext context = new ClassPathXmlApplicationContext("services.xml", "daos.xml");
//获取ioc容器的组件对象
PetStoreService service = context.getBean("petStore", PetStoreService.class);
//使用组件对象
List<String> userList = service.getUsernameList();
```