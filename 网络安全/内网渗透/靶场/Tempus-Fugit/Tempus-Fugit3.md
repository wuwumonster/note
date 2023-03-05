# 靶场拓扑&情况

# 渗透过程

nmap网络扫描

![](attachments/Pasted%20image%2020230305154310.png)

进入首页康康，有一个蹩脚的login，尝试sql注入，但是没有效果

![](attachments/Pasted%20image%2020230305155954.png)

在url中的值被读取到了页面上

![](attachments/Pasted%20image%2020230305160729.png)

确认是ssti，虽然现在我们可以通过`{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}`来实现命令执行，但是想要提权还是要获取到shell才行

![](attachments/Pasted%20image%2020230305164715.png)

发现popen类

![](attachments/Pasted%20image%2020230305163716.png)

这里感觉是一个平时CTF中没有遇到过的玩法拿shell[python中的subprocess.Popen() 执行shell命令 - 技术改变命运Andy - 博客园 (cnblogs.com)](https://www.cnblogs.com/andy0816/p/15624304.html)




# 参考链接
[python中的subprocess.Popen() 执行shell命令 - 技术改变命运Andy - 博客园 (cnblogs.com)](https://www.cnblogs.com/andy0816/p/15624304.html)
