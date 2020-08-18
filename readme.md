# 微信聊天记录导出(2020新版)

首先说明，坑的部分主要是数据库破解。

## 1. 本地备份提取聊天记录

这里主要讲小米手机，苹果手机参考https://www.zhihu.com/question/66251440，其他安卓手机可以用模拟器然后root提取。

要导出微信安卓客户端的聊天记录，首先得找到聊天记录的数据库。
安卓客户端的聊天记录储存在私有目录 `/data/data/com.tencent.mm/MicroMsg` 下，这个目录需要root权限才能进去，但是，那样太太太麻烦了，好在我们MI6有本地备份的功能，利用这个功能。我们轻而易举就可以获得数据库。

##### 需要的工具

[此处下载](https://github.com/Heyxk/notes/tree/master/resource/wechat-tools)

1. 首先到手机:设置->更多设置->备份和重置->本地备份 里面点击新建备份，选择软件程序中的微信进行备份，注意只选择微信。

2. 然后到文件管理 `/内部储存设备/MIUI/backup/ALLBackup/` 下将备份的文件夹复制到电脑
3. 然后用任意一种压缩包软件（我用的是7zip）打开这个`com.tencent.mm.bak`文件，并且将`apps\com.tencent.mm\r\MicroMsg\systemInfo.cfg`、`apps\com.tencent.mm\r\MicroMsg\CompatibleInfo.cfg`和`apps\com.tencent.mm\r\MicroMsg\xxxx\EnMicroMsg.db`三个文件解压到电脑上。这里xxxx是一串随机的字母，代表你的微信用户，每个人不一样，一般是最大的那个文件夹，我这里是下图所示文件夹：

![](https://gitee.com/hufanmax/image_bag/raw/master/img/20200816093241.png)

## 2. 破解数据库密码

找到聊天数据库了，但是目前还不能得到聊天记录，因为这个数据库是`sqlcipher`加密数据库，需要密码才能打开。

数据库密码有很多种生成方式：

1. 手机`IMEI`+`uin`(微信用户id `userinformation`) 将拼接的字符串[MD5加密](http://tool.chinaz.com/tools/md5.aspx)取前7位

   > 如`IMEI`为`123456`，`uin`为`abc`，则拼接后的字符串为`123456abc` 将此字符串用[MD5加密](http://tool.chinaz.com/tools/md5.aspx)(32位)后
   >
   > 为`df10ef8509dc176d733d59549e7dbfaf` 那么前7位`df10ef8` 就是数据库的密码，由于有的手机是双卡，有多个`IMEI`，或者当手机获取不到`IMEI`时会用默认字符串`1234567890ABCDEF`来代替，由于种种原因，并不是所有人都能得出正确的密码，此时我们可以换一种方法。

2. 反序列化`CompatibleInfo.cfg`和`systemInfo.cfg`

   > 不管是否有多个`IMEI` ，或者是微信客户端没有获取到`IMEI`，而使用默认字符串代替，微信客户端都会将使用的信息保存在`MicroMsg`文件夹下面的`CompatibleInfo.cfg`和`systemInfo.cfg`文件中，可以通过这两个文件来得到正确的密码，但是这两个文件需要处理才能看到信息。

3. 使用hook方式得到数据库的密码，这个方法最有效[参考](https://blog.csdn.net/qq_24280381/article/details/73521836)

4. 暴力破解



我开始用反序列化：

```bash
javac IMEI.java
java IMEI systemInfo.cfg CompatibleInfo.cfg
```

运行完成后就会得到密码
[参考链接](http://www.intohard.com/article-331-1.html)

但是出现了如下错误：

错误: 找不到或无法加载主类 IMEI 原因: java.lang.ClassNotFoundException: IMEI

于是我换了第一种方法，可是找不到uid

### 寻找uid

uid不是微信号，原来是保存在下面路径：

**/data/data/com.tencent.mm/shared_prefs/auth_info_key_prefs.xml，**

在该文件中，键值“auth_uin”即为该用户的uin。

但是我发现根本没有这个路径，可能是我的手机没有root，于是我把备份的文件解压，在里面搜索这个，终于找到了。

![](https://gitee.com/hufanmax/image_bag/raw/master/img/20200816094803.png)

最终确定uid，然后**MD5（IMEI少一位+uin）的输出字符串作为密码**，取前7位小写，就可以破解数据库了。

得到数据库之后可以分析一下你的聊天记录，顺便制作一个词云来给你的心上人看一下你们都聊了啥:eyes:



参考：

https://zhuanlan.zhihu.com/p/77418711

https://github.com/Heyxk/notes/issues/1

https://www.sohu.com/a/355273307_704736

# 数据分析

下面就是最关键的数据分析。聊天记录包含了非常丰富的数据，这里我只做了两个比较简单的例子，一个是针对时间做聊天时间段分布的统计；一个是针对内容做字符匹配，统计一些高频词汇出现的次数，比如“早安”、“晚安”、“想你”、“爱”等等（你懂的）。

详情见本项目。代码都有注释，我写了一个类把直方图，高频词汇统计，词云等结合起来了。

![](https://gitee.com/hufanmax/image_bag/raw/master/img/Figure_3.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190714130906379.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3hueHlneHA=,size_16,color_FFFFFF,t_70)



参考：https://blog.csdn.net/iphilo/article/details/79052325