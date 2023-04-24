ida pro打开 ，只有两个函数，后面有提到upx段，应该是upx的壳

![](attachments/Pasted%20image%2020230424120317.png)


OD打开后

![](attachments/Pasted%20image%2020230424123347.png)

查找popad，找了找了几个后到最后一个popad，有一个大跳

![](attachments/Pasted%20image%2020230424125005.png)

在下面这个大跳下一个F2断点，然后F9运行过来，F8单步进去，这里应该就是程序入口

![](attachments/Pasted%20image%2020230424125616.png)

这会儿应该是没壳了

![](attachments/Pasted%20image%2020230424125857.png)

ida pro

![](attachments/Pasted%20image%2020230424125950.png)

F5后很明显

![](attachments/Pasted%20image%2020230424130136.png)

HappyNewYear!

那么flag就是flag{HappyNewYear!}