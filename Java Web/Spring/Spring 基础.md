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

## Bean 概述
一个Spring IoC容器管理着一个或多个Bean。这些Bean是用你提供给容器的配置元数据创建的（例如，以XML `<bean/>` 定义的形式）。
在容器本身中，这些Bean定义被表示为 `BeanDefinition` 对象，它包含（除其他信息外）以下元数据。
- 一个全路径类名：通常，被定义的Bean的实际实现类。
- Bean的行为配置元素，它说明了Bean在容器中的行为方式（scope、生命周期回调，等等）。
- 对其他Bean的引用，这些Bean需要做它的工作。这些引用也被称为合作者或依赖。
- 要在新创建的对象中设置的其他配置设置—​例如，pool的大小限制或在管理连接池的Bean中使用的连接数。

| 属性                    | 解释        |
| ----------------------- | ----------- |
| Class                   | 实例化Bean  |
| Name                    | Bean命名    |
| Scope                   | Bean Scope  |
| Constructor argument    | 依赖注入    |
| Properties              | 依赖注入    |
| Autowiring mode         | 注入协助者  |
| Lazy initialzation mode | 懒加载 Bean |
| Initialization method   | 初始化回调  |
| Destruction             | 销毁回调            |

### Bean 命名
每个Bean都有一个或多个标识符（identifier）。这些标识符在承载Bean的容器中必须是唯一的。一个Bean通常只有一个标识符。然而，如果它需要一个以上的标识符，多余的标识符可以被视为别名。
你不需要为Bean提供一个 `name` 或 `id`。如果你不明确地提供 `name` 或 `id`，容器将为该 Bean 生成一个唯一的名称。然而，如果你想通过使用 `ref` 元素或服务定位器风格的查找来引用该 bean 的名称，你必须提供一个名称。

#### Bean的命名规则
惯例是在命名Bean时使用标准的Java惯例来命名实例字段名。也就是说，Bean的名字以小写字母开始，然后以驼峰字母开头。这种名称的例子包括 `accountManager`、`accountService`、`userDao`、`loginController` 等等。
```XML
<alias name="fromName" alias="toName"/>
```
在这种情况下，一个名为 `fromName` 的bean（在同一个容器中）在使用这个别名定义后，也可以被称为 `toName`。
>在Java配置中`@Bean` 注解可以被用来提供别名。

