## pickle库
- `pickle.dumps(x)`将x翻译为序列化字符串
- `pickle.loads()`将序列化字符串还原为对象
###  `pickle.loads()`底层调用 `_Unpickler`

## R指令码 `__reduce__`

## Bypass
### 函数黑名单绕过
#### 利用map
```PYTHON
class Exploit(object):
    def __reduce__(self):
	 	return map,(os.system,["ls"])
```

### R指令码禁用绕过
#### C指令码——全局变量包含
#### 绕过C指令module限制
`c`指令（也就是 GLOBAL 指令）基于`find_class`这个方法， 然而`find_class`可以被重写，如果只允许`c`指令包含`__main__`这一个 module，如何完成纂改
>　通过 GLOBAL 指令引入的变量，可以看作是原变量的引用。我们在栈上修改它的值，会导致原变量也被修改

#### 无reduce RCE
用指令码，构造出任意命令执行。那么我们需要找到一个函数调用`fun(arg)`，其中`fun`和`arg`都必须可控
下面是pickle中BULID指令的工作源码
![](attachments/Pasted%20image%2020240409105357.png)

果`inst`拥有`__setstate__`方法，则把`state`交给`__setstate__`方法来处理；否则的话，直接把`state`这个`dist`的内容，合并到`inst.__dict__` 里面

在构造时利用`{'__setstate__': os.system}`来 BUILE 这个对象，那么现在对象的`__setstate__`就变成了`os.system`
接下来利用`"ls /"`来再次 BUILD 这个对象，则会执行`setstate("ls /")` ，而此时`__setstate__`已经被我们设置为`os.system`，因此实现了 RCE.

