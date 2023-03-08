**流量中一共有多少条爆破记录**
3901
在wirshark中用`http && http.request.uri &&ip.addr == 192.168.162.1`进行过滤

![](attachments/Pasted%20image%2020230308181040.png)

剩余的全是sql时间盲注的内容，在导出特定分组可以看到总数量

![](attachments/Pasted%20image%2020230308181113.png)


**该盲注操作的字典内容是什么**
`abcdefghijklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ1234567890,_{}`
就是盲注中的内容

**藏有flag的数据库内有哪些数据表，以group_concat结果形式提交**
利用时间盲注的原理在将数据导出为csv后，用Excel对注入和回包之间时间差距在3秒以上的进行筛选，然后去除uri中的其余语句只留字典字符就是原始的group_concat格式，和flag

