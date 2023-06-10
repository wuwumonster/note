## Web
### CarelessPy
F12

![](attachments/Pasted%20image%2020230610114059.png)

download路由下载载源码被过滤了

在/eval路由的命令执行只能看到一层文件夹内容

/login抓包发现有flask session

![](attachments/Pasted%20image%2020230610115408.png)

![](attachments/Pasted%20image%2020230610115418.png)

download ban了py文件 通过eval路由读取到了pyc文件路径

/download?file=../../../../../app/__pycache__/part.cpython-311.pyc

![](attachments/Pasted%20image%2020230610145542.png)

在线反编译

```python
#!/usr/bin/env python
# visit https://tool.lu/pyc/ for more information
# Version: Python 3.11

import os
import random
import hashlib
from flask import *
from lxml import etree
app = Flask(__name__)
app.config['SECRET_KEY'] = 'o2takuXX_donot_like_ntr'

```

伪造session 
![](attachments/Pasted%20image%2020230610145827.png)


![](attachments/Pasted%20image%2020230610145817.png)

![](attachments/Pasted%20image%2020230610151935.png)

这个版本的 werkzeug应该是有漏洞的

