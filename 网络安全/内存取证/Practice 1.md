# 任务
## 识别系统中存在的恶意程序进程，提交进程PID

`volatility -f .\mem.dump imageinfo`

![](attachments/Pasted%20image%2020230309143833.png)

`volatility -f .\mem.dump --profile=Win7SP1x64 pstree`

`volatility -f .\mem.dump --profile=Win7SP1x64 memdump -p 2856 --dump-dir ./`
## 提交恶意程序识别的全部文件拓展名

## 提交恶意程序内存栈中的key地址

## 提交被破坏的word文件修复后的内容

## 分析恶意软件，写出文件加密算法
