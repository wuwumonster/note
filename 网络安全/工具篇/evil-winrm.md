## 简介
evil-winrm是Windows远程管理(WinRM) Shell的终极版本。

Windows远程管理是“WS 管理协议的 Microsoft 实施，该协议是基于标准 SOAP、不受防火墙影响的协议，允许不同供应商的硬件和操作系统相互操作。而微软将其包含在他们的系统中，是为了便于系统管理员在日常工作中，远程管理服务器，或通过脚本同时管理多台服务器，以提高他们的工作效率。

此程序可在启用此功能的任何Microsoft Windows服务器上使用（通常端口为5985），当然只有在你具有使用凭据和权限时才能使用。因此，我们说它可用于黑客攻击的后利用/渗透测试阶段。相对于攻击者来说，这个程序能为他们提供更好更简单易用的功能。当然，系统管理员也可以将其用于合法目的，但其大部分功能都集中于黑客攻击/渗透测试。
## 帮助
```SHELL
Evil-WinRM shell v3.7

Usage: evil-winrm -i IP -u USER [-s SCRIPTS_PATH] [-e EXES_PATH] [-P PORT] [-a USERAGENT] [-p PASS] [-H HASH] [-U URL] [-S] [-c PUBLIC_KEY_PATH ] [-k PRIVATE_KEY_PATH ] [-r REALM] [--spn SPN_PREFIX] [-l]
    -S, --ssl                        Enable ssl
    -a, --user-agent USERAGENT       Specify connection user-agent (default Microsoft WinRM Client)
    -c, --pub-key PUBLIC_KEY_PATH    Local path to public key certificate
    -k, --priv-key PRIVATE_KEY_PATH  Local path to private key certificate
    -r, --realm DOMAIN               Kerberos auth, it has to be set also in /etc/krb5.conf file using this format -> CONTOSO.COM = { kdc = fooserver.contoso.com }
    -s, --scripts PS_SCRIPTS_PATH    Powershell scripts local path
        --spn SPN_PREFIX             SPN prefix for Kerberos auth (default HTTP)
    -e, --executables EXES_PATH      C# executables local path
    -i, --ip IP                      Remote host IP or hostname. FQDN for Kerberos auth (required)
    -U, --url URL                    Remote url endpoint (default /wsman)
    -u, --user USER                  Username (required if not using kerberos)
    -p, --password PASS              Password
    -H, --hash HASH                  NTHash
    -P, --port PORT                  Remote host port (default 5985)
    -V, --version                    Show version
    -n, --no-colors                  Disable colors
    -N, --no-rpath-completion        Disable remote path completion
    -l, --log                        Log the WinRM session
    -h, --help                       Display this help message

```