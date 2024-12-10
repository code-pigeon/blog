# sublime text笔记
最后编辑：24/11/28/12:11

## 0. 参考
- [sublime官网文档](https://www.sublimetext.com/docs/)
- 《Mastering Sublime Text》Dan Peleg
- [ST Community Docs，Reference](https://docs.sublimetext.io/reference/)
- [Sublime Text API reference](https://www.sublimetext.com/docs/api_reference.html)

## 1. 基本用法
### 1.1 一般快捷键
`ctrl`+`P`：通过查找跳转到目录下任意文件；
`ctrl`+`shift`+`P`：通过查找使用快捷键；
`ctrl`+`M`：跳转到匹配的括号处；
`ctrl`+`G`：跳转到行；
`alt`+`数字`：跳转到对应位置的标签页；
`ctrl`+`PgUp/PgDn`：按顺序切换标签页；

### 1.2 查找与替换
`ctrl`+`F/H`：查找/替换；

在查找下的快捷键：
`alt`+`R`：正则表达式开关；
`alt`+`C`：大小写开关；
`alt`+`W`：精确匹配开关；
`enter`：查找下一个；
`shift`+`enter`：查找上一个；
`alt`+`enter`：查找全部；

### 1.3 代码的
`ctrl`+`R`：查找函数；
`ctrl`+`;`：查找；

### 1.4（不知起啥名）
`ctrl`+`X`：删除行；
`ctrl`+`enter`：行后插入行；
`ctrl`+`shift`+`enter`：行前插入行；
`ctrl`+`L`：选中行；
`ctrl`+`shitf`+`J`：合并行；
`ctrl`+`shift`+`/`：块注释；
`ctrl`+`shift`+`V`：粘贴并自动缩进；

### 1.5 方形选择
`鼠标右键`+`Shift`
添加到选择：`鼠标右键`+`Shift`+`Ctrl`
从选择中删除：`鼠标右键`+`Shift`+`Alt`

## 2. snippet
snippet：文件后缀`.sublime-snippet`的xml文件。
> 若想要在`<content>`标签中写`$`应该写`\$`。
```xml
<snippet>
  <content><![CDATA[<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="description" content="$1">
    <meta name="viewport" content="width=device-width, initial scale=1">
    <title>${2:Untitled}</title>
  </head>
  <body>
    Hello ${3:$TM_FULLNAME}! Welcome to $2!
    $0
  </body>
</html>]]>
  </content>
  <tabTrigger>doctype</tabTrigger>
  <description>HTML5 Structure</description>
  <scope>text.html</scope>
</snippet>
```
tabTrigger：触发snippet的关键字；
scope：表示此snippet的作用范围（文件类型），scope的完整类型见[https://gist.github.com/danpe/6993237](https://gist.github.com/danpe/6993237)；Hello you are sb!

触发此snippet之后，首先光标会到达`content="$1"`的`$1`处；
然后会到`${2:Unititled}`处，此处的默认值为`Untitled`；
接着会到`${3:$TM_FULLNAME}`处，此处的`$TM_FULLNAME`为环境变量，对于完整的环境变量见[https://gist.github.com/danpe/6996806](https://gist.github.com/danpe/6996806)；
最后退出snippet时，光标会到`$0`处，若没有`$0`，则默认跳转到snippet的最后。


## 3. command
### 3.1 调用command
#### 3.1.1 通过控制台调用
> 在[sublime官网文档](https://docs.sublimetext.io/reference/commands.html)可以找到所有`command`命令。

command命令可以使用控制台进行调用：
1. `ctrl`+`` ` ``打开控制台
2. 输入`<object>.run_command(<command>, { <command_param1>: <command_arg1>, ...})`
> 其中
> 1. `<object>`可以是`sublime`、`window`或`view`，分别代表当前sublime应用对象、当前sublime窗口对象、和当前的标签页对象，分别对应三种不同的[command类型](#3.2-command的三种类型)：`ApplicationCommand`、`WindowCommand`、`TextCommand`
> 2. `<command>`表示command的名称，`<command_param1>`表示command的参数名，`<command_arg1>`表示command的参数值。

例如，在当前标签页文件的末尾插入一段字符串，可以使用
```python
view.run_command('append', {'characters': "插入的文字", 'scroll_to_end': False})
```
> 根据sublime官网文档，`append`命令的格式为：
> 
> > `append`
> > 
> > Inserts a string at the end of the view.
> > 
> > - **characters** (String): String to be inserted.
> > - **force** (Bool):
> > - **scroll_to_end** (Bool):

#### 3.1.2 通过命令面板（Command Palette）调用
另外也可以用命令面板进行调用：
1. `ctrl`+`shift`+`P`打开命令面板
2. 查找需要的命令并用鼠标单击/按下`enter`键

> **注**
> 
> 有些command会根据当前标签页的情况判断是否展示，比如一个应用于C语言的command会检查文件的后缀名是否为`.c`。

#### 3.1.3 通过快捷键调用
略

### 3.2 command的三种类型
> 参考[https://docs.sublimetext.io/reference/plugins.html](https://docs.sublimetext.io/reference/plugins.html)

|command类型|对应的对象|表示的实体|
|:--|:--|:--|
|`ApplicationCommand`|`sublime`对象|sublime进程|
|`WindowCommand`|`window`对象|一个sublime应用窗口|
|`TextCommand`|`view`对象|sublime窗口中的一个标签页|

`WindowCommand`实例拥有`.window`属性，表示当前窗口。
`TextCommand`实例拥有`.view`属性，表示当前标签页。

三种类型都拥有：
- `.run()`方法：执行该command；
- `is_visible`方法：是否在Command Palette（即`ctrl`+`shift`+`P`出现的哪个）中显示；


### 零碎的
#### insert和insert_snippet这两个command的区别
`insert`用于简单地往光标处插入字符串：
```python
view.run_command('insert', {'characters': '插入的文字'})
```

`insert_snippet`可以插入一段snippet（这意味着可以使用`$1`等的占位符）：
```python
view.run_command('insert_snippet', { 'contents': 'hello ${1: sb}! $0'})
```
也可以直接调用一个snippet文件：
```python
view.run_command('insert_snippet', { 'name': 'Packages/User/test.sublime-snippet'})
```

## 4. 插件plugin
插件其实就是用户写一个属于自己的[command](#3.-command)。

插件使用python语言编写。

### 4.1 创建第一个plugin
#### 4.1.1 创建plugin
1. 依次点击选项卡`Tools/Developer/New Plugin`，出现一个新的标签页，里面会默认有一个示例的`.py`文件。
```python
import sublime
import sublime_plugin


class ExampleCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.insert(edit, 0, "Hello, World!")
```
2. 按下`ctrl`+`s`保存到默认的路径，可以随意命名。

这样一个简单的plugin就创建好了。

#### 4.1.2 运行plugin
运行创建好的plugin：
- `ctrl`+`` ` ``打开控制台，输入`view.run_command('example')`。
可以看到打开标签页的开头被插入了"Hello, World"。

### 4.2 plugin的命名约定
plugin必须是名字为`XxxCommand`的python类
> **注**
> 
> （而且必须继承`sublime_plugin.<object>Command`，`<object>`为`Text`、`Window`或`Application`，参见[3.2 command的三种类型](#3.2-command的三种类型)）。

sublime会将`XxxCommand`去掉后面的`Command`并将剩余的部分转化为蛇形命名形式（例如`OpenFileCommand` ==> `open_file`）作为command的名字。

### 零碎的
#### 实现插入当前日期的两个方法
##### 1、在插件中调用现成的command
```python
import datetime
import sublime_plugin

class AddCurrentTimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.run_command('insert', 
      {'characters': "%s" % datetime.datetime.now().strftime("%y/%m/%d/%H:%M")}
    )
```
调用了`insert`这个command进行插入。

##### 2、使用sublime API
```python
import datetime
import sublime_plugin

class AddCurrentTimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    # 定义要插入的字符串
    time_str = "%s" % datetime.datetime.now().strftime("%y/%m/%d/%H:%M")

    # 获取当前选择（光标）的区域
    sel = self.view.sel()

    # 遍历所有的选区（通常只有一个光标位置）
    for region in sel:
      # 在光标位置插入文本
      self.view.insert(edit, region.begin(), time_str)    

```
`view`表示当前的标签页，`view.sel()`会返回一组`region`（`Region`类型表示光标选中的文本区域），`region.begin()`会返回选中区域的开始位置（类型为`Point`，表示以文件开头为起始的偏移量），接着用`view.insert()`方法，指定位置并插入文本。

