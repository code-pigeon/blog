# Chapter 4：Processes
## Overview
进程被定义为程序的运行实例（instance），一个进程包含：
- 一个kernel对象，操作系统用此对象管理进程；kernel对象也记录了进程运行的统计信息。
- 一个地址空间，包含所有exe和dll代码和数据，同时也包含动态分配的内存空间（如线程栈和堆）。

## Writing Your First Windows Application

## A Process Instance Handle
所有被装入进程地址空间的exe或dll都被分配了一个唯一的实例句柄（Instance Handle）。
像（w）WinMain的第一个参数（hInstanceExe）就接收exe文件的Instance。

exe或dll的Instance Handle值往往用于加载资源的函数。
例如，加载一个exe或dll中所包含的图标信息：
```c
HICON LoadIcon(
	HINSTANCE hInstance,
	PCTSTR pszIcon);
```
第一个参数为包含要加载的图像的DLL或exe模块的句柄。
第二个参数为要加载的图像名称。
> 此函数已过时。

许多应用都会将`(w)WinMain`的`hInstanceExe`保存为全局变量，以方便随时访问。

> 一些函数的参数可能会出现`HMODULE`这个参数，其实等价于`HINSTANCE`（出现两个不同名字是历史原因）。
```c
DWORD GetModuleFileName(
	HMODULE hInstModule,
	PTSTR pszPath,
	DWORD cchPath);
```

`(w)WinMain`的`hInstanceExe`参数的确切值其实是exe文件在进程空间当中的内存基址（base memory address）。
例如，系统打开exe并将其装载到`0x00400000`地址上，那么`(w)WinMain`的`hInstanceExe`就为`0x00400000`。
exe被装载在哪里取决于链接器（linker），不同linker的策略不同。

```c
HMODULE GetModuleHandle(PCTSTR pszModule);
```
该函数用于获得进程空间中装入的exe或dll的句柄。传入的参数为以“\0”结尾的字符串，表示exe或dll的名字。若找不到该exe或dll，则返回NULL。
传入的参数可以为NULL，这时函数会返回调用此函数的exe文件的基址。
若此函数不在exe中，而是在dll中被调用，则不会返回dll的基址，而是会返回链接了该dll的exe的基址。
若确实想要获得dll的基址，可以有以下两种方式：
1. 利用linker提供的指向当前运行模块基址的伪变量`__ImageBase`；
2. 调用扩展版本——`GetModuleHandleEx`，传入`GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS`作为第一个参数、当前运行模块的地址作为第二个参数，dll的`HMODULE`值将返回给第三个指针参数。
```c
extern "C" const IMAGE_DOS_HEADER __ImageBase;
void DumpModule() {
	// Get the base address of the running application.
	// Can be different from the running module if this code is in a DLL.
	HMODULE hModule = GetModuleHandle(NULL);
	_tprintf(TEXT("with GetModuleHandle(NULL) = 0x%x\r\n"), hModule);
	// Use the pseudo-variable __ImageBase to get
	// the address of the current module hModule/hInstance.
	_tprintf(TEXT("with __ImageBase = 0x%x\r\n"), (HINSTANCE)&__ImageBase);
	// Pass the address of the current method DumpModule
	// as parameter to GetModuleHandleEx to get the address
	// of the current module hModule/hInstance.
	hModule = NULL;
	GetModuleHandleEx(
		GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
		(PCTSTR)DumpModule,
		&hModule);
	_tprintf(TEXT("with GetModuleHandleEx = 0x%x\r\n"), hModule);
}

int _tmain(int argc, TCHAR* argv[]) {
	DumpModule();
	return(0);
}
```

### A Process' Previous Instance Handle
C/C++ run-time startup code总是传入NULL给`(w)WinMain`的`hPrevInstance`参数。所以`(w)WinMain`函数可以写为：
```c
int WINAPI _tWinMain(
	HINSTANCE hInstanceExe,
	HINSTANCE,
	PSTR pszCmdLine,
	int nCmdShow);
```
> 这个参数的存在是历史原因。

