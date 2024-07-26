# Chapter 3：Kernel Objects
## What Is a Kernel Object?
### Usage Counting
Kernel对象属于Kernel。
Kernel对象内部记录了调用自己的进程的数量，当调用Kernel对象的进程数量为0时，Kernel会销毁该Kernel对象。

### Security
Kernel对象受到安全描述符（security descriptor）的保护。security descriptor描述了kernel对象的拥有者（通常是其创建者），哪个组/用户可以访问kernel对象，哪个组/对象不可以。


## A Process' Kernel Object Handle Table

## Sharing Kernel Objects Across Process Boundaries

### Using Object Handle Inheritance

### Naming Objects
许多kernel对象都可以被命名。例如，下面的函数可以创建named kernel objects：
```c
HANDLE CreateMutex(
	PSECURITY_ATTRIBUTES psa,
	BOOL bInitialOwner,
	PCTSTR pszName);
HANDLE CreateEvent(
	PSECURITY_ATTRIBUTES psa,
	BOOL bManualReset,
	BOOL bInitialState,
	PCTSTR pszName);
HANDLE CreateSemaphore(
	PSECURITY_ATTRIBUTES psa,
	LONG lInitialCount,
	LONG lMaximumCount,
	PCTSTR pszName);
HANDLE CreateWaitableTimer(
	PSECURITY_ATTRIBUTES psa,
	BOOL bManualReset,
	PCTSTR pszName);
HANDLE CreateFileMapping(
	HANDLE hFile,
	PSECURITY_ATTRIBUTES psa,
	DWORD flProtect,
DWORD dwMaximumSizeHigh,
	DWORD dwMaximumSizeLow,
	PCTSTR pszName);
HANDLE CreateJobObject(
	PSECURITY_ATTRIBUTES psa,
	PCTSTR pszName);
```
这些函数都有一个共同的参数：pszName。
当传入的实参为NULL时，将创建一个匿名的kernel对象，则只能通过继承、`DuplicateHandle`实现进程间共享kernel对象。
若要创建named kernel对象，则需传入'\0'结尾的字符串的指针，此字符串即为kernel对象的名字。名字最长可以有`MAX_PATH`（260）个字符的长度。

在Windows中，并没有告知开发者kernel对象名字被占用的机制；同时不同类型的kernel对象也都拥有相同的命名空间（这意味着两个不同类型的kernel对象不能有相同的名字）。
因此，下面的代码中，`CreateSemaphore`总是会返回NULL——因为JeffObj这个名字被hMutex占用了。
```c
HANDLE hMutex = CreateMutex(NULL, FALSE, TEXT("JeffObj"));
HANDLE hSem = CreateSemaphore(NULL, 1, 1, TEXT("JeffObj"));
DWORD dwErrorCode = GetLastError();
```
同时`GetLastError()`会返回`ERROR_INVALID_HANDLE`（6）。

接下来看看如何共享kernel对象。

```c
/* in Process A */
HANDLE hMutexProcessA = CreateMutex(NULL, FALSE, TEXT("JeffMutex"));
```

```c
/* in Process B */
HANDLE hMutexProcessB = CreateMutex(NULL, FALSE, TEXT("JeffMutex"));
```
当Process B运行时，系统首先检查"JeffMutex"名字是否已经存在；
若名字已经存在，则检查要创建的kernel对象的类型是否与其一致；
若类型一致，则进行安全检查，检查Process B是否有权限访问该kernel对象；
若有权限，则定位到Process B的句柄表的空行中，新建一个表项，指向已经存在的“JeffMutex”对象。
若类型不一致或者无权限，函数执行失败，返回NULL。
> 所以若当Process B的CreateMutex执行成功，并没有新的kernel对象被创建。只是Process B的句柄表多了一个执行“JeffMutex”对象的表项罢了。

> ps：
kernel对象的创建函数（如`CreateSemaphore`）总是返回有全部权限的句柄。
若想要限制句柄的权限，可以使用扩展版本的创建函数（带有`Ex`后缀），这些函数接收额外的`DWORD dwDesiredAccess`参数。
例如，若想控制semaphore句柄的`ReleaseSemaphore`是否能被调用，可以通过`SEMAPHORE_MODIFY_STATE`的使用与否来实现。

