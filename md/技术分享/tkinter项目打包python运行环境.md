# tkinter项目打包python运行环境
首次编辑：24/2/25/0:35  
最后编辑：24/2/25/0:57

## 尝试过程
最开始灵感还是来自于韦易笑的知乎回答（见[参考](#参考)第一条），它介绍了一个思路，下载python官网提供的嵌入式python运行环境，解压到项目的runtime文件夹下，然后在项目根目录下写个bat或者exe调用runtime中的python，并运行入口脚本。
```
./
    runtime/
        python.exe
        ...
    main.py
    invoke.bat
```
invoke.bat应该类似这样：
```bash
.\runtime\python.exe main.py
```
不过如果python使用了tkinter，则这样还不足够，会显示没有叫tkinter的模块。
这是因为嵌入式的python是不包含tkinter模块的。
不过很快找到了将Tk加入嵌入式python的方法（见[参考](#参考)第二条），很简单，只需要将安装版的python中的一些文件复制到嵌入式python的文件夹中即可。
```
C:\ProgramFiles\Python39  # System Python Location
|= tcl         --------------------------+
|= Lib                                   |
   |= tkinter  --------------------------|---+
|= DLLs                                  |   |
   |- _tkinter.pyd ----------------------|---|---+
   |- tcl86t.dll   ----------------------|---|---|---+
   |- tk86t.dll    ----------------------|---|---|---|---+
                                         |   |   |   |   |
~\runtime                                |   |   |   |   |
|= tcl          <------------------------+   |   |   |   |
|= tkinter      <----------------------------+   |   |   |
|- _tkinter.pyd <--------------------------------+   |   |
|- tcl86t.dll   <------------------------------------+   |
|- tk86t.dll    <----------------------------------------+
```
简而言之，把python中以t开头的文件（夹）全部复制到runtime中就行了。
这样一来，带有tkinter的嵌入式运行环境就准备好了。

## 参考
- [怎么样打包 pyqt 应用才是最佳方案？或者说 pyqt 怎样的发布方式最优？](https://www.zhihu.com/question/48776632/answer/2336654649)
- [如何将 Tk 套件加入到嵌入式 Python 中](https://github.com/Likianta/pyportable-installer/blob/master/docs/add-tkinter-to-embed-python.md)
