---
title: 【unity3D学习记录】FPS角色移动
date: 25-04-18 22:49
---

*环境：Unity 2023.2.20f1c1*


## 新系统的安装
1. 点击上方的*Window*选项卡，在下拉菜单中选择*Package Manager*；
2. 在弹出的窗口中，选择*Unity Registry*，然后在右侧搜索框中输入*Input System*；
3. 在最右边的面板中点击*Install*按钮；

## 创建并配置Input Actions
可以在*Assets*下新建一个*input*文件夹，用于存放自己创建的*Input Actions*。

怎么创建*Input Actions*呢，在*input*文件夹中，右键 -> 点击*create* -> 滑到最下面，点击*Input Actions*（随便起个名，这里我们取名为`PlayInput`）。

这时候应该会出现一个图标里带有蓝色闪电的文件，双击点开它，会出现一个新的窗口。

在最左侧的*Action Maps*，点击*+*号，新建一张输入映射表。
然后中间的*Actions*面板中会出现一个新的动作，在最右侧的*Action Properties*中，可以看到这个动作的*Action Type*，默认是*Button*，在处理移动逻辑时我们需要把它改成*Pass Through*。此时下面会多出来一个*Control Type*的下拉菜单，我们选择*Vector2*，因为角色在地面上的移动方向是一个二维的向量。

现在我们已经有了动作，还需要为动作添加按键的输入。在中间的*Actions*的动作中，如果正确设置了*Control Type*为*Vector2*，那么点击右边的*+*号，应该会出现*Add Up\Down\Left\Right Composite*（或者是*Add 2D Vector Composite*，不同版本显示不同）。
这时在动作下面会出现四个粉色的按键绑定，分别是“Up\Down\Left\Right”，点击它们，然后在右侧的*Binding Properties*中选择*Binding*的*Path*，可以搜索按键来添加按键绑定，比如*Up*对应*W\[Keyboard\]*；也可以点击*Listen*，然后直接按下你想绑定的按键，Unity会自动捕捉你的按键。

把所有按键都绑定完之后，还需要点击`Save Asset`进行保存。

接着还需要到unity主窗口的`Inspector`中勾选`Generate C# Class`，然后点击`Apply`，这将为我们自动生成Action的脚本（前面我们已经把我们的Input Action取名为`PlayerInput`了，所以会生成同名的脚本）。

## Input Actions和C#的对应
比方说，创建了一个叫`PlayerInput`的Input Action，叫`OnFoot`的Action Map，和叫`Movement`的Action，那么只要在C#脚本中引入了`InputSystem`：
```cs
using UnityEngine.InputSystem;
```
那么就能够引入下面的C#类：

|               | Input Actions | Action Map         | Actions                     |
|---------------|---------------|--------------------|-----------------------------|
| Input Actions | PlayerInput   | OnFoot             | Movement                    |
| C# class      | PlayerInput   | PlayerInput.OnFoot | PlayerInput.OnFoot.Movement |

比方说，新建一个`PlayerInput`对象：
```cs
playerInput = new PlayerInput();
playerInput.Enable();	// 启用这个Input Action
```
获得输入的值：
```cs
playerInput.OnFoot.Movement.ReadValue<Vector2>();
```
这里之所以是`ReadValue<Vector2>`是因为前面设置了Action的Control Type为`Vector2`，这里的实际类型要根据这个Control Type而定。

比如如果Control Type是简单的Button，那么应该换成
```cs
// 用float表示按下的程度，1表示完全按下，0表示没按
ReadValue<float>()	
// 或者只需要“按下”或者“没按下”两种情况，可以使用
ReadValueAsButton(); 	// 这会返回bool类型
```

前面都是一些准备工作，接下来才是核心部分。

## 新建一个Capsule作为Player
这里用`Capsule`作为Player来进行演示，在Unity左边的Hierarchy面板上，右键 -> 选择`3D Object` -> 选择`Capsule`，命名为`Player`。并且把`Main Camera`拖入`Player`，作为玩家的视角。

