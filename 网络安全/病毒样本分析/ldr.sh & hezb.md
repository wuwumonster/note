 定义样本下载地址，和检测hezb挖矿病毒是否已经在运行
![](attachments/Pasted%20image%2020230227224021.png)

定义curl工具参数
![](attachments/Pasted%20image%2020230227224339.png)

将前面的curl函数封装，便于调用
![](attachments/Pasted%20image%2020230227225240.png)

关闭防火墙并开放所有网络访问
![](attachments/Pasted%20image%2020230227224634.png)

移出云主机安全组件和服务
![](attachments/Pasted%20image%2020230227225351.png)

计算当前hezb程序md5值并比对，防止欺骗
![](attachments/Pasted%20image%2020230227230001.png)

通过受害主机主机的私钥信息与历史ssh连接的IP地址验证私钥是否匹配，尝试进行免密连接
![](attachments/Pasted%20image%2020230227225621.png)

将ldr.sh脚本的执行加入计划任务，同时将ls命令备份，在原有的ls命令中加入对脚本的执行
![](attachments/Pasted%20image%2020230227230137.png)

擦除日志信息
![](attachments/Pasted%20image%2020230227230200.png)