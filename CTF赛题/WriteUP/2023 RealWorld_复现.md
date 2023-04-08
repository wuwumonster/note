# Web
## the_cult_of_8bit
注册登录之后发现有简历post和to do的功能

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