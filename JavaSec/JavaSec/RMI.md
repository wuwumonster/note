# RMI

## 概述

RMI全称是Remote Method Invocation，远程⽅法调⽤。从这个名字就可以看出，他的⽬标和RPC其实是类似的，是让某个Java虚拟机上的对象调⽤另⼀个Java虚拟机中对象上的⽅法，只不过RMIJava独有的⼀种基于序列化的Java远程方法调用机制**。**

RMI依赖的通信协议为JRMP(Java Remote Message Protocol ，Java 远程消息交换协议)，该协议为Java定制，要求服务端与客户端都为Java编写。这个协议就像HTTP协议一样，规定了客户端和服务端通信要满足的规范。在RMI中对象是通过序列化方式进行编码传输的。

RMI的三层架构

- Client-客户端：客户端调用服务端的方法
- Server-服务端：远程调用方法对象的提供者，也是代码真正执行的地方，执行结束会返回给客户端一个方法执行的结果
- Registry-注册中心：其实本质就是一个map，相当于是字典一样，用于客户端查询要调用的方法的引用（在低版本的JDK中，Server与Registry是可以不在一台服务器上的，而在高版本的JDK中，Server与Registry只能在一台服务器上，否则无法注册成功）

![Untitled](RMI%20attachments/Untitled.png)

有点DNS的感觉

Server

```java
package org.rmi;

import java.rmi.Naming;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.server.UnicastRemoteObject;
public class RMI01_Server {
    public interface IRemoteHelloWorld extends Remote {
        public String hello() throws RemoteException;
    }
    public class RemoteHelloWorld extends UnicastRemoteObject implements IRemoteHelloWorld {
        protected RemoteHelloWorld() throws RemoteException {
            super();
        }
        public String hello() throws RemoteException {
            System.out.println("call from");
            return "Hello world";
        }
    }
    private void start() throws Exception{
    RemoteHelloWorld h = new RemoteHelloWorld();
    //创建并运行RMI Registry
    LocateRegistry.createRegistry(23456);
    //将RemoteHelloWorld对象绑定到Hello这个名字
    Naming.rebind("rmi://127.0.0.1:23456/Hello", h);
}
    public static void main(String[] args) throws Exception {
        new RMI01_Server().start();
    }
}
```

Client

```java
package org.rmi;

import java.rmi.Naming;

public class RMI01_Client {
    public static void main(String[] args) throws Exception {
        RMI01_Server.IRemoteHelloWorld hello = (RMI01_Server.IRemoteHelloWorld)
                Naming.lookup("rmi://127.0.0.1:23456/Hello");
        String ret = hello.hello();
        System.out.println(ret);
    }
}

```

Naming.bind 的第一个参数是一个URL，形如： rmi://host:port/name 。其中，host和port就是
RMI Registry的地址和端口，name是远程对象的名字。

如果RMI Registry在本地运行，那么host和port是可以省略的，此时host默认是 localhost ，port默认
是 1099 ：

Naming.bind("Hello", new RemoteHelloWorld());