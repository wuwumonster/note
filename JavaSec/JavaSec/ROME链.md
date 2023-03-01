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

这里结合上面的toString()，其实很任意想到去调用`EqualsBean`的HashCode()然后调用beanHashCode()

### ObjectBean.hashCode()
```java
public ObjectBean(Class beanClass,Object obj) {  
    this(beanClass,obj,null);  
}
```
这里发现ObjectBean既可以调用`equalsBean.beanHashCode()`还可用调用`toStringBean.toString()`
![](attachments/Pasted%20image%2020230301160102.png)

也就是说可用跳过`equalsBean.beanHashCode()`直接去触发`toStringBean.toString()`