> ps2：
Process B在执行CreateMutex的时候，若已经存在同名的kernel对象，它传入了安全属性信息和第二个参数都会被忽略。
一个进程可以使用如下方法检测创建kernel对象是否已经存在同名kernel对象。
```c
HANDLE hMutex = CreateMutex(&sa, FALSE, TEXT("JeffObj"));
if (GetLastError() == ERROR_ALREADY_EXISTS) {
 // Opened a handle to an existing object.
 // sa.lpSecurityDescriptor and the second parameter
 // (FALSE) are ignored.
} else {
 // Created a brand new object.
 // sa.lpSecurityDescriptor and the second parameter
 // (FALSE) are used to construct the object.
}
```

除了使用`Create*`系的函数来实现kernel对象的共享，还可以使用`Open*`系：
```c
HANDLE OpenMutex( DWORD dwDesiredAccess, BOOL bInheritHandle, PCTSTR pszName);
HANDLE OpenEvent( DWORD dwDesiredAccess, BOOL bInheritHandle, PCTSTR pszName);
HANDLE OpenSemaphore( DWORD dwDesiredAccess, BOOL bInheritHandle, PCTSTR pszName);
HANDLE OpenWaitableTimer( DWORD dwDesiredAccess, BOOL bInheritHandle, PCTSTR pszName);
HANDLE OpenFileMapping( DWORD dwDesiredAccess, BOOL bInheritHandle, PCTSTR pszName);
HANDLE OpenJobObject( DWORD dwDesiredAccess, BOOL bInheritHandle, PCTSTR pszName);
```
`pszName`不能为NULL。执行时，函数会尝试寻找系统中同名的kernel对象。
若没有现存的同名对象，则函数返回NULL，调用GetLastError返回2 （ERROR_FILE_NOT_FOUND）;
若有现存的同名对象，但类型不一致，返回NULL，调用GetLastError返回6（ERROR_INVALID_HANDLE）;
若有现存的同名对象，且类型一致，则检查权限（通过dwDesiredAccess参数）；
执行成功时，进程的句柄表将更新，kernel对象的计数加1。
若bInheritHandle传入的实参为TRUE，则返回的句柄将是可继承的。

`Create*`系和`Open*`系函数的最大不同在于，当同名句柄不存在时，前者会创建一个，但后者直接执行失败。

Named objects经常用于防止一个应用同时运行多个相同进程。
实现这一点，只需要在程序入口处调用一个`Create*`函数（什么类型并不重要）。
紧接着调用`GetLastError`，若返回`ERROR_ALREADY_EXISTS`，则说明该应用已经有其它的实例进程在运行了。
```c
int WINAPI _tWinMain(HINSTANCE hInstExe, HINSTANCE, PTSTR pszCmdLine, int nCmdShow) {
	HANDLE h = CreateMutex(NULL, FALSE,
	TEXT("{FA531CC1-0497-11d3-A180-00105A276C3E}"));
	if (GetLastError() == ERROR_ALREADY_EXISTS) {
		// There is already an instance of this application running.
		// Close the object and immediately return.
		CloseHandle(h);
		return(0);
	}
	// This is the first instance of this application running.
	// ...
	// Before exiting, close the object.
	CloseHandle(h);
	return(0);
}
```

#### Terminal Services Namespaces


### Duplicating Object Handles
第三种进程间共享kernel对象的方法就是DuplicateHandle。简单来说，Catalyst进程调用此函数，该函数会进入源（Source）进程的句柄表的表项，然后将此表项复制到目标（Target）进程的句柄表中。
> 此过程涉及三个进程。

```c
BOOL DuplicateHandle(
	HANDLE hSourceProcessHandle,
	HANDLE hSourceHandle,
	HANDLE hTargetProcessHandle,
	PHANDLE phTargetHandle,
	DWORD dwDesiredAccess,
	BOOL bInheritHandle,
	DWORD dwOptions);
```
调用此函数时，第一个参数和第三个参数都为Process kernel类型的句柄。
> 一个进程被创建时，内核会创建一个唯一对应的process kernel对象用于存储进程的相关信息。

