## Nginx缓存
Nginx 在后端 Fastcgi 响应过大 或 请求正文 body 过大时会产生临时文件。如果打开一个进程打开了某个文件，某个文件就会出现在 /proc/PID/fd/ 目录下，我们可以通过重复发包so造成文件缓存，然后用LD_PRELOAD去加载我们这个动态链接库

## 环境变量命令注入

-   `BASH_ENV`：可以在`bash -c`的时候注入任意命令
-   `ENV`：可以在`sh -i -c`的时候注入任意命令
-   `PS1`：可以在`sh`或`bash`交互式环境下执行任意命令
-   `PROMPT_COMMAND`：可以在`bash`交互式环境下执行任意命令
-   `BASH_FUNC_xxx%%`：可以在`bash -c`或`sh -c`的时候执行任意命令


## 相关文章
[我是如何利用环境变量注入执行任意命令 | 离别歌 (leavesongs.com)](https://www.leavesongs.com/PENETRATION/how-I-hack-bash-through-environment-injection.html)