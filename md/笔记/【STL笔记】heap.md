# 【STL笔记】heap

首次编辑：24/9/20/10:39
最后编辑：24/9/20/11:11

```c++
#include <iostream>
#include <vector>
#include <algorithm>

int main(){

// 1. stl中没有叫heap的数据结构，堆是以vector的形式存储的

    // Initializing a vector
    std::vector<int> v1 = { 20, 30, 40, 25, 15 };
 
// 2. 构建堆（make_heap）

    std::make_heap(v1.begin(), v1.end());  // 默认为大顶堆
 
    std::cout << "2. 堆中的最大元素为：";
    std::cout << v1.front() << std::endl;  // 注意v1.back()并不能获得最小元素
 
    // make_heap还可以有第三个参数，指定比较函数，默认为std::less()
    // std::make_heap(v1.begin(), v1.end(), std::greater<int>());  // 这样相当于小顶堆了

// 3. 添加堆元素（std::vector::push_back 加 std::push_heap）

    // ！注意在这之前v1要是一个堆，若不是，则会产生错误
    v1.push_back(200);
    std::push_heap(v1.begin(), v1.end());

    std::cout << "3. 堆中的最大元素为：";
    std::cout << v1.front() << std::endl;  // 注意v1.back()并不能获得最小元素

    // push_heap也可以有第三个参数，指定比较函数
    // std::push_heap(v1.begin(), v1.end(), std::greater<int>());

// 4. 删除堆顶元素（std::pop_heap 加 std::vector::pop_back）

    // ！调用者要保证，在调用pop_heap时[first, last)已经是一个堆(使用相同的排序准则)
    std::pop_heap(v1.begin(), v1.end());  // 这会把堆顶的最大元素交换到vecotr末尾，然后把除了尾部的元素的剩余区间重新调整成堆。
    v1.pop_back();

    std::cout << "4. 堆中的最大元素为：";
    std::cout << v1.front() << std::endl;  // 注意v1.back()并不能获得最小元素

    // pop_heap也可以有第三个参数，指定比较函数
    // std::pop_heap(v1.begin(), v1.end(), std::greater<int>());

// 5. 对vector堆进行排序（sort_heap）

    // ！注意：调用者仍需确保区间已经是一个堆。
    std::sort_heap(v1.begin(), v1.end());

    std::cout << "5. 排序之后的vector为：";
    for (auto i : v1){
    	std::cout << i << " ";
    }
    std::cout << std::endl;

    // sort_heap也可以有第三个参数，指定比较函数
    // std::sort_heap(v1.begin(), v1.end(), std::greater<int>());

    return 0;
}

// 6. 判断一个vector是不是堆（is_heap)
	
	bool res = std::is_heap(v1.begin(), v1.end());  // 返回bool

	if ( res == true){
		std::cout << "6. v1 为堆" << std::endl;
	}else{
		std::cout << "6. v1 非堆" << std::endl;
	}

	// sort_heap也可以有第三个参数，指定比较函数
	// std::is_heap(v1.begin(), v1.end(), std::greater<int>());

// 7. 判断vector中为堆的区间（is_heap_until）

	// 按下不表

```

## 参考
- 博客园，[C++ 标准库中的堆(heap)](https://www.cnblogs.com/deathmr/p/9015644.html)
- GeeksForGeeks，[Heap in C++ STL](https://www.geeksforgeeks.org/cpp-stl-heap/)