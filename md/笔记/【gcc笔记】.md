# gcc笔记
最后编辑：24/12/09/19:42

## gcc基本命令
*参考视频*：[gcc编译器的简单入门教程](https://www.bilibili.com/video/BV1V84y1D7nU)
```bash
gcc main.c  # 编译为可执行文件，文件默认与源码同名

gcc -o main.c main  # 指定可执行文件名
gcc main -o main.c  # 效果同上

gcc -static main.c  # 静态编译（即将所依赖的动态、静态库都直接链接到可执行文件上）

gcc -I ./path/to/header/ main.c  # -I 指定搜索头文件的路径


# 制作静态库
gcc -c add.c sub.c mul.c  # 编译为.o 文件（也可以加上-o add.o等）
ar crv libmyMath.a add.o sub.o mul.o  # 按照远古的记忆，这个静态库只能以lib开头，以.a为后缀

# 使用静态库
gcc -o main main.c libmyMath.a


# 制作动态库
gcc -c add.c sub.c mul.c -fPIC  # 生成位置无关的.o文件（position independent file）

gcc -shared -o libmyMath.so add.o sub.o mul.o  # 在Windows下应.so改为.dll

# 使用动态库
gcc main.c -o main -l myMath -L ./lib/ -I ./inc/  # -l指定动态库名，-L指定动态库所在的文件夹，-I寻找头文件

# 需要说明的是，如果动态库文件和可执行文件不在同一目录下，默认系统是找不到动态库的，此时需要别的方式让系统能去存放动态库的文件夹下寻找动态库，挺麻烦的，这里先不表。
```

## gcc和环境变量
### 头文件搜索
`CPATH`：指定头文件搜索路径（相当于gcc的`-I`选项）。多个路径之间用`:`分隔。
`C_INCLUDE_PATH`：同`CPATH`，但只对C语言源文件有效。
`CPLUS_INCLUDE_PATH`：同`CPATH`，但只对C++语言源文件有效。

### 库文件搜索
`LIBRARY_PATH`：指定库文件搜索路径（（相当于gcc的`-L`选项）。多个路径之间用`:`分隔。
> `LD_LIBRARY_PATH`用于指定进程运行时，动态链接库的搜索路径。

### 参考
[GNU官网](https://gcc.gnu.org/onlinedocs/gcc/Environment-Variables.html)

## gcc和响应文件
有时候一个编译的语句太长了：
```bash
# 假设这很长
gcc test1.c test2.c test3.c -o test -llib1 -llib2 -llib3
```
可以把编译的参数都放在一个文件中，类似这样：
```
test1.c 
test2.c 
test3.c
-o test
-llib1
-llib2
-llib3
```
假设这个文件叫`test.rsp`，编译时就可以使用`@test.rsp`作为编译选项进行编译：
```bash
gcc @test.rsp
```

## gdb调试器
```bash
# 1. 编译带有调试信息的可执行文件

gcc main.c -g  # -g 添加调试信息到可执行文件中（这会使文件更大些）


# 2. 进入调试模式

gdb main.exe  # 可以对带有调试信息的可执行文件进行调试


# 进入调试后，可以看到提示符变成
(gdb)


# 此时输入
list  # 可以查看源码，如果源码很长，按下回车键可以向下滚动
lay next  # 进入一个调试界面，可以多次按enter来调整视图

set args arg1 arg2  # 使用set args为main函数设置参数


# 3. 断点

# 添加断点（或者将"break"简写为"b"也是可以的）
break main  # 在main函数的第一行添加一个断点
break 6  # 在源码的第6行添加断点

# 删除断点（delete简写为d）
delete 1 #  删除第一个断点
delete #  删除所有断点

# 查看所有断点信息
info breakpoints

# 4. 单步执行
next  # 单步执行C代码（单步跳过执行，即step over）；（简写为n）
nexti  # 单步执行汇编代码（next instruction）；（简写为ni）

step  # 单步执行C代码（单步跳过执行，即step into）；（简写为s）

continue  # 继续执行（简写为c）

# 5. 查看变量
print x  # 打印变量x（简写为p）
print (char)x  # 以字符形式打印变量x
display x  # 每次程序暂停时，打印x
undisplay <编号>  # 删除display变量
info display
watch x  # 每当x改变时，打印x
info watch  # 查看观察列表

# 6. 查看寄存器
info reg  # 显示寄存器信息
print $rsi  # 打印寄存器rsi的变量
print/x $rsi  # 以十六进制的方式查看
x/s <pointer>  # 查看pointer所指向的内存地址中的数据
x/10x <pointer>  # 以16进制的形式查看连续的10个地址的数据

# 7. 查看当前程序执行到的位置
where
```