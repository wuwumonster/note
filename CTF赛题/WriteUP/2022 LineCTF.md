## gotm
#SSTI-GO-template
ssti获取给jwt加密的key

![](attachments/Pasted%20image%2020240401200536.png)

![](attachments/Pasted%20image%2020240401200627.png)


先构造一个id为`{{.}}`的用户
拿到访问auth拿到token，访问/拿到加密key

![](attachments/Pasted%20image%2020240401200828.png)


将key中的is_admin修改为true，用拿到的key签名后访问/flag

![](attachments/Pasted%20image%2020240401203757.png)


## Memo Driver
CVE-2021-23336
简单说就是在http中可以使用`;`作为查询分隔符和`&`相同
- Python **3.6.13** (2021-02-16) fixed by [commit 5c17dfc (branch 3.6)](https://github.com/python/cpython/commit/5c17dfc5d70ce88be99bc5769b91ce79d7a90d61) (2021-02-15)
- Python **3.7.10** (2021-02-16) fixed by [commit d0d4d30 (branch 3.7)](https://github.com/python/cpython/commit/d0d4d30882fe3ab9b1badbecf5d15d94326fd13e) (2021-02-15)
- Python **3.8.8** (2021-02-19) fixed by [commit e3110c3 (branch 3.8)](https://github.com/python/cpython/commit/e3110c3cfbb7daa690d54d0eff6c264c870a71bf) (2021-02-15)
- Python **3.9.2** (2021-02-19) fixed by [commit c9f0781 (branch 3.9)](https://github.com/python/cpython/commit/c9f07813ab8e664d8c34413c4fc2d4f86c061a92) (2021-02-15)
- Python **3.10.0** (2021-10-04) fixed by [commit fcbe0cb (branch 3.10)](https://github.com/python/cpython/commit/fcbe0cb04d35189401c0c880ebfb4311e952d776) (2021-02-14)
![](attachments/Pasted%20image%2020240402165406.png)

构造下面这样的payload相当于在将`;`作为分割符识别把`../../../`放在了filename前，path被构造为`./memo/id/../../../../etc/passwd`
```
id=etc/passwd;/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e
```

随便生成一个留言就可以拿到自己的id值

![](attachments/Pasted%20image%2020240402173308.png)

没有flag在根目录，最后在`/proc/1/environ`

![](attachments/Pasted%20image%2020240402173705.png)

