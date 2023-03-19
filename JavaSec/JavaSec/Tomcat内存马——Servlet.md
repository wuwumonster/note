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

到这里得话其实整个过程都看得差不多了，但是很乱，因为原本得目的带着一些想看看注释类型得webservlet是怎么注册的，所以直接拿web.xml从请求那里，跟了一次