接着点击`Player`，在右边的`Inspector`面板中，找到`Capsule Collider`，我们暂时不需要它，就先把它删除掉。然后点击`Add Component`，搜索`Character Controller`，点击创建一个组件，我们需要用它来实现角色的移动控制。

## 角色在地面上的移动
我们需要两个C#脚本：

| InputManager.cs | PlayerMotor.cs |
|-----------------|----------------|
|   获取玩家输入   | 处理角色的移动  |

首先来处理一下`PlayerMotor.cs`，首先要获取一下前面给角色添加的组件`CharacterController`：
```cs
private CharacterController controller;
void Start()
{
    controller = GetComponent<CharacterController>();
}
```
然后，还需要给角色设置一个移动速度：
```cs
public float speed = 5f;
```

接着创建一个函数，它接收输入的`Vector2`作为参数，然后根据这个参数让角色进行移动：
```cs
public void ProcessMove(Vector2 input){
	// 因为是3D空间，角色的移动方向实际上是个3D向量
    Vector3 moveDirection = Vector3.zero;
    moveDirection.x = input.x;
    moveDirection.z = input.y;	// 3D游戏里y是垂直于地面的轴

    // speed * Time.deltaTime就是在一帧里移动的距离
    // moveDirection是角色移动的方向（局部坐标系）
    // transform.TransformDirection()将局部坐标系转换到世界坐标系下
    // controller.Move()对角色进行移动
    controller.Move(transform.TransformDirection(moveDirection) * speed * Time.deltaTime);
}
```

> 这里的`Time`是Unity引擎提供的全局静态类；
> 而`transform`则是继承`MonoBehaviour`的脚本自动拥有的组件，属于成员实例；

目前`PlayerMotor.cs`的内容为：
```cs
public class PlayerMotor : MonoBehaviour
{
    private CharacterController controller;
    public float speed = 5f;

    // Start is called before the first frame update
    void Start()
    {
        controller = GetComponent<CharacterController>();
    }

    //  receive the inputs for ours InputManager.cs and apply them to our character controller.
    public void ProcessMove(Vector2 input){
        Vector3 moveDirection = Vector3.zero;
        moveDirection.x = input.x;
        moveDirection.z = input.y;

        controller.Move(transform.TransformDirection(moveDirection) * speed * Time.deltaTime);
    }
}
```

接下来看看`InputManager.cs`。

创建了`InputManager.cs`之后，Unity会为我们自动填充一些基本的代码，但我们还需要在最顶端导入Input System，这样才能使用新的输入系统：
```cs
using UnityEngine.InputSystem;
```

然后我们需要在这个脚本中引用一下我们之前创建好的Input Action（`PlayInput`类）和它的Action Map（`OnFoot`），另外还需要引用一下我们刚刚创建的`PlayerMotor`：
```cs
/* InputManager.cs */

public class InputManager : MonoBehaviour
{
    private PlayerInput playerInput;
    private PlayerInput.OnFootActions onFoot;

    private PlayerMotor motor;

    void Awake()
    {
        playerInput = new PlayerInput();
        onFoot = playerInput.OnFoot;
        // PlayerMotor脚本最后会附加到Player上，可以用GetComponent获取
        motor = GetComponent<PlayerMotor>();
    }

}
```
默认情况下，`onFoot`是disable状态的，我们需要手动开启：
```cs
private void OnEnable(){
    onFoot.Enable();
}

private void OnDisable(){
    onFoot.Disable();
}
```

每一帧都需要获取一下输入，并更新位置
```cs
void FixedUpdate()
{
    motor.ProcessMove(onFoot.Movement.ReadValue<Vector2>());
}
```

> 为什么是FixedUpdate而不是Update呢？
> 
> Update是每一帧会执行一次，但这个帧率可能随设备的不同而变动。但FixedUpdate则会有一个固定的调用频率。
>
> 根据deepseek的说法，FixedUpdate处理物理相关的逻辑（避免因为帧率太低而导致物理漏判等），Update里处理非物理相关的逻辑，是一个黄金法则。

