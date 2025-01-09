# 做桌面应用时的一些思考24-3-25
首次编辑：24/3/25/23:13
最后编辑：24/3/25/

## 
这几天都在琢磨tkinter桌面应用，本来想做个类似下面的`Cover`的一个控件。
```python
root = Tk()  # 新建一个应用窗口

c = Cover(root)  # c作为root的子控件
c.grid()  # 将c布局到root窗口中
```
一开始有了一个方案，并测试成功后，想要在自己写的程序中实现的时候，发现提供这样的接口似乎有点没必要。我想到了诸如Windows桌面中的那种message box式的接口。
```
# 这是一段伪代码
response = messageBox("这是提示消息")
```
调用`messageBox`接口时弹出一个窗口，然后假设有确定和取消两个按钮，用户按下后分别返回1和0，开发者就可以根据返回的response（1或者0）处理不同的逻辑。

然而我在tkinter中做了这么一个接口之后，还是出现了些问题。
```python
def messageBox(canvas, *, message="default message"):
	def handle_click_event(event):
		# 点击按钮后发生的事情
		...

	btn = canvas.create_rectangle(...)  # 创建一个正方形，用作按钮
	canvas.tag_bind(btn, '<Button-1>', handle_click_event)  # 按钮被点击时，触发handle_click_event

	canvas.create_text(..., text=message)

	return "yes"


root = Tk()
canvas = Canvas(root)

response = messageBox(canvas, message="哈哈")
print(response)

canvas.grid()
root.mainloop()
```
理论上来说，因为点击按钮之后，触发的函数是`handle_click_event`，所以返回值应该由`handle_click_event`返回。
但有三个问题：
1. 主程序中直接调用的是`messageBox`这个函数，所以收到的返回值也是`messageBox`返回的，而不是`handle_click_event`。
2. `handle_click_event`这个函数的返回值无法被获取。这是事件绑定方法的限制，不知道是不是所有的桌面应用框架都是这样。
3. `messageBox`被调用时，程序并不会阻塞等待用户点击，而是直接往下执行，因此在用户点击之前，`messageBox`就已经返回了返回值给response，无论`handle_click_event`是什么逻辑，都无法将用户点击情况传递给response。

现在解决思路有两个：
1. 若要保留`messageBox`这样的接口，那么必须让此接口被调用时，主程序能够被阻塞，这样主程序就能等待`messageBox`被用户点击，从而得到用户的点击情况。这也是许多桌面应用框架的对话框接口的做法。
2. 放弃`messageBox`这样的接口，将用户的点击情况保存在某个对话框和主程序都能访问的变量中，这样待用户点击完之后，主程序再访问该变量，就能知道用户的点击情况是什么了。

第一个思路在主要逻辑上显得很简单，也能让代码的耦合度降低，得到的`messageBox`接口插拔十分方便。但麻烦之处在于由于阻塞的存在，如果框架本身的接口没有阻塞功能，自己实现的话就需要使用多线程或者协程这样的技术了。而按道理应该是使用协程，但协程的书写却比多线程麻烦得多。

第二个思路的耦合度比较高，做起来也最好是使用面向对象技术。