### Bean 实例化
bean 定义（definition）本质上是创建一个或多个对象的“配方”。容器在被要求时查看命名的Bean的“配方”，并使用该Bean定义所封装的配置元数据来创建（或获取）一个实际的对象。
如果你使用基于XML的配置元数据，你要在 `<bean/>` 元素的 `class` 属性中指定要实例化的对象的类型（或class）。这个 `class` 属性（在内部是 `BeanDefinition` 实例的 `Class` 属性）通常是强制性的。（关于例外情况，请看 [用实例工厂方法进行实例化](https://springdoc.cn/spring/core.html#beans-factory-class-instance-factory-method) 和 [Bean 定义（Definition）的继承](https://springdoc.cn/spring/core.html#beans-child-bean-definitions)）。你可以以两种方式之一使用 `Class` 属性。
- 通常，在容器本身通过反射式地调用构造函数直接创建Bean的情况下，指定要构造的Bean类，有点相当于Java代码中的 `new` 操作符。
    
- 在不太常见的情况下，即容器在一个类上调用 `static` 工厂方法来创建 bean 时，要指定包含被调用的 `static` 工厂方法的实际类。从 `static` 工厂方法的调用中返回的对象类型可能是同一个类或完全是另一个类。

>**嵌套类名**
>如果你想为一个嵌套类配置一个Bean定义（definition），你可以使用嵌套类的二进制名称或源（source）名称。
例如，如果你在 `com.example` 包中有一个叫做 `SomeThing` 的类，而这个 `SomeThing` 类有一个叫做 `OtherThing` 的静态嵌套类，它们可以用美元符号（`$`）或点（`.`）分开。所以在Bean定义中的 `class` 属性的值将是 `com.example.SomeThing$OtherThing` 或 `com.example.SomeThing.OtherThing`。

#### 用构造函数进行实例化
当你用构造函数的方法创建一个Bean时，所有普通的类都可以被Spring使用并与之兼容。也就是说，被开发的类不需要实现任何特定的接口，也不需要以特定的方式进行编码。只需指定Bean类就足够了。然而，根据你对该特定Bean使用的IoC类型，你可能需要一个默认（空）构造函数。
Spring IoC容器几乎可以管理任何你希望它管理的类。它并不局限于管理真正的JavaBean。大多数Spring用户更喜欢真正的JavaBean，它只有一个默认的（无参数）构造函数，以及按照容器中的属性建模的适当的setter和getter。

#### 用静态工厂方法实例化
在定义一个用静态工厂方法创建的Bean时，使用 `class` 属性来指定包含 `static` 工厂方法的类，并使用名为 `factory-method` 的属性来指定工厂方法本身的名称。你应该能够调用这个方法（有可选的参数，如后文所述）并返回一个活的对象，随后该对象被视为通过构造函数创建的。这种Bean定义的一个用途是在遗留代码中调用 `static` 工厂。
```xml
<bean id="clientService"
    class="examples.ClientService"
    factory-method="createInstance"/>

```
#### 用实例工厂方法进行实例化
与用静态工厂方法实例化类似，用实例工厂方法进行的实例化从容器中调用现有 bean 的非静态方法来创建一个新的 bean。要使用这种机制，请将 `class` 属性留空，并在 `factory-bean` 属性中指定当前（或父代或祖代）容器中的一个 Bean 的名称，该容器包含要被调用来创建对象的实例方法。用 `factory-method` 属性设置工厂方法本身的名称。
```xml
<!-- the factory bean, which contains a method called createInstance() -->
<bean id="serviceLocator" class="examples.DefaultServiceLocator">
    <!-- inject any dependencies required by this locator bean -->
</bean>

<!-- the bean to be created via the factory bean -->
<bean id="clientService"
    factory-bean="serviceLocator"
    factory-method="createClientServiceInstance"/>
```

```java
public class DefaultServiceLocator {

    private static ClientService clientService = new ClientServiceImpl();

    public ClientService createClientServiceInstance() {
        return clientService;
    }
}
```

## 依赖
### 依赖注入
依赖注入（DI）是一个过程，对象仅通过构造参数、工厂方法的参数或在对象实例被构造或从工厂方法返回后在其上设置的属性来定义它们的依赖（即与它们一起工作的其它对象）。然后，容器在创建 bean 时注入这些依赖。这个过程从根本上说是Bean本身通过使用类的直接构造或服务定位模式来控制其依赖的实例化或位置的逆过程（因此被称为控制反转）。
DI有两个主要的变体：
- 基于构造器的依赖注入
- 基于setter的依赖注入

#### 基于构造器的依赖注入
基于构造函数的 DI 是通过容器调用带有许多参数的构造函数来完成的，每个参数代表一个依赖。调用带有特定参数的 `static` 工厂方法来构造 bean 几乎是等价的，本讨论对构造函数的参数和 `static` 工厂方法的参数进行类似处理。
```java
public class SimpleMovieLister {

    // the SimpleMovieLister has a dependency on a MovieFinder
    private final MovieFinder movieFinder;

    // a constructor so that the Spring container can inject a MovieFinder
    public SimpleMovieLister(MovieFinder movieFinder) {
        this.movieFinder = movieFinder;
    }

    // business logic that actually uses the injected MovieFinder is omitted...
}
```

#### 构造函数参数解析
构造函数参数解析匹配是通过使用参数的类型进行的。如果 bean 定义中的构造器参数不存在潜在的歧义，那么构造器参数在 bean 定义中的定义顺序就是这些参数在 bean 被实例化时被提供给适当的构造器的顺序。
```java
package x.y;

public class ThingOne {

    public ThingOne(ThingTwo thingTwo, ThingThree thingThree) {
        // ...
    }
}
```
假设 `ThingTwo` 和 `ThingThree` 类没有继承关系，就不存在潜在的歧义。因此，下面的配置可以正常工作，你不需要在 `<constructor-arg/>` 元素中明确指定构造函数参数的索引或类型。
```xml
<beans>
    <bean id="beanOne" class="x.y.ThingOne">
        <constructor-arg ref="beanTwo"/>
        <constructor-arg ref="beanThree"/>
    </bean>

    <bean id="beanTwo" class="x.y.ThingTwo"/>

    <bean id="beanThree" class="x.y.ThingThree"/>
</beans>
```

```java
package examples;

public class ExampleBean {

    // Number of years to calculate the Ultimate Answer
    private final int years;

    // The Answer to Life, the Universe, and Everything
    private final String ultimateAnswer;

    public ExampleBean(int years, String ultimateAnswer) {
        this.years = years;
        this.ultimateAnswer = ultimateAnswer;
    }
}
```

在前面的情况下，如果你通过使用 `type` 属性显式地指定构造函数参数的类型，容器就可以使用简单类型的类型匹配，如下例所示。

```xml
<bean id="exampleBean" class="examples.ExampleBean">
    <constructor-arg type="int" value="7500000"/>
    <constructor-arg type="java.lang.String" value="42"/>
</bean>
```

可以使用 `index` 属性来明确指定构造函数参数的索引，如下例所示。

```xml
<bean id="exampleBean" class="examples.ExampleBean">
    <constructor-arg index="0" value="7500000"/>
    <constructor-arg index="1" value="42"/>
</bean>
```

>索引（下标）从0开始

#### 基于Setter的依赖注入
基于 Setter 的 DI 是通过容器在调用无参数的构造函数或无参数的 `static` 工厂方法来实例化你的 bean 之后调用 Setter 方法来实现的。


#### 依赖的解析过程
- `ApplicationContext` 是用描述所有bean的配置元数据创建和初始化的。配置元数据可以由XML、Java代码或注解来指定。
- 对于每个Bean来说，它的依赖是以属性、构造函数参数或静态工厂方法的参数（如果你用它代替正常的构造函数）的形式表达的。在实际创建Bean时，这些依赖被提供给Bean。
- 每个属性或构造函数参数都是要设置的值的实际定义，或对容器中另一个Bean的引用。
- 每个作为值的属性或构造函数参数都会从其指定格式转换为该属性或构造函数参数的实际类型。默认情况下，Spring 可以将以字符串格式提供的值转换为所有内置类型，如 `int`、`long`、`String`、`boolean` 等等。