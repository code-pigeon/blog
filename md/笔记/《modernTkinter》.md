# 4. A First (Real) Example
## 4.3 Step-by-Step Walkthrough
### Incorporating Tk
一个Tk程序首先需要包含两个模块：
```python
from tkinter import *  # 加载Tk到系统
from tkinter import ttk  # ttk是tkinter的子模块，它实现了Tk8.5新增的“主题控件”
```

### Setting up the Main Application Window
接下来需要设置应用的主窗口，并设置窗口名：
```python
root = Tk()
root.title("Feet to Meters")
```

### Creating a Content Frame
接着创建一个放置控件的框架（Frame）
```python
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1) 
```
第一行：新建一个框架（但此时还没有被放置到主窗口中），边距为“3 3 12 12”（上左下右）。
第二行：`grid`将`mainframe`放置在`root`窗口中第0列和第0行，`sticky=(N, W, E, S)`表示水平和竖直都居中。
第三、四行：用来设置`root`窗口的列和行的权重，以便在窗口大小发生变化时，`mainframe`可以自适应地调整大小。`weight=1`表示该行/列的可伸缩性比重是1，如果窗口大小改变，会根据比重分配额外的空间。

### Creating the Entry Widget
第一个控件为文本输入框，在框中输入待转化的`feet`值。
```python
feet = StringVar()
feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)  # 第一个参数指定了输入框的父空间，此处为mainframe
feet_entry.grid(column=2, row=1, sticky=(W, E))  # 将其放在框架的第3列第2行。
```

### Creating the Remaining Widgets
```python
meters = StringVar()
ttk.Label(mainframe, textvariable=meters).grid(column=2,
row=2, sticky=(W, E))
ttk.Button(mainframe, text="Calculate",
command=calculate).grid(column=3, row=3, sticky=W)
ttk.Label(mainframe, text="feet").grid(column=3, row=1,
sticky=W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1,
row=2, sticky=E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2,
sticky=W)
```

### Adding Some Polish
```python
for child in mainframe.winfo_children(): 
	child.grid_configure(padx=5, pady=5)  # 为网格中的控件添加边距
	feet_entry.focus()  # 使程序打开时，输入框处于激活状态
	root.bind("<Return>", calculate)  # 将回车键与calculate函数绑定
```

### Performing the Calculation
```python
def calculate(*args):
	try:
		value = float(feet.get())
		meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)  # 乘10000.0再除以10000.0是为了规避浮点数的舍入问题
	except ValueError:
		print("错了！")
```

# 5. Tk Concepts
## 5.1. Widgets
### Creating Widgets
每个控件都是一个python对象。
每个控件的初始化函数都有一个父控件参数（显然，此参数用于指定父控件）——根窗口除外。
例如：
```python
root = Tk()
content = ttk.Frame(root)
button = ttk.Button(content)
```
> If you sneak a peek at how Tcl manages widgets, you'll see each widget has a specific pathname; you'll also see this pathname referred to in Tk reference documentation. Tkinter hooses and manages all these pathnames for you behind the scenes, so you should never have to worry about them. If you do, you can get the pathname from a widget by calling `str(widget`).

### Configuration Options
每个控件都有一些配置选项，它们决定了控件的外观和行为。
配置选项有多少取决于具体的控件——当然，不同控件拥有很多共同的配置选项。
配置选项可以在控件第一次创建的时候设定，并且可以在这之后获取这些配置的信息，并且除极少数控件外，配置可以在创建之后修改。

若不清楚控件提供了哪些配置选项，可以通过以下方法查询：
```python
button = ttk.Button(root, text="Hello", command="buttonpressed")  # 创建控件
button['text']  # 获取text选项的值
button.configure('text')  # 获取text选项的所有信息
'''
这将返回类似('text', 'text', 'Text', '', 'Hello')的文本
其分别对应(选项名，在数据库中的选项名，选项的类别，选项的默认值，选项的值)
“选项的默认值”指你不设定选项值时该选项的值
通常只需要关注“选项名”和“选项的值”就行了
'''

button.configure()  # 获取控件所有选项的信息

button['text'] = 'goodbye'  # 修改text选项的值为‘goodbye’
button.configure(text='goodbye')  # 同上

```

