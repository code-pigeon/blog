# Chapter 2：Working with Characters and Strings
## 须知
在学习的过程中，看到了不少网友对`tchar.h`这个头文件的吐槽，说这种过时的东西完全没有存在的必要。
我简单搜索了一下，他们的意思是，开发时用上tchar.h，那么后续的开发和维护会变得麻烦。而在如今，一两个字符的空间大小很廉价，以巨大代价换取这点空间不划算。
怪不得微软官方给的文档中的例程也都是直接用的Unicode，并没有用上`TEXT`来代替`L""`。
后文的记录中会有大量关于tchar.h的知识点，但会尽量找出Unicode版本的函数，而不是只给出和稀泥的版本（如TEXT宏）。

## String Data Types
Windows via C/C++定义了内置的数据类型`wchar_t`，表示UTF-16字符。
```c++
// A 16-bit character
wchar_t c = L'A';
// An array up to 99 16-bit characters and a 16-bit terminating zero.
wchar_t szBuffer[100] = L"A String";
```
windows团队为了建立与C无关的数据类型，在WinNT.h中定义了以下宏：
```c++
/* in WinNT.h */

typedef char CHAR; // An 8-bit character
typedef wchar_t WCHAR; // A 16-bit character

// Pointer to 8-bit character(s)
typedef CHAR *PCHAR;
typedef CHAR *PSTR;
typedef CONST CHAR *PCSTR
// Pointer to 16-bit character(s)
typedef WCHAR *PWCHAR;
typedef WCHAR *PWSTR;
typedef CONST WCHAR *PCWSTR;
```
为了兼顾ANSI和Unicode所定义的宏：
```c++
/* in WinNT.h */

#ifdef UNICODE
	typedef WCHAR TCHAR, *PTCHAR, PTSTR;
	typedef CONST WCHAR *PCTSTR;
	#define __TEXT(quote) quote // r_winnt
	#define __TEXT(quote) L##quote
#else
	typedef CHAR TCHAR, *PTCHAR, PTSTR;
	typedef CONST CHAR *PCTSTR;
	#define __TEXT(quote) quote
#endif
#define TEXT(quote) __TEXT(quote)
```
故总结之：
1. CHAR为8-bit字符；WCHAR为18-bit字符；TCHAR为通用字符（视情况而定是8-bit还是16-bit）。
2. PCHAR等价于PSTR，表示字符串。
3. 出现CSTR表示常量字符串。

## Unicode and ANSI Functions in Windows
Windows函数中若含有字符参数，则通常会提供两个版本的函数（分别为Unicode版和ANSI版）。
例如CreateWinEx：
```c++
HWND WINAPI CreateWindowExW(
	DWORD dwExStyle,
	PCWSTR pClassName, // A Unicode string
	PCWSTR pWindowName, // A Unicode string
	DWORD dwStyle,
	int X,
	int Y,
	int nWidth,
	int nHeight,
	HWND hWndParent,
	HMENU hMenu,
	HINSTANCE hInstance,
	PVOID pParam);

HWND WINAPI CreateWindowExA(
	DWORD dwExStyle,
	PCSTR pClassName, // An ANSI string
	PCSTR pWindowName, // An ANSI string
	DWORD dwStyle,
	int X,
	int Y,
	int nWidth,
	int nHeight,
	HWND hWndParent,
	HMENU hMenu,
	HINSTANCE hInstance,
	PVOID pParam);
```
后缀W表示宽字符，即Unicode；后缀A表示ANSI。

但通常应该使用`CreateWindowEx`函数，而不是`CreateWindowExW`或`CreateWindowExA`。因为在`WinUser.h`中，定义了如下的宏：
```c++
/* WinUser.h */

#ifdef UNICODE
	#define CreateWindowEx CreateWindowExW
#else
	#define CreateWindowEx CreateWindowExA
#endif
```
故当程序中定义了UNICODE宏时，`CreateWindowEx`会选择调用`CreateWindowExW`；否则会选择调用`CreateWindowExA`。

在Visual Studio中默认定义了UNICODE；
若不是使用Visual Studio开发，则使用以下语句定义UNICODE：
```c++
/* your code */

#ifndef UNICODE
	#define UNICODE
#endif
```

### 扩展
在Windows中，所有函数都是基于Unicode设计的，所以几乎所有ANSI版本的函数都只是简单将传入的ANSI字符串转化为Unicode字符串，然后调用Unicode版本的函数，等调用结束，再将返回的Unicode转化为ANSI字符串。

