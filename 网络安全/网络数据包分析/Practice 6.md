## 背景
You’re an agent with a government law enforcement agency. You’ve been tracking a group of criminal hackers known as “TufMups”. This group either keeps a low profile, your agency’s capacity to run investigations on the internet is very poor, or some combination of those two factors. Up until two days ago you had an active relationship with an informant who went by the handle “K3anu”. As you walked into your office you received a package containing a flash drive, a printed screenshot (at the top of this blog post) and a very short note.  
“Review this PCAP. It will all make sense. Woaaahhhh. – K3anu”  
That package was the last you heard from K3anu.

- 本数据包的开始时间和结束时间

![](attachments/Pasted%20image%2020230315101949.png)

- · What is the hostname of the system the PCAP was recovered from? (all caps)


- 收集数据包的主机名
NBNS包中找注册

![](attachments/Pasted%20image%2020230315102326.png)

- What exact version of browser did K3anu use? (exact number only)
63.0.3239.84

![](attachments/Pasted%20image%2020230315094956.png)

- · What operating system did K3anu use? (Name and number only)

Windows NT 10.0

- How many DNS queries in the PCAP received NXdomain responses?
`dns.response_to && dns.flags.rcode !=0`过滤

![](attachments/Pasted%20image%2020230315102717.png)


-  What is the hidden message in the TufMups website? (decoded)

![](attachments/Pasted%20image%2020230315103019.png)

- What is the key to decode the secret message in the TufMups website?
base64 + xor
ftp creds are p1ggy / ripgonzo
key =0a

![](attachments/Pasted%20image%2020230315103346.png)

- How did K3anu get access to the file? (lowercase, just protocol)


- 操作者的IRC nikename
k3anu

![](attachments/Pasted%20image%2020230315100808.png)