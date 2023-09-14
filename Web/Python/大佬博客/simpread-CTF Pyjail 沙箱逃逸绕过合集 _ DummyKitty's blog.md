> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [dummykitty.github.io](https://dummykitty.github.io/posts/python-%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E7%BB%95%E8%BF%87/)

> 文章首发于先知社区：CTF Pyjail 沙箱逃逸绕过合集 - 先知社区

> 文章首发于先知社区：[CTF Pyjail 沙箱逃逸绕过合集 - 先知社区](https://xz.aliyun.com/t/12647)

承接上一篇 CTF Pyjail 沙箱逃逸原理合集，本文主要来谈谈绕过手法，Pyjail 绕过过滤的手法千奇百怪, 本文在复现经典历史赛题的基础上，针对不同的沙箱类型对绕过手法进行了分类，篇幅较长敬请理解。

1.  绕过删除模块或方法
2.  绕过基于字符串匹配的过滤
3.  绕过长度限制
4.  绕过命名空间限制
5.  绕过多行限制
6.  变量覆盖与函数篡改
7.  绕过 audit hook
8.  绕过 AST 沙箱

> 原文太长了，为了方便编辑和及时补充，我将各个部分进行了切分。

绕过删除模块或方法
-----------------------

[redirect](https://dummykitty.github.io/posts/pyjail-bypass-01-%E7%BB%95%E8%BF%87%E5%88%A0%E9%99%A4%E6%A8%A1%E5%9D%97%E6%88%96%E6%96%B9%E6%B3%95/)

绕过基于字符串匹配的过滤
-----------------------------

[redirect](https://dummykitty.github.io/posts/pyjail-bypass-02-%E5%AD%97%E7%AC%A6%E4%B8%B2%E5%8F%98%E6%8D%A2%E7%BB%95%E8%BF%87/)

绕过命名空间限制
---------------------

[redirect](https://dummykitty.github.io/posts/pyjail-bypass-03-%E7%BB%95%E8%BF%87%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4%E9%99%90%E5%88%B6/)

绕过长度限制
-----------------

[redirect](https://dummykitty.github.io/posts/pyjail-bypass-04-%E7%BB%95%E8%BF%87%E5%A4%9A%E8%A1%8C%E9%99%90%E5%88%B6/)

绕过多行限制
-----------------

[redirect](https://dummykitty.github.io/posts/pyjail-bypass-05-%E7%BB%95%E8%BF%87%E9%95%BF%E5%BA%A6%E9%99%90%E5%88%B6/)

变量覆盖与函数篡改
-----------------------

[redirect](https://dummykitty.github.io/posts/pyjail-bypass-06-%E5%8F%98%E9%87%8F%E8%A6%86%E7%9B%96%E4%B8%8E%E5%87%BD%E6%95%B0%E7%AF%A1%E6%94%B9/)

绕过 audit hook
-------------------------------

[redirect](https://dummykitty.github.io/posts/pyjail-bypass-07-%E7%BB%95%E8%BF%87-audit-hook/)

绕过 AST 沙箱
-----------------------

[redirect](https://dummykitty.github.io/posts/pyjail-bypass-08-%E7%BB%95%E8%BF%87-AST-%E6%B2%99%E7%AE%B1/)

其他技巧
-------------

### 模拟 no builitins 环境[](#模拟-no-builitins-环境)

no builtins 环境和 python 交互式解析器还是有所差异, 但交互式解析器并没有提供指定命名空间的功能, 因此可以自己编写一个脚本进行模拟:

```python
def repl():
    global_namespace = {}
    local_namespace = {}

    while True:
        try:
            code = input('>>> ')
            try:
                # Try to eval the code first.
                result = eval(code, global_namespace, local_namespace)
            except SyntaxError:
                # If a SyntaxError occurs, this might be because the user entered a statement,
                # in which case we should use exec.
                exec(code, global_namespace, local_namespace)
            else:
                print(result)
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()
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