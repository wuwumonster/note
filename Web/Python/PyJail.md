## 常见沙箱
### exec执行
```python
exec(object[, globals[, locals]])
```
#### 参数
- object：必选参数，表示需要被指定的 Python 代码。它必须是字符串或 code 对象。如果 object 是一个字符串，该字符串会先被解析为一组 Python 语句，然后再执行（除非发生语法错误）。如果 object 是一个 code 对象，那么它只是被简单的执行。
- globals：可选参数，表示全局命名空间（存放全局变量），如果被提供，则必须是一个字典对象。
- locals：可选参数，表示当前局部命名空间（存放局部变量），如果被提供，可以是任何映射对象。如果该参数被忽略，那么它将会取与 globals 相同的值。

>exec 返回值永远为 None

### eval执行
```python
eval(expression[, globals[, locals]])
```

#### 参数

- expression -- 表达式。
- globals -- 变量作用域，全局命名空间，如果被提供，则必须是一个字典对象。
- locals -- 变量作用域，局部命名空间，如果被提供，可以是任何映射对象。

>eval() 函数将字符串转换为相应的对象，并返回表达式的结果。
eval不允许`\n`和`;` 进行换行，exec允许但是不会输出结果，eval会,放到compile中就只和compile有关

### compile
```python
compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1)
```
- 将 _source_ 编译成代码或 AST 对象。代码对象可以被 [`exec()`](https://docs.python.org/zh-cn/3/library/functions.html?highlight=compile#exec "exec") 或 [`eval()`](https://docs.python.org/zh-cn/3/library/functions.html?highlight=compile#eval "eval") 执行。_source_ 可以是常规的字符串、字节字符串，或者 AST 对象。参见 [`ast`](https://docs.python.org/zh-cn/3/library/ast.html#module-ast "ast: Abstract Syntax Tree classes and manipulation.") 模块的文档了解如何使用 AST 对象。
	- ‘exec’： exec 方式就类似于直接使用 exec 方法，可以处理换行符，分号，import语句等。
	- ‘eval’： eval 方式也就类似于直接使用 eval，只能处理简单的表达式，不支持换行、分号、import 语句
	- ‘single’：这个模式类似于 ‘exec’，但是只用于执行单个语句(可以在语句中添加换行符等)。
- _filename_ 实参需要是代码读取的文件名；如果代码不需要从文件中读取，可以传入一些可辨识的值（经常会使用 `'<string>'`）。
- _mode_ 实参指定了编译代码必须用的模式。如果 _source_ 是语句序列，可以是 `'exec'`；如果是单一表达式，可以是 `'eval'`；如果是单个交互式语句，可以是 `'single'`。（在最后一种情况下，如果表达式执行结果不是 `None` 将会被打印出来。）
- 可选参数 _flags_ 和 _dont_inherit_ 控制应当激活哪个 [编译器选项](https://docs.python.org/zh-cn/3/library/ast.html#ast-compiler-flags) 以及应当允许哪个 [future 特性](https://docs.python.org/zh-cn/3/reference/simple_stmts.html#future)。 如果两者都未提供 (或都为零) 则代码会应用与调用 [`compile()`](https://docs.python.org/zh-cn/3/library/functions.html?highlight=compile#compile "compile") 的代码相同的旗标来编译。 如果给出了 _flags_ 参数而未给出 _dont_inherit_ (或者为零) 则会在无论如何都将被使用的旗标之外还会额外使用 _flags_ 参数所指定的编译器选项和 future 语句。 如果 _dont_inherit_ 为非零整数，则只使用 _flags_ 参数 -- 外围代码中的旗标 (future 特性和编译器选项) 会被忽略。
- 编译器选项和 future 语句是由比特位来指明的。 比特位可以通过一起按位 OR 来指明多个选项。 指明特定 future 特性所需的比特位可以在 [`__future__`](https://docs.python.org/zh-cn/3/library/__future__.html#module-__future__ "__future__: Future statement definitions") 模块的 `_Feature` 实例的 `compiler_flag` 属性中找到。 [编译器旗标](https://docs.python.org/zh-cn/3/library/ast.html#ast-compiler-flags) 可以在 [`ast`](https://docs.python.org/zh-cn/3/library/ast.html#module-ast "ast: Abstract Syntax Tree classes and manipulation.") 模块中查找带有 `PyCF_` 前缀的名称。

>备注
在 `'single'` 或 `'eval'` 模式编译多行代码字符串时，输入必须以至少一个换行符结尾。 这使 [`code`](https://docs.python.org/zh-cn/3/library/code.html#module-code "code: Facilities to implement read-eval-print loops.") 模块更容易检测语句的完整性。

### 基于 audit hook 的沙箱
```python
sys.addaudithook(hook)
```
`sys.addaudithook(hook)` 的参数 `hook` 是一个函数，其定义形式为 `hook(event: str, args: tuple)`。其中，`event` 是一个描述事件名称的字符串，`args` 是一个包含了与该事件相关的参数的元组。

当通过 [`sys.audit()`](https://docs.python.org/zh-cn/3/library/sys.html?highlight=addaudithook#sys.audit "sys.audit") 函数引发审计事件时，每个钩子将按照其被加入的先后顺序被调用，调用时会传入事件名称和参数元组。 由 [`PySys_AddAuditHook()`](https://docs.python.org/zh-cn/3/c-api/sys.html#c.PySys_AddAuditHook "PySys_AddAuditHook") 添加的原生钩子会先被调用，然后是当前（子）解释器中添加的钩子。 接下来这些钩子会记录事件，引发异常来中止操作，或是完全终止进程。

调用 [`sys.addaudithook()`](https://docs.python.org/zh-cn/3/library/sys.html?highlight=addaudithook#sys.addaudithook "sys.addaudithook") 时它自身将引发一个名为 `sys.addaudithook` 的审计事件且不附带参数。 如果任何现有的钩子引发了派生自 [`RuntimeError`](https://docs.python.org/zh-cn/3/library/exceptions.html#RuntimeError "RuntimeError") 的异常，则新的钩子不会被添加并且该异常会被抑制。 其结果就是，调用者无法确保他们的钩子已经被添加，除非他们控制了全部现有的钩子。

### 基于 AST 的沙箱

抽象语法树可通过将 [`ast.PyCF_ONLY_AST`](https://docs.python.org/zh-cn/3/library/ast.html?highlight=ast#ast.PyCF_ONLY_AST "ast.PyCF_ONLY_AST") 作为旗标传递给 [`compile()`](https://docs.python.org/zh-cn/3/library/functions.html#compile "compile") 内置函数来生成，或是使用此模块中提供的 [`parse()`](https://docs.python.org/zh-cn/3/library/ast.html?highlight=ast#ast.parse "ast.parse") 辅助函数。返回结果将是一个由许多对象构成的树，这些对象所属的类都继承自 [`ast.AST`](https://docs.python.org/zh-cn/3/library/ast.html?highlight=ast#ast.AST "ast.AST")。抽象语法树可被内置的 [`compile()`](https://docs.python.org/zh-cn/3/library/functions.html#compile "compile") 函数编译为一个 Python 代码对象。

- `ast.Module`: 表示一个整个的模块或者脚本。
- `ast.FunctionDef`: 表示一个函数定义。
- `ast.AsyncFunctionDef`: 表示一个异步函数定义。
- `ast.ClassDef`: 表示一个类定义。
- `ast.Return`: 表示一个return语句。
- `ast.Delete`: 表示一个del语句。
- `ast.Assign`: 表示一个赋值语句。
- `ast.AugAssign`: 表示一个增量赋值语句，如`x += 1`。
- `ast.For`: 表示一个for循环。
- `ast.While`: 表示一个while循环。
- `ast.If`: 表示一个if语句。
- `ast.With`: 表示一个with语句。
- `ast.Raise`: 表示一个raise语句。
- `ast.Try`: 表示一个try/except语句。
- `ast.Import`: 表示一个import语句。
- `ast.ImportFrom`: 表示一个from…import…语句。
- `ast.Expr`: 表示一个表达式。
- `ast.Call`: 表示一个函数调用。
- `ast.Name`: 表示一个变量名。
- `ast.Attribute`: 表示一个属性引用，如`x.y`

全部文档[simpread-ast --- 抽象语法树 — Python 3.11.5 文档](文档/simpread-ast%20---%20抽象语法树%20—%20Python%203.11.5%20文档.md)

