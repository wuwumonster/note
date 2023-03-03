# 靶场拓扑&情况

# 渗透过程
网络扫描
`namp -v -A 192.168.1.0/24`
![](attachments/Pasted%20image%2020230303083516.png)

`dirsearch -u http://192.168.1.129/`
结果全为200，应该是做了防扫描的特殊设置
![](attachments/Pasted%20image%2020230303084150.png)

