# 常用的Web服务器
**Tomcat**
- Tomcat 服务器是一个免费的开放源代码的Web 应用服务器，属于轻量级应用服务器，在中小型系统和并发访问用户不是很多的场合下被普遍使用，是开发和调试JSP 程序的首选。对于一个初学者来说，可以这样认为，当在一台机器上配置好Apache 服务器，可利用它响应HTML（标准通用标记语言下的一个应用）页面的访问请求。实际上Tomcat是Apache 服务器的扩展，但运行时它是独立运行的，所以当你运行tomcat 时，它实际上作为一个与Apache 独立的进程单独运行的
**JBoss**
- 一个基于J2EE的开放源代码的应用服务器。 JBoss代码遵循LGPL许可，可以在任何商业应用中免费使用。JBoss是一个管理EJB的容器和服务器，支持EJB 1.1、EJB 2.0和EJB3的规范。但JBoss核心服务不包括支持servlet/JSP的WEB容器，一般与Tomcat或Jetty绑定使用。
**GlassFish**
- GlassFish 是用于构建 Java EE 5应用服务器的开源开发项目的名称。它基于 Sun Microsystems 提供的 Sun Java System Application Server PE 9 的源代码以及 Oracle 贡献的 TopLink 持久性代码。
**Resin**
- Resin是CAUCHO公司的产品，是一个非常流行的支持servlets和jsp的引擎，速度非常快。Resin本身包含了一个支持HTTP/1.1的WEB服务器。它不仅可以显示动态内容，而且它显示静态内容的能力也非常强，速度直逼APACHESERVER。许多站点都是使用该WEB服务器构建的。
**WebLogic**
- WebLogic是美国Oracle公司出品的一个application server，确切的说是一个基于JAVAEE架构的中间件，WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。

# Java Web三大件
- Servlet
- Filter
- Listener

> 当 Tomcat 接收到请求时候，依次会经过 Listener -> Filter -> Servlet

## Servlet
Java Servlet 是运行在 Web 服务器或应用服务器上的程序，它是作为来自 Web 浏览器或其他 HTTP 客户端的请求和 HTTP 服务器上的数据库或应用程序之间的中间层。
### Tomcat服务器和Servlet版本的对应关系
| Tomcat版本 | Servlet/JSP版本 | JavaEE版本 | 运行环境 |
| ---------- | --------------- | ---------- | -------- |
| 4.1        | 2.3/1.2         | 1.3        | JDK1.3   |
| 5.0        | 2.4/2.0         | 1.4        | JDK1.4   |
| 5.5/6.0    | 2.5/2.1         | 5.0        | JDK5.0   |
| 7.0        | 3.0/2.2         | 6.0        | JDK6.0   |
| 8.0        | 3.1/2.3         | 7.0        | JDK8.0   |
| 9.0        | 4.0/2.3         |            |          |
| 10.1           |  6.0/3.1               |            |          |

### Servlet与请求处理
- 客户端发起一个 http 请求，比如 get 类型。
- Servlet 容器接收到请求，根据请求信息，封装成 HttpServletRequest 和HttpServletResponse 对象。这步也就是我们的传参。
- Servlet容器调用 HttpServlet 的 init() 方法，init 方法只在第一次请求的时候被调用。
- Servlet 容器调用 service() 方法。
- Service()方法根据请求方法调用对应的处理方法doPost()或doGet()，还有一些其他的请求方法doPut() doOptions()...但这些方法不常用，并且从安全的角度都是建议屏蔽的
- 当Server不再需要Servlet时（一般当Server关闭时），Server调用 Servlet 的 destroy() 方法

### Servlet生命周期
>初始化->处理请求->销毁

- **初始化(调用init()方法)**
  当客户端向 Servlet 容器发出 HTTP 请求要求访问 Servlet 时，Servlet 容器首先会解析请求，检查内存中是否已经有了该 Servlet 对象，如果有，则直接使用该 Servlet 对象，如果没有，则创建 Servlet 实例对象，然后通过调用 init() 方法实现 Servlet 的初始化工作。需要注意的是，在 Servlet 的整个生命周期内，它的 init() 方法只能被调用一次。
- **处理/响应客户端的请求(调用service()方法)**
  这是 Servlet 生命周期中最重要的阶段，在这个阶段中，Servlet 容器会为这个请求创建代表 HTTP 请求的 ServletRequest 对象和代表 HTTP 响应的 ServletResponse 对象，然后将它们作为参数传递给 Servlet 的 service() 方法。service() 方法从 ServletRequest 对象中获得客户请求信息并处理该请求，通过 ServletResponse 对象生成响应结果。在 Servlet 的整个生命周期内，对于 Servlet 的每一次访问请求，Servlet 容器都会调用一次 Servlet 的 service() 方法，并且创建新的 ServletRequest 和 ServletResponse 对象，也就是说，service() 方法在 Servlet 的整个生命周期中会被调用多次。
- **销毁(调用destory()方法，最后由JVM的垃圾回收器进行垃圾回收)**
  当服务器关闭或 Web 应用被移除出容器时，Servlet 随着 Web 应用的关闭而销毁。在销毁 Servlet 之前，Servlet 容器会调用 Servlet 的 destroy() 方法，以便让 Servlet 对象释放它所占用的资源。在 Servlet 的整个生命周期中，destroy() 方法也只能被调用一次。需要注意的是，Servlet 对象一旦创建就会驻留在内存中等待客户端的访问，直到服务器关闭或 Web 应用被移除出容器时，Servlet 对象才会销毁。

