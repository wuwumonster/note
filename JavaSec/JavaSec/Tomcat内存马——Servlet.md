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

getWrapper的声明和用例

![](attachments/Pasted%20image%2020230316151633.png)






###  Servlet的注册
在之前的[Java Web基础](../../Java%20Web/Java%20Web基础.md)中有说到过，Servlet是在首次对其进行访问时，检测是否存在该Servlet没有的话就会执行init开始初始化，现在我使用的是注解的方式来完成Servlet的注册的
在上面的执行流程中，最后一个invoke，在调用allocate前，servlet的值还是null，那么我们就到invoke后面去仔细看看
