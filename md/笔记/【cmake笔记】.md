# cmake 笔记

## 
add_executable(myexe test.cpp)：以test.cpp为源码创建一个名为myexe的可执行文件；

```cmake
// 
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)
```

## 设置编译器为MinGW
在Windows下，除非调用CMake时显式指定了生成器，否则CMake使用最新的Visual Studio安装作为默认生成器。此行为是硬编码的，不能更改。

所以只能写个bat包装一下cmake命令：
```bat
@cmake.exe -G"MinGW Makefiles" %*
```
参考链接：[关于C ++：在CMake中设置默认编译器](https://www.codenong.com/7081820/)