### A Process' Command Line
当C run time's startup code开始执行GUI应用时，它会调用`GetCommandLine`获得完整的命令行参数，然后跳过exe文件名，将剩下的参数的地址传给`WinMain`的`pszCmdLine`参数。
你可以写一个指向`pszCmdLine`所指向的缓存的指针，但不要越界——建议将此缓存作为只读缓存，若真的需要修改它，最好复制一个副本再进行修改。
`GetCommandLine`函数可以在程序的任何位置调用，它将返回完整命令行参数。但它返回的指针永远指向那一个地址——这就是为什么建议不要修改这个缓存中的内容。

`CommandLineToArgvW`函数可以将命令行参数（除去exe名称）提取并存储在`argv`数组中。
```c
int argc; 
PWCHAR* argv = CommandLineToArgvW(lpCmdLine, &argc);
for (int i = 0; i < argc; ++i)
{
    wprintf(L"argv[%d] = %s\n", i, argv[i]);
}
```
在上面的例子中，若传入的命令行参数为`-lshell32`和`-lkernel32`，则输出为
```
argv[0] = -lshell32
argv[1] = -lkernel32
```

`CommandLineToArgW`的函数内存会为命令行参数的存储分配空间（在Heap上），多数应用并不释放这些内存——它们依赖操作系统来释放这些空间（在进程结束时）。这是可行的。
若需要手动释放这些空间，可以使用`HeapFree`函数：
```c
int nNumArgs;
PWSTR *ppArgv = CommandLineToArgvW(GetCommandLineW(), &nNumArgs);
// Use the arguments…
if (*ppArgv[1] == L'x') {
	// ...
}
// Free the memory block
HeapFree(GetProcessHeap(), 0, ppArgv);
```

### A Process' Environment Variables
每个进程都有一个与之相关联的环境块（environment block）。
environment block是进程内存中的一块包含一系列如下样子的字符串的内存：
```
=::=::\ ...
VarName1=VarValue1\0
VarName2=VarValue2\0
VarName3=VarValue3\0 ...
VarNameX=VarValueX\0
\0
```
每个字符串都以环境变量名开始，中间一个等于号，再接上环境变量的值。
除了第一行的`=::=::\`之外，可能还有其它行也以等号开头，这些字符串不作为环境变量使用。

有两种方式可以访问environment block：
第一种方式：通过`GetEnvironmentStrings`（在winbase.h头文件中）获得整个environment block。下面的程序将演示如何用此函数获得environment block并提取环境变量。
```c
#include <windows.h>
#include <stdio.h>
#include <strsafe.h>

#ifndef UNICODE
#define UNICODE
#endif

#ifndef _UNICODE
#define _UNICODE
#endif

void DumpEnvStringsW() {
    PWSTR pEnvBlock = GetEnvironmentStringsW();
    // Parse the block with the following format:
    // =::=::\
    // =...
    // var=value\0
    // ...
    // var=value\0\0
    // Note that some other strings might begin with '='.
    // Here is an example when the application is started from a network share.
    // [0] =::=::\
    // [1] =C:=C:\Windows\System32
    // [2] =ExitCode=00000000
    //
    WCHAR szName[MAX_PATH];
    WCHAR szValue[MAX_PATH];
    PWSTR pszCurrent = pEnvBlock;
    HRESULT hr = S_OK;
    PCWSTR pszPos = NULL;
    int current = 0;
    while (pszCurrent != NULL) {
        // Skip the meaningless strings like:
        // "=::=::\"
        if (*pszCurrent != L'=') {
            // Look for '=' separator.
            pszPos = wcschr(pszCurrent, L'=');
            // Point now to the first character of the value.
            pszPos++;
            // Copy the variable name.
            size_t cbNameLength = // Without the' ='
            (size_t)pszPos - (size_t)pszCurrent - sizeof(WCHAR);
            hr = StringCbCopyNW(szName, MAX_PATH, pszCurrent, cbNameLength);
            if (FAILED(hr)) {
                break;
            }
            // Copy the variable value with the last NULL character
            // and allow truncation because this is for UI only.
            hr = StringCchCopyNW(szValue, MAX_PATH, pszPos, wcslen(pszPos)+1);
            if (SUCCEEDED(hr)) {
                wprintf(L"[%u] %s=%s\r\n", current, szName, szValue);
            } else if (hr == STRSAFE_E_INSUFFICIENT_BUFFER) {
                // something wrong happened; check for truncation.
                wprintf(L"[%u] %s=%s...\r\n", current, szName, szValue);
            } else { // This should never occur.
                wprintf(
                    L"[%u] %s=???\r\n", current, szName
                );
                break;
            }
        } else {
            wprintf(L"[%u] %s\r\n", current, pszCurrent);
        }
        // Next variable please.
        current++;
        // Move to the end of the string.
        while (*pszCurrent != L'\0')
            pszCurrent++;
        pszCurrent++;
        // Check if it was not the last string.
        if (*pszCurrent == L'\0')
            break;
    };
    // Don't forget to free the memory.
    FreeEnvironmentStringsW(pEnvBlock);
}

