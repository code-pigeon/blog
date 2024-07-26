# windows .bat批处理文件 笔记

### 判断文件是否存在
```bat
@echo off
set file_path=C:\path\to\file.txt
IF EXIST "%file_path%" (
    echo File exists
) else (
    echo File does not exist
)
```

### exit /b
```bat
exit /b
```
这表示退出当前的批处理，而不是退出整个cmd.exe。

### 内置变量ERRORLEVEL
这是一个无需声明的内置变量，cmd中此变量用于表示上一段命令是否执行成功，若成功，则为0。
例如：
```bat
@echo off
echo Testing ERRORLEVEL variable example

dir non_existent_folder

set flag0=%ERRORLEVEL%
if %flag0% equ 0 (
    echo Command executed successfully
) else (
    echo Command failed with error
)
```

如果在批处理文件中使用`exit /B 1`来设置退出代码为 1，那么在调用该批处理文件的CMD窗口中，`%ERRORLEVEL%`的值就会变为 1。这样就可以通过判断`%ERRORLEVEL%`的值来获取批处理文件的执行状态。

### setlocal和endlocal
在setlocal之后声明的变量，在执行endlocal之后会被自动删除。
即setlocal和endlocal规定了变量的作用域范围。相当于C语言的`{}`。
```bat
@echo off
set var=1

setlocal
set var_in_local=2
echo var = %var%, var_in_local=%var_in_local%
rem 输出为var = 1, var_in_local=2
endlocal

echo var = %var%, var_in_local=%var_in_local%
rem 输出为var = 1, var_in_local=
```

### del /q
通常使用del进行批量删除时，会询问用户确认，例如：
```bat
D:\test>del .\*
D:\test\*, Are you sure (Y/N)?
```
`/q`参数表示在执行删除操作时不要提示用户确认，直接删除。

### set /p
相当于python的`name = input("请输入您的名字")`。
```bat
@echo off
set /p name=请输入你的名字: 
echo 你输入的名字是 %name%
```

可以用于提示用户确认：
```bat
@echo off
setlocal

set /p confirm=确认执行吗？(输入Y/N) 
if /i "%confirm%"=="Y" (
    echo 用户确认执行，开始执行相应操作
    REM 在这里编写需要执行的命令
) else (
    echo 用户取消执行，退出脚本
)

endlocal
```

### equ和==
听说`==`用于判断字符串相同，而`equ`除了字符串，还可以用于判断数值。
```bat
if hah equ hah (echo yes)
rem 输出 yes

if 10 equ 0x0a (echo yes)
rem 因为0x0a表示十六进制的10，所以条件成立，输出yes

if 10 equ 012 (echo yes)
rem 因为012表示八进制的10，所以输出yes
```

### call指令
`call`指令可以实现程序跳转，当跳转到的程序执行完毕之后，会返回到`call`语句的下一条继续执行。
`call`后可以跟bat标签、或者其它bat文件名。

需要注意的是，`call`指令只是简单的执行流跳转，并不会开辟新的进程。
也就是说，若parent.bat调用了child.bat，在child.bat中可以访问到parent.bat中定义的变量。
```bat
rem 此为parent.bat

@echo off
set x=2
call child.bat
echo call结束之后会执行这条语句
exit
```

```bat
rem 此为child.bat

@echo off
echo x
rem 可以输出parent.bat中定义的x
```

使用`call`跳转到标签处，可以模拟函数：
```bat
@echo off

rem 定义函数
:myFunction
	echo 函数被调用了
	exit /b

rem 主程序开始
echo 主程序开始
rem 调用函数
call :myFunction
echo 主程序结束
pause
```
其中`:myFunction`中的`exit /b`可以使程序跳转回`call`语句处继续执行，若将`exit /b`替换为`exit`，则`:myFunction`结束之后将直接退出cmd。