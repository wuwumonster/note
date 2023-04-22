## 配置
### Xdebug 配置
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
xdebug.mode=debug 
xdebug.client_host=127.0.0.1 
xdebug.client_port="9003"
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