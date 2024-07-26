# 【C笔记】打印不同的颜色字体

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
