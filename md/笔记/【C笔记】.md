# C笔记
最后编辑：24/11/27/23:15

## time.h
类型介绍：
```c
time_t
// 以整型的形式存储时间（即时间戳），0表示1970年1月1日8:00:00

clock_t
// todo：目前不研究，以后再补充

struct tm {
   int tm_sec;         // 秒，范围从 0 到 59     
   int tm_min;         // 分，范围从 0 到 59     
   int tm_hour;        // 小时，范围从 0 到 23     
   int tm_mday;        // 一月中的第几天，范围从 1 到 31 
   int tm_mon;         // 月，范围从 0 到 11     
   int tm_year;        // 自 1900 年起的年数（这和时间戳的1970并不一致）     
   int tm_wday;        // 一周中的第几天，范围从 0 到 6 
   int tm_yday;        // 一年中的第几天，范围从 0 到 365 
   int tm_isdst;       // 夏令时             
};
// struct tm以结构化的形式（年月日时分）存储时间
```

### 关于时间戳和时间结构体的函数
```c
// 1. 获取当前时间戳
time_t t = time(NULL);
// 或者
time_t t;
time(&t);

// 2. 两个时间戳的差
// 函数原型：
double difftime(time_t time1, time_t time2);

// 3. 时间戳 ==> 时间结构体（指针）
struct tm *struct_t     = localtime(&t);    // 以当前时区来表示
struct tm *struct_t_UTC = gmtime(&t);   // 以格林尼治时间来表示
/* 注：
    （此二函数是线程不安全的！）
    这里返回的时间结构体指针指向了 静态内存区域，不需要手动管理内存 
    不过这意味着每次调用localtime或者gmtime的时候，会覆盖之前的内容。  
*/

// 4. 时间结构体 ===> 时间戳
time_t t = mktime(struct_t);    // 以当前时区来转化

// 5. 时间戳/时间结构体 ==> 字符串
const char* str_from_t          = ctime(&t);            // "Tue Nov 26 15:35:43 2024"
const char* str_from_struct_t   = asctime(struct_t);    // "Tue Nov 26 15:35:43 2024"
/* 注：
    （此二函数是线程不安全的！）
    同样地，返回的字符指针指向的是一个静态分配的内存区域
    每次调用这两个函数的其中之一也会覆盖之前的内容
*/

// 6. 时间结构体 ==> 格式化字符串
char buffer[128];
strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &now);
// 下文会给出所有可能的格式化方式

// 7. 格式化字符串 ==> 时间结构体
struct tm tm = {0};
if (strptime("24/11/27/22:50", "%y/%m/%d/%H:%M", &tm) == NULL){
    /* Handle error */;
}
```
> `strptime`这个函数在编译时需要定义宏`_XOPEN_SOURCE=600`：
> ```bash
> gcc -D_XOPEN_SOURCE=600 main.c 
> ```
> 否则会出现警告：`warning: implicit declaration of function ‘strptime’; did you mean ‘strftime’?`。
> 尚不明原因。
> 
> 参考[0.6.2 warning: implicit declaration of function 'strptime'](https://sourceforge.net/p/wput/bugs/75/)

#### strftime的所有格式
**日期和时间元素**
|格式符号|描述|示例|
|:--|:--|:--|
|%Y|四位年份|2024|
|%y|两位年份|24（表示2024）|
|%m|月份（01到12）|11（11月）|
|%d|一个月中的天数（01到31）|26（26日）|
|%H|小时（00到23，24小时制）|08（上午8点）|
|%I|小时（01到12，12小时制）|08（下午8点）|
|%M|分钟（00到59）|30（30分）|
|%S|秒（00到59）|45（45秒）|
|%p|AM/PM标记|AM（上午）|
|%A|星期几的完整名称|Monday（星期一）|
|%a|星期几的缩写|Mon（周一）|
|%B|月份的完整名称|November（十一月）|
|%b|月份的缩写|Nov（11月）|
|%d|一个月中的天数（01到31）|26|
|%j|一年中的第几天（001到366）|330（第330天）|
|%U|一年中的第几周（00到53，星期天是周首）|47（第47周）|
|%W|一年中的第几周（00到53，星期一是周首）|47（第47周）|
|%Z|时区名称（例如"UTC"）|UTC|
|%z|时区偏移（例如+0800）|+0800|

**时间和日期的其他常用格式**
|格式符号|描述|示例|
|:--|:--|:--|
|%c|完整的日期和时间（本地格式）|Mon Nov 26 08:30:45 2024|
|%x|本地日期（如 MM/DD/YY）|11/26/24|
|%X|本地时间（如 HH:MM:SS）|08:30:45|
|%F|等同于 %Y-%m-%d（ISO 8601日期）|2024-11-26|
|%T|等同于 %H:%M:%S（ISO 8601时间）|08:30:45|
|%r|12小时制的时间（%I:%M:%S %p）|08:30:45 AM|
|%R|24小时制的时间（%H:%M）|08:30|

## C语言中的文件操作
### 打开文件fopen
```c
// 打开文件
FILE* f = fopen("test.txt", "r");  // 只读形式打开
```

### 文件操作指针
```c
// 1. ftell(FILE* file_ptr)
long position = ftell(f); // 返回目前文件操作指针的相对与文件开头的位置
/* 
比如说test.txt中存放了一段文字I'm so handsome.
刚打开时文件是这样的：
-----------------------
_ptr
↓
I'm so handsome.
-----------------------
ftell返回的就是0

假如文件指针移动到了字母h处，即
-----------------------
       _ptr
       ↓
I'm so handsome.
-----------------------
ftell返回的就是7
*/

//2. fseek(FILE* file_ptr, offset, origin)
fseek(f, 0, SEEK_SET);  // 将文件指针f所指向的文件的_ptr设置到文件开头（SEEK_SET表示文件开头），偏移量为0
/*
SEEK_SET 为文件开头
SEEK_CUR 为当前_ptr的位置
SEEK_END 为文件末尾
*/

//3. rewind(file_ptr)
rewind(f);  // 重置_ptr到文件开头
```

### 文件读写
```c
// size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
size_t n = fwrite(data_array, 3, 2, file_ptr);  // 从data_array的开头开始写入数据到文件中
// 以3bytes为写入单位
// 写入2个单位大小
// 故写入的总大小为3*2 = 6
/*
比方说          
                      data_array
                         ↓
char[7] = data_array = {'c', 'p', 'p', '=', 'c', '+', '+'};  

此时一次写入的单位大小为3（byte），写入2个3byte的数据，所以会将"cpp=c+"写入到文件中

如果执行成功，fwrite返回的n应该等于nmemb的大小，在本例中为2；若不相等，则会显示一个错误。
*/

// size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream)
size_t n = fread(read_buf, 3, 2, file_ptr);  // 从文件当前的操作指针开始，以3bytes为一个单位，读取2个单位（即3bytes）的数据。
/*
基本与fwrite相同，唯一需要注意的点是，读文件并不一定从文件开头开始读，要看此时的文件操作指针在什么位置。
*/

```

## 【C笔记】打印不同的颜色字体
> 实际上是利用了终端的功能，详见[《Linux终端控制》](Linux终端控制.html)

```c
#include <stdio.h>

int main() {
    printf("\033[31m"); // Set text color to red
    printf("This text will be in red color\n");
    printf("\033[0m");  // Reset text color to default
    printf("This text will be in default color\n");
    return 0;
}
```

- 30m - Black
- 31m - Red
- 32m - Green
- 33m - Yellow
- 34m - Blue
- 35m - Purple
- 36m - Cyan
- 37m - White


## 宏技巧
首次编辑：24/5/15/17:26  
最后编辑：24/5/15/

```c++
/*
    1、 需要以C的形式编译某些内容，但不知道源文件是C还是C++
*/
#ifdef __cplusplus
extern "C" {
#endif

// C 语言代码或头文件包含

#ifdef __cplusplus
}
#endif

/*
    2、 需要以C的形式编译某些内容，且已知源文件是c++文件
*/
extern "C" {
    // C 语言代码或头文件包含
}
```