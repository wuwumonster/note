## NTLM协议
NTLM协议既可用于工作组中的机器身份验证，又可用于域环境身份验证，还可为SMB、HTTP、LDAP、SMTP等上层微软应用提供身份验证
### SSPI
SSPI（Security Service Provider Interface或Security Support Provider Interface，安全服务提供接口），该接口定义了与安全有关的功能函数,SSPI是Microsoft定义的一套统一的编程接口（一组API）。它位于应用程序和实际的认证协议（如NTLM、Kerberos）之间，为应用程序提供了一套与协议无关的安全服务，包括认证、消息完整性和消息保密性。
- 身份验证机制
- 为其他协议提供的Session Security机制。Session Security（会话安全）可为通信提供数据的完整性校验以及数据的加密、解密功能
### SSP
SSP（Security Service Provider，安全服务提供者）是SSPI的实现者。微软自己实现了很多SSP，用于提供安全功能
- NTLM SSP：Windows NT 3.51中引入(msv1_0.dll)，为Windows 2000之前的客户端-服务器域和非域身份验证(SMB/CIFS)提供NTLM质询/响应身份验证
- Kerberos SSP：Windows 2000中引入，Windows Vista中更新为支持AES(kerberos.dll)，为Windows 2000及更高版本中首选的客户端–服务器域提供相互身份验证
- Digest SSP：Windows XP中引入(wdigest.dll)，在Windows系统与非Windows系统间提供基于HTTP和SASL身份验证的质询/响应
- Negotiate SSP：Windows 2000中引入(secur32.dll)，默认选择Kerberos，如果不可用，则选择NTLM协议。Negotiate SSP提供单点登录功能，有时称为集成Windows身份验证（尤其是用于IIS时）​。在Windows 7及更高版本中引入了客户端和服务器上支持的已安装定制SSP进行身份验证。
- Cred SSP：Windows Vista中引入，Windows XP SP3上也可用(credssp.dll)，为远程桌面连接提供单点登录和网络级身份验证。
- Schannel SSP：Windows 2000中引入(schannel.dll)，Windows Vista中更新为支持更强的AES加密和ECC[6]​，该提供者使用SSL/TLS记录来加密数据有效载荷
- PKU2U SSP：Windows 7中引入(pku2u.dll)，在不隶属域的系统之间提供使用数字证书的对等身份验证


SSPI中定义了与Session Security有关的API，所以上层应用利用任何SSP与远程的服务进行身份验证后，此SSP都会为本次连接生成一个随机Key。这个随机Key被称为Session Key。上层应用经过身份验证后，可以选择性地使用这个Key对之后发往服务端或接收自服务端的数据进行签名或加密。在系统层面，SSP就是一个dll，用来实现身份验证等安全功能。不同的SSP，实现的身份验证机制是不一样的，比如NTLM SSP实现的是一种基于质询/响应的身份验证机制，而Kerberos SSP实现的是基于Ticket（票据）的身份验证机制。我们可以编写自己的SSP，然后注册到操作系统中，让操作系统支持我们自定义的身份验证方法。
![](attachments/Pasted%20image%2020250821085134.png)

>SSPI就像是一个**通用的“电源插座”**。 
>**应用程序**（比如浏览器、文件管理器）就像是一个电器（比如笔记本电脑），它只需要插上就能用，它不关心发电厂是火电、水电还是核电。 
 **SSP (Security Support Provider)**，例如NTLM SSP、Kerberos SSP，就像是**不同的“电源适配器”**。它们负责将插座的标准接口转换成各自协议（NTLM或Kerberos）所需的特定“电压和电流”。
应用程序（电器）只管插到SSPI（插座）上，请求“电力”（安全连接）。SSPI会根据系统策略和可用性，选择合适的SSP（适配器）来提供电力。

![](attachments/Pasted%20image%2020250821090015.png)

如上图为在SSP的交互中三个主要函数得对工作过程
1. **`AcquireCredentialsHandle` (双方都调用)**
    - 客户端和服务器端程序首先都会调用这个函数。它的作用是**获取一个凭证句柄**。        
    - 客户端指定：“我要用`Negotiate`协议，以用户`Alice`的身份去连接”。      
    - 服务器端指定：“我要用`Negotiate`协议，来接受传入的连接”。        
    - 这个函数并不进行网络通信，它只是在本地准备好身份凭据。        
