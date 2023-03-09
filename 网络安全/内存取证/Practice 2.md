`volatility -f .\mem.dump imageinfo`

![](attachments/Pasted%20image%2020230309135304.png)

`volatility -f .\mem.dump --profile=Win10x64_17134 pstree`

![](attachments/Pasted%20image%2020230309135733.png)

`volatility -f .\mem.dump --profile=Win10x64_17134 memdump -p 3000 --dump-dir E:\应急响应与数字调查取证\45-内存取证\win_image_task2\win_image\`

