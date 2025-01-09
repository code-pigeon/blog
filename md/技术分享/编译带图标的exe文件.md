# 编译带图标的exe文件
首次编辑：24/2/25/0:17  
最后编辑：24/2/25/0:30

## 尝试过程
先参考了第一个链接（见[参考](#参考)），做了如下事情：

文件结构为：
```comment
./
    main.c
    ico.ico
    ico.rc
```

ico.rc的内容为：
```comment
id ICON "ico.ico"
```

接着运行`windres.exe -i ico.rc -o ico.o`。
但出现报错：
```comment
windres.exe: can't open file `page:': Invalid argument
ico.rc:2: fatal error: when writing output to : Invalid argument
compilation terminated.
windres.exe: preprocessing failed.
```

死活不成功，然后参考了链接二，加了个选项`--use-temp-file`，就成功了。

现在的文件结构为：
```comment
./
    main.c
    ico.ico
    ico.rc
    ico.o
```
接下来直接用gcc把main.c和ico.o编译并链接到一起即可：
```bash
gcc main.c ico.o -o out.exe
```
## 参考
- [给GCC编译出来的可执行文件添加图标](https://blog.csdn.net/yanhanhui1/article/details/110238429)
- [PW系列 | 用windres 编译.rc 资源文件](https://blog.csdn.net/big_cheng/article/details/127183433#Original)