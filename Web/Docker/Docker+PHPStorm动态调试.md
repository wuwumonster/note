## 配置
### Xdebug 配置
#### phpinfo确定版本
phpinfo内容放入下面网站
[Xdebug: Support — Tailored Installation Instructions](https://xdebug.org/wizard)
如果挂载了目录的话可以`php -r 'phpinfo();' > phpinfo.txt`直接粘贴
网站分析后会给出下面的步骤

![](attachments/Pasted%20image%2020230422172358.png)

下载后扔到目录里 或者直接执行 wget https://xdebug.org/files/xdebug-3.1.6.tgz

可能没有php.ini
![](attachments/Pasted%20image%2020230422173212.png)
这是生产和开发两个环境备份后选择一个改为php.ini即可
#### Xdebug2
php.ini配置
```
[xdebug] 
zend_extension="<path to xdebug extension>" 
xdebug.remote_enable=1 
xdebug.remote_host=127.0.0.1 
xdebug.remote_port="9000"
```

>In PHP 5.3 and later, you need to use only `zend_extension`, not `zend_extension_ts`, `zend_extension_debug`, or `extension`

docker下载
```dockerfile
RUN pecl install xdebug \ 
&& docker-php-ext-enable xdebug 
&& echo "xdebug.remote_enable=on" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \ 
&& echo "xdebug.remote_host = host.docker.internal" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
```
#### Xdebug3
php.ini配置
```
[xdebug]
zend_extension="<path to xdebug extension>"
xdebug.mode = debug 
xdebug.start_with_request = yes 
xdebug.client_port = 9003
xdebug.client_host=127.0.0.1 
xdebug.remote_handler=dbgp 
xdebug.idekey=PHPSTORM 
```
docker下载
```dockerfile
RUN pecl install xdebug \  
&& docker-php-ext-enable xdebug \  
&& echo "xdebug.mode=debug" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \  
&& echo "xdebug.client_host = host.docker.internal" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
```

### PHPStorm配置
端口设置

![](attachments/Pasted%20image%2020230422170458.png)

IDE key设置

![](attachments/Pasted%20image%2020230422170556.png)
## 参考文章
[Configure Xdebug | PhpStorm Documentation (jetbrains.com)](https://www.jetbrains.com/help/phpstorm/configuring-xdebug.html)