## Flipped
#CBC 

```PYTHON
#-*- coding:utf8 -*-
import base64
import urllib.parse

#iv
#{"admin": 0, "us
#ername": "guest"
#}
 
cipher = base64.b64decode("MwzLr+nNIeN9B8onuSw3GeLfM5DsJUbtY3in/WZiV12lAa6H95lUw67DZ481wNcqYH7A5O1LlW2myTjLRDQUnA==")
print(len(cipher))

array_cipher = bytearray(cipher)
iv = array_cipher[0:16]
print(iv)

decode_plain = '{"admin": 0, "username": "guest"}'

#原始明文
plain = '{"admin": 1, "us'
newiv = list(iv)

for i in range(0,16):
    newiv[i] = (ord(plain[i].encode('utf-8')) ^ iv[i] ^ ord(decode_plain[i].encode('utf-8')))
newiv = bytes(newiv)

print('newiv:',base64.b64encode(newiv+cipher[16:]))
```