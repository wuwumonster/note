# 靶场拓扑&情况

# 渗透过程
网络扫描
`namp -v -A 192.168.1.0/24`
![](attachments/Pasted%20image%2020230303083516.png)

`dirsearch -u http://192.168.1.129/`
结果全为200，应该是做了防扫描的特殊设置
![](attachments/Pasted%20image%2020230303084150.png)

发现网站由上传文件的功能
试着上传一个shell，发现不支持php文件，只允许txt和rtf，上传txt文件后发现文件内容出现在了网页
![](attachments/Pasted%20image%2020230303085226.png)


猜测后台有读文件的相关操作