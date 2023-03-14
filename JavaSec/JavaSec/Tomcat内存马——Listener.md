## 基础环境
Servlet，Filter环境与Filter内存马的环境一致，增加了Listener
*Listener.java*

```java
package org.example.listener;  
  
import javax.servlet.ServletRequestEvent;  
import javax.servlet.ServletRequestListener;  
import javax.servlet.annotation.WebListener;  
  
@WebListener("Listener")  
public class Listener implements ServletRequestListener {  
    public Listener() {  
    }  
  
    @Override  
    public void requestDestroyed(ServletRequestEvent servletRequestEvent) {  
  
    }  
  
    @Override  
    public void requestInitialized(ServletRequestEvent servletRequestEvent) {  
        System.out.println("Listener 被调用");  
  
    }  
}
```

在实际运行中的顺序

![](attachments/Pasted%20image%2020230314162559.png)

>在IDEA中搭建tomcat时需要注意字节码的版本，特别是当出现内部java编译器出错的时候

## Listener运行流程
在前面[Java Web基础](../../Java%20Web/Java%20Web基础.md)的时候提到过执行顺序为 *Listener -> Filter -> Servlet* ，Listener的具体功能实现所依赖的函数，当在idea中新建一个Listener时就可以看到这些函数和基本的解释
```java
@Override  
public void contextInitialized(ServletContextEvent sce) {  
    /* This method is called when the servlet context is initialized(when the Web application is deployed). */  
}  
  
@Override  
public void contextDestroyed(ServletContextEvent sce) {  
    /* This method is called when the servlet Context is undeployed or Application Server shuts down. */  
}  
  
@Override  
public void sessionCreated(HttpSessionEvent se) {  
    /* Session is created. */  
}  
  
@Override  
public void sessionDestroyed(HttpSessionEvent se) {  
    /* Session is destroyed. */  
}  
  
@Override  
public void attributeAdded(HttpSessionBindingEvent sbe) {  
    /* This method is called when an attribute is added to a session. */  
}  
  
@Override  
public void attributeRemoved(HttpSessionBindingEvent sbe) {  
    /* This method is called when an attribute is removed from a session. */  
}  
  
@Override  
public void attributeReplaced(HttpSessionBindingEvent sbe) {  
    /* This method is called when an attribute is replaced in a session. */  
}
```

当然这里缺少了对于Listener内存马来说最为，适用的方法，就是上面的listener中的两个方法`requestInitialized`和`requestDestroyed`
当访问页面的时候触发

先前看这个方法的接口

![](attachments/Pasted%20image%2020230314181322.png)

### Listener的执行
先在执行的Listener中下个断点调试，看的出来后面的一系列invoke都是前面分析过的很熟悉的流程

![](attachments/Pasted%20image%2020230314181855.png)

这里有一个不一样的函数方法`fireRequestInitEvent`,


