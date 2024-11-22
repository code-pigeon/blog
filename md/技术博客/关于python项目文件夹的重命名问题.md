# 关于python项目文件夹的重命名问题

首次编辑：2024/11/22/15:26
最后编辑：2024/11/22/15:46

写项目的时候，一开始可能只是一个小小的需求，也不知道起什么名字。后来越写越大了，感觉这个名字配不上它的逼格，于是又想着改一个名字。

此时可能会遇到一些问题，比如项目的git仓库会不会受到影响，（假如用了python）项目的python虚拟环境会不会受影响。

试了一下，结论是：
||是否受影响|
|--|--|
|git仓库|否|
|python虚拟环境|是|

git好像只依赖于`.git`文件夹，并不关心根路径名的问题。

python虚拟环境就不一样了。

python虚拟环境中会有一个叫`activate`的脚本，在Linux和Windows下它们的路径分别是（假设虚拟环境的文件夹名为`venv`）：
```bash
#Linux
venv/bin/activate
# Windows
venv/Scripts/activate.bat
```
如果修改了项目文件夹的名字，则需要到这个`activate`脚本中去找到`VIRTUAL_ENV`这个变量，并修改它的值。
例如在Linux中，这个变量的赋值语句如下：
```bash
VIRTUAL_ENV="/path/to/yourProject"
```
假如把项目名`yourProject`改成了`myProject`，则需要对`VIRTUAL_ENV`进行相应的修改：
```bash
VIRTUAL_ENV="/path/to/myProject"
```
这样虚拟环境才能正常工作。

> **【注】**
> 
> 在Linux中还会看到有不同后缀名的`activate`脚本，例如`.csh`；
> Windows也类似，有`.ps1`的后缀名版本。
> 
> 需要修改哪一个后缀名的脚本取决于使用的命令行。
> 如果是用Windows cmd，就用`activate.bat`；
> 如果是用Windows powershell，就用`activate.ps1`；
> 如果是用Linux C Shell，就用`activate.csh`；
> 如果是用Linux bash，就用`activate`；
>
> 当然也可以全部都改（狗头）

令人惊讶的是，我上网找居然找不到这个问题，更多的是在讨论“怎么修改虚拟环境文件夹名而不导致出错”。