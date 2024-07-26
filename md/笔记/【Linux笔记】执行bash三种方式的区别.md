# 【Linux笔记】bash/sh、./和source执行bash脚本的区别

1. 显式指定解释器（如`bash mybat.sh`）的情况下，每次执行脚本时都会开启一个子shell，因此不保留当前的shell变量；
2. 使用source或者点./执行（如`./mybat.sh`、`source mybat.sh`），在当前shell环境加载脚本，因此保留脚本中的变量；

例如：  
有脚本文件内容为
```bash
#!/bin/bash
name="cxk"
```

在终端中用bash命令调用该脚本后，echo ${name}，会发现name为空。

但若用source或者 . 调用，再echo ${name}，会返回cxk