所以完整的代码为：
```cs
using UnityEngine.InputSystem;

public class InputManager : MonoBehaviour
{
    private PlayerInput playerInput;
    private PlayerInput.OnFootActions onFoot;

    private PlayerMotor motor;

    void Awake()
    {
        playerInput = new PlayerInput();
        onFoot = playerInput.OnFoot;    
        motor = GetComponent<PlayerMotor>();
    }

    void FixedUpdate()
    {
        // tell the playermotor to move using the value from our movement action
        motor.ProcessMove(onFoot.Movement.ReadValue<Vector2>());
    }

    private void OnEnable(){
        onFoot.Enable();
    }

    private void OnDisable(){
        onFoot.Disable();
    }

}
```

最后，把这两个脚本都拖拽到Player上，就可以实现角色的移动了。

*测试*：
可以新建一个Cube作为地面，测试一下角色在地面上的移动。


## 加入重力
在上面的处理中并没有考虑到重力的作用，我们现在来添加一下。

首先是重力导致角色的掉落。

掉落是因为角色没有“站在地面上”，所以我们需要一方法来判断角色是否在地面上。好在这非常的方便，因为我们在上一步中已经给角色添加了一个`CharacterController`组件了，可以用它的`isGrounded`属性来判断：
```cs

public class PlayerMotor: MonoBehaviour{
    private CharacterController controller;     // 这是前面已经写过的
    private bool isGrounded;    // 新建这个成员变量来保存是否在地面上
    // ... 省略其它代码

    void FixedUpdate(){
        // 我们需要以固定的频率来获取角色的（是否在地面上的）状态
        isGrounded = controller.isGrounded;
    }

    // ... 省略其它代码
}
```

那么如果没有在地面上，会以什么样的方式掉落呢？死去的中学物理知识召唤术！角色会竖直向下掉落，并且速度不断增加，具体来说，速度变化率为`g ≈ -9.8m/s²`，也就是重力加速度`gravity`。
```cs
/* PlayerMotor.cs */
public class PlayerMotor: MonoBehaviour{
    // ... 省略其它代码
    private float gravity = -9.8f;  // 新建重力加速度
    // ... 省略其它代码
}
```
重力加速度是往下的，所以前面会有一个负号。

接下来就是在`ProcessMove`中添加一下角色掉落的逻辑了：
```cs
/* PlayerMotor.cs */

public void ProcessMove(Vector2 input){
    Vector3 moveDirection = Vector3.zero;
    moveDirection.x = input.x;
    moveDirection.z = input.y;

    controller.Move(transform.TransformDirection(moveDirection) * speed * Time.deltaTime);

    // 以下为新增的代码

    // 角色受到重力影响，速度以g的加速度不断增加
    playerVelocity.y += gravity * Time.deltaTime;

    // 假如角色在地面上，且不处于跳跃状态（这里是未雨绸缪，加入跳跃逻辑之后，y方向速度就可能大于0了）
    // 那么就把角色向下的速度置为 -2
    // （为什么不是0而是-2呢，这是因为0可能会造成一些细小的bug？
    //   -2能更好的把角色“摁”在地面上）
    if ( isGrounded && playerVelocity.y < 0 ){
        playerVelocity.y = -2f;     
    }

    // 最后再让角色在y方向上进行移动
    controller.Move(playerVelocity * Time.deltaTime);
}
```
在代码里可以看到，角色的移动分为了两步实现：1、先处理水平方向的移动（这个我们在之前就已经实现了）；2、然后再处理竖直方向的移动。这是为啥呢？

这是一种常见的处理方式，`isGrounded`这个判断需要在水平移动之后再进行更新。且水平方向的移动由玩家控制，竖直方向的移动则是由物理环境影响，分开处理可以避免两种运动相互干扰。

这样角色受重力影响掉落的逻辑就完成了。

*测试*：
可以把角色的初始位置设置在半空中，并且在下方放置一个Cube，看看角色是否能够正常掉落，掉落之后是否能够正常落在地面上。

## 角色的跳跃
接下来我们来考虑一下，实现跳跃需要些什么因素。

