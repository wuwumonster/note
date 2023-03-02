# Javassist 介绍
 Javaassist是处理Java字节码的类库，Java字节码以二进制的形式存储在class文件中，每个class文件中包含一个java类或者接口。其主要的优点，在于简单，而且快速。直接使用java编码的形式，而不需要了解虚拟机指令，就能动态改变类的结构，或者动态生成类。而个人感觉在安全中最重要的就是在使用Javassist时我们可以像写Java代码一样直接插入Java代码片段，让我们不再需要关注Java底层的字节码的和栈操作，仅需要学会如何使用Javassist的API即可实现字节码编辑，类似于可以达到任意代码执行的效果。

# Javassist 类
## ClassPool
一个基于`HashMap`实现的`CtClass`对象容器，其中键是类名称，值是表示该类的`CtClass对象`。默认的`ClassPool`使用与底层JVM相同的类路径，因此在某些情况下，可能需要向`ClassPool`添加类路径或类字节。
| ClassPool             | getDefault()                     | 返回默认的类池                               |
| --------------------- | -------------------------------- | -------------------------------------------- |
| ClassPath             | insertClassPath(String pathname) | 在搜索路径的开头插入目录或jar（或zip）文件。 |
| ClassPath             | insertClassPath(ClassPath cp)    | ClassPath在搜索路径的开头插入一个对象。      |
| java.lang.ClassLoader | getClassLoader()                 | 获取类加载器                                 |
| CtClass               | get(java.lang.String,Classname)  | 从源中读取类文件，并返回对CtClass 表示该类文件的对象的引用。                         |
| ClassPath             | appendClassPath(ClassPath cp)    | 将ClassPath对象附加到搜索路径的末尾          |
| CtClass                      |           makeClass(java.lang.String classname)                       |      创建一个新的public类                                        |
## CtClass
表示一个类，一个CtClass(编译时类）对象可以处理一个class文件,这些CtClass对象可以从ClassPool获得，从上面的测试也能大概了解一些关于CtClass的相关知识。
| Void                | setSuperclass(CtClass clazz)                          | 更改超类，除非此对象表示接口                 |     |     |     |
| ------------------- | ----------------------------------------------------- | -------------------------------------------- | --- | --- | --- |
| java.lang.Class\<?> | toClass(java.lang.invoke.MethodHandles.Lookup lookup) | 将此类转换为java.lang.Class对象。            |     |     |     |
| byte\[]             | toBytecode()                                          | 将该类转换为类文件                           |     |     |     |
| void                | writeFile()                                           | 将由此CtClass 对象表示的类文件写入当前目录。 |     |     |     |
| void                | writeFile(java.lang.String directoryName)             | 将由此CtClass 对象表示的类文件写入本地磁盘   |     |     |     |
| CtConstructor       | makeClassInitializer()                                | 制作一个空的类初始化程序（静态构造函数）     |     |     |     |
## CtMethod
表示类中的方法。超类为CtBehavior，很多有用的方法都在CtBehavior

| void | insertBefor(java.lang.String src)                | 在正文的开头插入字节码 |
| ---- | ------------------------------------------------ | ---------------------- |
| Void | insertAfter(java.lang.String src)                | 在正文末尾插入         |
| void | toMetod(java.lang.String name,CtClass declaring) | 从另一个方法复制构造体 |
## CtConstructor
CtConstructor的实例表示一个构造函数。它可能代表一个静态构造函数。

| void | SetBody(java.lang.String src)                      | 设置构造函数主题                     |
| ---- | -------------------------------------------------- | ------------------------------------ |
| void | setBody(CtConstructor src,ClassMap map)            | 从另一个构造函数复制一个构造函数主体 |
| void | toMethod(java.lang.String name, CtClass declaring) | 复制次构造函数并将其转换为方法       |
## CtField
表示类中字段
