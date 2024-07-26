# 【lua笔记】
## lua函数
### 函数参数默认值的实现
```lua
function derivative (f, delta)
    delta = delta or 1e-4  -- 如果没有传递参数delta，则delata = nil or 1e-4 = 1e-4
        return  function (x)
                    return (f(x + delta) - f(x))/delta
                end
                -- 返回了一个匿名函数
end
```
## lua与C交互
### 例1
```c
/* 
    编译语句：gcc tmp.c -I path\to\lua\ -L path\to\lua\ -llua
    功能：通过C调用lua

*/


#include <stdio.h>
#include <string.h>
#include "lua.h"
#include "lauxlib.h"
#include "lualib.h"

int main (void) {
    char buff[256];  // 存储终端输入
    int error;
    lua_State *L = luaL_newstate(); /* opens Lua */
    luaL_openlibs(L); /* opens the standard libraries */

    while (fgets(buff, sizeof(buff), stdin) != NULL) {
        /*
            下面这行代码比较有意思
            首先luaL_loadstring(L, buff)将buff中的字符串当作lua命令进行编译，
            若编译成功，返回0，且将编译后的代码块作为一个函数（闭包）压入 Lua 栈顶；此时||后的lua_pcall会执行编译后的lua命令。
            若编译失败，返回非0值，且将错误信息压入栈顶；此时||后的lua_pcall不会执行。
        */
        error = luaL_loadstring(L, buff) || lua_pcall(L, 0, 0, 0);

        if (error) {
            fprintf(stderr, "%s\n", lua_tostring(L, -1));
            lua_pop(L, 1); /* pop error message from the stack */
            // 第二个参数1表示从栈顶弹出1个元素
        }
    }
    lua_close(L);
    return 0;
}
```

### 头文件包含
若不知道是C还是C++程序
```c++
#ifdef __cplusplus
extern "C" {
#endif

#include <lua.h>

#ifdef __cplusplus
}
#endif
```
若确定是C程序：
```c
#include <lua.h>
```
若确定是C++程序
```c++
#include <lua.hpp>
```

### 向lua栈添加元素
```c
void lua_pushnil (lua_State *L);  // push了个空（暂时还不知道push了个啥）
void lua_pushboolean (lua_State *L, int bool);  // push布尔变量（在C里是int）
void lua_pushnumber (lua_State *L, lua_Number n);  // push double变量
void lua_pushinteger (lua_State *L, lua_Integer n);  // push整型
void lua_pushlstring (lua_State *L, const char *s, size_t len);  // push一个string，用len指定string的长度
void lua_pushstring (lua_State *L, const char *s);  // push一个以'\0'结尾的C风格string
```

### 访问lua栈元素
#### 查询lua栈元素的类型
判断lua栈的元素是否为某一类型：
```c
/*
    说明：
        lua_is*的*表示lua的类型
        如：lua_isnil, lua_isnumber, lua_isstring, lua_istable
    功能：
        判断lua栈上第index个元素是否是*类型
    注：
        实际上，lua_isnumber 函数并不检查值是否具有特定类型，而是检查该值是否可以转换为该类型；
        lua_isstring也类似：实际上，任何数字都满足 lua_isstring。
*/

int lua_is* (lua_State *L, int index);
```

查询lua栈的元素的类型还有一个函数：
```c
lua_type
```
每种类型都有一个常数表示：`LUA_TNIL, LUA_TBOOLEAN, LUA_TNUMBER, LUA_TSTRING`等。
此函数通常用于与`switch`配合。

#### 获得lua栈元素
使用`lua_to*`族函数：
```c
int lua_toboolean (lua_State *L, int index);
const char *lua_tolstring (lua_State *L, int index, size_t *len);  // len返回字符串的实际长度
// 当我们不需要长度信息时，可以传NULL给第三个参数。也可以调用宏lua_tostring——实际上就是lua_tolstring传入NULL给第三个参数

lua_State *lua_tothread (lua_State *L, int index);
lua_Number lua_tonumber (lua_State *L, int index);
lua_Integer lua_tointeger (lua_State *L, int index);
```

```c
/* lua 5.2 以上 */
lua_Number lua_tonumberx (lua_State *L, int idx, int *isnum);  // isnum返回一个标志，表示要获取的元素是否为数字类型
lua_Integer lua_tointegerx (lua_State *L, int idx, int *isnum);
```

#### 例2
```c
static void stackDump (lua_State *L) {
    int i;
    int top = lua_gettop(L); /* depth of the stack */
    for (i = 1; i <= top; i++) { /* repeat for each level */
        int t = lua_type(L, i);
        switch (t) {
            case LUA_TSTRING: { /* strings */
                printf("'%s'", lua_tostring(L, i));
                break;
            }
            case LUA_TBOOLEAN: { /* Booleans */
                printf(lua_toboolean(L, i) ? "true" : "false");
                break;
            }
            case LUA_TNUMBER: { /* numbers */
                printf("%g", lua_tonumber(L, i));  
                /* 
                    所有类型的数字都会在这里输出
                    若要区分整型和浮点数，可以写：
                    case LUA_TNUMBER: { 
                        if (lua_isinteger(L, i)) 
                            printf("%lld", lua_tointeger(L, i));
                        else 
                            printf("%g", lua_tonumber(L, i));
                        break;
                    }

                */
                break;
            }
            default: { /* other values */
                printf("%s", lua_typename(L, t));  // 一些C语言不能表示的类型，如table，就直接输出类型名
                break;
            }
        }
        printf(" "); /* put a separator */
    }
    printf("\n"); /* end the listing */
}
```