## Unicode and ANSI Functions in the C Run-Time Library
C运行时库也有属于两种不同编码的不同版本函数。但不同于Windows，C运行时库的ANSI版本函数和Unicode版本函数并不存在互相调用的情况，它们都独立完成自己的工作。

例如，计算字符串长度的函数`strlen`——ANSI版本，`wcslen`——Unicode版本。
这两个函数都定义在String.h头文件中。

如果要兼顾两种编码，则可以使用TChar.h头文件中的`_tcslen`函数（需要定义宏_UNICODE）。
```c++
#ifdef _UNICODE
	#define _tcslen wcslen
#else
	#define _tcslen strlen
#endif
```

同样在Visual Studio中默认定义了_UNICODE；
若不是使用Visual Studio开发，则使用以下语句定义_UNICODE：
```c++
/* your code */

#ifndef _UNICODE
	#define _UNICODE
#endif
```

### 扩展
在C运行时库中，前面有下划线的宏（如_UNICODE）表示这不是C++的标准。但Windows团队并不这么做，所以在你的程序中，应当保证要么UNICODE和_UNICODE同时被定义，要么两者同时不被定义。

## Secure String Functions in the C Run-Time Library
在C语言中，任何对字符串做修改的函数都有潜在的风险：若字符串缓存不够容纳字符串，就会发生内存损坏（memory corruption）。
```c++
// The following puts 4 characters in a
// 3-character buffer, resulting in memory corruption
WCHAR szBuffer[3] = L"";
wcscpy(szBuffer, L"abc"); // The terminating 0 is a character too!
```
问题在于`strcpy`和`wcscpy`（及许多其它字符串函数）并没有用于指明缓存大小的参数，故函数并不知道发生了内存损坏。

为了解决这种问题，微软提供了一系列更安全的字符串函数用于代替C运行时库中的字符串函数，这些更安全的字符串函数被定义在StrSafe.h中。

### Introducing the New Secure String Functions
#### strsafe.h
当你包含 `<StrSafe.h>` 头文件时，会自动包含 `<String.h>` 头文件，并且在编译过程中对 C 运行时库中现有的字符串操作函数（如 `_tcscpy` 宏背后的函数）进行标记为过时警告。
strsafe.h需要在所有头文件之后被包含。

在strsafe.h中，每个字符串函数，例如`_tcscpy`或`_tcscat`都有对应的带`_s`后缀的安全版本。
> PS
实际上，当我去查看strsafe.h头文件（mingw版）时，并没有找到带有`_s`后缀的函数。而strsafe.h本身包含string.h，我在string.h里找，却也找不到。
不过在string.h中有一条语句是`#include <sec_api/string_s.h>`，我便去看了一下string_s.h，果然所有`_s`结尾的函数都在里面。
windows SDK则不同，带`_s`后缀的函数都在string.h中（Windows SDK压根没有string_s.h这个文件）。
然而奇怪的是，在mingw的string_s.h中，有短字符的`_s`函数，以`str`开头，也有宽字符的，以`wcs`开头。但在windows SDK的string.h中却没有宽字符的版本。

例如：
```c++
PTSTR _tcscpy (PTSTR strDestination, PCTSTR strSource);
errno_t _tcscpy_s(PTSTR strDestination, size_t numberOfCharacters, PCTSTR strSource);

PTSTR _tcscat (PTSTR strDestination, PCTSTR strSource);
errno_t _tcscat_s(PTSTR strDestination, size_t numberOfcharacters, PCTSTR strSource);
```
所有安全（带有`_s`后缀的）函数在执行任何操作之前都会首先验证其参数。这些函数会进行一系列检查，以确保指针不为空、整数在有效范围内、枚举值有效、并且缓冲区足够大以容纳结果数据。
如果其中任何一个检查失败，函数将设置线程局域的C运行时变量（thread-local C run-time variable） `errno`，并返回一个`errno_t`值来指示成功或失败。

只有当函数执行成功时，返回的`errno_t`值为`S_OK`，其它可能值在`errno.h`中可以找到。
> ps
查看errno.h时，只找到了许多`E`开头的宏（应为取error的首字母），没找到`S_OK`，但在winerror.h中找到了`S_OK`。（mingw、Windows SDK都是这样）

