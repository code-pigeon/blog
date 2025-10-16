---
title: 【unity3D学习记录】FPS角色交互
date: 25-04-23 22:33
---

*环境：Unity 2023.2.20f1c1*

在[上一期学习记录中](unity3D_FPS_game_movement.html)，我们完成了FPS游戏的角色的移动、跳跃、镜头旋转的功能。但此时角色和环境唯一的互动方式就是可以踩在某个东西上，这显然非常的无聊。

在这一期学习记录中，我将介绍一下如何实现角色和其它物体的交互。

本期将要实现的场景为：角色与开关（keypad）交互打开大门。

闲话少叙，进入正题。


## 创建场景
你可以像我一样创建一堆不同的Cube，中间两片作为门，旁边贴一小片作为开关。

![图片：简单的场景]({{img_url}}Snipaste_2025-04-23_22-49-56.jpg "简单的场景")

可以把两个门用放在一个空的Object下。

![图片：场景的Hierarchy]({{img_url}}Snipaste_2025-04-23_22-52-46.jpg "场景的Hierarchy")

## 创建Interactable基类
在游戏里，可以和玩家互动的东西应当有很多（物品/敌人等等），它们的共同点当然就是能与玩家互动，所以可以抽象出它们的共同基类，命名为`Interactable`。

新建一个`Interactable.cs`脚本，键入以下内容：
```cs
/* Interactable.cs */
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public abstract class Interactable : MonoBehaviour{
    public string promptMessage;

    public void BaseInteract(){
        Interact();
    }

    protected virtual void Interact(){

    }
}
```
这些代码实现了一个抽象类，它规定了一个接口`BaseInteract`，并且预留了一个扩展点，子类可以通过重写`Interact`来实现不同的行为。
而`prompMessage`则用于存储提示词，提示玩家如何与物体进行交互。

> 为什么要设计一个`BaseInteract`里作为公共接口，再在公共接口里调用`Interact`的形式呢，直接把`Interact`作为公共借口不行吗，反正子类也还是可以重写`Interact`。
> 
> 假如真的这么做了，就像下面这样：
> ```cs
> public abstract class Interactable : MonoBehaviour{
>  
>     public virtual void Interact(){
> 
>     }
> }
> ```
> 那么当有朝一日，老板突然说要在`Interact`执行之前输出日志，于是牛马们彻底傻眼了，每个子类都要加一遍。
> 但如果是前面的代码写法，那么只需要在父类的`BaseInteract`中，调用`Interact`之前写上输出日志的代码就行了，一次修改，所有子类都生效。
> ```cs
> public abstract class Interactable : MonoBehaviour{
>  
>     public void BaseInteract(){
> 	      // 在这里输出日志
>         Interact();
>     }
> 
>     protected virtual void Interact(){
> 
>     }
> ```
> 这属于设计模式中的“模板方法模式”。

## Interactable的子类Keypad
接下来我们实现一下`Interactable`的子类`Keypad`类，作为我们前面搭好的场景中的门开关Keypad的脚本。
```cs
/* Keypad.cs */
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Keypad : Interactable
{
    protected override void Interact(){
        Debug.Log(promptMessage);
    }
}
```
目前它相当简单，就是重写了一下父类规定的私有接口。

最后记得把`Keypad.cs`作为组件添加给场景中的Keypad，然后给组件中的`promptMessage`（继承于`Interactable`）先随便添加一段话。

## 创建PlayerInteract脚本
现在有了能够与玩家交互的物体，那么玩家要怎么探测到它们呢？我们需要创建脚本`PlayerInteract.cs`，它的功能是探测可交互的物体，并处理交互逻辑。

在FPS游戏里，玩家一般通过屏幕中间的准心来探测物体，因此需要在脚本中引用一下玩家的镜头。
```cs
/* PlayerInteract.cs */
private Camera cam;

void Start(){
    // 因为在PlayerLook脚本中已经引用过Camera了，可以直接去PlayerLook中拿。
    cam = GetComponent<PlayerLook>().Cam;
}
```
但我们怎么知道镜头中心看到的物体是什么呢？

Unity中提供了一个`Ray`类，顾名思义表示一条射线，还提供了一个`Physics.Raycast`函数：
```cs
bool Physics.Raycast(Ray ray, out RaycastHit hitInfo, float maxDistance, int layerMask);
```
它能够探测射线在`maxDistance`的距离内是否hit到了属于`layerMask`的物体，如果是，就返回`True`，并把此次的hit记录到`hitInfo`中。

这里的`layerMast`是每一个场景中的物体都拥有的属性，Unity主窗口右边的Inspector右上方可以看到一个叫Layer的下拉菜单。

我们可以点击它，可以看到有一些默认的Layer。为了给可交互的物体单独进行区分，我们点击下拉菜单最下方的“Add Layer”，在User Layer 6的位置键入“Interactable”。

然后点击前面搭场景时做好的Keypad，在Inspector里把Layer修改为“Interactable”。

现在我们有了属于“Interactable”的Keypad开关，有了相机，于是可以通过从相机的位置发射出一条射线，检查这条射线是否hit到了“Interactable”的Keypad，如果是，那么就进行交互逻辑的编写。