int main(){
    DumpEnvStringsW();
    return 0;
}
```
> `MAX_PATH`定义在`windef.h`头文件中。


获取环境变量的第二种方式只适用于CUI程序——通过main函数的`TCHAR* env[]`参数。
不同于`GetEnvironmentStrings`，`env[]`是一个`PTSTR`的数组，其中每个数组元素都为C风格的字符串，每个字符串都为“envName=envVar”格式的字符串。
此数组中的最后一个元素是一个NULL指针，用于标记数组的结尾。
```c
#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#include <strsafe.h>
#ifndef UNICODE
#define UNICODE
#endif

#ifndef _UNICODE
#define _UNICODE
#endif
void DumpEnvVariables(PTSTR pEnvBlock[]) {
	int current = 0;
	PTSTR* pElement = (PTSTR*)pEnvBlock;
	PTSTR pCurrent = NULL;
	while (pElement != NULL) {
		pCurrent = (PTSTR)(*pElement);
		if (pCurrent == NULL) {
			// No more environment variable.
			pElement = NULL;
		} else {
			_tprintf(TEXT("[%u] %s\r\n"), current, pCurrent);
			current++;
			pElement++;
		}
	}
}

int main(int argc, char const *argv[], PTSTR env[]){
	DumpEnvVariables(env);
	return 0;
}
```

---

当用户登录Windows时，系统会创建一个shell进程，并通过注册表中的两个键（key）来获取环境变量。
第一个键包含系统环境变量：`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment`；
第二个键包含用户环境变量：`HKEY_CURRENT_USER\Environment`。

程序中可以使用一些函数（Windows api）来修改这些注册表项。
当在程序中使用函数（Windows api）来修改注册表时，可以手动发送`WM_SETTINGCHANGE`消息。
```c
SendMessage(HWND_BROADCAST, WM_SETTINGCHANGE, 0, (LPARAM) TEXT("Environment"));
```
有些应用内部对`WM_SETTINGCHANGE`消息进行了响应处理，这些应用可以立即响应注册表的修改（但有些应用不处理`WM_SETTINGCHANGE`，便无法立即生效）。
而对于没有处理`WM_SETTINGCHANGE`消息的程序，要想让修改对其生效，需要注销并重新登录。
> 当使用注册表（regedit.exe）来修改注册表值时，修改完之后系统会自动发送`WM_SETTINGCHANGE`消息。

---

一般子程序可以继承父进程的环境变量（只是完整地复制了一份，若子进程对自己的环境变量进行修改，不会影响到父进程）。
父进程也可以决定继承哪些环境变量给子进程。

---

#### 环境变量相关的函数
`GetEnvironmentVariable`函数：
```c
DWORD GetEnvironmentVariable(
	PCTSTR pszName,
	PTSTR pszValue,
	DWORD cchValue);
