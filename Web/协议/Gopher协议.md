# 简述
Gopher是Internet上一个非常有名的信息查找系统，它将Internet上的文件组织成某种索引，很方便地将用户从Internet的一处带到另一处。在WWW出现之前，Gopher是Internet上最主要的信息检索工具，Gopher站点也是最主要的站点，使用tcp70端口。
**gopher协议支持发出GET、POST请求**：可以先截获get请求包和post请求包，在构成符合gopher协议的请求。gopher协议是ssrf利用中最强大的协议
| 协议 | 支持情况                              |
| ---- | ------------------------------------- |
| PHP  | --wite-curlwrappers且php版本至少为5.3 |
| Java | 小于JDK1.7                            |
| Curl | 低版本不支持                          |
| Perl | 支持                                  |
|   ASP.NET   |                 小于版本3                      |
# 格式
`URL:gopher://<host>:<port>/<gopher-path>_后接TCP数据流`
- gopher的默认端口是70
- 如果发起POST请求，回车换行需要使用%0D%0A，如果多个参数，参数之间&也需要进行URL编码