2. **`InitializeSecurityContext` (客户端调用)**    
    - 客户端调用此函数。输入是上一步的凭证句柄和一个目标SPN（例如`cifs/fileserver.domain.com`）。        
    - 这个函数会执行认证协议（如Kerberos）的**第一步**。它生成一个令牌（Token），这可能是一个NTLM Type 1消息，或者是Kerberos的AS-REQ请求（但票据请求通常在本地就由KDC处理了，这里输出的是AP-REQ）。  
    - 客户端程序将这个令牌通过网络发送给服务器。        
3. **`AcceptSecurityContext` (服务器端调用)**    
    - 服务器收到客户端发来的令牌后，调用此函数。        
    - 服务器端的SSP（比如Kerberos SSP）会**验证这个令牌**。        
    - 验证可能需要多轮。如果令牌有效，函数返回成功，服务器就认证了客户端的身份。        
    - 如果需要回复（例如在NTLM的Challenge/Response中），此函数也会生成一个输出令牌，服务器会将其发回给客户端。        
4. **循环 (如果需要)**    
    - 客户端收到服务器的回复令牌后，可能需要再次调用`InitializeSecurityContext`进行处理（例如在NTLM中计算Response）。        
    - 这个过程会持续，直到双方认证成功（函数返回`SEC_OK`）。 
>整个流程由应用程序的代码控制，但认证协议的具体实现完全由底层的SSP（如Kerberos.dll）完成

### LM Hash加密算法
LM是微软推出的一个身份认证协议，使用的加密算法是LM Hash。LM (LAN Manager) Hash是Microsoft在**1987年**为当时的LAN Manager网络操作系统设计的密码哈希算法，本质是DES加密，尽管LM Hash较容易被破解，但为了保证系统的兼容性，Windows只是将LM Hash禁用（从Windows Vista和Windows Server 2008开始，Windows默认禁用LM Hash）
LM Hash的设计几乎是一个“安全反面教材”，其弱点非常明显：
1. **密码大写**：消除了大小写敏感性，大幅降低破解难度。    
2. **长度限制**：最长14字符，且无法处理更长的复杂密码。    
3. **分块处理**：将密码分成两半独立加密。这意味着攻击者可以**分别暴力破解前7个字符和后7个字符**。破解一个7字符的密码（即使是大写、数字、符号混合）的计算复杂度远低于破解一个14字符的密码。    
    - 破解复杂度从 `C^14` 降为 `C^7 + C^7`（C是字符集大小）。        
4. **弱DES密钥**：插入0位的做法使得生成的DES密钥强度很弱。    
5. **固定的明文**：永远加密 `KGS!@#$%`，这使得预计算攻击（如彩虹表）异常高效。

攻击中的常见手法
- **密码破解**：
	- 使用 **rainbow tables**（彩虹表）进行极速破解
	- 使用 **hashcat** 模式 `-m 3000` 或 **John the Ripper** 进行暴力破解或字典攻击。可以分块破解，速度极快。
- **哈希传递(Pass-the-Hash)**：
	- 虽然PtH更常用NT Hash，但LM Hash在古老的系统上也可以用于PtH攻击（配合NTLMv1响应）

### NTLM Hash加密算法
微软于1993年在Windows NT 3.1中首次引入了NTLM Hash，NTLM Hash算法是微软为了在提高安全性的同时保证兼容性而设计的散列加密算法，它是基于MD4加密算法进行加密的。
在用户输入密码进行本地认证的过程中，所有操作都是在本地进行的。系统将用户输入的密码转换为NTLM Hash，然后与SAM文件中的NTLM Hash进行比较，如果相同，说明密码正确，反之则错误。当用户注销、重启、锁屏后，操作系统会让winlogon.exe显示登录界面，也就是输入框。当winlogon.exe接收输入后，将密码交给lsass.exe进程，lsass.exe进程中会存一份明文密码，将明文密码加密成NTLM Hash，与SAM数据库进行比较和认证。
常见获取方式：
1. **本地SAM数据库**：    
    - 位置：`%SystemRoot%\system32\config\SAM`        
    - 权限：需要**SYSTEM**权限才能读取。        
    - 工具：`reg save hklm\sam sam.save` + `reg save hklm\system system.save`，然后使用`secretsdump.py`或Mimikatz离线提取。        
2. **域控NTDS.dit数据库**：    
    - 位置：`%SystemRoot%\NTDS\NTDS.dit`        
    - 权限：需要**Domain Admin**权限。        
    - 工具：`volume shadow copy`创建副本，或使用Mimikatz的`lsadump::dcsync`功能直接从DC内存同步提取。        