#### 例子
下面看个例子：
```c
/* 完整代码见扩展1 */
#define SIZE 8

WCHAR dest[SIZE] = L"Hello";
const WCHAR* source = L" World!";

errno_t result = wcscat_s(dest, _countof(dest), source);

if (result == 0) {
    wprintf(L"successed! result: %ls\n", dest);
} else {
    fwprintf(stderr, L"error! \n");
    wprintf(L"result: %ls\n", dest);
}
```
`"hello World!"`的长度显然大于8，所以dest数组大小不足以容纳之。
因此会进入`else`分支，此时输出dest数组中的内容，可以看到，什么都没有。
`_s`族的函数在执行失败时会把目标数组清空，只留下`\0`。

### How to Get More Control When Performing String Operations
除了`_s`族的安全函数，在strsafe.h头文件中还定义了其它功能更丰富的安全字符串函数（同样，Unicode版本和ANSI版本分别带有W和A的函数名后缀）。
例如：
```c
HRESULT StringCchCat(PTSTR pszDest, size_t cchDest, PCTSTR pszSrc);
HRESULT StringCchCatEx(PTSTR pszDest, size_t cchDest, PCTSTR pszSrc, PTSTR *ppszDestEnd, size_t *pcchRemaining, DWORD dwFlags);

HRESULT StringCchPrintf(PTSTR pszDest, size_t cchDest,
 PCTSTR pszFormat, ...);
HRESULT StringCchPrintfEx(PTSTR pszDest, size_t cchDest,
 PTSTR *ppszDestEnd, size_t *pcchRemaining, DWORD dwFlags,
 PCTSTR pszFormat,...);
```
可见每个函数名中都包含“Cch”，这表示“Count of characters”，可以使用`_countof`宏来获得字符串数量。
同样也有包含“Cb”的函数，例如`StringCbCat(Ex)`，`StringCbCopy(Ex)`、`StringCbPrintf(Ex)`；这一组函数的`size`参数以字节（Byte）为单位，可以使用`sizeof`来获取字节数。

所有上述函数的返回值类型`HRESULT`的可能取值为：
|HRESULT值|描述|
|--|--|
|S_OK|Success. The destination buffer contains the source string and is terminated by '\0'|
|STRSAFE_E_INVALID_PARAMETER|Failure. The NULL value has been passed as a parameter.|
|STRSAFE_E_INSUFFICIENT_BUFFER|Failure. The given destination buffer was too small to contain the entire source string.|

可以用`SUCCEEDED`宏和`FAILED`宏来判断函数是否执行成功：
```c
WCHAR str1[10] = L"Hello ";
WCHAR str2[] = L"world!";
WCHAR *pStrEnd;
size_t cchRemaining;

/* 
	Ex版本的string函数，第四个参数接收一个字符串指针，函数执行后该指针指向字符串的结束符'\0'；
	第五个参数接收一个size_t指针，函数执行后该指针指向的数据变为数组剩下的长度（包含结束符'\0'，所以最小总是1）
*/
HRESULT hResult = StringCchCatExW(str1, _countof(str1), str2, &pStrEnd, &cchRemaining, 0);
if (SUCCEEDED(hResult)) {
	wprintf(L"successed!\n");
    wprintf(L"Remaining characters: %d\n", (int)cchRemaining);
} else {
	wprintf("Failed!\n");
}
wprintf(L"The resulting string is: %s\n", str1);
```

不同于`_s`族函数，这些函数在字符串数组空间不足时，会对字符串进行截断，而不是清空（所以在上一个示例中，str1 = "Hello wor" + '\0'）。

