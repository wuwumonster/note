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
本地用python起一个简单的smtp服务
`sudo python3 -m smtpd -n -c DebuggingServer 192.168.163.135:25`
然后启动ettercup开始攻击



