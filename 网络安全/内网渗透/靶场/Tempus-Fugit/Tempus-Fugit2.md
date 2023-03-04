# 靶场拓扑&情况


# 渗透过程

nmap网络扫描
`nmap -v -A 192.168.163.0/24`

![](attachments/Pasted%20image%2020230304092401.png)

站点为WordPress 5.2.3，WPscan扫描
`wpscan --url http://192.168.163.135 -e u `

![](attachments/Pasted%20image%2020230304095111.png)

扫目录也没有效果，这个靶机一扫就烂，非常的卡，在进入login的时候发现很卡顿，而且url变成了tf2的域名
在hosts文件中加入tf2.com的记录

这里提供了忘记密码的选项
但是在尝试获得新密码的时候，出现了报错，猜测是邮件服务没有

![](attachments/Pasted%20image%2020230304103734.png)

wirshark监听，也证实了这个猜想，可以通过建立一个smtp服务，通过中间人攻击来拿到新的密码

修改etter.dns 中的值来将域名伪造为需要的 `smtp.tempusfugit2.com`和 `smtp.tempusfugit2.com.localdomain`

![](attachments/Pasted%20image%2020230304111035.png)

本地用python起一个简单的smtp服务
`sudo python3 -m smtpd -n -c DebuggingServer 192.168.163.135:25`
然后启动ettercup扫描host主机，将靶机添加到target1中，同时选择dns_spoof插件，注意要在MITM中打开ARP sniff remote connection

![](attachments/Pasted%20image%2020230304111546.png)

在这之后提交reset admin的密码,伪造的邮箱就会收到更新链接,进去后更新为新的直接登录后台

![](attachments/Pasted%20image%2020230304144148.png)

![](attachments/Pasted%20image%2020230304144413.png)

主题没有办法提交,用激活插件的方法反弹shell,需要自己写一个插件
[register_activation_hook() - 设置插件的激活（启用）钩子 - WordPress函数 - WordPress动力 (wpdongli.com)](https://www.wpdongli.com/reference/functions/register_activation_hook/)

压缩为zip包上传后激活就可以弹到shell

![](attachments/Pasted%20image%2020230304151542.png)

但是现在的shell并不是tty,在这个里面找到了别的东西`dG9ycmllOjlhNGx3MHI4MmN4Mgo=`

![](attachments/Pasted%20image%2020230304151838.png)

在wordpress中有一篇文章

![](attachments/Pasted%20image%2020230304151955.png)

是port koncking
[靶机-简单谈一下端口碰撞技术 (Port Knocking) - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/210177505)

![](attachments/Pasted%20image%2020230304152256.png)

很明显了`1981 867 5309`
不知道为什么我的kali没有办法下载konckd,所有用nmap来替代了
`nmap 192.168.1.132 -Pn -p 1981,867,5309`

![](attachments/Pasted%20image%2020230304152901.png)

这个时候该连ssh了但是,发觉自己没有账号密码,回想起了刚刚的nb.txt,base64一下
`torrie:9a4lw0r82cx2`

![](attachments/Pasted%20image%2020230304153209.png)


登录的时候傻了,没反应登不上,感觉可能是konck没到

![](attachments/Pasted%20image%2020230304154012.png)

grissel:9l4lw0r82cp9
