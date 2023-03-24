## 配置
### 不小于10的密码长度&三次尝试
```
password    required    pam_pwquality.so try_first_pass local_user_only retry=3 authtk_type= minlen=10
password    sufficient  pam_unix.so sha512 shadow nullok try_first_pass use_authtok
password    required    pam_deny.so
```

### 强密码
```
password    required    pam_pwquality.so try_first_pass local_user_only retry=3 authtk_type= minlen=10 lcredit=-1 ucredit=-1 ocredit=-1 dcraedit=-1
password    sufficient  pam_unix.so sha512 shadow nullok try_first_pass use_authtok
password    required    pam_deny.so
```


### 三次失败锁定1分种
```conf
auth           required       pam_faillock.so  preauth_audit_deny=2 unlock_time=60
auth           [default=die]      pam_faillock.so  audit deny=2 unlock_time=60
account        required       pam_faillock.so
```
## 参考链接
[PAM](PAM.md)

[Linux-PAM 中文文档 - Linux-PAM 1.1.2 Developers' Guide | Docs4dev](https://www.docs4dev.com/docs/zh/linux-pam/1.1.2/reference/)