# 关于桌面应用与web应用之间的区别的思考
首次编辑：24/3/24/19:41
最后编辑：24/3/24/

## 引子
最近在用tkinter写桌面应用，但怎么写都感觉很别扭，思路永远无法像在写web应用时那么顺畅。
比如我在思考一个方法，让一个自定义的窗口类能拥有一个方便插拔的控件，控件上的按钮点击时，可以像web前端那样携带数据发送一个请求给后端（对应自定义的窗口类），后端返回一个响应给前端（对应方便插拔的控件），再由前端对响应进行处理并渲染页面即可。但似乎这种在web应用中非常容易的事情，在桌面应用中的实现显得很蹩脚。

## 区别在于网络与url接口吗
我一开始想的是，由于桌面应用的“前端”和“后端”之间少了一层网络，所以用不着网络请求这种东西，而网络请求的请求端和接收端所负责的逻辑，大概率与开发者没啥关系（请求端，即前端的请求功能由浏览器完成了，接收端，即后端的接收功能由服务器完成了，应用开发者所做的不过是使用浏览器和服务器框架提供的接口罢了）。所以当在桌面应用中，需要开发者直面请求端和接收端的逻辑，所以从web应用转到桌面应用开发可能会有些不适应。

按照这种思路，只需要将“请求端->网络->接收端->网络->请求端”这样的数据路径改成“请求端->接收端->请求端”即可。

虽然好像有了一点点思路，但是还是有点迷惑，无奈还是去请教了AI。

下面这个例子中，由root窗口充当前端，向后端MyDialog发送数据，然后MyDialog在`handle_data`方法中处理数据，同时返回响应。
```python
class MyDialog:
    def __init__(self, root):
        self.toplevel = Toplevel(root)
        self.label = Label(self.toplevel)

        self.init_ui()

    def init_ui(self):
        self.toplevel.title("我不是主窗口")
        self.toplevel.geometry("500x200+500+500")
        self.label.grid(row = 0, column=0, sticky=(N, W, E, S))

    def handle_data(self, data):
        '''
            处理数据，并返回响应
        '''
        self.label.config(text=data)
        response = "我已经收到消息了"
        return response

    def grid(self):
        self.toplevel.grid()


def send_data(data, receiver):
    res = receiver.handle_data(data)
    print(res)

root = Tk()
m = MyDialog(root)
m.grid()

e = Entry(root)
e.grid(row=0, column =0)
b = Button(root)
b.grid(row=0, column =1)
b.config(text="发送数据")

b.config(command=lambda: send_data(e.get(), m))

root.title("主窗口")
root.geometry("500x200+1000+500")
root.mainloop()
```
这个例子实际上的思路就是把后端MyDialog的`handle_data`暴露给前端root窗口去调用。
想到这里我豁然：这不就是API吗？

至此，一个方便插拔的控件完成了：要使用时，只需要new一个MyDialog对象，然后在按钮按下的事件逻辑中调用一下MyDialog提供的`handle_data`接口即可。

但接着思考我们的主题，总觉得这和web应用的机制的差距不仅仅只是在网络请求这一点上：数据是从root窗口发过去的，root窗口确实收到了响应；MyDialog收到了请求数据，也能进行响应；但毕竟MyDialog也不是个类似服务器的东西，而是类似前端的东西，所以实际上……我们是在两个前端之间通信。

## 