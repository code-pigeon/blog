# C语言实现交互式终端
首次编辑：2024/6/21/14:34
最后编辑：2024/6/21/15:15

## 实现
我们首先需要一个循环，能够循环读入用户在标准输入敲下的字符：
```c
int main()
{
	char buf[256];
	while ( fgets(buf, sizeof(buf), stdin) != NULL){
		// 在这里对读入的字符串进行处理
	}
	return 0;
}
```
为了能够实现输入EOF（在Windows中是`ctrl + z`，Linux中是`ctrl + d`）退出循环，我舍弃了`scanf("%s") != EOF`这种读取输入的方式，因为在`%s`模式下，似乎无法很好地读入EOF。

通常我们需要在输出命令之前输出一个命令行提示符，否则很难分清楚程序是正在等待输入还是卡死了：
```c
int main()
{
	char buf[256];
	printf(">> ");
	while ( fgets(buf, sizeof(buf), stdin) != NULL){
		// 在这里对读入的字符串进行处理
		printf(">> ");
	}
	return 0;
}
```
到这里就可以在while循环中实现你想要对字符串进行的处理了。

然而这里还有一个小陷阱。

我们先观察一下这个程序读入的字符串长什么样子。在只输入ascii字符的情况下，用十六进制打印一下读入的字符串的ascii码：
```c
int main()
{
	char buf[32];
	printf(">> ");
	while ( fgets(buf, sizeof(buf), stdin) != NULL){
		for( int i = 0 ; i < 32; i++){
			printf("%2x ", buf[i]);
		}
		printf("\n");
		// 在这里对读入的字符串进行处理
		printf(">> ");
	}
	return 0;
}
```
编译运行程序：
```
>> nihao
6e 69 68 61 6f  a  0  0 20 ......
>> haha
68 61 68 61  a  0  0  0 ......
>> 8345923489539
38 33 34 35 39 32 33 34 38 39 35 33 39  a  0 66 ......
```
可以看到这些字符串都有共同的结尾`a 0`。

在C语言里，字符串都以0（也就是`'\0'`）结尾，但`a`又是啥呢。

查看ASCII表，可以发现，`a`表示LF，也就是换行符（`\n`）。因为我们每次输入的结束都是回车键，所以换行符自然就在字符串的末尾出现了。

但大多数时候我们并不喜欢它出现在字符串末尾，所以需要替换掉它：
```c
int main()
{
	char buf[256];
	printf("ASCII value of LF (\\n): %x\n", '\n');

	printf(">> ");
	while ( fgets(buf, sizeof(buf), stdin) != NULL){
		for( int i = 0 ; i < 32; i++){
			printf("%2x ", buf[i]);
		}
		buf[strcspn(buf, "\n")] = 0;  // 替换掉行末尾的换行符

		// 在这里对读入的字符串进行处理

		printf(">> ");
	}
	return 0;
}

```

到这里想要的功能就实现了。

## 例子
最后给个判断输入是否为数字的例子：
```c
int is_number(char *str){
	if(str == NULL){
		return 0;
	}

	int i = 0;
	if( !(str[i] >= '0' && str[i] <= '9' ) ){
		return 0;
	}
	i++;

	while ( str[i] ){
		switch(str[i++]){
		case '0':case'1':case'2':case'3':case'4':
		case'5':case'6':case'7':case'8':case'9':
			continue;
		default:
			return 0;
		case '.':
		}
		break;
	}

	while ( str[i] ){
		switch(str[i++]){
		case '0':case'1':case'2':case'3':case'4':
		case'5':case'6':case'7':case'8':case'9':
			continue;
		default:
			return 0;
		}
	}
	return 1;
}

int main()
{
	char buf[256];
	printf(">> ");
	while ( fgets(buf, sizeof(buf), stdin) != NULL){
		buf[strcspn(buf, "\n")] = 0;

		if( is_number(buf)){
			printf("%s is number\n", buf);
		}else{
			printf("%s is not number\n", buf);
		}

		printf(">> ");
	}
	return 0;
}
```
效果如下：
```
>> .9
.9 is not number
>> 90.09
90.09 is number
>> 0.1.2
0.1.2 is not number
>> j
j is not number
```