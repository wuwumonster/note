> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [dummykitty.github.io](https://dummykitty.github.io/posts/pyjail-bypass-01-%E7%BB%95%E8%BF%87%E5%88%A0%E9%99%A4%E6%A8%A1%E5%9D%97%E6%88%96%E6%96%B9%E6%B3%95/)

> 绕过删除模块或方法

绕过删除模块或方法[](#绕过删除模块或方法)
-----------------------

在一些沙箱中，可能会对某些模块或者模块的某些方法使用 `del` 关键字进行删除。 例如删除 builtins 模块的 eval 方法。

```
>>> __builtins__.__dict__['eval']
<built-in function eval>
>>> del __builtins__.__dict__['eval']
>>> __builtins__.__dict__['eval']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'eval'
```

### reload 重新加载[](#reload-重新加载)

reload 函数可以重新加载模块，这样被删除的函数能被重新加载

```
>>> __builtins__.__dict__['eval']
<built-in function eval>
>>> del __builtins__.__dict__['eval']
>>> __builtins__.__dict__['eval']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'eval'
>>> reload(__builtins__)
<module '__builtin__' (built-in)>
>>> __builtins__.__dict__['eval']
<built-in function eval>
```

在 Python 3 中，reload() 函数被移动到 importlib 模块中，所以如果要使用 reload() 函数，需要先导入 importlib 模块。

### 恢复 sys.modules[](#恢复-sysmodules)

一些过滤中可能将 `sys.modules['os']` 进行修改. 这个时候即使将 os 模块导入进来, 也是无法使用的.

```
>>> sys.modules['os'] = 'not allowed'
>>> __import__('os').system('ls')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'str' object has no attribute 'system'
```

由于很多别的命令执行库也使用到了 os, 因此也会受到相应的影响, 例如 subprocess

```
>>> __import__('subprocess').Popen('whoami', shell=True)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/kali/.pyenv/versions/3.8.10/lib/python3.8/subprocess.py", line 688, in <module>
    class Popen(object):
  File "/home/kali/.pyenv/versions/3.8.10/lib/python3.8/subprocess.py", line 1708, in Popen
    def _handle_exitstatus(self, sts, _WIFSIGNALED=os.WIFSIGNALED,
AttributeError: 'str' object has no attribute 'WIFSIGNALED'
```

由于 import 导入模块时会检查 sys.modules 中是否已经有这个类，如果有则不加载, 没有则加载. 因此我们只需要将 os 模块删除, 然后再次导入即可.

```
sys.modules['os'] = 'not allowed' # oj 为你加的

del sys.modules['os']
import os
os.system('ls')
```

### 基于继承链获取[](#基于继承链获取)

在清空了 `__builtins__`的情况下，我们也可以通过索引 subclasses 来找到这些内建函数。

```
# 根据环境找到 bytes 的索引，此处为 5
>>> ().__class__.__base__.__subclasses__()[5]
<class 'bytes'>
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

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.