回到`PlayerInteract.cs`脚本中，新增以下内容：
```cs
[SerializeField]
private float distance = 3f;    // 射线能够探测的最大范围
[SerializeField]
private layerMask mask;

void Update(){
    // 以相机为原点，朝着相机正方向发射的射线
    Ray ray = new Ray(cam.transform.position, cam.transform.forward);

    RaycastHit hitInfo; // 存放hit信息
    if ( Physics.Raycast(ray, out hitInfo, distance, mask) ){
        // 获取被射线hit到的物体
        Interactable interactable = hitInfo.collider.GetComponent<Interactable>();
        if ( interactable != null ){
            // 如果确实hit到了一个Interactable，那么就调用它的交互函数
            interactable.BaseInteract();
        }
    }
}
```
*测试*：
现在可以运行游戏，走到Keypad面前看着它，应当会在控制台输出Keypad的`promptMessage`。

## 创建UI界面
很显然，上面的结果并没有特别好的游戏体验，作为一个FPS游戏，它居然没有靶子！而我们在与Keypad交互时，完全是用人脑来感知画面中心的。

而且交互的信息现在还只能在控制台打印，而我们需要的是在游戏画面中显示出提示词，否则真的把游戏打包好了，玩家又看不到控制台。

所以这时候需要请出我们的UI界面。

在Unity主窗口右边的Hierarchy点击鼠标右键，点击“UI”，接着点击“Text-TextMeshPro”。如果是第一次用它，可能会提示需要安装，安装就行了。

创建完TextMeshPro之后，在右边的Inspector中可能出现一个红色的感叹号，下面有一个按钮“Replace with InputSystemUIInputiModule”，点击就行了。（大概的意思是说我们使用了新的Input System，这个TextMeshPro却是为旧的InputSystem设计的，需要替换掉某些东西）


！!todo：这里还有一个很无聊的步骤，等后面再补充。


可以看到“TextMeshPro”是位于一个叫“Canvas”的物体中的，说明在创建“TextMeshPro”，首先需要创建一个画布。

我们把这个“TextMeshPro”重命名为“promptText”。并把文本的位置移动到你想要的位置。

接着创建一个准心，我们可以右键点击“Canvas”，接着先后点击UI和Image。将它重命名为“Crosshair”。然后在右边的Inspector中把它的x、y、z都调整为0（将它置于屏幕正中心），把宽、高调整到自己的满意的大小，接着在下面的“Source Image”把图片换成一个圆形。这样一个简易的准心就做好了。

## 创建UI脚本
在`PlayerInteract.cs`中，玩家能够探测到Interactable，并进行交互，所以应该能够在`PlayerInteract.cs`中操作到UI界面的“promptText”，这样才能提示玩家如何与物体进行交互。

不过为了理清脚本责任及让代码清晰，我们要创建一个单独的`PlayerUI.cs`脚本来管理UI界面。

```cs
/* PlayerUI.cs */
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;    // 别忘了导入这个，否则引用不了“promptText”

public class PlayerUI : MonoBehaviour
{

    // 引用UI界面里的“promptText”
    [SerializeField]
    private TextMeshProUGUI promptText;

    public void UpdateText(string promptMessage){
        promptText.text = promptMessage;
    }
}
```
别忘了把这个脚本拖动到Player里，并且把“promptText”拖到此脚本的promptText中。

这样一来，`PlayerInteract.cs`中只需要引用一下这个`PlayerUI`，每次探测到可交互的物体时，就让`PlayerUI`调用一下`UpdateText`就行了。

```cs
private PlayerUI playerUI;
// ...

void Start(){
    playerUI = GetComponent<PlayerUI>();
    // ...
}

void Update(){
    playerUI.UpdateText(string.Empty);  // 将UI的promptMessage初始化为空

    Ray ray = new Ray(cam.transform.position, cam.transform.forward);

    RaycastHit hitInfo;
    if ( Physics.Raycast(ray, out hitInfo, distance, mask) ){
        Interactable interactable = hitInfo.collider.GetComponent<Interactable>();
        if ( interactable != null ){
            // 当玩家探测到Interactable时，UI界面显示提示信息
            playerUI.UpdateText(interactable.promptMessage);
        }
    }
}
```

## 交互Action
玩家探测到了Interactable是否代表他一定要交互呢？No，所以需要再创建一个交互的按键。

在“PlayerInput”中添加新的Action——Interact，按键设置为E。

是的，涉及到输入，又得请出`InputManager`老祖了，不过这次是在`PlayerInteract.cs`中请它。

```cs
private InputManager inputManager;
void Start(){
    // ...

    inputManager = GetComponent<InputManager>();
}
void Update(){
    playerUI.UpdateText(string.Empty);

    Ray ray = new Ray(cam.transform.position, cam.transform.forward);

    RaycastHit hitInfo;
    if ( Physics.Raycast(ray, out hitInfo, distance, mask) ){
        Interactable interactable = hitInfo.collider.GetComponent<Interactable>();
        if ( interactable != null ){
            playerUI.UpdateText(interactable.promptMessage);

            // 当玩家按下E键——玩家主动进行交互，则触发交互行为
            if (inputManager.onFoot.Interact.triggered ){
                interactable.BaseInteract();
            }
        }
    }
}
```
这时可能会报错，因为`inputManager.onFoot`是个私有的属性，我们需要回到`InputManager.cs`中把它改为`public`的属性。

