# 靶场拓扑&情况

# 渗透过程

nmap网络扫描

![](attachments/Pasted%20image%2020230305154310.png)

进入首页康康，有一个蹩脚的login，尝试sql注入，但是没有效果

![](attachments/Pasted%20image%2020230305155954.png)

在url中的值被读取到了页面上

![](attachments/Pasted%20image%2020230305160729.png)

确认是ssti不过页面没有办法确定相关利用类。粘贴出来用vscode看看，发现popen类

![](attachments/Pasted%20image%2020230305163716.png)

# 参考链接

