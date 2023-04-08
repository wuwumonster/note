SOME是同源方法执行漏洞（Same Origin Method Execution）的简称，SOME是web应用程序攻击方法中的一种，类似于Hijacking攻击，它通过强制受害者在endpoints的域上执行任意页面的脚本方法来滥用回调endpoints，理论上任何具备点击功能（比如添加删除、授权确认等）的网站都存在遭受这种攻击的可能，缺陷是不能带参数操作。  
既然叫同源方法执行漏洞，要想利用该漏洞针对的就是同源网站下的页面
## 基本攻击流程

![](attachments/Pasted%20image%2020230408145523.png)

## 参考文章

https://michaelwayneliu.github.io/2017/12/21/SOME%E6%94%BB%E5%87%BB/