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