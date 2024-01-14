## 形形色色的DDoS
该流量包是某台服务器在被DDoS攻击期间内的部分PCAP流量数据。已知此次攻击，攻击者采用了多种DDoS攻击方法，请找出这些攻击流量，并将攻击类型相同的源IP进行归类，无需给出具体的DDoS攻击类型。
答题格式(每一行代表一类IP)：**q1_answer.txt**

```
IP,IP,IP,IP,IP,IP,IP
IP,IP,IP,IP,IP,IP,IP
IP,IP,IP,IP,IP,IP,IP
......
```

- TCP SYN泛洪攻击（攻击目标: web服务器）
![](attachments/Pasted%20image%2020231107111848.png)
- cc攻击（攻击目标: web服务器）
![](attachments/Pasted%20image%2020231107104652.png)
- UDP flood （攻击目标: 各种服务器）
![](attachments/Pasted%20image%2020231107111835.png)
- ICMP flood (攻击目标: 各种服务器)
- Smurf 攻击（攻击目标为路由器，交换机，服务器）
- ntp DDos
![](attachments/Pasted%20image%2020231107111821.png)

## 威胁情报的关联分析
已知本次的DDoS攻击由僵尸网络团伙发起，且该团伙传播了两种恶意样本文件。请结合PCAP流量数据和蜜罐日志，找到这两种恶意样本文件，并给出每种恶意样本文件的MD5以及每种恶意样本文件在蜜罐日志的传播源IP和下载站IP（作答时只需给出IP即可，无需具体指定每个IP是传播源还是下载站）。
在确认分数后，选手可在【赛题解答】中的【解答记录】中查看【判分日志】，判分日志会显示选手回答正确的样本MD5下载链接，请选手及时下载保存，用以后续题目使用。
答题格式：**q2_answer.txt**
```
样本MD5:IP,IP,IP,IP,IP 
样本MD5:IP,IP,IP,IP,IP
```

45.15.158.124/tf.sh
45.15.158.124/cf.sh