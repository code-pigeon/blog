# xmake 笔记

## 设置编译器为MinGW
```lua
-- xmake.lua
set_toolchains("mingw@mingw-w64")
```

## 指定目标编译/运行
```bash
xmake --target=my_target_name  # 指定目标编译

xmake run my_target_name  # 指定目标运行
# 或者
xmake r my_target_name
```

## 设置所有目标为debug模式
```bash
xmake f --mode=release
# 或者
xmake f -m debug
```

## 调试运行
```bash
xmake run -d my_target_name
```
windows下的默认调试器为vs，可以手动更改调时器：
```bash
xmake f --debugger=gdb
```
