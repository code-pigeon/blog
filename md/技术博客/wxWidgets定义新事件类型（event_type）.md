# wxWidgets定义新事件类型（event type）
首次编辑：2024/8/12/16：51
最后编辑：2024/8/12/

## 引子
在wxWidgets中，有很多事件（events），每个事件类又具有很多不同的事件类型（event types）[^1]。
例如，`wxMouseEvent`是一个鼠标事件，而`wxEVT_LEFT_UP`、`wxEVT_LEFT_DOUN`则是鼠标事件的两个事件类型。

所以说事件是一个类（class），而事件类型是一个枚举值（enum）。

## 自定义事件类型以及使用
1. 创建新的事件类型：
```c++
/* in cpp file */

wxDEFINE_EVENT(MY_NEW_TYPE, wxCommandEvent);
```
> 需要注意这行代码必须写在`.cpp`文件中，不能写在头文件中。

这行代码为`wxCommandEvent`事件创建了新的事件类型。你可以为任何别的事件创建新的事件类型，如`wxMouseEvent`、`wxTimerEvent`等。
不过对于自定义事件类型，通常`wxCommandEvent`就足够了。

2. 向某个控件发送自定义事件类型的事件
```c++
wxCommandEvent event(MY_NEW_TYPE); // 只有一个参数时，该事件类型没有特定的id

// 为事件添加数据
event.SetString(wxT("我是数据"));

// 分送事件
wxPostEvent(this, event);         // 发送给自己
wxPostEvent(p_to_widget, event);  // 发送给p_to_widget指向的控件
```

3. 处理事件
```c++
Bind(MY_NEW_TYPE, &MyWidget::OnMyEvent, this);

void MyWidget::OnMyEvent(wxCommandEvent& event){
    wxLogMessage(wxT("接收到事件，数据为: %s"), event.GetString());
}
```

### 头文件和cpp文件分离的情况
头文件和cpp文件分离的情况下，除了在cpp文件中“定义”事件类型——`wxDEFINE_EVENT(MY_NEW_TYPE, wxCommandEvent)`之外，还需要在头文件中先对事件类型进行“声明”：
```c++
/* in .h file */
wxDECLARE_EVENT(MY_NEW_TYPE, wxCommandEvent);
```
否则虽然编译会通过，但却不会有效果。

### 为事件类型指定id
```c++
// 用枚举值来标识不同的事件id
enum { foo_one = 1, foo_two, foo_three };

wxCommandEvent event_a(MY_NEW_TYPE, foo_one); 
event_a.SetString("data one"); wxPostEvent(this, event_a);

wxCommandEvent event_b(MY_NEW_TYPE, foo_two); 
event_b.SetString("data two"); wxPostEvent(this, event_b);

wxPostEvent(this, event_a); wxPostEvent(this, event_b);
wxPostEvent(p_to_widget, event_b);
```
这种情况下，绑定事件处理函数时，可以在最后一个参数传入事件id：
```c++
Bind(MY_NEW_TYPE, &MyWidget::OnMyEvent1, this, foo_one);
Bind(MY_NEW_TYPE, &MyWidget::OnMyEvent2, this, foo_two);
```

### 完整示例
文件结构
```
├── include
│   ├── App.h
│   └── Panel.h
└── src
    ├── App.cpp
    └── Panel.cpp
```

下面的代码包含4个文件的内容：
```c++
/* ---- App.h ---------------------------------------------------------------------------- */

#include <wx/wx.h>
#include "Panel.h"

class MyFrame : public wxFrame {
public:
    MyFrame();
    void OnCustomEvent(wxCommandEvent& event);
};

class MyApp : public wxApp {
public:
    virtual bool OnInit() {
        MyFrame* frame = new MyFrame();
        frame->Show(true);
        return true;
    }
};

wxIMPLEMENT_APP(MyApp);


/* ---- App.cpp ---------------------------------------------------------------------------- */

#include "App.h"

MyFrame::MyFrame() : wxFrame(NULL, wxID_ANY, "Custom Command Event Example") {
    MyPanel* panel = new MyPanel(this);
    Bind(MY_NEW_TYPE, &MyFrame::OnCustomEvent, this);
}

void MyFrame::OnCustomEvent(wxCommandEvent& event) {
    wxLogMessage("Frame Received Custom Command Event: %s", event.GetString());
}


/* ---- Panel.h ---------------------------------------------------------------------------- */

#include <wx/wx.h>
wxDECLARE_EVENT(MY_NEW_TYPE, wxCommandEvent);

class MyPanel : public wxPanel {
public:
    MyPanel(wxWindow* parent) ;
    void OnButtonClicked(wxCommandEvent& event);
};


/* ---- Panel.cpp ---------------------------------------------------------------------------- */
#include "Panel.h"

wxDEFINE_EVENT(MY_NEW_TYPE, wxCommandEvent);

MyPanel::MyPanel(wxWindow* parent) : wxPanel(parent) {
    // Bind a button to send a custom event
    wxButton* button = new wxButton(this, wxID_ANY, "Send Custom Event");
    button->Bind(wxEVT_BUTTON, &MyPanel::OnButtonClicked, this);
}

void MyPanel::OnButtonClicked(wxCommandEvent& event) {
    wxCommandEvent customEvent(MY_NEW_TYPE);
    customEvent.SetString("Hello from custom command event!");
    wxPostEvent(GetParent(), customEvent);
}
```

## 参考
[^1]: wxWiki [Custom Events/2.1 Events and Event-types](https://wiki.wxwidgets.org/Custom_Events#Events_and_Event-types)