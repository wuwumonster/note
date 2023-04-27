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
i32的大小是 -2147483648~2147483647