3. **LSASS进程内存**：    
    - 这是**最常用**的在线提取方式。用户登录后，其凭证（包括NTLM Hash、Kerberos票据等）会保存在LSASS进程的内存中以便后续认证。        
    - 权限：需要**Administrator**权限。        
    - 工具：**Mimikatz** (`privilege::debug` + `sekurlsa::logonpasswords`)，Cobalt Strike的`hashdump`命令。        
4. **网络嗅探与中继**：    
    - 通过LLMNR/NBNS/MDNS欺骗等手段，诱使客户端向攻击者发起NTLM认证，从而捕获Hash（对于NTLMv1）或直接中继（对于NTLMv1/v2）。
### NTLM协议认证
**NTLM** (NT LAN Manager) 是一套由Microsoft设计的**挑战/响应**认证协议套件，用于在不信任的网络（如互联网或普通局域网）上证明用户的身份。
- 在Windows域环境中，它是**Kerberos协议的fallback方案**。当Kerberos因各种原因（如无法联系KDC、目标服务为IP地址、跨林信任未配置等）无法使用时，系统会自动降级使用NTLM。
- **核心特点**：**无状态**。服务器不需要与域控制器保持持续连接来验证客户端，它可以在认证时直接联系DC进行验证。
NTLM协议由三种类型消息组成：
- Type 1（协商，Negotiate）
	- **主要字段**：    
	    - **Negotiate Flags**：一系列位标志，告知服务器客户端支持的功能（如NTLMv2、签名、密钥交换等）。        
	    - **Supplied Domain**：客户端提供的域名（通常为空）。        
	    - **Supplied Workstation**：客户端计算机名（通常为空）。        
	- **渗透意义**：分析Flags可以判断客户端支持的协议版本和安全性设置。
- Type 2（质询，Challenge）
	- **核心字段**：    
	    - **Challenge**：一个**8字节（NTLMv1）或16字节（NTLMv2）** 的随机数。这是整个协议安全性的基石，确保每次认证的响应都不同（防止重放攻击）。        
	    - **Target Name**：服务器的域名或计算机名。        
	    - **Negotiate Flags**：服务器选择的最终功能标志。        
	- **渗透意义**：攻击者（在 Relay 攻击中）会将自己的Challenge发送给受害者。如果Challenge太弱（如8字节），NTLMv1响应可能被破解。
- Type 3（认证，Authentication）​
	- **核心字段**：    
    - **NT Proof Str** / **NTLMv2 Response**：这是**身份证明（Proof）**。它是使用用户的**NTLM Hash作为密钥**，对服务器发来的Challenge以及其他一些固定数据（如Server Challenge、时间戳等）进行**HMAC-MD5**运算的结果。    
    - **User Name**：尝试认证的用户名。        
    - **Domain Name**：用户所属的域。        
    - **Workstation Name**：客户端计算机名。        
- **渗透意义**：这是PtH攻击利用的关键。攻击者窃取的不是这个Response本身，而是用于计算Response的**NTLM Hash**。有了Hash，攻击者就可以为任何Challenge计算出正确的Response。
![](attachments/Pasted%20image%2020250821092942.png)

服务器收到Type 3消息后，自己并不能直接验证Response的正确性，因为它没有用户的密码Hash。它必须将关键信息发给域控制器（DC）来裁决。
1. **服务器联系DC**：服务器将以下三项打包发送给DC：    
    - **用户名**        
    - **原始的Challenge**（来自Type 2消息）        
    - **客户端计算的Response**（来自Type 3消息）        
2. **DC进行计算验证**：    
    - DC根据**用户名**，在它的数据库（NTDS.dit）中查找该用户的**NTLM Hash**        
    - DC使用这个NTLM Hash和收到的**原始Challenge**，**自己重新计算一遍预期的Response**。计算过程与客户端完全相同。        
    - DC将**自己计算的结果**与**客户端发来的Response**进行比对。        
3. **返回结果**：    
    - 如果两者完全匹配，DC告诉服务器认证成功。        
    - 如果不匹配，认证失败。

常用攻击手法
1. **哈希传递 (Pass-the-Hash, PtH)**：    
    - **原理**：绕过Response的计算过程，直接使用窃取的NTLM Hash去应对服务器的Challenge。        
    - **工具**：`Mimikatz` (`sekurlsa::pth`), `Impacket`套件 (所有`*exec.py`工具), `Cobalt Strike`。        
