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