```
作用：获取指定的环境变量；
参数一：要获取的环境变量名；
参数二（out）：环境变量的值；
参数三：pszValue指向的缓存的大小；
返回值：环境变量值的大小（单位：字符），若找不到指定的环境变量，返回值为0。
用法：
```c
void PrintEnvironmentVariable(PCTSTR pszVariableName) {
	PTSTR pszValue = NULL;
	// Get the size of the buffer that is required to store the value
	DWORD dwResult = GetEnvironmentVariable(pszVariableName, pszValue, 0);
	if (dwResult != 0) {
		// Allocate the buffer to store the environment variable value
		DWORD size = dwResult * sizeof(TCHAR);
		pszValue = (PTSTR)malloc(size);
		GetEnvironmentVariable(pszVariableName, pszValue, size);
		_tprintf(TEXT("%s=%s\n"), pszVariableName, pszValue);
		free(pszValue);
	} else {
		_tprintf(TEXT("'%s'=<unknown value>\n"), pszVariableName);
	}
}
```

`ExpandEnvironmentStrings`函数：
```c
DWORD ExpandEnvironmentStrings(
	PCTSTR pszSrc,
	PTSTR pszDst,
	DWORD chSize);
```
作用：将形如`%PATH%`的字符串中的`PATH`根据对应的环境变量值展开；
参数：如上一个函数。
用法：
```c
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include "myheader.h"

int main(){
	DWORD chValue = ExpandEnvironmentStringsW(L"PATH='%PATH%'", NULL, 0);
	PWSTR pszBuffer = (PWSTR)malloc((chValue + 1)*sizeof(WCHAR));
	chValue = ExpandEnvironmentStringsW(L"PATH='%PATH%'", pszBuffer, chValue);
	wprintf(L"%s\r\n", pszBuffer);
	free(pszBuffer);
}
```
> 此处用了宽字符版，参数中含有TCHAR、PCTCHAR、PCTSTR等的函数都有对应的宽字符版函数。

`SetEnvironmentVariable`函数：
```c
BOOL SetEnvironmentVariable(
	PCTSTR pszName,
	PCTSTR pszValue);
```
作用：增、删、改，环境变量的值（只对当前进程有效）；
参数一：环境变量名；
参数二（optional）：环境变量的值，当此值为NULL，该环境变量将被删除；

### A Process' Affinity
通常一个进程的线程可以运行在任意CPU上，但这些线程也可以被限制在某几个CPU上运行。
这被称为processor affinity。
子进程会继承父进程的affinity。

### A Process' Error Mode
这是一系列与进程相关联的标志，告诉系统该进程应该怎样对errors做出回应。
这些errors包括：disk media failures、unhandled exceptions、file-find failures、data misalignment。
进程可以通过`SetErrorMode`告诉系统怎么处理这些errors。
```c
UINT SetErrorMode(UINT fuErrorMode);
```
参数`fuErrorMode`可以是以下值或其组合：
|Flag|Description|
|--|--|
|SEM_FAILCRITICALERRORS|The system does not display the critical-error-handler message box and returns the error to the calling process.|
|SEM_NOGPFAULTERRORBOX|The system does not display the general-protection-fault message box. This flag should be set only by debugging applications that handle general protection (GP) faults themselves with an exception handler.|
|SEM_NOOPENFILEERRORBOX|The system does not display a message box when it fails to find a file.|
|SEM_NOALIGNMENTFAULTEXCEPT|The system automatically fixes memory alignment faults and makes them invisible to the application. This flag has no effect on x86/x64 processors.|

默认情况下，子进程继承父进程的Error Mode（但子进程不会知晓这一点）。
父进程可以在调用`CreateProcess`时使用`CREATE_DEFAULT_ERROR_MODE`标志来防止子进程继承Error Mode。

### A Process' Current Drive and Directory
系统会保持对当前启动器（current drive）和当前目录（current directory）的追踪。
进程中任意一个线程改变current drive或current directory都会导致整个进程的current drive 或current directory的改变。

线程可以通过以下两个函数获得或设置current drive and directory：
```c
DWORD GetCurrentDirectory(
	DWORD cchCurDir,
	PTSTR pszCurDir);
