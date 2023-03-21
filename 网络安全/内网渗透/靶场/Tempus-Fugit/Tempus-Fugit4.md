# 靶场&拓扑情况

# 渗透过程

nmap网络环境扫描

![](attachments/Pasted%20image%2020230321103537.png)

访问网页服务，信息收集

![](attachments/Pasted%20image%2020230321103914.png)

在contact发现了一个功能点

![](attachments/Pasted%20image%2020230321104043.png)

dirsearch目录扫描

![](attachments/Pasted%20image%2020230321112141.png)

后台

![](attachments/Pasted%20image%2020230321112408.png)

登录报文

![](attachments/Pasted%20image%2020230321112434.png)

这里思考了组件的漏洞和jwt的cookie伪造没有办法
最后的解决是XSS，在这里一个早一些和这个功能联系起来的

![](attachments/Pasted%20image%2020230321153525.png)

![](attachments/Pasted%20image%2020230321153920.png)

