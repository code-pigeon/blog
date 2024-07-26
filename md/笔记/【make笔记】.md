# make笔记
*参考视频*：[跟着GNU make官方文档从入门到精通makefile(持续更新中)](https://www.bilibili.com/video/BV1xC4y1d7Xs)
## 1-入门
### 第一个makefile
在项目根目录下新建一个makefile文件（无需后缀）
编辑makefile文件
```makefile
# make默认构建一个目标，本例中为hello目标文件，但它需要依赖hello.o
# 而当前目录下没有hello.o，于是make往下查找，看是否有hello.o被生成
# 所以在本例中，两个目标都会被构建

hello: hello.o  # hello是目标文件，冒号后面是依赖文件
	gcc -o hello hello.o  # 制表符表示后面的是命令行语句

hello.o: hello.c
	gcc -o hello.o hello.c 

```
编辑完成后，直接在项目根目录下执行`make`即可。

### 伪目标.PHONY

在makefile文件中添加clean目标
```makefile
hello: hello.o
	gcc -o hello hello.o

hello.o: hello.c
	gcc -c hello.c -o hello.o

.PHONY: clean  # 因为clean并不是一个我们要生成的目标文件，所以定义为伪目标
clean:
	rm hello
	rm hello.o
```
这样在命令行执行`make clean`，clean:下面的两条语句就会执行。

### 设置默认构建目标.DEFAULT_GOAL := [目标文件]
如果在上面的makefile中，我们只想要构建hello.o而不想构建hello，可以用关键字.DEFAULT_GOAL指定默认要构建的目标
```makefile
.DEFAULT_GOAL := hello.o
hello: hello.o
	gcc -o hello hello.o

hello.o: hello.c
	gcc -c hello.c -o hello.o

.PHONY: clean
clean:
	rm hello
	rm hello.o
```
这样执行make的时候就会默认构建hello.o文件了。

### 使用变量
```makefile
obj = hello.o  # 定义obj变量
hello: $(obj)
	gcc -o hello $(obj)

$(obj): hello.c
	gcc -c hello.c -o $(obj)

.PHONY: clean 
clean:
	rm hello
	rm $(obj)
```

### 隐式推断
make会根据生成的目标推断所需依赖，以及所需的命令
所以其实上面的makefile可以省略为
```makefile
obj = hello.o 
hello:

$(obj):

.PHONY: clean 
clean:
	rm hello
	rm $(obj)
```

## 2-Writing Makefiles
### 分割字符串
```makefile
str = hello \
      world
# str = hello world

str = hello$\
      world
# str = helloworld
```

### makefile的名字
1. 对于GNU的make有三种命名：GNUmakefile > makefile > Makefile（即如果目录下有这三个文件，make会优先执行GNUmakefile）
2. 可以用-f或者-file来指定要执行的makefile

### makefile文件include别的makefile文件
在./path/to/another/路径下新建一个makefile文件
```makefile
# ./path/to/another/makefile.mk
# 当然，不要.mk后缀也可以
varInAnotherMk = fuck!
```

在当前目录下引用上面的mk文件
```makefile
include ./path/to/another/makefile.mk

print:
	echo $(varInAnotherMk)
```

### 头文件查找
.INCLUDE_DIRS这个变量记录了默认搜索头文件的路径

在makefile中，如果需要引用头文件，可以用变量的方式
```makefile
INCLUDES = -I ./inc

hello: hello.c add.c
	gcc -o hello hello.c add.c $(INCLUDES)
```
（不知道可不可以直接修改.INCLUDE_DIRS，还没试过）
