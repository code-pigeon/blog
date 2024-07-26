# 【Linux笔记】tar——压缩与解压

## 打包与压缩

#### 打包文件（生成新的tar文件）：
```bash
tar -cf newTar.tar file.txt
```


#### 打包并压缩文件（生成新的.tar.gz文件）：  
```bash
tar -zcf newTar.tar.gz file.txt  
```

> **注**：打包和压缩是不一样的概念
> - gzip这种压缩方式默认只能压缩一个文件，所以当有多个文件需要压缩时，就需要用到把多个文件打包成一个文件，这就是tar -cf打包的作用。打包操作并不涉及压缩。
> - 而tar -zcf实际是两个步骤的结合：
> 	1. 先把多个文件打包成一个.tar文件；
> 	2. 对生成的.tar文件进行压缩；


> **注：** 
> 1. 在敲命令时，生成的文件要手动加后缀名。
> 2. -z表示用gzip压缩算法进行压缩

## 拆包与解压：

#### 拆包（打包的逆过程）.tar文件：
```bash
tar -xf myTar.tar # 默认拆包到当前目录下
```

#### 解压.tar.gz文件：
```bash
tar -zxf myGZ.tar.gz # 同样默认解压到当前目录下
```
#### 解压到指定路径（使用-C选项）：
```bash
tar -zxf myGZ.tar.gz -C /home/user/文档/
```
（假设指定路径为/home/user/文档/）

#### 打印压缩包文件：

打印压缩包中文件列表到终端：
```bash
tar -tf myGZ.tar.gz
```

## 追加：

#### 在（原本已经存在的）.tar文件中添加新文件：
```bash
tar -rf myTar.tar myNewFile.txt
```
#### ~~在.tar.gz文件中添加新文件：~~

>（tar命令不支持这种操作）
> 会出现报错—— *tar：无法更新压缩归档文件* 
> 想要实现该功能只能先解压再压缩回去了。

---

**最后：** 再以上指令中加-v，会在终端输出tar的工作信息，例如：
```bash
tar -zxvf myGZ.tar.gz # v加在f前面即可
```
这样终端就会在压缩时打印压缩的文件名

---
更多高级用法可以参考大佬文章： [# linux压缩打包命令—tar命令](https://zhuanlan.zhihu.com/p/109665217)






