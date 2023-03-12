搭的时候看了狂神说的JavaWeb部分，但是总是报404的错，在init里面写了print函数，发现servlet根本没有初始化，调来调去，踩了好几个坑，在这里记录Servlet的环境搭建流程，和一些坑的注意点

## 环境搭建
### 基于Maven的Servlet搭建
新建项目就，下面的Maven archetype是对项目模板的不同选择，更多模板细节可以看[Maven 三种archetype说明_maven-archetype-webapp_大旭123456的博客-CSDN博客](https://blog.csdn.net/cx1110162/article/details/78297654)，，这里使用`maven-archetype-webapp`

![](attachments/Pasted%20image%2020230312143315.png)

直接创建后得到的是一个目录结构已经完成的maven项目

![](attachments/Pasted%20image%2020230312143709.png)

手动添加一个java文件夹，并设置为源文件夹

![](attachments/Pasted%20image%2020230312143919.png)

还要构建软件包结构

![](attachments/Pasted%20image%2020230312144736.png)

pom.xml添加依赖

```xml
<!-- https://mvnrepository.com/artifact/javax.servlet/javax.servlet-api -->  
<dependency>  
  <groupId>javax.servlet</groupId>  
  <artifactId>javax.servlet-api</artifactId>  
  <version>4.0.1</version>  
  <scope>provided</scope>  
</dependency>  
<!-- https://mvnrepository.com/artifact/javax.servlet.jsp/javax.servlet.jsp-api -->  
<dependency>  
  <groupId>javax.servlet.jsp</groupId>  
  <artifactId>javax.servlet.jsp-api</artifactId>  
  <version>2.3.3</version>  
  <scope>provided</scope>  
</dependency>
```

新建servlet，IDEA中是直接有这个选项的，值得一提的是用这样的方式新建的servlet是不用在web.xml中去注册的，它自己使用了注解来进行注册
`@WebServlet(name = "Servlet", value = "/Servlet")`

![](attachments/Pasted%20image%2020230312145414.png)

## 坑点

这里的部署工件，应用程序上下文是会对访问路径产生影响的想要和注解一致，而不用带上这个路径

![](attachments/Pasted%20image%2020230312150558.png)

## 参考资料
[Maven 三种archetype说明_maven-archetype-webapp_大旭123456的博客-CSDN博客](https://blog.csdn.net/cx1110162/article/details/78297654)