1. 首先，跳跃是角色主动发出的操作，所以需要有一个方式捕获角色输入——自然又要用到input system了。
2. 角色发起跳跃之后是不是一定能够跳跃？不，只有在地面上时才能完成跳跃。
3. 跳跃多高？这是一个可以自定义的值。

清楚了这些之后，就可以开始动手了。

首先是捕获跳跃输入。

我们需要新建一个Action，所以又要点开创建好的`PlayerInput`，新建一个`Action`，Action Type设置为`Button`（因为跳跃是一个非1既0的输入，要么跳要么不跳，所以按键类型就足矣），命名为`Jump`，然后右键`Adding Binding`，将`Path`设置为跳跃常用的空格键吧。最后点击`Save Asset`保存。

然后需要来修改一下脚本。

首先打开`PlayMotor.cs`，我们需要添加跳跃的高度`jumpHeight`作为成员属性，然后再添加成员函数`Jump`：
```cs
/* PlayMotor.cs */
public class PlayerMotor : MonoBehaviour
{
    public float jumpHeight = 2f;
    // ... 省略其它代码
    public void Jump(){
        if ( isGrounded ){
            playerVelocity.y = Mathf.Sqrt(jumpHeight * -2.0f * gravity);
        }
    }
    // ... 省略其它代码
}
```
如你所见，`Jump`方法很简单，当用户在地面上时，`Jump`的效果就是让它在y方向的速度大于零。

那么这个y方向的速度是怎么算出来的呢？——死去的中学物理知识召唤术！
在最高点的速度为0，而跳跃高度和加速度（`g`）已知，所以有
```
    0² - v² = 2g * jumpHeight
=>  v = (-2 * g *jumpHeight) ^ 0.5
```
所以我们可以计算出跳跃时的初速度`v`。

接下来只剩下最后一步了，当用户按下跳跃键（空格）时，就会触发`Jump`。

还记得吗，我们把处理用户输入的逻辑都写在`InputManager.cs`里了，我们打开它，新增代码：
```cs
/* InputManager.cs */
public class InputManager : MonoBehaviour
{
    private PlayerInput playerInput;
    private PlayerInput.OnFootActions onFoot;

    void Awake()
    {
        playerInput = new PlayerInput();
        onFoot = playerInput.OnFoot;    
        motor = GetComponent<PlayerMotor>();
        // 当Jump Action被触发时，执行motor.Jump()
        onFoot.Jump.performed += ctx => motor.Jump();
    }
    // ... 省略其它代码
}
```
这里我们只新增了一行代码，但它看起来可能有些令人迷惑。我们来仔细看看。

首先，所有的Action，都拥有三个回调函数。

| 输入阶段 | 对应事件       | 触发时机                  |
|:--------|:--------------|:---------------------------|
| 按下瞬间 | .started      | 按键刚接触时（按下第一帧）  |
| 按住期间 | .performed    | 按键有效触发时（如完全按下） |
| 松开瞬间 | .canceled     | 按键释放时                 |

也就是说当`Jump`这个Action被有效触发时，`performed`的所有回调都会被触发。

现在我们做的就是再多加了一个`Motor.Jump()`的回调。
```cs
// += 表示添加一个回调函数给performed
onFoot.Jump.performed += ctx => motor.Jump();
```

但这个回调实际上需要一个参数，参数类型为`InputAction.CallbackContext`，但是我们的`Motor.Jump()`是无参的，那怎么办呢。

两种方式，第一种就是把我们的`Motor.Jump`添加一个`InputAction.CallbackContext`类型的参数，不过我们在函数里没有用到这个参数。
第二种方式就是我们上面写的，把`Motor.Jump()`放在一个接受一个参数的匿名函数里，这样还省去了写这个又臭又长的函数参数类型。

到这里跳跃的逻辑就完成了。


## 镜头的旋转
搞了半天，居然连镜头都没办法转，只能瞅着一个方向，太难受了，我们来解决它！

同样我们来思考一样视角移动的逻辑：

1. 首先还是需要获取玩家的输入，这次输入来源于鼠标。
2. 一般来说，镜头的移动分为俯仰和左右，俯仰对应鼠标上下移动，左右对应鼠标左右移动。

