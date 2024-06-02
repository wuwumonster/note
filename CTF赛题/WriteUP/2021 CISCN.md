## upload
```PHP
<?php  
if (!isset($_GET["ctf"])) {    
	highlight_file(__FILE__);  
    die();  
}  
  
if(isset($_GET["ctf"]))    
$ctf = $_GET["ctf"];  
  
if($ctf=="upload") {  
    if ($_FILES['postedFile']['size'] > 1024*512) {  
        die("这么大个的东西你是想d我吗？");  
    }    $imageinfo = getimagesize($_FILES['postedFile']['tmp_name']);  
    if ($imageinfo === FALSE) {  
        die("如果不能好好传图片的话就还是不要来打扰我了");  
    }  
    if ($imageinfo[0] !== 1 && $imageinfo[1] !== 1) {  
        die("东西不能方方正正的话就很讨厌");  
    }    $fileName=urldecode($_FILES['postedFile']['name']);  
    if(stristr($fileName,"c") || stristr($fileName,"i") || stristr($fileName,"h") || stristr($fileName,"ph")) {  
        die("有些东西让你传上去的话那可不得了");  
    }    $imagePath = "image/" . mb_strtolower($fileName);  
    if(move_uploaded_file($_FILES["postedFile"]["tmp_name"], $imagePath)) {  
        echo "upload success, image at $imagePath";  
    } else {  
        die("传都没有传上去");  
    }  
}
```

example.php
```php
<?php  
if (!isset($_GET["ctf"])) {    
	highlight_file(__FILE__);  
    die();  
}  
  
if(isset($_GET["ctf"]))    
	$ctf = $_GET["ctf"];  
  
if($ctf=="poc") {    
	$zip = new \ZipArchive();    
	$name_for_zip = "example/" . $_POST["file"];  
    if(explode(".",$name_for_zip)[count(explode(".",$name_for_zip))-1]!=="zip") {  
        die("要不咱们再看看？");  
    }  
    if ($zip->open($name_for_zip) !== TRUE) {  
        die ("都不能解压呢");  
    }  
  
    echo "可以解压，我想想存哪里";    
	    $pos_for_zip = "/tmp/example/" . md5($_SERVER["REMOTE_ADDR"]);    
		$zip->extractTo($pos_for_zip);    
		$zip->close();    
		unlink($name_for_zip);    
		$files = glob("$pos_for_zip/*");  
    foreach($files as $file){  
        if (is_dir($file)) {  
            continue;  
        }        
        $first = imagecreatefrompng($file);        
        $size = min(imagesx($first), imagesy($first));        
        $second = imagecrop($first, ['x' => 0, 'y' => 0, 'width' => $size, 'height' => $size]);  
        if ($second !== FALSE) {
	        $final_name = pathinfo($file)"basename"];            
	        imagepng($second, 'example/'.$final_name);            
	        imagedestroy($second);  
        }        
        imagedestroy($first);        
        unlink($file);  
    }  
  
}
```

构造zip包内有图片马即可
i的过滤利用mb_strtolower

![](attachments/Pasted%20image%2020240401094521.png)

用`%c4%b0`代替`İ`字符，绕过i的限制上传zip文件

制作图片马

![](attachments/Pasted%20image%2020240401103414.png)

修改原payload，虽然有报错但是能生成

```
#define width 1 
#define height 1
```
绕过宽高检查

![](attachments/Pasted%20image%2020240401105522.png)


访问解压

![](attachments/Pasted%20image%2020240401105642.png)

flag藏在etc下