上面提到的函数例子中，有带Ex后缀的版本，这些版本提供了额外的三个参数，作用如下：
|参数/值|描述|
|--|--|
|size_t* pcchRemaining|指向一个size_t数据，该数据显示dest数组剩下的空间（包含结束符'\0'，所以最小总是为1）。若该参数传入值为NULL，则不返回dest数组剩余的空间|
|LPTSTR* ppszDestEnd|若该参数非NULL，则函数执行后该指针指向dest数组的结束符'\0'。|
|DWORD dwFlags|该参数的传入值为一个或多个由\|分隔的以下值↓|
|STRSAFE_FILL_BEHIND_NULL|还是直接看[官网](https://learn.microsoft.com/en-us/windows/win32/api/strsafe/nf-strsafe-stringcchcopyexw)吧。|
|STRSAFE_IGNORE_NULLS||
|STRSAFE_FILL_ON_FAILURE||
|STRSAFE_NULL_ON_FAILURE||
|STRSAFE_NO_TRUNCATION||

### Windows String Functions
windows也提供了许多字符串函数。其中许多因为没有考虑数组溢出而被淘汰了（如lstrcat、lstrcpy）。
ShlwApi.h中定义了许多格式化字符串函数——与数值相关的，如StrFormatKBSize、StrFormatByteSize。
> 其中，StrFormatKBSize 函数可以将以字节为单位的数字值转换为最接近的千字节（KB）的字符串表示形式，例如将 2048 字节转换为 "2 KB"。类似地，StrFormatByteSize函数可以将以字节为单位的数字值转换为易读的字符串表示形式，例如将 1048576 字节转换为 "1.00 MB"。

着重介绍下字符串比较函数。
CompareString(Ex)和CompareStringOrdinal是比较字符串的最佳选择。
> CompareString的宽字符版本CompareStringW在Windows 8之后转移到Stringapiset.h中定义（原来和窄字符版本一样定义在Winnls.h中）。
而CompareStringEx则直接没有窄字符版本了，同样定义在Stringapiset.h中。

```c
int CompareString(
	LCID locale,
	DWORD dwCmdFlags,
	PCTSTR pString1, int cch1,
	PCTSTR pString2, int cch2);
```
第一个参数传入locale ID（LCID）。可以用Windows函数GetThreadLocale来获取LCID：
```c
LCID GetThreadLocale();
```
> locale ID是标识特定语言和文化区域的数字代码。Locale ID 由一个数字和一个可选的字符串组成，它们一起标识特定的语言和区域设置。例如，Locale ID 1033 表示英语（美国），而 Locale ID 2052 表示中文（中国）。

CompareString的第二个参数用于标识比较方法，其可选值参考[官网](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-comparestringex#parameters)。
剩下的4个参数分别是两个字符串的指针和长度（以字符为单位）。若给`cch1`/`cch2`传入一个负值，函数会假定`pString1`/`pString1`是以'\0'结尾的，并会自动计算其长度。

CompareString会根据不同语言和dwCmdFlags给定的不同策略进行不同的比较，因此常用于客户端。但CompareStringOrdinal则不同，它直接比较二进制码，因此常作为工具给编程人员使用。
```c
int CompareStringOrdinal(
	PCWSTR pString1,
	int cchCount1,
	PCWSTR pString2,
	int cchCount2,
	BOOL bIgnoreCase);
```
> 该函数只有Unicode版本。

与C运行时库的xxcmp系函数不同，CompareString和CompareStringOrdinal的返回值为：
- 0：函数执行出（即ANSI）错；
- CSTR_LESS_THAN（定义为1）：pString1小于pString2；
- CSTR_EQUAL（定义为2）：相等；
-  CSTR_GREATER_THAN （定义为3）：pString1大于pString2；

> 为了方便，在函数执行成功之后，可以将返回值减掉2，与C运行时库保持一致。

#### 总结
|函数名|Unicode版本|ANSI版本|
|--|--|--|--|
|CompareString|CompareStringW（Stringapiset.h）|CompareStringA（Winnls.h）|
|CompareStringEx|CompareStringEx（Stringapiset.h）|无|
|CompareStringOrdinal|CompareStringOrdinal（Stringapiset.h）|无|

### How We Recommend Working with Characters and Strings
basic guidelines
- 总是使用`_s`后缀的函数，或者`StringCch`前缀的函数。当需要显式截断时，使用后者；其它情况使用前者。
- 不要使用不检测目标数组大小的函数。
- 不要使用 Kernel32方法进行字符串操作，如 lstrcat 和 lstrcpy

### Translating Strings Between Unicode and ANS
使用 Windows 函数 MultiByteToWideChar 将多字节字符串（即ANSI）转换为宽字符串。
```c
int MultiByteToWideChar(
	UINT uCodePage,
	DWORD dwFlags,
	PCSTR pMultiByteStr,
	int cbMultiByte,
	PWSTR pWideCharStr,
	int cchWideChar);
```
第一个参数为与multibyte字符串（ANSI）相关的code page（好像一般填CP_UTF8）。
第二个参数用于指定一个额外的控制选项，影响带有变音符号（如重音符）的字符；一般都填0。
第三个参数为待转化的字符串。
第四个参数为待转化的字符串的字节数。此参数若填-1，函数会在内部自动计算字符串的长度。
第五个参数（out，optional）存储转化后的宽字符串。
第六个参数为存储转化后字符串的数组的大小。若此参数为0，则该函数不会执行转化，但会返回目标数组所需的大小（以字符为单位），包含'\0'。
返回值：
- 若函数执行失败，返回0；
- 若函数执行成功，则返回转化后的字符串的长度（以字符为单位）。

通常要将ANSI转化为Unicode，可以执行以下：
1. 调用 MultiByteToWideChar 函数，将 pWideCharStr 参数设为 NULL，cchWideChar 参数设为 0，cbMultiByte 参数设为 -1。
2. 分配足够大的内存块来保存转换后的 Unicode 字符串。该大小根据前一次调用 MultiByteToWideChar 返回的值乘以 sizeof(wchar_t) 计算得出。
3. 再次调用 MultiByteToWideChar 函数，这次将缓冲区的地址作为 pWideCharStr 参数传入，并将基于第一次调用 MultiByteToWideChar 返回的值乘以 sizeof(wchar_t) 计算得出的大小作为 cchWideChar 参数传入。
4. 使用转换后的字符串。
5. 释放占用 Unicode 字符串的内存块。

例如：
```c
/* gcc multibyteToWideByte_test.c */
#include <windows.h>
#include <stdio.h>

int main() {
    DWORD ws; // 作为WriteConsoleW的参数（目前还不知何用处）
    const char* mbString = "Hello, 世界！"; // Multibyte character string

    // 第一遍调用MultiByteToWideChar用于获取目标数组所需空间（函数返回值即为所需的空间，单位为字符）
    int requiredSize = MultiByteToWideChar(CP_UTF8, 0, mbString, -1, NULL, 0);
    if (requiredSize == 0) {
        printf("Error in determining buffer size: %d\n", GetLastError());
        return 1;
    }

    // Allocate the destination buffer
    PWCHAR wideString = (PWCHAR)malloc(requiredSize * sizeof(wchar_t));

    // Perform the actual conversion from multibyte to wide-character string
    int result = MultiByteToWideChar(CP_UTF8, 0, mbString, -1, wideString, requiredSize);
    if (result == 0) {
        printf("Error in converting string: %d\n", GetLastError());
        free(wideString);
        return 1;
    }

    // 用Windows api输出unicode字符
    WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE),L"Wide-character string: ", 
        wcslen(L"Wide-character string: "),&ws,NULL);
    WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE),wideString,wcslen(wideString),&ws,NULL);
    WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE),L"\n", wcslen(L"\n"), &ws,NULL);
    

    // Clean up
    free(wideString);

    return 0;
}
```

反过来，从宽字符转窄字符的函数为：
```c
int WideCharToMultiByte(
	UINT uCodePage,
	DWORD dwFlags,
	PCWSTR pWideCharStr,
	int cchWideChar,
	PSTR pMultiByteStr,
	int cbMultiByte,
	PCSTR pDefaultChar,
	PBOOL pfUsedDefaultChar);
```
用法与`MultiByteToWideChar`相似。
不过多了两个参数：
pDefaultChar（optional）：因为宽字符转化成窄字符时，有些宽字符没有对应的窄字符，所以此参数用于指定找不到对应窄字符时使用的默认值。若此参数为NULL，则会使用系统的默认值（书里说是问号符号）。[官网](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-widechartomultibyte)说如果Code Page为CP_UTF7或CP_UTF8，此参数必须为NULL，否则函数执行失败（ERROR_INVALID_PARAMETER）。
> 官网同时提到，可以用GetCPInfo或GetCPInfoEx获取系统的默认值。

pfUsedDefaultChar（out，optional）：当转化过程中有找不到对应值的字符时，此指针指向的值为TRUE，否则为FALSE。

### 扩展1
在动手实践的时候，写了这样的代码：
```c
#include <strsafe.h>
#include <windows.h>

#include <stdlib.h>

#ifndef UNICODE
#define UNICODE
#endif

#ifndef _UNICODE
#define _UNICODE
#endif

int main() {
    WCHAR dest[20] = L"Hello";
    const WCHAR* source = L" World!";

    errno_t result = wcscat_s(dest, _countof(dest), source);

    return 0;
}
```
用mingw的gcc进行编译：
```shell
gcc 宽字符函数.c -municode -l user32 -l kernel32
```
一直遇到报错：
```shell
mingw64/x86_64-w64-mingw32/include/winbase.h:1501:37: error: expected identifier or '(' before 'LPSTR'
 1501 |   WINBASEAPI LPSTR WINAPI lstrcpyA (LPSTR lpString1, LPCSTR lpString2);
      |                                     ^~~~~
```
很纳闷，问了ChatGPT，大概意思是说可能windows.h头文件之前有其它头文件定义了与`LPSTR`相关的宏或类型。因此，要把windows.h放在最前面。
此时我又想起来书里说要把strsafe.h放在最后面。
于是把windows.h放在最前面包含，把strsafe.h放在最后面包含。果然这个报错就没了。

不过还有个bug，好像只要包含了windows.h，程序入口就得改成WinMain了，而且因为我用的是Unicode模式，所以是wWinMain（不知道是UNICODE宏起的作用还是编译选项`-municode`起的作用）。

最后修改为能够编译通过的代码：
```c
#include <windows.h>

#include <stdlib.h>

#include <strsafe.h>
#include <stdio.h>  // wprintf和fwprintf都在此头文件中

#ifndef UNICODE
#define UNICODE
#endif

#ifndef _UNICODE
#define _UNICODE
#endif

int WINAPI wWinMain (HINSTANCE hInstance, HINSTANCE hPrevInstance, LPWSTR lpCmdLine, int nShowCmd) {
    WCHAR dest[20] = L"Hello";
    const WCHAR* source = L" World!";

    errno_t result = wcscat_s(dest, _countof(dest), source);

    if (result == 0) {
        wprintf(L"successed! result: %ls\n", dest);
    } else {
        fwprintf(stderr, L"error! \n");
        wprintf(L"result: %ls\n", dest);
    }

    return 0;
}
```
编译语句为：
```shell
gcc 宽字符函数.c -municode -l user32 -l kernel32
```

为什么不用中文作为输出？实际上这不是装不装逼的问题，而是`wprintf`无法输出中文（详情参考扩展2）！

### 扩展2：windows下输出unicode
C运行时库并不提供Unicode的输出。
但可以调用windows api，WriteConsoleW来实现unicode输出：
```c
wchar_t test[] = L"测试1234";
DWORD ws;
WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE),test,wcslen(test),&ws,NULL);
```
> 引用一下参考链接的回答
1. printf 只能提供ANSI/MB 的输出，不支持输出unicode stream.
例如:
```c
wchar_t test[]=L"测试1234";
printf("%s",test);
```
是不会正确输出的
2. wprintf 同样不会提供unicode output,
但是他会把wchar_t的string转为locale的SB/MB字符编码，然后输出
例如：
```c
wchar_t test[] = L"测试Test";
wprintf(L"%s",test);
```
会输出??1234之类的字符串，或者不输出任何结果
因为wprintf没有办法把L"测试Test"转为默认的ANSI,需要设置locale
```c
setlocale(LC_ALL,"chs");
wchar_t test[] = L"测试Test";
wprintf(L"%s",test);
```
会有正确的输出
等同于`printf("%ls",test);`
综上: CRT I/O functions do not provide Unicode output.
3. Window console自从NT4就是一个真正的unicode console
不过输出unicode string,只有使用Windows API, WriteConsoleW
例如：
```c
wchar_t test[] = L"测试1234";
DWORD ws;
WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE),test,wcslen(test),&ws,NULL);
```
可以正确的输出而不需要设置locale,因为是真正的unicode的输出，跟codepage无关

[参考链接](https://bbs.csdn.net/topics/80484331)

### 扩展3：ATL和MFC类库都用了安全的字符串函数。

### 扩展4：`_countof`和`wcslen`
动手实践的时候发现这两个函数的功能似乎有点像。琢磨了一下，其实他们就是`sizeof`和`strlen`对应的宽字符版本。
```c
// 加上空格共10个字符（不包含'\0'），数组容量为20
const wchar_t wstr[20] = L"Hello, 世界!";  
wprintf(L"%d\n", length);  // 10
wprintf(L"%d\n", _countof(wstr));  // 20
```

### 扩展5：`wsprintf`和`swprintf`
恐怕不仔细根本发现不了这是俩东西。
`wsprintf`意为windows版本的`sprintf`，只支持普通字符（宽字符版本为`wsprintfW`）。
`swprintf`则是C标准库（`whcar.h`中定义）的东西，是宽字符版本的`sprintf`。

还有一些其它细节上的区别，按下不表。