似乎没有更多需要考虑的了。但（预警）实现起来却有不少讲究。

首先我们需要在`PlayerInput`里新建一个Action，起名为`Look`，Action Type设置为`Value`，Control Type设置为`Vector2`。然后新建一个Binding，Path就设置为`Delta[Mouse]`。这样子`Look`这个Action就能获得鼠标移动的向量了。同样点击`Save Asset`保存。

接下来编写脚本。

因为`Look`并不属于角色的移动逻辑，所以就不把相应的代码放到`PlayMotor.cs`里了，这里新建一个`PlayerLook.cs`单独处理镜头的旋转。
因为细节比较多，这里直接给出完整的脚本代码。

```cs
/* PlayerLook.cs */

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerLook : MonoBehaviour
{
    public Camera cam;      // 用于引用角色的相机
    private float xRotation = 0f;   // 用于临时存放俯仰的旋转角度

    public float xSensitivity = 30f;    // 左右旋转的灵敏度
    public float ySensitivity = 30f;    // 俯仰旋转的灵敏度

    public void ProcessLook(Vector2 input){
        // 参数input是鼠标的移动向量
        float mouseX = input.x;
        float mouseY = input.y;

        // 俯仰旋转
        xRotation -= (mouseY *Time.deltaTime ) * ySensitivity;
        // 因为我们的头的俯仰旋转角度是有限的，仰俯的最大角度都接近90度，
        // 所以当超过这个范围时，需要做一个截断
        xRotation = Mathf.Clamp(xRotation, -80f, 80f);
        // 然后对镜头进行旋转
        // 这里的旋转方式是用了欧拉（Euler）角来处理，
        // 三个参数分别是俯仰角（pitch）、偏航角（yaw）、滚动角（roll）
        // 如果不了解可以搜索一下“欧拉角”
        cam.transform.localRotation = Quaternion.Euler(xRotation, 0, 0);

        // 左右旋转
        // 这里则是直接以竖直方向（y轴）为轴进行旋转
        transform.Rotate(Vector3.up *(mouseX * Time.deltaTime ) * xSensitivity );
    }
}
```
为什么俯仰转的是相机`cam`，而左右旋转的是角色本体（`transform`是角色的成员变量）呢？

这种分离的处理一方面是为了避免**万向节死锁**（比如说pitch是点头，yaw是摇头，roll是歪脑袋，当你低头看地面的时候，yaw和roll就没区别了，丢失了一个自由度——应该可以这么理解），另一方面，当角色左右旋转时，我们并不希望它只是旋转了脑袋，而是整个身体都旋转了。

接下来还需要在`InputManager.cs`中获取用户输入并调用这个`ProcessLook`。

```cs
public class InputManager : MonoBehaviour
{
    private PlayerLook look;
    void Awake(){
        look = GetComponent<PlayerLook>();
        // ... 省略其它代码

    }

    void LateUpdate(){
        look.ProcessLook(onFoot.Look.ReadValue<Vector2>());
    }
    // ... 省略其它代码
}
```

> `LateUpdate`的触发时机是一帧的最后一刻，因为镜头看到的应该是一帧里更新完之后的场景，所以应该使用`LateUpdate`来调用`ProcessLook`而不是`Update`或者`FixedUpdate`。


到此为止，镜头旋转的逻辑就完成了。

别忘了把新建的脚本`PlayerLook.cs`作为组件添加给Player。

在`PlayerLook`中还有一个`cam`变量，其实并没有被赋值，为了给它赋值，需要先点击左边的Hierarchy的Player，然后再把Player下的Main Camera拖动到右边Inspector中，`PlayerLook.cs`的变量`Cam`中。

## 参考
- Youtube，Natty GameDev，[#1 FPS Movement: Let's Make a First Person Game in Unity!](https://www.youtube.com/watch?v=rJqP5EesxLk&list=PLGUw8UNswJEOv8c5ZcoHarbON6mIEUFBC&index=1)
- bilibili，埃罗毛阿老师，[【Unity创作心得·第10期】新输入系统Input System的基本使用](https://www.bilibili.com/video/BV1xT4y1L7Cj)