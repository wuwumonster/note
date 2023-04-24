32位无壳

关键函数
![](attachments/Pasted%20image%2020230424134644.png)

在这里对输入的字符串进行了处理，极具base64特征的字符串

![](attachments/Pasted%20image%2020230424134822.png)

最后用来对比的字符串

![](attachments/Pasted%20image%2020230424135031.png)

e3nifIH9b_C@n@dH
在主函数中对对应位的字符进行了一个加的操作

![](attachments/Pasted%20image%2020230424135305.png)

对这串字符串解base64

```python
from base64 import *

str = "e3nifIH9b_C@n@dH"
flag = ""
for i in range(0,16):
	flag += chr(ord(str[i])-i)
print(flag)
print(b64decode(flag))
```

flag{i_l0ve_you}