### Widget Introspection
关于控件的信息，可以参考[winfo](https://tkdocs.com/man/winfo)。
下面是一个小例子，它通过控件的`winfo_children`方法来遍历控件的层级关系：
```python
def print_hierarchy(w, depth=0):
	print(' '*depth + w.winfo_class() + ' w=' +
		str(w.winfo_width()) + ' h=' + str(w.winfo_height()) + ' x=' +
		str(w.winfo_x()) + ' y=' + str(w.winfo_y()))
	for i in w.winfo_children():
	print_hierarchy(i, depth+1)
print_hierarchy(root)

```

一些比较有用的方法：
- winfo_class：获得控件类名
- winfo_children：获得所有子控件构成的列表
- winfo_parent：获得父控件
- winfo_toplevel：获得祖宗控件
- winfo_width, winfo_height：控件目前的宽度、高度（在控件显示于屏幕之前不会返回正确的数字）
- winfo_reqwidth, winfo_reqheight：the width and height the widget requests of the geometry manager (more on this shortly)
- winfo_x, winfo_y：the position of the top-left corner of the widget relative to its parent
- winfo_rootx, winfo_rooty：the position of the top-left corner of the widget relative to the entire screen
- winfo_vieweable：whether the widget is displayed or hidden (all its ancestors in the hierarchy must be viewable for it to be viewable)

## 5.2. Geometry Management
创建控件时，控件并不会直接显示在屏幕上，Geometry Management表示的便是将控件显示在屏幕某位置上的操作。
在前面的例子中，`grid`就是一种Geometry Management。Tk有很多种Geometry Management，但`grid`是最有用的。

## 5.3. Event Handling
Tk运行着一个用于接收操作系统事件（event）的事件循环（event loop）。事件的类型有鼠标点击、键盘按下等。

### Command Callbacks
按钮（button）控件被按下所触发的效果可以通过Command选项来设置：
```python
def calculate(*args):
	...
ttk.Button(mainframe, text="Calculate", command=calculate)
```

### Binding to Events
对于一些无法用`command`选项来设置效果的事件，可以通过`bind`来实现触发效果与事件的绑定。
```python
from tkinter import *
from tkinter import ttk
root = Tk()
l =ttk.Label(root, text="Starting...")
l.grid()
l.bind('<Enter>', lambda e: l.configure(text='Moved mouse inside'))
l.bind('<Leave>', lambda e: l.configure(text='Moved mouse outside'))
l.bind('<ButtonPress-1>', lambda e: l.configure(text='Clicked left mouse button'))
l.bind('<3>', lambda e: l.configure(text='Clicked right mouse button'))
l.bind('<Double-1>', lambda e: l.configure(text='Double clicked'))
l.bind('<B3-Motion>', lambda e: l.configure(text='right button drag to %d,%d' % (e.x, e.y)))
root.mainloop()
```

`<ButtonPress>`是一个按钮按下的事件，而`<ButtonPress-1>`中的`-1`表示的是鼠标的左键，所以`<ButtonPress-1>`事件表示的事件为鼠标左键按下按钮。`-1`在此被称为“event detail”（事件细节）。
`<3>`事件实际上是`<ButtonPress-3>`事件的缩写，表示右键按下按钮。
`<Double-1>`表示鼠标左键双击按钮（`<Double-ButtonPress-1>`的缩写），`Double`用于表示两次点击。
`<B3-Motion>`中的`Motion`表示鼠标移动事件，但前面的`B3`限制了该事件只在鼠标右键按下的时候会触发。这行代码也展示了事件参数（e）的使用方法，`e.x`和`e.y`分别为事件触发时鼠标的横纵坐标。在事件触发时，很多关于鼠标键盘等的参数会被传递到事件参数e当中。

### Multiple Bindings for an Event
控件不仅可以绑定单个事件，还可以绑定多个事件。
例如`<KeyPress-A><KeyPress-B>`表示的事件为按键A和B同时按下，也可以使用缩写`<ab>`。
> 实际测试的时候发现`<ab>`这种写法会出错。同时`<KeyPress-A>`也只对应大写的A，小写的a无效。

Less commonly, you can create event bindings that are triggered when a matching event occurs anywhere in the application, or even for events received by any widget of a given class, e.g., all buttons.
> More than one binding can fire for an event. This keeps event handlers concise and limited in scope, meaning more modular code. For example, the behavior of each widget class in Tk is itself defined with script-level event bindings. These stay separate from event bindings in your application. Event bindings can also be changed or deleted. They can be modified to alter event handling for widgets of a certain class or parts of your application. You can reorder, extend, or change the sequence of event bindings that will be triggered for each widget; see the [bindtags](https://tcl.tk/man/tcl8.6/TkCmd/bindtags.htm) command reference if you're curious.

### Available Events
参考[bind](https://tkdocs.com/man/bind)。
最常用的事件：
- `<Activate>`：Window has become active.
- `<Deactivate>`：Window has been deactivated.
- `<MouseWheel>`：Scroll wheel on mouse has been moved.
- `<KeyPress>`：Key on keyboard has been pressed down.
- `<KeyRelease>`：Key has been released.
- `<ButtonPress>`：A mouse button has been pressed.
- `<ButtonRelease>`：A mouse button has been released.
- `<Motion>`：Mouse has been moved.
- `<Configure>`：Widget has changed size or position.
- `<Destroy>`：Widget is being destroyed.
- `<FocusIn>`：Widget has been given keyboard focus.
- `<FocusOut>`：Widget has lost keyboard focus.
- `<Enter>`：Mouse pointer enters widget.
- `<Leave>`：Mouse pointer leaves widget.
Event detail for mouse events are the button that was pressed, e.g. `1`, `2`, or `3`. For keyboard events, it's the specific key, e.g. `A`, `9`, `space`, `plus`, `comma`, `equal`. A complete list can be found in the [keysyms](https://tkdocs.com/man/keysyms) command reference.
Event modifiers for include, e.g. `B1` or `Button1` to signify the main mouse button being held down, `Double` or `Triple` for sequences of the same event. Key modifiers for when keys on the keyboard are held down inline `Control`, `Shift`, `Alt`, `Option`, and `Command`.

### Virtual Events
到目前为止我们接触到的事件都是一些低级的系统事件。很多控件会产生一些更高级的事件，称作虚拟事件。
例如`listbox`在它的选择被修改时会产生`<<ListboxSelect>>`事件。
一个控件所支持的虚拟事件可以在控件类的文档中查看。
Tk也定义了一些常见操作的虚拟事件（跨平台的）。包括`<<Cut>>`、`<<Copy>>`、`<<Paste>>`。
也可以定义自己的虚拟事件，这是一种很有用的方法，可以将特定于平台的细节隔离在单个模块中。
在自己的代码中可以通过与Tk虚拟事件相同的方法来产生你自定义的虚拟事件：
```python
root.event_generate("<<MyOwnEvent>>")
```

# 6. Basic Widgets
## 6.1 Frame
[https://tkdocs.com/man/ttk_frame](https://tkdocs.com/man/ttk_frame)
Frame通常用作容纳其它控件的容器。
### Requested Size
它的大小通常由它所容纳的容器决定。若要显式地指定它的大小，可以用`width`和`height`配置选项来设置。一般尺寸的单位为像素，例如`350`为350像素，也有其它单位，例如`350c`表示350厘米，`350m`表示毫米，`350i`表示inch，`350p`表示350个printer's points（1/72inches）。
> 虽然可以显式地指定frame的大小，但它所容纳的控件有最终决定权（have the final say），即若所容纳的控件超过指定大小，尺寸可能会变化。

### Padding
Padding配置选项用于指定frame的边距大小。
```python
f['padding'] = 5 # 5 pixels on all sides
f['padding'] = (5,10) # 5 on left and right, 10 on top and bottom
f['padding'] = (5,7,10,12) # left: 5, top: 7, right: 10, bottom: 12
```

### Borders
frame的边界可以通过`borderwidth`和`relief`两个配置选项来实现。
`borderwidth`设置边界的宽度，`relief`设置边界的样式，可选的样式有`flat (default)`、`raised`、`sunken`、`solid`、`ridge`、`groove`。
```python
frame['borderwidth'] = 2
frame['relief'] = 'sunken'
```

### Changing Styles
Frame有一个`style`配置选项。其它主题控件（themed widgets）也有同样的选项。该选项可以令你改变控件的其它外观和行为。

`style`选项是一个深入的话题，我们在此不过多展开。
但姑且给出一个使用`Danger`风格的frame的创建方式：
```python
s = ttk.Style()
s.configure('Danger.TFrame', background='red', borderwidth=5, relief='raised')
ttk.Frame(root, width=200, height=200, style='Danger.TFrame').grid()
```

## 6.2 Label
[https://tkdocs.com/man/ttk_label](https://tkdocs.com/man/ttk_label)
### Displaying Text
一般来说，Label显示的文本无需改变，只要在创建的时候直接赋值就可以了。
```python
label = ttk.Label(parent, text='Full name:')
```
若需要动态监控和变化Label文本，则可以使用Tk提供的`StringVar`来实现：
```python
resultsContents = StringVar()
label['textvariable'] = resultsContents
resultsContents.set('New value to display')
```

### Displaying Images
Label也可显示图片：
```python
image = PhotoImage(file='myimage.gif')
label['image'] = image
```
Label也可以同时显示图片和文本，这是通过`compound`配置选项实现的。此选项的默认值为`none`，意味着有图片时显示图片，没有图片时显示`text`或`textvariable`选项所设置的文本。
`compound`选项的其它可能值为：
- text：仅文本；
- image：仅图片；
- center：文本在图片中心；
- top：图片在文本上；
- left：
- bottom：
- right：

### Fonts, Colors, and More
可以使用`Font`配置选项来改变Label的字体。
字体不是跨平台的，用时要小心。
下面是一些Tk预定义的字体：
- TkDefaultFont: Default for all GUI items not otherwise specified.
- TkTextFont: Used for entry widgets, listboxes, etc.
- TkFixedFont: A standard fixed-width font.
- TkMenuFont: The font used for menu items.
- TkHeadingFont: A font for column headings in lists and tables.
- TkCaptionFont: A font for window and dialog caption bars.
- TkSmallCaptionFont: Smaller captions for subwindows or tool dialogs.
- TkIconFont: A font for icon captions.
- TkTooltipFont: A font for tooltips.

可以用`background`和`foreground`配置选项修改字体的前景色（即字体颜色）/背景色。
还可以使用`relief`配置选项修改边界样式。

### Layout
虽然整体布局是由geometry manager决定的，但还是有些选项可以帮助你控制Label在geometry manager产生的矩形中的位置