#### 其它lua栈操作
```c
int lua_gettop (lua_State *L);  // 获得lua栈的元素数量
void lua_settop (lua_State *L, int index);  // 将lua栈的元素数量设置为index，若index>原来的元素数量，则用nil填充；否则丢弃掉多的元素
void lua_pushvalue (lua_State *L, int index);
void lua_rotate (lua_State *L, int index, int n);
void lua_remove (lua_State *L, int index);
void lua_insert (lua_State *L, int index);
void lua_replace (lua_State *L, int index);
void lua_copy (lua_State *L, int fromidx, int toidx);
```

### lua用于配置
```lua
--[[ config.lua ]]

-- define window size
width = 200
height = 300
```

```c
int getglobint(lua_State *L, const char *var) {
    int isnum, result;
    lua_getglobal(L, var);  // 获取变量var，将其置于lua栈顶
    result = (int)lua_tointegerx(L, -1, &isnum);
    if (!isnum)
        error(L, "'%s' should be a number\n", var);
    lua_pop(L, 1);   /* remove result from the stack */
    return result;
}
void load(lua_State *L, const char *fname, int *w, int *h) {
    if (luaL_loadfile(L, fname) || lua_pcall(L, 0, 0, 0))
        error(L, "cannot run config. file: %s", lua_tostring(L, -1));
    *w = getglobint(L, "width");
    *h = getglobint(L, "height");
}
```

#### 获取table类型
获取table中某个键的值，需要先将这个table压到栈顶，然后再把键压到栈顶，接着用`lua_gettable(L, -2)`就可以将键值压到栈顶（在此之前已经将键从栈顶弹出了）。
```c
lua_getglobal(L, "mytable"); // 将表推送到栈上，栈索引为 -1
lua_pushstring(L, "key"); // 将键推送到栈上，栈索引为 -2
/*  此时的栈： mytable key */

lua_gettable(L, -2); // 使用键从表中获取值，并将这个值推送到栈顶，移除栈顶的键
/*  此时的栈： mytable value */

// 现在栈顶就是 "mytable[key]" 的值，栈索引为 -1
// 原始的表仍然在栈上，栈索引为 -2
if (lua_isnumber(L, -1)) {
    double value = lua_tonumber(L, -1);
    printf("The value is: %f\n", value);

lua_pop(L, 1); // 移除栈顶的值
```
下面给一个封装好的例子：
```lua
-- config.lua 
background = {red = 0.30, green = 0.10, blue = 0}
```

```c
#define MAX_COLOR 255
/* assume that table is on the top of the stack */
int getcolorfield (lua_State *L, const char *key) {
    int result, isnum;
    lua_pushstring(L, key);  /* push key */
    lua_gettable(L, -2);  /* get background[key] */
    result = (int)(lua_tonumberx(L, -1, &isnum) * MAX_COLOR);
    if (!isnum)
        error(L, "invalid component '%s' in color", key);
    lua_pop(L, 1);  /* remove number */
    return result;
}

lua_getglobal(L, "background");
if (!lua_istable(L, -1))
    error(L, "'background' is not a table");
red = getcolorfield(L, "red");
green = getcolorfield(L, "green");
blue = getcolorfield(L, "blue");
```

#### 设置table的值
和获取table的值类似。
设置table的值时，假如此时table位于lua栈顶，需要先将键压入栈顶，然后再将键值压入栈，接着调用`settable(L, -3);`即可。
```c
lua_pushstring(L, "key"); /* key */
lua_pushnumber(L, 250);  /* value */
lua_settable(L, -3);
```

#### 在C语言中设置lua全局变量
```c
lua_pushstring(L, "hello world"); // 将字符串 "hello world" 推送到栈上
lua_setglobal(L, "greeting"); // 将栈顶的字符串设置为全局变量 "greeting"，完成之后此变量会从栈顶弹出
```

结合前面的设置table的值的方法，我们也可以为lua创建一个table类型的全局变量
```c
lua_newtable(L);  // 这会创建一个空的table置于栈顶

lua_pushstring(L, "key"); /* key */
lua_pushnumber(L, 250);  /* value */
lua_settable(L, -3);

lua_setglobal(L, "mytable");
```

#### 一点扩展
在《Programming in Lua》（Roberto Ierusalimschy）一书中，介绍了两种使用预定义名称（例如：RED、BLUE……）来表示颜色的机制。

**第一种方法**：
通过在C语言中预设`RED`的值，然后将`RED = {red = 1.0, green = 0, blue = 0 }`这个table变量设置为lua的全局变量，再读取lua配置文件。
其效果为：
```lua
--[[
    相当于C语言帮lua脚本在脚本的开头写了这么一段
    RED = {red = 1.0, green = 0, blue = 0 }
]]

background_color = RED
```

**第二种方法**：
用户可以直接在脚本中写:
```lua
background_color = 'RED'  -- 注意这里的'RED'是字符串了
```
然后在C语言中，需要判断background_color这个变量是字符串还是table，分两种情况分别处理。

#### 一些简化的函数
获取table键值：
```c
lua_getfield(L, -1, key); 
/*  
    等同于
    lua_pushstring(L, key);
    lua_gettable(L, -2);
*/

// 同时lua_getfield还提供了类型判断
if (lua_getfield(L, -1, key) != LUA_TNUMBER)
    error(L, "invalid component in background color");


```

设置table键值：
```c
lua_pushnumber(L, 250);
lua_setfield(L, -2, "string_key");
/*  
    等同于
    lua_pushstring(L, "string_key"); 
    lua_pushnumber(L, 250);  
    lua_settable(L, -3);
*/
```

### 在C中调用lua函数
