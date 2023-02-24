## 名词

**镜像(image)**

-   Docker镜像就好比是一个模板，可以通过这个模板来创建容器服务，tomcat镜像 ===> run ===> tomcat01容器， 通过这个镜像可以创建多个容器（最终服务运行或者项目运行就是在容器中的）

**容器(container)**

-   Docker利用容器技术，独立运行或者一组应用，通过镜像来创建
-   启动，停止，删除，基本命令
-   容器可理解为一个建议的linux系统

**仓库(repository)**

-   存放镜像的地方
-   Docker Hub
-   阿里云等也有容器服务

## 仓库设置

**官方**

$ sudo yum-config-manager \

--add-repo \

[https://download.docker.com/linux/centos/docker-ce.repo](https://download.docker.com/linux/centos/docker-ce.repo)

**阿里云**

$ sudo yum-config-manager \

--add-repo \

[http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo](http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo)

**清华大学**

$ sudo yum-config-manager \

--add-repo \

[https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/centos/docker-ce.repo](https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/centos/docker-ce.repo)

****安装 Docker Engine-Community****

`$ sudo yum install docker-ce docker-ce-cli containerd.io`

## Docker常用命令

### 帮助

docker version → docker版本信息

docker info → 系统级别信息，包括镜像和容器的数量

docker 命令 —help

### 镜像命令

docker images 查看所有本地主机上的镜像

docker search 查找镜像 可选—filter=STARS=3000#搜索出的镜像大于3000的

docker pull 镜像名[:tag}→下拉镜像 # 不选择tag，默认为latest

docker rmi 删除镜像

### 容器命令

docker run [可选参数] image

# 参数

-   —name=”Name” 容器名字 用来区别容器
-   -d 后台方式运行
-   -it 交互方式运行，进入容器查看内容
-   -p 指定容器端口
    -   -p ip:主机端口：容器端口
    -   -p 主机端口：容器端口
-   exit 从容器退回主机

docker ps 命令

`#列出当前正在运行的容器`

`-a #列出正在运行的容器包括历史容器`

-n=?#显示最近创建的容器

`-q #只显示当前容器的编号`

**退出容器**

exit → 退出容器并关闭

Ctrl + P + Q → 容器不关闭退出

**删除容器**

`docker rm -f 容器id #删除指定容器`

`docker rm -f $(docker ps -aq) #删除所有容器`

`docekr ps -a -q|xarg docker rm -f #删除所有容器`

**启动和停止容器**

`docker start 容器id #启动容器`

`docker restart 容器id #重启容器`

`docker stop 容器id #停止当前正在运行的容器`

`docker kill 容器id #强制停止当前的容器`

### 其他

**查看日志**

`docker logs -tf —tail number 容器id`

`#显示日志`

`—tf → 显示日志`

`—tail number →显示日志条数`

**查看镜像的元数据**

`docker inspect 容器id`

**进入当前正在运行的容器**

`docker exec -it 容器id /bin/bash`

`docker attach 容器id`

**从容器拷贝文件到主机**

`docker cp 容器id:容器内路径 目的地主机`

**可视化**

`docker run -d -p 8088:9000 —restart=alway -v /var/ran/docker.sock:/var/run/docker.sock —priveged=true portainer`
外网访问http://ip:8088

# DockerFile

**DockerFile构建流程**

-   编写一个dockerfile文件
-   docker build构建成为一个镜像
-   docker run 运行镜像
-   docker push 发布镜像

## DockerFile的构建过程

### 基础知识：

-   每个关键字（指令）都必须是大写
-   执行从上到下顺序执行
-   # 表示注释
-   每个指令都会创建提交一个新的镜像层，并提交

```docker
FROM            # 基础镜像，一切从这里开始构建
MAINTAINER      # 镜像是谁写的， 姓名+邮箱
RUN             # 镜像构建的时候需要运行的命令
ADD             # 步骤， tomcat镜像， 这个tomcat压缩包！添加内容
WORKDIR         # 镜像的工作目录
VOLUME          # 挂载的目录
EXPOSE          # 保留端口配置
CMD             # 指定这个容器启动的时候要运行的命令，只有最后一个会生效可被替代
ENTRYPOINT      # 指定这个容器启动的时候要运行的命令， 可以追加命令
ONBUILD         # 当构建一个被继承DockerFile 这个时候就会运行 ONBUILD 的指令，触发指令
COPY            # 类似ADD, 将我们文件拷贝到镜像中
ENV             # 构建的时候设置环境变量！
```

### 换源

**ubuntu**

```docker
RUN sed -i s/archive.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list
&& sed -i s/security.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list
&& apt-get update && apt-get upgrade

```

**pip3**

```docker
pip install -i <https://pypi.tuna.tsinghua.edu.cn/simple> pip -U # 将 pip 升级到最新版本
pip config set global.index-url <https://pypi.tuna.tsinghua.edu.cn/simple>

```

**远程调试**

```docker
#安装 xdebug 扩展 并开启
RUN pecl install xdebug && \\
docker-php-ext-enable xdebug
```

[start.sh](http://start.sh)

```bash
#配置 Xdebug
echo "xdebug.client_host = host.docker.internal" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
echo "xdebug.client_port = 9003" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
echo "xdebug.mode = debug" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
echo "xdebug.max_nesting_level = 1000" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
echo "xdebug.discover_client_host = true" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
#重启 apache ssh
service apache2 restart
```