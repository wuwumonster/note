## 环境搭建
### Tabby

[wh1t3p1g/tabby: A CAT called tabby ( Code Analysis Tool ) (github.com)](https://github.com/wh1t3p1g/tabby)

完成下载后在Idea里面自己去编译一个tabby的jar包，jdk8u版本高一些会比较好
- gradle Tasks
- gardle clean
- gardle bootjar

细节在文档里面有，对应的apoc的jar包在里面翻找对应的releases

#### 导出依赖jar包
**dependency:copy-dependencies -DoutputDirectory=lib**