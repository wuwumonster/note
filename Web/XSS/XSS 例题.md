

### [Zer0pts2020]musicblog

### [BBCTF2020]note

xss插入后就变成了这样

![Untitled](../../CTF赛题/BUU月赛/attachment/XSS%20a51e2f7243d74880af9d0bb380b2db36/Untitled.png)

### [LineCTF2022]online-library

XSS点

```jsx
app.get("/:t/:s/:e", (req: Express.Request, res: Express.Response): void => {
    const s: number = Number(req.params.s)
    const e: number = Number(req.params.e)
    const t: string = req.params.t

    if ((/[\x00-\x1f]|\x7f|\<|\>/).test(t)) {
        res.end("Invalid character in book title.")
    } else  {
        Fs.stat(`public/${t}`, (err: NodeJS.ErrnoException, stats: Fs.Stats): void => {
            if (err) {
                res.end("No such a book in bookself.")
            } else {
                if (s !== NaN && e !== NaN && s < e) {
                    if ((e - s) > (1024 * 256)) {
                        res.end("Too large to read.")
                    } else {
                        Fs.open(`public/${t}`, "r", (err: NodeJS.ErrnoException, fd: any): void => {
                            if (err || typeof fd !== "number") {
                                res.end("Invalid argument.")
                            } else {
                                let buf: Buffer = Buffer.alloc(e - s);
                                Fs.read(fd, buf, 0, (e - s), s, (err: NodeJS.ErrnoException, bytesRead: number, buf: Buffer): void => {
                                    res.end(`<h1>${t}</h1><hr/>` + buf.toString("utf-8"))
                                })
                            }
                        })
                    }
                } else {
                    res.end("There isn't size of book.")
                }
            }
        })
    }
});
```

一个fs.open一个fs.read

![Untitled](../../CTF赛题/BUU月赛/attachment/XSS%20a51e2f7243d74880af9d0bb380b2db36/Untitled%201.png)

![Untitled](../../CTF赛题/BUU月赛/attachment/XSS%20a51e2f7243d74880af9d0bb380b2db36/Untitled%202.png)

在参数中则为t为路径，s和e决定了读入的数据量

构造路径为../../../../../etc/passwd/0/1024