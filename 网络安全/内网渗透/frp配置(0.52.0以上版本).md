>会运行在ipv6上，导致无法访问，暂时没有解决
## 服务端配置
### ServerConfig[](https://gofrp.org/zh-cn/docs/reference/server-configures/#serverconfig)

| Field                           | Type                                                                                                     | Description                                   | Required |
| ------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------- | -------- |
| auth                            | [AuthServerConfig](https://gofrp.org/zh-cn/docs/reference/server-configures/#authserverconfig)           | 鉴权配置。                                         | No       |
| bindAddr                        | string                                                                                                   | 服务端监听地址，用于接收 frpc 的连接，默认监听 0.0.0.0。           | No       |
| bindPort                        | int                                                                                                      | 服务端监听端口，默认值为 7000。                            | No       |
| kcpBindPort                     | int                                                                                                      | 服务端监听 KCP 协议端口，用于接收配置了使用 KCP 协议的 frpc 连接。     | No       |
| quicBindPort                    | int                                                                                                      | 服务端监听 QUIC 协议端口，用于接收配置了使用 QUIC 协议的 frpc 连接。   | No       |
| proxyBindAddr                   | string                                                                                                   | 代理监听地址，可以使代理监听在不同的网卡地址，默认情况下同 bindAddr。       | No       |
| vhostHTTPPort                   | int                                                                                                      | HTTP 类型代理监听的端口，启用后才能支持 HTTP 类型的代理。            | No       |
| vhostHTTPTimeout                | int                                                                                                      | HTTP 类型代理在服务端的 ResponseHeader 超时时间，默认为 60s。   | No       |
| vhostHTTPSPort                  | int                                                                                                      | HTTPS 类型代理监听的端口，启用后才能支持 HTTPS 类型的代理。          | No       |
| tcpmuxHTTPConnectPort           | int                                                                                                      | tcpmux 类型且复用器为 httpconnect 的代理监听的端口。          | No       |
| tcpmuxPassthrough               | bool                                                                                                     | 对于 tcpmux 类型的代理是否透传 CONNECT 请求。               | No       |
| subDomainHost                   | string                                                                                                   | 二级域名后缀。                                       | No       |
| custom404Page                   | string                                                                                                   | 自定义 404 错误页面地址。                               | No       |
| sshTunnelGateway                | [SSHTunnelGateway](https://gofrp.org/zh-cn/docs/reference/server-configures/#sshtunnelgateway)           | ssh 隧道网关配置。                                   | No       |
| webServer                       | [WebServerConfig](https://gofrp.org/zh-cn/docs/reference/common#webserverconfig)                         | 服务端 Dashboard 配置。                             | No       |
| enablePrometheus                | bool                                                                                                     | 是否提供 Prometheus 监控接口，需要同时启用了 webServer 后才会生效。 | No       |
| log                             | [LogConfig](https://gofrp.org/zh-cn/docs/reference/common#logconfig)                                     | 日志配置。                                         | No       |
| transport                       | [ServerTransportConfig](https://gofrp.org/zh-cn/docs/reference/server-configures/#servertransportconfig) | 网络层配置。                                        | No       |
| detailedErrorsToClient          | bool                                                                                                     | 服务端返回详细错误信息给客户端，默认为 true。                     | No       |
| maxPortsPerClient               | int                                                                                                      | 限制单个客户端最大同时存在的代理数，默认无限制。                      | No       |
| userConnTimeout                 | int                                                                                                      | 用户建立连接后等待客户端响应的超时时间，单位秒，默认为 10 秒。             | No       |
| udpPacketSize                   | int                                                                                                      | 代理 UDP 服务时支持的最大包长度，默认为 1500，服务端和客户端的值需要一致。    | No       |
| natholeAnalysisDataReserveHours | int                                                                                                      | 打洞策略数据的保留时间，默认为 168 小时，即 7 天。                 | No       |
| allowPorts                      | [[]PortsRange](https://gofrp.org/zh-cn/docs/reference/common#portsrange)                                 | 允许代理绑定的服务端端口。                                 | No       |
| httpPlugins                     | [[]HTTPPluginOptions](https://gofrp.org/zh-cn/docs/reference/server-configures/#httppluginoptions)       | 服务端 HTTP 插件配置。                                | No       |

### AuthServerConfig[](https://gofrp.org/zh-cn/docs/reference/server-configures/#authserverconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|method|string|鉴权方式，可选值为 token 或 oidc，默认为 token。|No|
|additionalScopes|[]string|鉴权信息附加范围，可选值为 HeartBeats 和 NewWorkConns|No|
|token|string|在 method 为 token 时生效，客户端需要设置一样的值才能鉴权通过。|No|
|oidc|[AuthOIDCServerConfig](https://gofrp.org/zh-cn/docs/reference/server-configures/#authoidcserverconfig)|oidc 鉴权配置。|No|

### AuthOIDCServerConfig[](https://gofrp.org/zh-cn/docs/reference/server-configures/#authoidcserverconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|issuer|string||No|
|audience|string||No|
|skipExpiryCheck|bool||No|
|skipIssuerCheck|bool||No|

### ServerTransportConfig[](https://gofrp.org/zh-cn/docs/reference/server-configures/#servertransportconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|tcpMuxKeepaliveInterval|int|tcp mux 的心跳检查间隔时间，单位秒。|No|
|tcpKeepalive|int|和客户端底层 TCP 连接的 keepalive 间隔时间，单位秒，配置为负数表示不启用。|No|
|maxPoolCount|int|允许客户端设置的最大连接池大小，如果客户端配置的值大于此值，会被强制修改为最大值，默认为 5。|No|
|heartbeatTimeout|int|服务端和客户端心跳连接的超时时间，单位秒，默认为 90 秒。|No|
|quic|[QUICOptions](https://gofrp.org/zh-cn/docs/reference/common#quicoptions)|QUIC 协议配置参数。|No|
|tls|[TLSServerConfig](https://gofrp.org/zh-cn/docs/reference/server-configures/#tlsserverconfig)|服务端 TLS 协议配置。|No|

### TLSServerConfig[](https://gofrp.org/zh-cn/docs/reference/server-configures/#tlsserverconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|force|bool|是否只接受启用了 TLS 的客户端连接。|No|
||[TLSConfig](https://gofrp.org/zh-cn/docs/reference/common#tlsconfig)|TLS 协议配置，内嵌结构。|No|

### HTTPPluginOptions[](https://gofrp.org/zh-cn/docs/reference/server-configures/#httppluginoptions)

|Field|Type|Description|Required|
|---|---|---|---|
|name|string|插件名称。|Yes|
|addr|string|插件接口的地址。|Yes|
|path|string|插件接口的 Path。|Yes|
|ops|[]string|插件需要生效的操作列表，具体可选值请参考服务端插件的说明文档。|Yes|
|tlsVerify|bool|当插件地址为 HTTPS 协议时，是否校验插件的 TLS 证书，默认为不校验。|No|

### SSHTunnelGateway[](https://gofrp.org/zh-cn/docs/reference/server-configures/#sshtunnelgateway)

|Field|Type|Description|Required|
|---|---|---|---|
|bindPort|int|SSH 服务器监听端口。|YES|
|privateKeyFile|string|SSH 服务器私钥文件路径。若为空，frps将读取autoGenPrivateKeyPath路径下的私钥文件。|No|
|autoGenPrivateKeyPath|string|私钥文件自动生成路径，默认为./.autogen_ssh_key。若文件不存在或内容为空，frps将自动生成RSA私钥文件并存储到该路径。|No|
|authorizedKeysFile|string|SSH 客户端授权密钥文件路径。若为空，则不进行SSH客户端鉴权认证。非空可实现SSH免密登录认证。|No|

## 客户端配置
frp 客户端的详细配置说明。
### ClientConfig[](https://gofrp.org/zh-cn/docs/reference/client-configures/#clientconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ClientCommonConfig](https://gofrp.org/zh-cn/docs/reference/client-configures/#clientcommonconfig)|客户端通用配置。|Yes|
|proxies|[[]ProxyConfig](https://gofrp.org/zh-cn/docs/reference/proxy)|代理配置，不同的代理类型对应不同的配置，例如 [TCPProxyConfig](https://gofrp.org/zh-cn/docs/reference/proxy#tcpproxyconfig) 或 [HTTPProxyConfig](https://gofrp.org/zh-cn/docs/reference/proxy#httpproxyconfig)。|No|
|visitors|[[]VisitorConfig](https://gofrp.org/zh-cn/docs/reference/visitor)|访问者配置，不同的访问者类型对应不同的配置，例如 [STCPVisitorConfig](https://gofrp.org/zh-cn/docs/reference/visitor#stcpvisitorconfig)。|No|

### ClientCommonConfig[](https://gofrp.org/zh-cn/docs/reference/client-configures/#clientcommonconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|auth|[AuthClientConfig](https://gofrp.org/zh-cn/docs/reference/client-configures/#authclientconfig)|客户端鉴权配置。|No|
|user|string|用户名，设置此参数后，代理名称会被修改为 {user}.{proxyName}，避免代理名称和其他用户冲突。|No|
|serverAddr|string|连接服务端的地址。|No|
|serverPort|int|连接服务端的端口，默认为 7000。|No|
|natHoleStunServer|string|xtcp 打洞所需的 stun 服务器地址，默认为 stun.easyvoip.com:3478。|No|
|dnsServer|string|使用 DNS 服务器地址，默认使用系统配置的 DNS 服务器，指定此参数可以强制替换为自定义的 DNS 服务器地址。|No|
|loginFailExit|bool|第一次登陆失败后是否退出，默认为 true。|No|
|start|[]string|指定启用部分代理，当配置了较多代理，但是只希望启用其中部分时可以通过此参数指定，默认为全部启用。|No|
|log|[LogConfig](https://gofrp.org/zh-cn/docs/reference/common#logconfig)|日志配置。|No|
|webServer|[WebServerConfig](https://gofrp.org/zh-cn/docs/reference/common#webserverconfig)|客户端 AdminServer 配置。|No|
|transport|[ClientTransportConfig](https://gofrp.org/zh-cn/docs/reference/client-configures/#clienttransportconfig)|客户端网络层配置。|No|
|udpPacketSize|int|代理 UDP 服务时支持的最大包长度，默认为 1500，服务端和客户端需要保持配置一致。|No|
|metadatas|map[string]string|附加元数据，会传递给服务端插件，提供附加能力。|No|
|includes|[]string|指定额外的配置文件目录，其中的 proxy 和 visitor 配置会被读取加载。|No|

### ClientTransportConfig[](https://gofrp.org/zh-cn/docs/reference/client-configures/#clienttransportconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|protocol|string|和 frps 之间的通信协议，可选值为 tcp, kcp, quic, websocket, wss。默认为 tcp。|No|
|dialServerTimeout|int|连接服务端的超时时间，默认为 10s。|No|
|dialServerKeepalive|int|和服务端底层 TCP 连接的 keepalive 间隔时间，单位秒。|No|
|connectServerLocalIP|string|连接服务端时所绑定的本地 IP。|No|
|proxyURL|string|连接服务端使用的代理地址，格式为 {protocol}://user:passwd@192.168.1.128:8080 protocol 目前支持 http、socks5、ntlm。|No|
|poolCount|int|连接池大小。|No|
|tcpMux|bool|TCP 多路复用，默认启用。|No|
|tcpMuxKeepaliveInterval|int|`tcp_mux` 的心跳检查间隔时间。|No|
|quic|[QUICOptions](https://gofrp.org/zh-cn/docs/reference/common#quicoptions)|QUIC 协议配置参数。|No|
|heartbeatInterval|int|向服务端发送心跳包的间隔时间，默认为 30s。建议启用 `tcp_mux_keepalive_interval`，将此值设置为 -1。|No|
|heartbeatTimeout|int|和服务端心跳的超时时间，默认为 90s。|No|
|tls|[TLSClientConfig](https://gofrp.org/zh-cn/docs/reference/client-configures/#tlsclientconfig)|客户端 TLS 协议配置。|No|

### TLSClientConfig[](https://gofrp.org/zh-cn/docs/reference/client-configures/#tlsclientconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|enable|bool|是否和服务端之间启用 TLS 连接，默认启用。|No|
|disableCustomTLSFirstByte|bool|启用 TLS 连接时，不发送 0x17 特殊字节。默认为 true。当配置为 true 时，无法和 vhostHTTPSPort 端口复用。|No|
||[TLSConfig](https://gofrp.org/zh-cn/docs/reference/common#tlsconfig)|TLS 协议配置，内嵌结构。|No|

### AuthClientConfig[](https://gofrp.org/zh-cn/docs/reference/client-configures/#authclientconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|method|string|鉴权方式，可选值为 token 或 oidc，默认为 token。|No|
|additionalScopes|[]string|鉴权信息附加范围，可选值为 HeartBeats 和 NewWorkConns|No|
|token|string|在 method 为 token 时生效，客户端需要设置一样的值才能鉴权通过。|No|
|oidc|[AuthOIDCClientConfig](https://gofrp.org/zh-cn/docs/reference/client-configures/#authoidcclientconfig)|oidc 鉴权配置。|No|

### AuthOIDCClientConfig[](https://gofrp.org/zh-cn/docs/reference/client-configures/#authoidcclientconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|clientID|string||No|
|clientSecret|string||No|
|audience|string||No|
|scope|string||No|
|tokenEndpointURL|string||No|
|additionalEndpointParams|map[string]string||No|
## 代理配置

frp 代理的详细配置说明。

### ProxyBaseConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|name|string|代理名称。|Yes|
|type|string|代理类型，可选值为 tcp, udp, http, https, tcpmux, stcp, sudp, xtcp。|Yes|
|annotations|map[string]string|代理的注释信息，会被展示在 server 的 dashboard 中。|No|
|transport|[ProxyTransport](https://gofrp.org/zh-cn/docs/reference/proxy/#proxytransport)|代理网络层配置。|No|
|metadatas|map[string]string|附加元数据，会传递给服务端插件，提供附加能力。|No|
|loadBalancer|[LoadBalancerConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#loadbalancerconfig)|负载均衡配置。|No|
|healthCheck|[HealthCheckConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#healthcheckconfig)|健康检查配置。|No|
||[ProxyBackend](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybackend)|代理后端服务配置。|Yes|

### ProxyTransport[](https://gofrp.org/zh-cn/docs/reference/proxy/#proxytransport)

|Field|Type|Description|Required|
|---|---|---|---|
|useEncryption|bool|是否启用加密功能，启用后该代理和服务端之间的通信内容都会被加密传输，如果 frpc 启用了全局 TLS，则不需要再启用此参数。|No|
|useCompression|bool|是否启用压缩功能，启用后该代理和服务端之间的通信内容都会被压缩传输。|No|
|bandwidthLimit|string|设置单个 proxy 的带宽限流，单位为 MB 或 KB，0 表示不限制，如果启用，默认会作用于对应的 frpc。|No|
|bandwidthLimitMode|string|限流类型，客户端限流或服务端限流，可选值为 client 和 server，默认为客户端限流。|No|
|proxyProtocolVersion|string|启用 proxy protocol 协议的版本，可选值为 v1 和 v2。如果启用，则 frpc 和本地服务建立连接后会发送 proxy protocol 的协议，包含了原请求的 IP 地址和端口等内容。|No|

### ProxyBackend[](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybackend)

|Field|Type|Description|Required|
|---|---|---|---|
|localIP|string|被代理的本地服务 IP，默认为 127.0.0.1。|No|
|localPort|int|被代理的本地服务端口。|No|
|plugin|[ClientPluginOptions](https://gofrp.org/zh-cn/docs/reference/client-plugin)|客户端插件配置，如果启用了客户端插件，则不需要配置 localIP 和 localPort，流量会由客户端插件接管。不同的插件类型对应不同的配置，例如 [HTTPProxyPluginOptions](https://gofrp.org/zh-cn/docs/reference/client-plugin#httpproxypluginoptions)。|No|

### LoadBalancerConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#loadbalancerconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|group|string|负载均衡分组名称，用户请求会以轮询的方式发送给同一个 group 中的代理。|Yes|
|groupKey|string|负载均衡分组密钥，用于对负载均衡分组进行鉴权，groupKey 相同的代理才会被加入到同一个分组中。|No|

### HealthCheckConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#healthcheckconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|type|string|健康检查类型，可选值为 tcp 和 http，配置后启用健康检查功能，tcp 是连接成功则认为服务健康，http 要求接口返回 2xx 的状态码则认为服务健康。|Yes|
|timeoutSeconds|int|健康检查超时时间(秒)，默认为 3s。|No|
|maxFailed|int|健康检查连续错误次数，连续检查错误多少次认为服务不健康，默认为 1。|No|
|intervalSeconds|int|健康检查周期(秒)，每隔多长时间进行一次健康检查，默认为 10s。|No|
|path|string|健康检查的 HTTP 接口，如果健康检查类型是 http，则需要配置此参数，指定发送 http 请求的 path，例如 `/health`。|No|
|httpHeaders|[[]HTTPHeader](https://gofrp.org/zh-cn/docs/reference/common#httpheader)|健康检查的 HTTP 请求头，仅在健康检查类型是 http 时生效。|No|

### DomainConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#domainconfig)

|Field|Type|Description|Required|
|---|---|---|---|
|customDomains|[]string|自定义域名列表。|No|
|subdomain|string|子域名。|No|

### TCPProxyConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#tcpproxyconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ProxyBaseConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)|基础配置。|Yes|
|remotePort|int|服务端绑定的端口，用户访问服务端此端口的流量会被转发到对应的本地服务。|No|

### UDPProxyConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#udpproxyconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ProxyBaseConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)|基础配置。|Yes|
|remotePort|int|服务端绑定的端口，用户访问服务端此端口的流量会被转发到对应的本地服务。|No|

### HTTPProxyConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#httpproxyconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ProxyBaseConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)|基础配置。|Yes|
||[DomainConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#domainconfig)|域名配置。|Yes|
|locations|[]string|URL 路由配置。|No|
|httpUser|string|HTTP Basic Auth 用户名。|No|
|httpPassword|string|HTTP Basic Auth 密码。|No|
|hostHeaderRewrite|string|替换 Host Header。|No|
|requestHeaders|[HeaderOperations](https://gofrp.org/zh-cn/docs/reference/common#headeroperations)|对请求 Header 的操作配置。|No|
|responseHeaders|[HeaderOperations](https://gofrp.org/zh-cn/docs/reference/common#headeroperations)|对响应 Header 的操作配置。|No|
|routeByHTTPUser|string|根据 HTTP Basic Auth user 路由。|No|

### HTTPSProxyConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#httpsproxyconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ProxyBaseConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)|基础配置。|Yes|
||[DomainConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#domainconfig)|域名配置。|Yes|

### TCPMuxProxyConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#tcpmuxproxyconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ProxyBaseConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)|基础配置。|Yes|
||[DomainConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#domainconfig)|域名配置。|Yes|
|httpUser|string|用户名，如果配置此参数，通过 HTTP CONNECT 建立连接时需要通过 Proxy-Authorization 附加上正确的身份信息。|No|
|httpPassword|string|密码。|No|
|routeByHTTPUser|string|根据 HTTP Basic Auth user 路由。|No|
|multiplexer|string|复用器类型，目前仅支持 httpconnect。|No|

### STCPProxyConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#stcpproxyconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ProxyBaseConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)|基础配置。|Yes|
|secretKey|string|密钥，服务端和访问端的密钥需要一致，访问端才能访问到服务端。|No|
|allowUsers|[]string|允许访问的 visitor 用户列表，默认只允许同一用户下的 visitor 访问，配置为 * 则允许任何 visitor 访问。|No|

### XTCPProxyConfig[](https://gofrp.org/zh-cn/docs/reference/proxy/#xtcpproxyconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ProxyBaseConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)|基础配置。|Yes|
|secretKey|string|密钥，服务端和访问端的密钥需要一致，访问端才能访问到服务端。|No|
|allowUsers|[]string|允许访问的 visitor 用户列表，默认只允许同一用户下的 visitor 访问，配置为 * 则允许任何 visitor 访问。|No|

### SUDPProxyConfig [](https://gofrp.org/zh-cn/docs/reference/proxy/#sudpproxyconfig)

|Field|Type|Description|Required|
|---|---|---|---|
||[ProxyBaseConfig](https://gofrp.org/zh-cn/docs/reference/proxy/#proxybaseconfig)|基础配置。|Yes|
|secretKey|string|密钥，服务端和访问端的密钥需要一致，访问端才能访问到服务端。|No|
|allowUsers|[]string|允许访问的 visitor 用户列表，默认只允许同一用户下的 visitor 访问，配置为 * 则允许任何 visitor 访问。|No|

- 服务端连接端口
```TOML
bindport = 7000 # 服务端监听端口
```
- 服务端身份认证及密码（可选）
```toml
auth.method = "token" # 服务端身份认证，默认token
auth.token = "test" # 服务端token密码
```
- 服务端TLS加密（可选）
```toml
transport.tls.force = false # 是否只接受启用了TLS的客户端连接
```
- 服务端Web界面（可选）
>不配置WebSSL，网页为http
```toml
webServer.port = 7001   #Web页面端口号
webServer.user = "admin"   #(可选)Web页面账号
webServer.password = "123456"   #(可选)Web页面密码
webServer.tls.certFile = "server.pem"   #(可选)WebSSL证书
webServer.tls.keyFile = "server.key"   #(可选)WebSSL私钥
```
- 服务端HTTP(s)监听端口(可选)
```toml
vhostHTTPPort = 80
vhostHTTPSPort = 443
```

## 可用插件
- unix_domain_socket
- http_proxy
- socks5
- static_file
- http2https
- https2http
- https2https
## socks5 反向代理 + proxifier

vps frps
```
bindPort = 7000 #服务端的端口号 
webServer.addr = "0.0.0.0"
webServer.port = 7500 #服务端仪表盘界面的访问端口 
webServer.user = admin #仪表盘的用户名 
webServer.password = ************ #仪表盘的用户密码
```

外网跳板 frpc
```
serverAddr = ip #服务器的地址 
serverPort = 7000 #服务器监听的端口号 
tls_enable = ture #启用tls加密连接 
[plugin socks] type = tcp #指定协议类型为tcp 
plugin = socks5 #使用的插件为socks5 
remote_port = 46075 #指定socks5代理的远程端口 
use_encryption = true 
use_compression = true
```