## Filter
filter 也称之为过滤器，是对 Servlet 技术的一个强补充，其主要功能是在 HttpServletRequest 到达 Servlet 之前，拦截客户的 HttpServletRequest ，根据需要检查 HttpServletRequest，也可以修改 HttpServletRequest 头和数据；在 HttpServletResponse 到达客户端之前，拦截 HttpServletResponse ，根据需要检查 HttpServletResponse，也可以修改 HttpServletResponse 头和数据。
![](attachments/Pasted%20image%2020230302180540.png)

### 基本工作原理
- Filter程序是一个实现了特殊接口的Java类，与Servlet类似，也是由Servlet容器进行调用和执行的
- Filter程序在可以在HttpServletRequest到达Servlet和HTTPServletResponse到达客户端前对其进行检查和修改头和数据，实现了一个类防火墙的功能
- Filter接口中有一个doFilter方法，当开发人员编写好Filter，并配置对哪个web资源进行拦截后，Web服务器每次在调用web资源的service方法之前，都会先调用一下filter的doFilter方法，doFilter方法中有一个filterChain对象,用于继续传递给下一个filter,在传递之前我们可以定义过滤请求的功能,在传递之后,我们可以定义过滤响应的功能
>1、 Filter.doFilter 方法中不能直接调用 Servlet 的 service 方法，而是调用 FilterChain.doFilter 方法来激活目标 Servlet 的 service 方法，FilterChain 对象时通过 Filter.doFilter 方法的参数传递进来的
>2、在 Filter.doFilter 方法中调用 FilterChain.doFilter 方法的语句前后增加某些程序代码，这样就可以在 Servlet 进行响应前后实现某些特殊功能
>3、如果在 Filter.doFilter 方法中没有调用 FilterChain.doFilter 方法，则目标 Servlet 的 service 方法不会被执行，这样通过 Filter 就可以阻止某些非法的访问请求


### Filter生命周期

与 servlet 一样，Filter 的创建和销毁也由 Web 容器负责。Web 应用程序启动时，Web 服务器将创建 Filter 的实例对象，并调用其 init() 方法，读取 web.xml 配置，完成对象的初始化功能，从而为后续的用户请求作好拦截的准备工作（filter 对象只会创建一次，init 方法也只会执行一次）。开发人员通过init方法的参数，可获得代表当前filter配置信息的FilterConfig对象。
Filter 对象创建后会驻留在内存，当 Web 应用移除或服务器停止时才销毁。在 Web 容器卸载 Filter 对象之前被调用。该方法在 Filter 的生命周期中仅执行一次。在这个方法中，可以释放过滤器使用的资源。

### Fileter链
![](attachments/Pasted%20image%2020230302185705.png)

## Listener
Java Web 开发中的监听器（Listener）就是 Application、Session 和 Request 三大对象创建、销毁或者往其中添加、修改、删除属性时自动执行代码的功能组件

- *ServletContextListener*：对Servlet上下文的创建和销毁进行监听； ServletContextAttributeListener：监听 Servlet 上下文属性的添加、删除和替换
- *HttpSessionListener*：对 Session 的创建和销毁进行监听。Session 的销毁有两种情况，一个中 Session 超时，还有一种是通过调用 Session 对象的 invalidate() 方法使 session 失效。
- *HttpSessionAttributeListener*：对 Session 对象中属性的添加、删除和替换进行监听；
- *ServletRequestListener*：对请求对象的初始化和销毁进行监听； 


# Tomcat
Apache 是 Web 服务器（静态解析，如 HTML），Tomcat 是 java 应用服务器（动态解析，如 JSP）
Tomcat 只是一个 servlet (jsp 也翻译成 servlet)容器，可以认为是 Apache 的扩展，但是可以独立于 Apache 运行。
理解为一个Web服务器即可，但是加点比较极端

## Tomcat服务器与Servlet
**Tomcat 是 Web 应用服务器，是一个 Servlet/JSP 容器**，而 Servlet 容器从上到下分别是 Engine、Host、Context、Wrapper。
- Engine即为全局引擎容器，它的标准实现是StandardEngine。
- Host在整个Servlet引擎中抽象出Host容器用于表示虚拟主机，它是根据URL地址中的主机部分抽象的，一个Servlet引擎可以包含若干个Host容器，而一个Host容器可以包含若干个Context容器。在Tomcat中Host的标准实现是StandardHost，它从虚拟主机级别对请求和响应进行处理。
- 一个Context对应一个Web应用程序，但Web项目的组成比较复杂，它包含很多组件。对于Web容器，需要将Web应用程序包含的组件转换成容器的组件。
- Wrapper属于Tomcat中4个级别容器中最小级别的容器，与之相对应的是Servlet。

在 Tomcat 中 Wrapper 代表一个独立的 servlet 实例， StandardWrapper 是 Wrapper 接口的标准实现类（StandardWrapper 的主要任务就是载入 Servlet 类并且进行实例化），同时其从 ContainerBase 类继承过来，表示他是一个容器，只是他是最底层的容器，不能再含有任何的子容器了，且其父容器只能是 context。