BOOL SetCurrentDirectory(PCTSTR pszCurDir);
```
使用方法跟之前的函数差不多，就不赘述了，具体参考官网。
写个示例：
```c
#include <windows.h>
#include <stdio.h>
#ifndef UNICODE
#define UNICODE
#endif

#ifndef _UNICODE
#define _UNICODE
#endif

int main(){
	WCHAR path[MAX_PATH];
    DWORD result = GetCurrentDirectoryW(MAX_PATH, path);
    if (result != 0){
        wprintf(L"Current Path: %s\n", path);
    }else{
        wprintf(L"Something error in GetCurrentDirectoryW! \n");
    }

    BOOL res = SetCurrentDirectoryW(L"D:/DataDisk/");
    if( res == TRUE){
        wprintf(L"Current directory has been changed! \n");
        result = GetCurrentDirectoryW(MAX_PATH, path);
        if (result != 0){
        wprintf(L"Current Path: %s\n", path);
        }else{
            wprintf(L"Something went error in GetCurrentDirectoryW! \n");
        }
    }else{
        wprintf(L"Something went error in SetCurrentDirectoryW! \n");
    }
}
```

### A Process' Current Directories
系统会保持追踪进程的current drive and directory，但不会保持对所有drive的current directory的追踪（可能是说每个drive都会有一个current directory，但对于进程，系统只会追踪其中一个drive的current directory）。
但有些操作系统支持处理多个drive的current directory，这是通过进程的环境字符串（environment strings）实现的。
例如，一个进程有如下两个环境变量（此称为drive-letter环境变量）：
```
=C:=C:\Utility\Bin
=D:=D:\Program Files
```
这表示此进程在C盘的当前目录为`\Utility\Bin`，在D盘的当前目录为`\Program Files`。

调用函数时，若传入了指定了盘符（drive）的文件名，且盘符不是当前盘符（current drive），系统会去环境块（environment block）中寻找与指定盘符相关联的环境变量。若能找到，则系统使用该环境变量的值作为当前目录（current directory）；若找不到，系统会假定指定盘符的根目录为当前目录（current directory）。

比如，进程的当前目录为`C:\Utility\Bin`，而你使用`CreateFile`并传入文件名`D:ReadMe.Txt`（此即为指定了盘符的文件名），系统会寻找名为`=D:`的环境变量。
若`=D:`变量存在，则系统会尝试打开`D:\Program Files\ReadMe.txt`（这里引用了上一个例子）。
若`=D:`变量不存在，则系统假定进程在D盘的当前目录为`D:\`，并尝试打开`D:\ReadMe.txt`。
> windows文件函数永远不会添加或修改drive-letter环境变量，只会读取这些变量的值。

> note
若要改变当前目录，可以使用C运行时函数`_chdir`来代替Windows函数`SetCurrentDirectory`。
`_chdir`函数在内部调用`SetcurrentDirectory`，但`_chdir`也通过`SetEnvironmentVariable`函数增加、修改环境变量，这样不同drive的当前目录得以保留。
（意为：一个进程拥有1、系统设置的当前目录；2、环境变量中的当前目录，使用`SetCurrentDirectory`只能改变前者，并不能使两个当前目录保持一致，而使用`_chdir`则可以。）
（`_chdir`的宽字符版为`_wchdir`。）

#### GetFullPathNameW函数
```c
DWORD GetFullPathNameW(
	_In_ LPCWSTR lpFileName,
	_In_ DWORD nBufferLength,
	_Out_ LPWSTR lpBuffer,
	_Outptr_opt_ LPWSTR* lpFilePart);
