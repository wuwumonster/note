#Linux #Easy

![](attachments/Pasted%20image%2020240801104705.png)

找到了对应版本的一把梭脚本，但是要求能够登录后台

nmap 扫描结果

![](attachments/Pasted%20image%2020240801113639.png)

3000端口对应了他的git服务

按照感觉找到pass.php

![](attachments/Pasted%20image%2020240801114719.png)

```PHP
<?php
$ww = 'd5443aef1b64544f3685bf112f6c405218c573c7279a831b1fe9612e3a4d770486743c5580556c0d838b51749de15530f87fb793afdcc689b6b39024d7790163';
?>
```
login 中对密码的检验是sha512

![](attachments/Pasted%20image%2020240801114811.png)

![](attachments/Pasted%20image%2020240801115111.png)

