# Windows将多个图标编译为dll
首次编辑：2024/7/18/9:52
最后编辑：2024/7/18/10:21

## 方法
### 工具
- MinGW

### 步骤
假如这是文件夹的内容：
```
./
	dog.ico
	cat.ico
	music.ico
	tree.ico
```

首先新建一个`icon.rc`文件，内容为：
```
dog		 ICON	dog.ico
cat		 ICON	cat.ico
music	 ICON	music.ico
tree	 ICON	tree.ico
```

然后在命令行下输入：
```bash
windres -i icon.rc -o icon.o --use-temp-file
gcc -shared icon.o -o icon.dll
```

得到的`icon.dll`中就包含有我们想要放入的`.ico`文件了。

## 使用这个dll文件在windows下自定义文件夹图标
这个dll的一个用处就是拿来更换文件夹/快捷方式的图标了，这也是我挖掘这个方法的原因。

右键点击一个快捷方式，选择“属性”，在属性窗口中点击“更改图标”，可以看到系统中有个`imageres.dll`中带有很多图标。
![更改图标](../media/image/article/Snipaste_2024-07-18_10-08-07.png)

点击“浏览”，然后找到我们编译好的`icon.dll`，在下面的选择框中就会出现我们编译进去的图标。
![选择图标](../media/image/article/Snipaste_2024-07-18_10-18-51.png)

> 当然，直接选择一个`.ico`文件也是可以的，并不一定非要`.dll`文件。