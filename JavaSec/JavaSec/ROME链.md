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
