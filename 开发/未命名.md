
```bash
# 拉取镜像
docker pull portainer/portainer-ce

# 启动镜像
docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v /dockerData/portainer:/data --restart=always --name portainer portainer/portainer-ce:latest
```