2. **NTLM中继攻击 (NTLM Relay)**：    
    - **原理**：攻击者扮演“中间人”，将受害者的NTLM认证请求转发到另一台目标机器。如果受害者对目标机器有权限，攻击者就能获得访问权限。        
    - **前提**：SMB签名未强制启用（在大多数非DC的Windows系统上默认关闭）。        
    - **工具**：`Impacket`的`ntlmrelayx.py`。        
3. **Net-NTLM Hash破解**：    
    - **注意**：从网络抓包中获取的不是NTLM Hash，而是**Net-NTLM Hash**（即Challenge + Response的组合）。        
    - **原理**：通过暴力破解或字典攻击，从Net-NTLM Hash中还原出原始的NTLM Hash。这对NTLMv1是可行的，但对NTLMv2几乎不可能（除非密码极弱）。        
    - **工具**：`Hashcat` (`-m 5500` for NTLMv1, `-m 5600` for NTLMv2)。

## Kerberos协议
Kerberos是一种基于票据(Ticket)的认证方式。客户端想要访问服务端的某个服务，首先需要购买服务端认可的ST（Service Ticket，服务票据）​。也就是说，客户端在访问服务之前需要先买好票，等待服务验票之后才能访问。但是这张票并不能直接购买，需要一张TGT（Ticket Granting Ticket，认购权证）​。也就是说，客户端在买票之前必须先获得一张TGT。TGT和ST均是由KDC发放的，因为KDC运行在域控上，所以说TGT和ST均是由域控发放的。
Kerberos协议有两个基础认证模块—AS_REQ & AS_REP和TGS_REQ &TGS_REP，以及微软扩展的两个认证模块S4U和PAC。S4U是微软为了实现委派而扩展的模块，分为S4u2Self和S4u2Proxy。在Kerberos最初设计的流程里只说明了如何证明客户端的真实身份，并没有说明客户端是否有权限访问该服务，因为在域中不同权限的用户能够访问的资源是不同的。因此微软为了解决权限这个问题，引入了PAC（Privilege Attribute Certificate，特权属性证书）的概念。
### PAC
**PAC** 是Microsoft对标准Kerberos协议的一个**扩展**。你可以把它理解为附在Kerberos票据（TGT和ST）里的一个**安全通行证**或**附加信息包**
PAC包含各种授权信息、附加凭据信息、配置文件和策略信息等，例如用户所属的用户组、用户所具有的权限等。在最初的RFC1510规定的标准Kerberos认证过程中并没有PAC，服务服务器接收到ST后，它只知道“这个用户是谁”，但并不知道“这个用户**有什么权限**”,服务服务器为了判断用户的访问权限，不得不再次去联系域控制器（DC）查询用户的组成员身份等信息。这增加了DC的负载，也违背了Kerberos无状态设计的初衷。微软在自己的产品所实现的Kerberos流程中加入了PAC的概念。由于在域中不同权限的用户能够访问的资源是不同的，因此微软设计PAC用来辨别用户身份和权限。
#### PAC的结构与内容
![](attachments/Pasted%20image%2020250821100119.png)
![](attachments/Pasted%20image%2020250821100326.png)
- cBuffers：包含数组缓冲区中的条目数。
- Version：版本。
- Buffers：包含一个PAC_INFO_BUFFER结构的数组。
PAC被放置在票据的`Authorization Data`字段中。它本身是一个复杂的结构，主要包含以下关键信息(Buffers)：
1. **登录信息 (Logon Info)**：    
    - **用户SID**：用户的安全标识符。        
    - **主组SID**：用户所属的主组。        
    - **额外组SID**：用户所属的所有其他组的SID列表。**这是权限判断的核心**。       
    - **登录时间、有效期**等。        
2. **服务器签名**：整个PAC内容使用**KDC的密钥（`KRBtgt`）** 进行的签名。    
3. **KDC签名**：整个PAC内容使用**服务服务器密钥**的签名。（在某些情况下）   
**关键点**：PAC由**KDC**（域控制器）生成和签署。客户端和服务器都无法伪造一个有效的PAC，因为它们没有`KRBtgt`密钥。
![](attachments/Pasted%20image%2020250821100401.png)
#### PAC凭证信息
PAC不仅仅是“一些组信息”，它是一个结构化的数据库，包含了在Windows域环境中进行授权决策所需的**全部身份和权限凭证**。
Logon Info类型的PAC_LOGON_INFO包含Kerberos票据客户端的凭据信息。数据本身包含在一个KERB_VALIDATION_INFO结构中，该结构是由NDR编码的。NDR编码的输出被放置在Logon Info类型的PAC_INFO_BUFFER结构中。
##### a. `LOGON_INFO` (最重要的部分)

