### 基础知识
JWT标准文档 [RFC 7519: JSON Web Token (JWT)](https://www.rfc-editor.org/rfc/rfc7519)
### 简介
JWT全称为JSON Web Token,将json对象作为载体来传输信息。通常用于身份认证和信息交换。JWT 可以使用密钥（HMAC 算法）或使用 RSA 或 ECDSA 的公钥/私钥对自身进行签名。
### 结构
JWT分为三部分，分别为Header，Payload以及Signature
我们通过解密网站来看看整体的情况
![](https://cdn.nlark.com/yuque/0/2023/png/25358086/1702367909640-74a217e6-36f5-4985-8291-74129603d21b.png#averageHue=%23fcfcfc&clientId=ud281539c-f800-4&from=paste&id=u5c01545e&originHeight=977&originWidth=1818&originalType=url&ratio=1.5&rotation=0&showTitle=false&status=done&style=none&taskId=uea595c88-25f4-4a22-83ba-7801b6381c6&title=)
####  Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
头部包含JWT的配置信息，alg代表JWT的签名算法，typ代表类型。还有像jwk，kid，jku，cty，x5c等参数信息
这段Json通过Base64Url编码组成JWT的第一个部分
#### Payload
```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```
payload包含着一些声明，这里有三种类型的声明：注册声明，公共声明，私有声明
##### 注册声明
例如，**iss**(issuer) jwt签发人，**exp**(expiration time) 过期时间, **sub**(subject) jwt所面向的用户等
更多细节可以查看RFC文档 [RFC 注册声明](https://www.rfc-editor.org/rfc/rfc7519)
##### 公共声明
这些声明可以由使用JWT的人随意定义，但为了避免冲突，最好是在[IANA JSON Web Token Registry](https://www.iana.org/assignments/jwt/jwt.xhtml)上定义
##### 私有声明
这些声明是为了各方进行信息交换自定义的声明，既不属于注册声明，也不属于私有声明
这段Json也会通过Base64Url编码组成JWT的第二个部分
#### Signature
要想创建签名，你需要获取header，payload以及相应的密钥。
例如，假如我们使用的是HS256算法进行加密，签名将通过以下方式创建
```json
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```
创建的签名作为第三部分组成JWT的最后部分
最后形成的就是我们下图看到的样子，由点进行分割。
![](https://cdn.nlark.com/yuque/0/2023/png/25358086/1702368190942-09a2e348-2282-470a-b83b-685519a60798.png#averageHue=%23fefefd&clientId=u38095455-fa2a-4&from=paste&id=udb8e168f&originHeight=336&originWidth=461&originalType=url&ratio=1.5&rotation=0&showTitle=false&status=done&style=none&taskId=u15d26672-8885-44f3-ac4b-bf88a5bc527&title=)
### JWT相关安全问题
#### 敏感信息泄露
JWT本身包含一些敏感信息，我们可以通过[JSON Web Tokens - jwt.io](https://jwt.io/)对相关JWT进行解码从而获取敏感信息
#### 未对签名进行验证
如果服务端并没有对签名进行验证，那我们就可以随意修改JWT中的信息，从而可能达到越权的目的。
#### 未对加密算法进行强验证
我们知道Header部分的alg声明了加密的算法
例如这里，我们原本声明的是HS256加密算法
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
但如果服务端并未对Header声明的加密算法进行强验证，我们就可以通过将alg修改来绕过签名认证，达到随意修改JWT的目的。
##### 空加密算法绕过
修改脚本
```python
import jwt

# payload
token_dict = {
    "secretid": "",
    "username": "admin",
    "password": "123",
    "iat": 1660183824
}

headers = {
    "alg": "none",
    "typ": "JWT"
}
jwt_token = jwt.encode(token_dict,  # payload, 有效载体
                       "",  # 进行加密签名的密钥
                       algorithm="none",  # 指明签名算法方式, 默认也是HS256
                       headers=headers
                       # json web token 数据结构包含两部分, payload(有效载体), headers(标头)
                      )

print(jwt_token)
```
[虎符 CTF Web 部分 Writeup – glzjin](https://www.zhaoj.in/read-6512.html)
HFCTF2020的easyLogin考察了相关的知识点
因为开发者的使用不当，导致参数`alorithms`错写成了`algorithm`。`node`中的`jsonwebtoken`库中判断如果`!secret&&!argorithms`则使用传入JWT的`header`中的`algorithm`，所以只需要绕过题目中对`secretid`的限制，将`secret`置为空，就可以使用`none`算法，从而无需验证签名。
##### 将RS256修改未HS256绕过
HS256为对称加密算法，使用相同的密钥进行解密。而RS256为非对称加密算法，使用私钥对消息进行签名并使用公钥进行身份验证。
如果我们能获得公钥，并且服务端对加密算法没有进行强验证，我们就可以将header头中的算法改为HS256算法，通过公钥进行签名来生成我们需要的JWT从而实现越权等操作。
修改脚本
```python
import jwt
public = open('public.key', 'r').read()
payload={"user": "admin"}
print(jwt.encode(payload, key=public, algorithm='HS256'))
```
#### 绕过弱签名密钥
如果签名使用了弱密钥，我们可以尝试使用工具对密钥进行爆破
##### 相关工具
[c-jwt-cracker](https://github.com/brendan-rius/c-jwt-cracker.git)
##### 使用示例
![](https://cdn.nlark.com/yuque/0/2023/png/25358086/1702368622898-3a0fda67-54fa-4bde-9fce-6bc2dc652572.png#averageHue=%232b323e&clientId=u38095455-fa2a-4&from=paste&id=u068fe1fb&originHeight=99&originWidth=1101&originalType=url&ratio=1.5&rotation=0&showTitle=false&status=done&style=none&taskId=u9c1f334d-8088-400e-b168-bfa8d8cc736&title=)
#### JWT标头注入
##### 通过jwk参数注入自签名的JWT
JWK 英文全称为 JSON Web Key，是一个JSON对象，表示一个加密的密钥，他不同于alg属性，JWK是可选的，以下就是一个示例
```json
{
  "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
  "typ": "JWT",
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "e": "AQAB",
    "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
    "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9m"
  }
}
```
在理想情况下，服务器应该是只使用公钥白名单来验证JWT签名的，但对于一些相关配置错误的服务器会用JWK参数中嵌入的任何密钥进行验证，攻击者就可以利用这一行为，用自己的RSA私钥对修改过的JWT进行签名，然后在JWK头部中嵌入对应的公钥进行越权操作
##### 通过jku参数注入自签名的JWT
有些服务器并不会直接使用JWK头部参数来嵌入公钥，而是使用JKU（JWK Set URL）来引用一个包含了密钥的JWK Set，我们就可以借此来构造一个密钥从而实现越权操作
##### 通过kid参数注入自签名的JWT
服务器可能会使用多个加密密钥来为不同类型的数据进行签名，出于这个原因，在JWT头部有时会包含一个kid参数，以避免服务器验证签名时出现错误，而在JWT规范中并没有对这个kid定义具体的结构，他仅仅是开发人员任意选择的一个字符串，可能只是一个指向数据库中的一个特定条目，甚至只是一个文件的名称也有可能
我们有时可以通过修改KID参数来达到相关的攻击

- 任意文件读取

kid参数用于读取密钥文件，但系统并不会知道用户想要读取的到底是不是密钥文件，所以，如果在没有对参数进行过滤的前提下，攻击者是可以读取到系统的任意文件的。
```json
{
    "alg" : "HS256",
    "typ" : "jwt",
    "kid" : "/etc/passwd"
}
```

- SQL注入

kid也可以从数据库中提取数据，这时候就有可能造成SQL注入攻击，通过构造SQL语句来获取数据或者是绕过signature的验证
```json
{
    "alg" : "HS256",
    "typ" : "jwt",
    "kid" : "key11111111' || union select 'secretkey' -- "
}
```

- 命令注入

对kid参数过滤不严也可能会出现命令注入问题，但是利用条件比较苛刻。如果服务器后端使用的是Ruby，在读取密钥文件时使用了open函数，通过构造参数就可能造成命令注入。
```json
"/path/to/key_file|whoami"
```
对于其他的语言，例如php，如果代码中使用的是exec或者是system来读取密钥文件，那么同样也可以造成命令注入，当然这个可能性就比较小了。
### 防御措施
● 使用最新的 JWT 库，虽然最新版本的稳定性有待商榷，但是安全性都是较高的
● 对 jku 标头进行严格的白名单设置
● 确保 kid 标头不容易受到通过 header 参数进行目录遍历或 SQL 注入的攻击
● 始终为颁发的任何令牌设置一个到期日
● 尽可能避免通过URL参数发送令牌
● 提供aud声明（或类似内容），以指定令牌的预期接收者，防止其应用在不同网站
● 让颁发服务器能够撤销令牌
