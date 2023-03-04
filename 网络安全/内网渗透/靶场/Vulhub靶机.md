

### attack2

nmap扫描

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled.png)

主页信息

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%201.png)

dirsearch

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%202.png)

cupp制作字典

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%203.png)

密码结果

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%204.png)

ssh进去直接su root

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%205.png)

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%206.png)

**************attack3**************

namp扫描

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%207.png)

smb空口令

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%208.png)

进入share文件夹，网站为wp

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%209.png)

获取配置文件

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%2010.png)

部分似乎存在混淆

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%2011.png)

但是拿到了数据库的一些信息

同时dirsearch的扫描结果

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%2012.png)

可以进入数据库

但是不太能写shell，用同样密码进入后台

直接写一句话木马，蚁剑连接

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%2013.png)

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%2014.png)

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%2015.png)

**sql注入get**

很明显

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%2016.png)

RCE

![Untitled](Vulhub%20890f01955a4f4345beea2c751d36b3c5/Untitled%2017.png)