这是PAC的**核心**，包含了用户登录和授权所需的所有基本信息。它本身又是一个复杂的结构（`KERB_VALIDATION_INFO`），主要包含：
- **用户标识信息**：    
    - `UserId`：用户的**相对标识符 (RID)**。        
    - `PrimaryGroupId`：用户**主要组**的RID（通常是`Domain Users`的RID）。    
    - `GroupIds`：一个**SID列表**，包含了用户所属的所有**额外组**（如`Domain Admins`, `Schema Admins`等）。**这是权限提升的关键**。    
    - `LogonDomainId`：用户所在域的SID。
>域用户的Group RID恒为513 （也就是Domain Users的RID）​，机器用户的Group RID恒为515（也就是Domain Comp­uters的RID）​，域控的Group RID恒为516 （也就是Domain Controllers的RID）​。
- **登录元数据**：    
    - `LogonTime`：用户登录时间。        
    - `LogoffTime`：用户登录会话过期时间。        
    - `KickOffTime`：强制注销时间。        
    - `PasswordLastSet`：密码最后修改时间。        
    - `PasswordCanChange`：允许修改密码的时间。        
    - `PasswordMustChange`：必须修改密码的时间。        
- **登录类型和来源**：    
    - `LogonType`：登录类型（如交互式、网络、批处理等）。        
    - `UserFlags`：用户账户标志。        
    - `LogonServer`：用户进行认证的域控制器名称。        
    - `LogonServerName`：用户进行认证的域控制器名称。        
    - `UserSessionKey`：用户会话密钥（已废弃，通常为空）。       

**渗透视角**：`GroupIds`列表是黄金票据攻击中你最想篡改的部分。如果你能成功伪造一个包含`Domain Admins`组SID的PAC，你就能获得域管理员权限。但正如之前所述，签名是最大的障碍。
##### b. `CLIENT_INFO`
这是一个简单但重要的结构，用于快速验证。
- `ClientId`：用户的登录时间（与`LOGON_INFO`中的`LogonTime`相同）。    
- `NameLength` / `ClientName`：用户的账户名（例如`alice`）。    
- **作用**：服务服务器可以快速检查这个明文名称是否与票据中的用户名匹配，作为一个初步的、非加密的完整性检查。   

##### c. `UPN_DNS_INFO`
包含用户的更多标识信息。
- `UpnLength` / `UserPrincipalName`：用户的UPN（例如`alice@corp.com`）。    
- `DnsDomainNameLength` / `DnsDomainName`：用户的完全限定域名（FQDN）（例如`corp.com`）。    
- `Flags`：标志位。    
- **作用**：提供额外的用户身份信息，特别是在跨域或联邦身份验证场景中。    

##### d. `SERVER_CHECKSUM` 和 `PRIVSVR_CHECKSUM`
这是PAC的**防伪标签**，是保证PAC可信度的核心。
- `SERVER_CHECKSUM`：使用**服务服务器的长期密钥**（NTLM Hash）生成的签名。    
- `PRIVSVR_CHECKSUM`：使用**KDC的长期密钥（`KRBtgt`的NTLM Hash）** 生成的签名。    
- **算法**：通常是HMAC，使用MD5或SHA1等算法。    
- **渗透视角**：这是攻击者无法完美伪造的。任何对PAC内容的修改都会导致签名验证失败。黄金票据攻击的局限性正源于此。`PRIVSVR_CHECKSUM`是PAC的“皇帝玉玺”，只有KDC才拥有。
### 核心概念与“票券”
1. **Principal (主体)**：Kerberos系统中被认证的对象，通常是用户或服务。每个主体都有一个唯一的名称，如 `user@DOMAIN.COM` 或 `host/fileserver.domain.com@DOMAIN.COM`。    
2. **Secret Key (密钥)**：    
    - 每个用户和每个服务都与KDC共享一个**长期的秘密密钥**。这个密钥由用户密码派生而来。        
    - **用户的密钥**： `KRBtgt = Hash(Domain SID)` | 用户的密钥： `KRBusr = Hash(password)` |        
    - **服务的密钥**： `KRBsvc = Hash(<service_account_password>)`        
