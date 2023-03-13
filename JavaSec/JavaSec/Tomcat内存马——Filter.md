## 原理
在[Java Web基础](../../Java%20Web/Java%20Web基础.md)里面有提到客户端的请求是经过了Filter的过滤后才交给servlet处理的，就像下面的代码
*servlet.java*
```java
package org.example.demo;  
  
import javax.servlet.*;  
import javax.servlet.http.*;  
import javax.servlet.annotation.*;  
import java.io.IOException;  
  
@WebServlet(name = "Servlet", value = "/Servlet")  
public class Servlet extends HttpServlet {  
    @Override  
    public void init() throws ServletException {  
        System.out.println("servlet初始化");  
    }  
  
    @Override  
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {  
        System.out.println("Servlet处理请求");  
        response.getWriter().println("<html>\n" +  
                "<body>\n" +  
                "<h2>Hello wuwumonster </h2>\n" +  
                "</body>\n" +  
                "</html>\n");  
    }  
  
    @Override  
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {  
  
    }  
  
    @Override  
    public void destroy() {  
        System.out.println("Servlet销毁");  
        super.destroy();  
    }  
}
```
*filter1.java*
```java
package org.example.demo.filter;  
  
import javax.servlet.*;  
import javax.servlet.annotation.*;  
import java.io.IOException;  
  
@WebFilter(filterName = "Filter1", urlPatterns = "/Servlet")  
public class Filter1 implements Filter {  
    public void init(FilterConfig config) throws ServletException {  
        System.out.println("Filter1创建");  
    }  
  
    public void destroy() {  
        System.out.println("Filter1销毁");  
    }  
  
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws ServletException, IOException {  
        System.out.println("Filter1执行");  
        chain.doFilter(request, response);  
    }  
}
```

处理的请求就像这样

![](attachments/Pasted%20image%2020230312225836.png)

>所以说，只要在程序中注册一个恶意的filter并使其处于Filter链的最前面，就可以确保我们的请求能够去触发这个恶意的filter

## Filter执行流程分析
在filter1中调用`doFilter`的地方下断点进行调试

![](attachments/Pasted%20image%2020230312230852.png)

在执行请求后可以看到基本的函数调用

![](attachments/Pasted%20image%2020230312233716.png)

但是在这个时候我们步入是无法看到函数流程的，需要导入对应的`catalina`和`tomcat`的jar包

这个时候就可以直观的看到代码了

代码执行,现在在`ApplicationFilterChain`，看名字的话大概可以知道是做了一个全局安全的开启检查，然后就直接进到`else`中，调用`internaklDoFilter()`

![](attachments/Pasted%20image%2020230313090949.png)

在`internalDoFilter`中这个if能够看得出来是有对Filter的遍历获取

![](attachments/Pasted%20image%2020230313091634.png)

![](attachments/Pasted%20image%2020230313091757.png)

这里有两个filter但是只有第一个是我们自己写的filter，pos为1时获取的是tomcat的filter,调试的时候进来pos就是1
进行`getFilter`，这里已经是一个新的class叫做`ApplicationFilterConfi

```java
Filter getFilter() throws ClassCastException, ClassNotFoundException, IllegalAccessException, InstantiationException, ServletException, InvocationTargetException, NamingException, IllegalArgumentException, NoSuchMethodException, SecurityException {  
    if (this.filter != null) {  
        return this.filter;  
    } else {  
        String filterClass = this.filterDef.getFilterClass();  
        this.filter = (Filter)this.getInstanceManager().newInstance(filterClass);  
        this.initFilter();  
        return this.filter;  
    }  
}
```

get后