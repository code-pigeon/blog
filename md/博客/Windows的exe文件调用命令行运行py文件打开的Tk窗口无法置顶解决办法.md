# Windows的exe文件调用命令行运行py文件打开的Tk窗口无法置顶解决办法
首次编辑：24/3/5/16:17  
最后编辑：24/3/5

## 引子
用Tkinter写了一个小游戏，要打包给没有编程基础的人玩。因为大家早已习惯了一件事：只有exe文件才可以双击运行，遂决定编译一个exe文件，在exe文件中调用命令`python myGame.py`，即可以运行该py文件。
但发现直接在cmd下执行该命令时，弹出的Tk窗口会自动置于所有已打开的窗口之上，且点击其他窗口时可以顺利使其他窗口置顶。但通过双击exe文件打开的Tk窗口却会位于资源管理器窗口之下。

## 尝试过程
### 1
一开始是直接在py代码中将Tk窗口置顶：
```python
import tkinter
root = tkinter.Tk()
root.wm_attributes('-topmost', True)  # 窗口置顶

 # 其它代码……
```
但这样也有问题：无论如何点击其他窗口，Tk窗口都位于其他窗口之上。

### 2
后来想着，先置顶再取消置顶不就行了？
```python
import tkinter
root = tkinter.Tk()
root.wm_attributes('-topmost', True)  # 窗口置顶
root.wm_attributes('-topmost', False)  # 窗口取消置顶
# 其它代码
```
但还是太天真了，并没有想象中的效果，这样写的话就跟没写这两句置顶操作的语句一样，Tk窗口依旧藏在资源管理器窗口之后，可能遇到这两个语句前后接在一起python会优化什么的吧。

### 3
要先说明的是，在py的代码中，是有对Tk窗口的位置进行调整的。就像这样：
```python
# 设置窗口尺寸为100x100，位于（0，0）坐标处
root.geometry("100x100+0+0")
```

基于前一种方式的失利，我又想了一种方式，既然“置顶”和“取消置顶”紧贴着不行，那隔远一点兴许可以吧？
于是如下面的方式调整了代码顺序：
```python
import tkinter
root = tkinter.Tk()
root.wm_attributes('-topmost', True)  # 窗口置顶

 # 其它代码……

root.geometry("100x100+0+0")  # 设置窗口大小和位置

# 其它代码……

root.wm_attributes('-topmost', False)  # 窗口取消置顶

# 其它代码……
```
结果是，窗口确实置顶了，但位置跑偏了。ChatGPT说“当将窗口置顶或取消置顶时，窗口的位置可能会发生变动”。可真麻烦。

### 4
后来又马上想到了，要是把“取消置顶”的代码放在调整窗口大小和位置之前，那就算它再怎么跑偏位置，最后都会被调整回来了。于是一个奇怪的解决方案诞生了。

## 解决方案
先让Tk窗口置顶，再在一定量的代码之后把Tk窗口取消置顶，最后再调整窗口的大小和位置。如下所示：
```python
import tkinter
root = tkinter.Tk()
root.wm_attributes('-topmost', True)  # 窗口置顶

 # 其它代码……

root.wm_attributes('-topmost', False)  # 窗口取消置顶

root.geometry("100x100+0+0")  # 设置窗口大小和位置

# 其它代码……
```



## 参考
[给GCC编译出来的可执行文件添加图标](https://blog.csdn.net/yanhanhui1/article/details/110238429)
[PW系列 | 用windres 编译.rc 资源文件](https://blog.csdn.net/big_cheng/article/details/127183433#Original)
