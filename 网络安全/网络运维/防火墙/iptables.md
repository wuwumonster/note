## 结构
### 表Table&链Chains
#### Filter表
- INPUT链
- OUTPUT链
- FORWARD链
#### NAT表
- PREROUTING链
- POSTROUTING链
- OUTPUT链
#### Mangle表
- PREROUTING链
- OUTPUT链
- FORWARD链
- INPUT链
- POSTROUTING链
#### Raw表
- PREROUTING
- OUTPUT
### 规则Rules
- ACCEPT
- DROP
- QUEUE
- RETURN

```HELP
-p 协议（protocol）
  指定规则的协议，如tcp, udp, icmp等，可以使用all来指定所有协议。
  如果不指定-p参数，则默认是all值。这并不明智，请总是明确指定协议名称。
  可以使用协议名(如tcp)，或者是协议值（比如6代表tcp）来指定协议。映射关系请查看/etc/protocols
  还可以使用–protocol参数代替-p参数
-s 源地址（source）
  指定数据包的源地址
  参数可以使IP地址、网络地址、主机名
  例如：-s 192.168.1.101指定IP地址
  例如：-s 192.168.1.10/24指定网络地址
  如果不指定-s参数，就代表所有地址
  还可以使用–src或者–source
-d 目的地址（destination）
  指定目的地址
  参数和-s相同
  还可以使用–dst或者–destination
-j 执行目标（jump to target）
  -j代表”jump to target”
  -j指定了当与规则(Rule)匹配时如何处理数据包
  可能的值是ACCEPT, DROP, QUEUE, RETURN
  还可以指定其他链（Chain）作为目标
-i 输入接口（input interface）
  -i代表输入接口(input interface)
  -i指定了要处理来自哪个接口的数据包
    这些数据包即将进入INPUT, FORWARD, PREROUTE链
  例如：-i eth0指定了要处理经由eth0进入的数据包
  如果不指定-i参数，那么将处理进入所有接口的数据包
  如果出现! -i eth0，那么将处理所有经由eth0以外的接口进入的数据包
  如果出现-i eth+，那么将处理所有经由eth开头的接口进入的数据包
  还可以使用–in-interface参数
-o 输出（out interface）
  -o代表”output interface”
  -o指定了数据包由哪个接口输出
  这些数据包即将进入FORWARD, OUTPUT, POSTROUTING链
  如果不指定-o选项，那么系统上的所有接口都可以作为输出接口
  如果出现! -o eth0，那么将从eth0以外的接口输出
  如果出现-i eth+，那么将仅从eth开头的接口输出
  还可以使用–out-interface参数

```