3. **Ticket (票据)**：用于安全传递身份信息的加密数据块。主要有两种：    
    - **TGT (Ticket-Granting Ticket)**：由AS发放的“入场券”，证明用户已成功通过KDC认证，用于向TGS申请其他服务的票据。**这是通往TGS的通行证**。        
    - **ST (Service Ticket)** 或 **TGS Ticket**：由TGS发放的“具体项目门票”，用于访问特定的服务服务器（如CIFS、HTTP、LDAP）。**这是访问具体服务的门票**。        
4. **Authenticator (验证器)**：一个包含客户端身份和时间戳的记录，用会话密钥加密，用于证明票据的发送者就是票据的合法所有者（防止重放攻击）。
### Kerberos认证流程
**第1步：AS-REQ - 客户端请求TGT**  
客户端向KDC的AS发送一个明文请求：“我是用户`alice`，我想申请一个TGT。” 该请求包含一个预认证信息（如加密的时间戳），以防止离线暴力破解。

**第2步：AS-REP - KDC发放TGT**  
AS验证用户`alice`的预认证信息。通过后，AS会生成：
1. **一个随机的`Session Key_1`**（用于客户端与TGS之间的通信）。    
2. **TGT票据本身**。TGT包含`Session Key_1`、用户信息、有效期等，所有这些都用**KDC自己的密钥（`KRBtgt`）** 进行加密。客户端无法解密TGT。AS将这两样东西一起发给客户端：    
	- **A部分**： `{Session Key_1}` 用 **`alice`的密钥（`Hash(alice's password)`）** 加密。    
	- **B部分**： `{TGT}` 用 **`KRBtgt`** 加密。 
客户端收到后，用自己的密码派生的密钥解密A部分，得到`Session Key_1`。它无法解密B部分（TGT），但会保存起来。
**第3步：TGS-REQ - 客户端请求访问服务的ST**  
当客户端想访问一个特定服务（如`cifs/fileserver.domain.com`）时，它需要向KDC的TGS申请ST。它会发送：
1. 之前收到的**TGT**（B部分）。    
2. 一个用`Session Key_1`加密的**Authenticator**（包含客户端ID、时间戳等），用于证明自己是TGT的合法所有者。    
3. 明文的**服务SPN**（如`cifs/fileserver.domain.com`）。    

**第4步：TGS-REP - KDC发放ST**  
TGS收到请求后：
1. 用自己的`KRBtgt`密钥**解密TGT**，取出其中的`Session Key_1`。    
2. 用`Session Key_1`解密**Authenticator**，验证其与TGT中的用户信息是否一致，并检查时间戳以防重放。    
3. 验证通过后，TGS生成：    
    - **一个随机的`Session Key_2`**（用于客户端与服务服务器之间的通信）。       
    - **ST票据**。ST包含`Session Key_2`、用户信息、有效期等，所有这些都用**目标服务的密钥（`Hash(service_account_password)`）** 加密。  
        TGS将这两样东西发给客户端：      
	- **C部分**： `{Session Key_2}` 用 **`Session Key_1`** 加密。   
	- **D部分**： `{ST}` 用 **目标服务的密钥** 加密。   
	客户端收到后，用`Session Key_1`解密C部分，得到`Session Key_2`。它无法解密D部分（ST），但会保存起来。
	
**第5步：AP-REQ - 客户端向服务服务器请求服务**  
客户端现在可以连接目标服务服务器了。它发送：
4. 之前收到的**ST**（D部分）。    
5. 一个用`Session Key_2`加密的**Authenticator**。    

**第6步：AP-REP - 服务服务器验证（可选双向认证）**  
服务服务器收到请求后：
1. 用自己的密钥（`Hash(service_account_password)`）**解密ST**，取出其中的`Session Key_2`。    
2. 用`Session Key_2`解密**Authenticator**，验证用户信息和时间戳。    
3. 验证通过后，即授予客户端访问权限。    
4. （可选）为了证明自己是真正的服务（双向认证），服务服务器可以从Authenticator中取出时间戳，用`Session Key_2`加密后发回给客户端（AP-REP）。客户端解密验证后，即可确认服务器的真实性。
![](attachments/Pasted%20image%2020250821095201.png)
## LDAP协议