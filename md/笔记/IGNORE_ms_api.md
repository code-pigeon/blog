## 窗口
### 管理应用程序状态
窗口过程只是针对每条消息调用的函数，因此它本质上是无状态的。因此，需要一种方法来跟踪应用程序从一个函数调用到下一个函数调用的状态。
CreateWindowEx 函数提供了一种将任何数据结构传递到窗口的方法。 调用此函数时，它会将以下两条消息发送到窗口过程：
- WM_NCCREATE
- WM_CREATE
这些消息按列出的顺序发送。 (这并非 在 CreateWindowEx 期间发送的唯一两条消息，但我们可以忽略此讨论的其他消息。)

WM_NCCREATE和WM_CREATE消息在窗口可见之前发送。 它们可以很好地应用于初始化 UI（例如，确定窗口的初始布局）。
CreateWindowEx 的最后一个参数是 void* 类型的指针。 可以在此参数中传递所需的任何指针值。 当窗口过程处理 WM_NCCREATE 或 WM_CREATE 消息时，它可以从消息数据中提取此值。

自定义一个状态信息的类或结构：
```c++
struct StateInfo {
	// ... (struct members not shown)
};
```
调用 CreateWindowEx 时，在末尾的 void* 参数中传递指向此结构的指针。
```c++
// std::nothrow的作用是让对象创建失败时不抛出异常，而是返回NULL指针。
StateInfo *pState = new (std::nothrow) StateInfo;
if (pState == NULL){
	return 0;
}
// Initialize the structure members (not shown).
HWND hwnd = CreateWindowEx(
	0, // Optional window styles.
	CLASS_NAME, // Window class
	L"Learn to Program Windows", // Window text
	WS_OVERLAPPEDWINDOW, // Window style
	// Size and position
	CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,
	NULL, // Parent window 
	NULL, // Menu
	hInstance, // Instance handle
	pState // Additional application data
);
```

```
   MSG消息
+-----------+
| WM_CREATE |
+-----------+
|  wParam   |------> Not used
+-----------+
|  lParam   |------>  +----------------+
+-----------+         |  CREATESTRUCT  |
                      +----------------+
                      | lpCreateParams |------->  +-----------+
                      +----------------+          | StateInfo |
                      |      ...       |          |           |
                      +----------------+          +-----------+
```
因此，在消息中提取StateInfo的方法为：
```c++
CREATESTRUCT *pCreate = reinterpret_cast<CREATESTRUCT*>(lParam);
pState = reinterpret_cast<StateInfo*>(pCreate->lpCreateParams);
```

## COM
### 初始化单线程的COM库
```c
// HRESULT 返回类型包含错误或成功代码。 我们将在下一部分中介绍 COM 错误处理。
HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED | COINIT_DISABLE_OLE1DDE);
```
其中第一个参数为保留参数，必须为NULL；
第二个参数指定程序将使用的线程模型：①单元线程：COINIT_APARTMENTTHREADED；②多线程：COINIT_MULTITHREADED；
> 除了前面提到的标志外，最好在 dwCoInit 参数中设置 COINIT_DISABLE_OLE1DDE 标志。
设置此标志可避免与对象链接和嵌入 (OLE) 1.0（一种过时的技术）关联的一些开销。

### 取消初始化COM库
```c
CoUninitialize();
```
每次成功调用CoInitializeEx时，都必须在线程退出之前调用CoUninitialize。此函数不采用任何参数，并且没有返回值。

### COM中的错误代码
为了指示成功或失败，COM方法和函数返回HRESULT类型的值。HRESULT是32位整数。HRESULT的高阶位表示成功或失败。零(0)表示成功，1表示失败。
这会生成以下数值范围：
- 成功代码：0x0-0x7FFFFFFF。
- 错误代码：0x80000000–0xFFFFFFFF。

> 少数COM方法不返回HRESULT值。例如，AddRef和Release方法返回无符号的长值。但是，每个返回错误代码的COM方法都通过返回HRESULT值来执行此操作。

若要检查COM方法是否成功，请检查返回的HRESULT的高阶位。Windows SDK标头提供了两个使此操作更简单的宏：SUCCEEDED宏和FAILED宏。如果HRESULT是成功代码，则SUCCEEDED宏返回TRUE;如果它是错误代码，则返回FALSE。以下示例检查CoInitializeEx 是否成功。

```c++
HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED | COINIT_DISABLE_OLE1DDE);
if (SUCCEEDED(hr))
{
 // The function succeeded.
}
else
{
 // Handle the error.
}
```

FAILED宏与SUCCEEDED相反。对于错误代码，它返回TRUE，对于成功代码，则返回FALSE。
```c++
HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED | COINIT_DISABLE_OLE1DDE);
if (FAILED(hr))
{
 // Handle the error.
}
else
{
// The function succeeded.
}
```

### COM的公共接口
每个COM接口都必须直接或间接继承自名为IUnknown的接口。
IUnknown接口定义了三种方法：
- QueryInterface
- AddRef
- Release

