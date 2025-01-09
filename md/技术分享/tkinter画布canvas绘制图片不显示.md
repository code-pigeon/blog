# tkinter画布canvas绘制图片不显示
首次编辑：24/3/22/13:59  
最后编辑：24/3/22/14:08

## 原因与解决办法
在canvas中创建图片一般如下：
```python
from tkinter import *
root = Tk()
c = Canvas(root)
# 在canvas中创建图片
image = PhotoImage(file="img/熊猫人.png")
canvas.create_image(100, 100, image = image)

c.grid()
root.mainloop()
```
但如果将创建图片的步骤封装在函数中：
```python
from tkinter import *

def func(canvas):
	# 在canvas中创建图片
    image = PhotoImage(file="img/熊猫人.png")
    canvas.create_image(100, 100, image = image)

root = Tk()
c = Canvas(root)
c.grid()

func(c)
root.mainloop()
```
会发现图片无法显示。

### 原因
这是由于image这个变量定义于函数func中，属于局部变量，在函数结束之后，变量就被垃圾回收了。
而`create_image`所指定的`image`参数却直接与这个被回收的变量相关，因此图片无法显示。

### 解决办法
只要保证image这个变量不被垃圾回收即可。
按照这个思路可以采取的办法有很多，比如将image声明为全局变量。
```python
def func(canvas):
	# 在canvas中创建图片
	global image
    image = PhotoImage(file="img/熊猫人.png")
    canvas.create_image(100, 100, image = image)
```

如果是在对象的方法中创建这个图片，则可以把`image`变量设置为成员变量。
