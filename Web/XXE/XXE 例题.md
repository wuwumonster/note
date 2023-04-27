
## xml结构说明

![Untitled](../../CTF赛题/BUU月赛/attachment/XXE%206cc3380a764c481ea029944ba543a2db/Untitled.png)

- `<?xml version="1.0"?>   *XML文档定义*`
- `<!DOCTYPE Profile [<!ENTITY file SYSTEM "file:///etc/passwd">]>`  DTD对文档进行定义
- &file;   对实体进行引用

## [NCTF2019]Fake XML cookbook

![Untitled](../../CTF赛题/BUU月赛/attachment/XXE%206cc3380a764c481ea029944ba543a2db/Untitled%201.png)