第二个参数是要被复制的源Handle值，此值与源进程相关（意为此Handle值是源进程的句柄表中的Handle值）。
第四个参数（out）是目标进程的句柄表中存放复制的Handle值的表项的地址（地址指被复制的句柄在Target进程的句柄表中的索引值）。
剩余的三个参数用于指示目标进程中复制过来的句柄所使用的访问掩码（access mask）和继承标识（inheritance flag）。
`dwOptions`参数可以为0；或者为以下的数值的任意组合：
- DUPLICATE_SAME_ACCESS：这让目标句柄拥有和源句柄相同的权限（使用此值时，`dwDesiredHandle`会被忽略）。
- DUPLICATE_CLOSE_SOURCE：这会在复制完成后关闭源句柄。

一个奇怪的点是，在Catalyst进程把Handle复制到Target进程之后，Target进程并不知道它对那个Handle有了访问权限。
因此Catalyst必须用某种办法通知Target进程这一点。利用命令行参数或者改变Target进程的环境变量是不可能的——因为Target进程早就存在了。
因此必须使用window message或者其它进程间通信机制（interprocess communication，IPC）。

下面介绍此函数常用的两种用法：
1. Source进程有某Handle的访问权限，Source进程使用此函数将Handle复制到Target进程的句柄表中。
```c
// All of the following code is executed by Process S

// Create a mutex object accessible by Process S.
HANDLE hObjInProcessS = CreateMutex(NULL, FALSE, NULL);
// Get a handle to Process T's kernel object.
HANDLE hProcessT = OpenProcess(PROCESS_ALL_ACCESS, FALSE,
 dwProcessIdT);
HANDLE hObjInProcessT; // An uninitialized handle relative to Process T.
// Give Process T access to our mutex object.
DuplicateHandle(GetCurrentProcess(), hObjInProcessS, hProcessT,
 &hObjInProcessT, 0, FALSE, DUPLICATE_SAME_ACCESS);
// Use some IPC mechanism to get the handle value of hObjInProcessS into Process T.
// ...
// We no longer need to communicate with Process T.
CloseHandle(hProcessT);
// ...
// When Process S no longer needs to use the mutex, it should close it.
CloseHandle(hObjInProcessS);
```
应注意，Source进程一定不能执行`CloseHandle(hObjInProcessT);`，因为hObjInProcessT这个索引值是Target进程的句柄表的索引值，而不是Source进程的。如果执行了这个语句，会关闭Source进程句柄表中索引值为hObjInProcessT的句柄——说不定那是个什么句柄。

2. 某个进程对某Handle有读写权限，但此进程中的某个函数只允许以读权限使用该Handle，此时可以复制该Handle到自己的句柄表中，但控制访问权限为只读，然后让函数使用这个只读的Handle。
```c
int WINAPI _tWinMain(HINSTANCE hInstExe, HINSTANCE,	LPTSTR szCmdLine, int nCmdShow) {
	// Create a file-mapping object; the handle has read/write access.
	HANDLE hFileMapRW = CreateFileMapping(INVALID_HANDLE_VALUE,
		NULL, PAGE_READWRITE, 0, 10240, NULL);
	// Create another handle to the file-mapping object;
	// the handle has read-only access.
	HANDLE hFileMapRO;
	DuplicateHandle(GetCurrentProcess(), hFileMapRW, GetCurrentProcess(),
		&hFileMapRO, FILE_MAP_READ, FALSE, 0);
	// Call the function that should only read from the file mapping.
	ReadFromTheFileMapping(hFileMapRO);
	// Close the read-only file-mapping object.
	CloseHandle(hFileMapRO);
	// We can still read/write the file-mapping object using hFileMapRW.
	// ...
	// When the main code doesn't access the file mapping anymore,
	// close it.
	CloseHandle(hFileMapRW);
}
```
