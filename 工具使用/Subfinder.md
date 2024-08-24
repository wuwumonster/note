```
Flags:
输入:
  -d, -domain string[]  要查找子域名的域名
  -dL, -list string     包含要进行子域名发现的域名列表的文件
 
来源:
  -s, -sources string[]           用于发现的特定来源（-s crtsh,github）。使用 -ls 显示所有可用来源。
  -recursive                      仅使用能够递归处理子域的来源（例如 subdomain.domain.tld vs domain.tld）
  -all                            使用所有来源进行枚举（速度较慢）
  -es, -exclude-sources string[]  从枚举中排除的来源（-es alienvault,zoomeyeapi）
 
过滤:
  -m, -match string[]   要匹配的子域名或子域名列表（文件或逗号分隔）
  -f, -filter string[]   要过滤的子域名或子域名列表（文件或逗号分隔）
 
速率限制:
  -rl, -rate-limit int  每秒发送的最大HTTP请求数
  -rls value            每秒为四个提供程序发送的最大HTTP请求数（以 key=value 格式，例如 -rls "hackertarget=10/s,shodan=15/s"）
  -t int                用于解析的并发goroutines数（仅在 -active 模式下）（默认 10）
 
更新:
   -up, -update                 更新 subfinder 到最新版本
   -duc, -disable-update-check  禁用自动 subfinder 更新检查
 
输出:
  -o, -output string       要写入输出的文件
  -oJ, -json               以 JSONL(ines) 格式写入输出
  -oD, -output-dir string  要写入输出的目录（仅对 -dL 有效）
  -cs, -collect-sources    在输出中包含所有来源（仅在 -json 模式下有效）
  -oI, -ip                 在输出中包含主机IP（仅在 -active 模式下有效）
 
配置:
  -config string                配置文件路径（默认为 "$CONFIG/subfinder/config.yaml"）
  -pc, -provider-config string  提供程序配置文件路径（默认为 "$CONFIG/subfinder/provider-config.yaml"）
  -r string[]                   逗号分隔的要使用的解析器列表
  -rL, -rlist string            包含要使用的解析器列表的文件
  -nW, -active                  仅显示活动的子域
  -proxy string                 用于 subfinder 的 HTTP 代理
  -ei, -exclude-ip              从域名列表中排除IP地址
 
调试:
  -silent             仅显示输出中的子域名
  -version            显示 subfinder 的版本
  -v                  显示详细输出
  -nc, -no-color      禁用输出中的颜色
  -ls, -list-sources  列出所有可用来源
 
优化:
  -timeout int   在超时之前等待的秒数（默认 30）
  -max-time int  等待枚举结果的分钟数（默认 10）
```