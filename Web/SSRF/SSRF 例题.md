
### [De1CTF 2019]SSRF Me

将flag.txt写入result.txt

hashlib.md5(secert_key + param + action).hexdigest()

在geneSign中已经给出action=scan

![Untitled](../../CTF赛题/BUU月赛/attachment/SSRF%20086ebd7db5a04a9188a2ca987467c35b/Untitled.png)

可以通过tmpfile来写入flag.txt的内容

sign储存在cookie中，而比较时若要将flag.txt写入result.txt需要将param设为flag.txt,action为readscan

![Untitled](../../CTF赛题/BUU月赛/attachment/SSRF%20086ebd7db5a04a9188a2ca987467c35b/Untitled%201.png)

![Untitled](../../CTF赛题/BUU月赛/attachment/SSRF%20086ebd7db5a04a9188a2ca987467c35b/Untitled%202.png)

获取sign  04b41211b6d59cbb6c5c353a07abe153

![Untitled](../../CTF赛题/BUU月赛/attachment/SSRF%20086ebd7db5a04a9188a2ca987467c35b/Untitled%203.png)

![Untitled](../../CTF赛题/BUU月赛/attachment/SSRF%20086ebd7db5a04a9188a2ca987467c35b/Untitled%204.png)