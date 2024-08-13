# C语言自定义错误打印函数
最后编辑：2024/6/10/12:33

## 引子
写程序难免需要错误处理，而为了把错误信息输出到标准错误中，通常会选择使用`fprintf`函数来打印错误信息。
```c
#include <stdio.h>
int main(int argc, char const *argv[])
{
	int error_code = -1;
	fprintf(stderr, "error: %d\n", error_code);
	return 0;
}
```
为了方便观看，还可能使用彩色打印
```c
fprintf(stderr, "\033[31merror:\033[0m %d\n", error_code);
```
显然在每个出错的地方都写上这么冗长的一句代码不仅观感非常差，而且一旦需要修改将会非常麻烦。

所以在思考写出这样一个函数：
```c
void error(char* fmt, ...);
```
它能够像`printf`一样使用，但又能够将错误信息输出到标准错误中，还能够输出彩色的字符：
```c
error("%d", error_code);
// 等价于↓
// fprintf(stderr, "\033[31merror:\033[0m %d\n", error_code);
```

## 实现
正好标准库中有一个非常适合实现这个功能的函数，它就是`vprintf`，当然它还需要和`stdarg.h`头中的仨哥们`va_list`、`va_start`和`va_end`配合一下：
```c
void error(char* fmt, ...){
	va_list ap;
	va_start(ap, fmt);
	printf("\033[31m");  // 将字体转为红色
	printf("error: ");
	printf("\033[0m");  // 将字体转为默认颜色
	vprintf(fmt, ap);  // 这里才是真正打印错误信息的地方
	va_end(ap);
}
```
这样在主函数中就很方便的可以使用`error`函数打印错误信息了：
```c
int main(int argc, char const *argv[])
{
	int error_code = -1;
	error("%d\n", error_code);

	error("this is an error message. ");
}
```
不过上面的`error`函数还没有把信息打印在标准错误中。

但就像`printf`有兄弟`fprintf`一样，`vprintf`也有它的兄弟`vfprintf`，只要把上面的`vprintf(fmt, ap);`替换为：
```c
vfprintf(stderr, fmt, ap);
```
即可。

> 这个`vprintf`和`vfprintf`可能是专门为套娃而生的。