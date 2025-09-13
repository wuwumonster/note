关闭时间同步
```SHELL
systemctl stop systemd-timesyncd
```
## 扫描
```shell
nmap -sS -p 1-65535 -Pn -v 10.10.11.69
```

## 域环境
```SHELL
bloodhound-python -u ryan.naylor -p HollowOct31Nyt -k -ns 10.10.11.76 -c All -d voleur.htb --zip
```
## 票据
获取用户票据
```shell
impacket-getTGT [domain/]username[:password]
```
