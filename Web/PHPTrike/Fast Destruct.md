## 示例代码
```PHP
<?php

class B {
    public function __call($f,$p) {
        echo "B::__call($f,$p)\n";
    }
    public function __destruct() {
        echo "B::__destruct\n";
    }
    public function __wakeup() {
        echo "B::__wakeup\n";
    }
}

class A {
    public function __destruct() {
        echo "A::__destruct\n";
        $this->b->c();
    }
}
//正常反序列化
$payload = 'O:1:"A":1:{s:1:"b";O:1:"B":0:{}}';
//Fast Destruct
$payload = 'a:2:{i:0;O:7:"classes":0:{}i:1;O:4:"Test":0:{}';  
$payload = 'a:3:{i:0;O:7:"classes":0:{}i:1;O:4:"Test":0:{}}';  
$payload = 'a:2:{i:0;O:7:"classes":0:{}i:1;O:4:"Test":0:{};}';
unserialize($payload);


```

## stdClass和__PHP_Incomplete_Class
所有的类都是`stdClass`类的子类，`stdClass`是所有类的基类

### __PHP_Incomplete_Class特性

如果不指定`__PHP_Incomplete_Class_Name`的话，那么`__PHP_Incomplete_Class`类下的变量在序列化再反序列化之后就会消失，从而绕过某些关键字


## 参考文章
[PHP反序列化小技巧之Fast Destruct · HacKerQWQ's Studio](https://hackerqwq.github.io/2021/08/29/PHP%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%B0%8F%E6%8A%80%E5%B7%A7%E4%B9%8BFast-Destruct/)