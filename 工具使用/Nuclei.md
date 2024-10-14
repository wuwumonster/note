## 常用选项
|**选项标签**|**描述信息**|**使用样例**|
|---|---|---|
|-c|并发请求数（默认为10）|nuclei -c 100|
|-l|要运行模板的URL列表|nuclei -l urls.txt|
|-t|需跨主机检测的模板输入文件|nuclei -t git-core.yaml|
|-t|需跨主机检测的模板输入文件|nuclei -t "path/*.yaml"|
|-nC|输出中不使用高亮颜色|nuclei -nC|
|-o|保存输出结果文件（可选）|nuclei -o output.txt|
|-silent|在输出中仅显示找到的结果|nuclei -silent|
|-retries|重试失败请求的次数（默认值1）|nuclei -retries 1|
|-timeout|超时前等待的秒数（默认为5）|nuclei -timeout 5|
|-v|显示详细输出|nuclei -v|
|-version|显示Nuclei版本|nuclei -version|
|-proxy-url|代理URL|nuclei -proxy-url [http://user:pass@this.is.a.proxy:8080](http://this.is.a.proxy:8080/)|
|-proxy-socks-url|代理Socks URL|nuclei -proxy-socks-url socks5://user:[pass@this.is.a.proxy.socks](mailto:pass@this.is.a.proxy.socks):9050|

```SHELL
# 单一模板扫描
nuclei -l urls.txt -t git-core.yaml -o results.txt
# 多模板扫描
nuclei -u https://example.com -t cves/ -t exposures/
```

## 扫描模板库
[projectdiscovery/nuclei-templates: Community curated list of templates for the nuclei engine to find security vulnerabilities. (github.com)](https://github.com/projectdiscovery/nuclei-templates)

### 目录结构
```
nuclei-templates/
├── CODE_OF_CONDUCT.md  # 行为准则文件
├── CONTRIBUTING.md     # 贡献指南文件
├── LICENSE.md          # 项目许可证文件
├── README.md           # 项目介绍和使用说明
├── SECURITY.md         # 安全政策文件
├── templates/
│   ├── cves/
│   ├── dns/
│   ├── exposures/
│   ├── files/
│   ├── headless/
│   ├── panels/
│   ├── ssl/
│   ├── vulnerabilities/
│   └── workflows/
└── tools/
```

