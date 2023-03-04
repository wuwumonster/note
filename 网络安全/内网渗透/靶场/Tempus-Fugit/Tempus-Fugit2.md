# 靶场拓扑&情况


# 渗透过程

nmap网络扫描
`nmap -v -A 192.168.163.0/24`

![](attachments/Pasted%20image%2020230304092401.png)

站点为WordPress 5.2.3，WPscan扫描
`wpscan --url http://192.168.163.135 -e u `

![](attachments/Pasted%20image%2020230304095111.png)

扫目录也没有效果，这个靶机一扫就烂