```
此函数将返回文件`lpFileName`的完整路径（只会在当前目录下搜索）。
若传入的文件名是盘符（例如`C:`，注意不要加斜杠），则会返回进程在此盘符下的当前目录；
若传入的文件名同时带有盘符（例如`C:myData.txt`，注意同样无斜杠），则会在对应盘符的当前目录下搜索。

#### 我的实践
用`GetCurrentDirectoryW`获得的永远是系统设置的当前目录。
用`GetFullPathNameW`传入盘符获取的当前目录要分情况讨论：
假如传入的盘符与系统设置的当前目录的盘符一致，则返回系统设置的当前目录；
假如传入的盘符与系统设置的当前目录的盘符不一致，则在环境变量中寻找对应盘符的当前目录。

#### 补充说明
> 还有一部分关于当前路径的继承的，没看明白，等后面再补充吧。


### The System Version
> 跳过。

## The CreateProcess Function
```c
BOOL CreateProcessW(
  [in, optional]      LPCWSTR               lpApplicationName,
  [in, out, optional] LPWSTR                lpCommandLine,
  [in, optional]      LPSECURITY_ATTRIBUTES lpProcessAttributes,
  [in, optional]      LPSECURITY_ATTRIBUTES lpThreadAttributes,
  [in]                BOOL                  bInheritHandles,
  [in]                DWORD                 dwCreationFlags,
  [in, optional]      LPVOID                lpEnvironment,
  [in, optional]      LPCWSTR               lpCurrentDirectory,
  [in]                LPSTARTUPINFOW        lpStartupInfo,
  [out]               LPPROCESS_INFORMATION lpProcessInformation
);
```
当线程调用`CreateProcessW`时，系统创建一个进程内核对象（process kernel object），其使用计数（usage count）为1。
此进程内核对象时是操作系统用于管理进程的数据结构。
接着系统创建一个虚拟地址空间（virtual address space），并将代码和数据加载到进程的地址空间上。
接着系统再为进程的主线程（primary thread）创建一个线程内核对象（thread kernel object），其使用计数为1。
同样，线程内核对象是系统用于管理线程的。
这个主线程以执行链接器设置的C/C++运行时启动代码为起点，最终调用WinMain、wWinMain、main或wmain函数。
若系统成功创建新进程和主线程，`CreateProcessW`返回`TRUE`。
> CreateProcess在进程完全初始化之前返回TRUE。这意味着操作系统加载程序尚未尝试定位所有所需的DLL。如果无法找到DLL或无法正确初始化，进程将被终止。由于CreateProcess返回了TRUE，父进程并不知道任何初始化问题。

### pszApplicationName and pszCommandLine
首先看`pszCommandLine`参数，在函数原型中，此函数的类型为`LPWSTR`，而不是`LPCWSTR`，这意味着无法直接传递字符串字面量作为此参数的值，即：
```c
/* 此代码将出错 */

STARTUPINFO si = { sizeof(si) };
PROCESS_INFORMATION pi;
CreateProcess(NULL, TEXT("NOTEPAD"), NULL, NULL,
 FALSE, 0, NULL, NULL, &si, &pi);