### COM的强转
先有一个FileOpenDialog的指针，要强转为FileDialogCustomize指针，需要使用QueryInterface接口。
- riid参数是标识要请求的接口的GUID。数据类型REFIID是的const GUID& typedef。请注意，不需要CLSID) (类标识符，因为对象已创建。只需要接口标识符。
- ppvObject参数接收指向接口的指针。此参数的数据类型为void**，原因与CoCreateInstance使用此数据类型的原因相同：QueryInterface可用于查询任何COM 接口，因此不能强类型化参数。
```c++
hr = pFileOpen->QueryInterface(IID_IFileDialogCustomize, reinterpret_cast<void**>(&pCustom));
if (SUCCEEDED(hr))
{
	// Use the interface. (Not shown.)
	// ...
	pCustom->Release();
}
else
{
	// Handle the error.
}

```

### COM中的内存分配
COM定义了一对函数，用于分配和释放堆上的内存。
- CoTaskMemAlloc 函数分配内存块。
- CoTaskMemFree 函数释放使用 CoTaskMemAlloc 分配的内存块。
```c++
PWSTR pszFilePath;
// 在GetDisplayName内部调用了CoTaskMemAlloc，分配给pszFilePath
hr = pItem->GetDisplayName(SIGDN_FILESYSPATH, &pszFilePath);
if (SUCCEEDED(hr))
{
	// ...

	// 调用方负责把分配的内存释放掉
	CoTaskMemFree(pszFilePath);
}
```

### COM错误处理
|常数|数值|说明|
|---|---|---|
|E_ACCESSDENIED|0x80070005|访问被拒绝。|
|E_FAIL|0x80004005|错误。|
|E_INVALIDARG|0x80070057|参数值无效。|
|E_OUTOFMEMORY|0x8007000E|内存不足。|
|E_POINTER|0x80004003|错误地为指针值传递|NULL。|
|E_UNEXPECTED|0x8000FFFF|意外情况。|
|S_OK|0x0|成功。|
|S_FALSE|0x1|成功。|

前缀为“E_”的所有常量都是错误代码。 S_OK和S_FALSE常量都是成功代码。 可能 99% 的COM 方法在成功时返回 S_OK ;但不要让这个事实误导你。 方法可能会返回其他成功代码，因此始终使用`SUCCEEDED`或`FAILED`宏测试错误。
以下示例代码演示了测试函数调用是否成功的错误方式和正确方法。
```c++
// Wrong.
HRESULT hr = SomeFunction();
if (hr != S_OK)
{
	printf("Error!\n"); // Bad. hr might be another success code.
}
// Right.
HRESULT hr = SomeFunction();
if (FAILED(hr))
{
	printf("Error!\n"); 
}
```
S_FALSE的成功代码值得提及。 某些方法使用 S_FALSE 来大致表示非失败的负条件。 它还可能指示“no-op”-该方法成功，但没有效果。 例如，如果从同一线程再次调用CoInitializeEx 函数，则返回 S_FALSE 。 如果需要区分代码中的S_OK和 S_FALSE ，则应直接测试值，但仍使用 FAILED 或 SUCCEEDED 来处理剩余情况，如以下示例代码所示。
```c++
if (hr == S_FALSE)
{
	// Handle special case.
}
else if (SUCCEEDED(hr))
{
	// Handle general success case.
}
else
{
	// Handle errors.
	printf("Error!\n"); 
}

```
某些 HRESULT 值特定于 Windows 的特定功能或子系统。 例如，Direct2D 图形 API 定义D2DERR_UNSUPPORTED_PIXEL_FORMAT错误代码，这意味着程序使用的像素格式不受支持。 MSDN 文档通常提供方法可能返回的特定错误代码列表。 但是，不应认为这些列表是明确的。 方法始终可以返回文档中未列出的 HRESULT 值。 同样，请使用SUCCEEDED 和 FAILED 宏。 如果测试特定错误代码，则还包括默认情况。

### 错误处理模式
应遵守的规则：
- 对于返回 HRESULT 的每个方法或函数，检查返回值，然后再继续。
- 使用资源后释放资源。
- 请勿尝试访问无效或未初始化的资源，例如 NULL 指针。
- 释放资源后，请勿尝试使用资源。

考虑到这些规则，下面是用于处理错误的四种模式。
- 嵌套 ifs
- 级联 ifs
- 跳转失败
- 失败时引发

#### 嵌套ifs
每次调用返回 HRESULT 后，请使用 if 语句来测试是否成功。 然后，将下一个方法调用置于 if 语句的范围内。 更多 if 语句可以根据需要嵌套得更深。 
本模块中前面的代码示例都使用了此模式，但此处再次显示：
```c++
HRESULT ShowDialog()
{
	IFileOpenDialog *pFileOpen;
	HRESULT hr = CoCreateInstance(__uuidof(FileOpenDialog), NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pFileOpen));
	if (SUCCEEDED(hr))
	{
		hr = pFileOpen->Show(NULL);
		if (SUCCEEDED(hr))
		{
			IShellItem *pItem;
			hr = pFileOpen->GetResult(&pItem);
			if (SUCCEEDED(hr))
			{
				// Use pItem (not shown). 
				pItem->Release();
			}
		}
		pFileOpen->Release();
	}
	return hr;
}

```