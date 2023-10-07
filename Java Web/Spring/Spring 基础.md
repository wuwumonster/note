# Ioc容器
IoC也被称为依赖注入（DI）。它是一个过程，对象仅通过构造参数、工厂方法的参数或在对象实例被构造或从工厂方法返回后在其上设置的属性来定义其依赖关系（即它们与之合作的其他对象）。
容器在创建 bean 时注入这些依赖关系。这个过程从根本上说是Bean本身通过使用直接构建类或诸如服务定位模式的机制来控制其依赖关系的实例化或位置的逆过程（因此被称为控制反转）。
**Spring Framework的IoC容器的基础**
- `org.springframework.beans`
- `org.springframework.context`

>`BeanFactory` 提供了配置框架和基本功能，而 `ApplicationContext` 则增加了更多的企业特定功能。

## 容器概述
`org.springframework.context.ApplicationContext` 接口代表Spring IoC容器，负责实例化、配置和组装bean。容器通过读取配置元数据来获得关于要实例化、配置和组装哪些对象的指示。配置元数据以XML、Java注解或Java代码表示。
可以通过提供少量的 XML 配置来指示容器使用 Java 注解或代码作为元数据格式，以声明性地启用对这些额外元数据格式的支持。

应用程序类与配置元数据相结合，这样，在 `ApplicationContext` 被创建和初始化后，就有了一个完全配置好的可执行系统或应用程序。

![](attachments/Pasted%20image%2020231007191731.png)

### 配置元数据
配置元数据，将会告诉Spring容器在应用中的实例化、配置和组装对象。

>基于XML的元数据并不是唯一被允许的格式，Ioc容器本身是和配置元数据完全解耦的。

- 基于注解的配置：适用基于注解的配置元数据定义Bean
- Java-based configuration ：使用Java而不是XML文件来定义你的应用类外部的Bean。要使用这些特性，请参阅 `@Configuration`, `@Bean`, `@Import`, 和 `@DependsOn` 注解。

>Spring的配置包括至少一个，通常是一个以上的Bean定义，容器必须管理这些定义。基于XML的配置元数据将这些Bean配置为顶层 `<beans/>` 元素内的 `<bean/>` 元素。Java配置通常使用 `@Configuration` 类中的 `@Bean` 注解的方法。

通常，你会定义服务层对象、持久层对象（如存储库或数据访问对象（DAO））、表现对象（如Web控制器）、基础设施对象（如JPA `EntityManagerFactory`）、JMS队列等等。

下面的例子显示了基于XML的配置元数据的基本结构。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.springframework.org/schema/beans
        https://www.springframework.org/schema/beans/spring-beans.xsd">

    <bean id="..." class="..."> (1) (2)
        <!-- 这个bean的合作者和配置在这里 -->
    </bean>

    <bean id="..." class="...">
        <!-- c这个bean的合作者和配置在这里 -->
    </bean>

    <!-- 更多bean 定义在这里 -->

</beans>
```
- `id` 属性是一个字符串，用于识别单个Bean定义。
- `class` 属性定义了 Bean 的类型，并使用类的全路径名