```
由于`TEXT("NOTEPAD")`为`const`类型，执行这个代码片段将会出错。

解决方式为，先将命令行参数赋值给非const变量。
```c
STARTUPINFO si = { sizeof(si) };
PROCESS_INFORMATION pi;
TCHAR szCommandLine[] = TEXT("NOTEPAD");
```
之所以需要`pszCommandLine`为非const类型，是因为在`CreateProcess`函数中，`pszCommandLine`将会被修改，但在最终返回时，又会被退回到最初的样子。

`pszCommandLine`参数为包含运行程序所使用的命令行，当`CreateProcess`解析`pszCommandLine`之后，会假定第一个单元为可执行文件的名字。若第一个单元的名字中不带`.exe`后缀，CreateProcess会假定后缀为`.exe`。
`CreateProcess`将按照以下顺序寻找可执行文件：
1. The directory containing the .exe file of the calling process
2. The current directory of the calling process
3. The Windows system directory—that is, the System32 subfolder as returned by GetSystemDirectory
4. The Windows directory
5. The directories listed in the PATH environment variable

上面的这些发生的前提是`pszApplicationName`参数为NULL（99%的情况是这样）。
若不将此参数设定为NULL，你可以传入可执行文件的文件名给此参数（与`pszCommandLine`不同，必须带后缀名，`CreateProcess`不会假定该文件名带有`.exe`后缀）。
`CreateProcess`将在进程的当前文件夹中搜索此文件（除非文件名中包含绝对路径），若搜索不到，函数执行失败（并不会去任何其它地方搜索该可执行文件）。

当`pszApplicationName`不为NULL时，你仍然可以向`pszCommandLine`传递参数，但此时`pszCommandLine`中的内容会被视为命令行参数。
例如：
```c
TCHAR szPath[] = TEXT("main.c -o main");
CreateProcess(TEXT("gcc.exe"),szPath,...);
```
这段代码的作用等同于命令行`gcc.exe main.c -o main`。
### ppiProcInfo
书里按顺序讲了参数，但我感觉先讲最后一个流畅一点。

假设进程A调用`CreateProcess`创建了进程B，系统会为进程B创建一个进程内核对象和一个主线程内核对象。
内核对象都有其对应的句柄（Handle），而`CreateProcess`成功之后，进程B的进程内核对象和主线程内核对象的Handle都会被添加到进程A的句柄表中，进程A通过这些Handle实现对进程B的控制。
所以`ppiProcInfo`参数就用于接收子进程（进程B）的进程内核对象和主线程内核对象的Handle值。
> 系统创建进程B的进程内核对象和主线程内核对象时，这两对象的使用计数初始都为1，而在`CreateProcess`函数内部，因为这两个对象的Handle被添加到了进程A的句柄表中，所以使用计数再加1，变为2。
所以对于这两个对象，在它们自己终止之后，还需要进程A调用`CloseHandle`函数，才能使使用计数减为0，此时这两个对象才能够被系统释放。

它的用法如下：
```c
...
PROCESS_INFORMATION piProcessB;
CreateProcess(..., &piProcessB);
```
`PROCESS_INFORMATION`结构体的原型如下：
```c
typedef struct _PROCESS_INFORMATION {
	HANDLE hProcess;
	HANDLE hThread;
	DWORD dwProcessId;
	DWORD dwThreadId;
} PROCESS_INFORMATION;
```
其中`hProcess`对应进程B的进程内核对象Handle，`hThread`对应进程B的主线程内核对象的Handle值。

内核对象被创建之后都会被分配一个唯一标识符。
进程和线程共用一个ID池，即进程和线程不会拥有同样的ID。
> 内核对象不会被分配到0号ID，在任务管理器中，0号ID被分配给了“System Idle Process”，但这个进程并不存在。
System Idle Process的线程数量总是与CPU的个数相同。

`CreateProcess`函数返回之前，会将进程内核对象和主线程内核对象的ID分别赋值到`dwProcessId`和`dwThreadId`中。
> ID可以方便你在系统中辨别进程和线程。通常只用于utility applications，很少用于productivity applications，所以很多应用直接忽略ID号。

当一个进程/线程的结束时，它的ID号将会给下一个新建的进程/线程使用。所以在使用ID追踪进程/线程时要格外小心。
`GetCurrentProcessId`和`GetCurrentThreadId`分别用于获取当前进程和线程。
提供进程/线程的Handle值，`GetProcessId`和`GetThreadId`可以返回对应的进程/线程ID。
线程可以调用`GetProcessIdOfThread`来获取所属的进程。


### psaProcess, psaThread, and bInheritHandles
进程A创建新进程B时，系统会为进程B创建一个进程内核对象和一个主线程内核对象。


`pasProcess`和`psaThread`用于指定进程和线程对象的安全属性。
这两个参数可以为NULL，这样的话系统会为其设置默认的安全属性。
若不为NULL，需要分配并初始化两个`SECURITY_ATTRIBUTES`结构体，用于指定进程和线程的安全权限。
另一个使用`SECURITY_ATTRIBUTES`的原因是让进程或线程对象句柄可以被以后所创建的子进程继承。