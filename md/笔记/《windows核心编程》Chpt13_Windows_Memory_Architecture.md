# Virtual Memory
## 概念
- free：进程虚拟内存中没有使用的区域（region）is free。
- reserving：进程在使用某块虚拟内存区域之前，需要先对其进行分配（allocate），这一动作称为reserving。
- releasing：当虚拟内存的某块区域不再需要使用时，可以释放（releasing）它。
- committing：在使用已经预定（reserved）的虚拟空间之前，需要先分配物理空间，并映射（map）到已经预定的虚拟空间中。
> 虚拟空间的一个区域（region）通常有几个页那么大，而commit的物理空间则可能比这个region小，比如一个页，或者4个页，且可以乱序分布于region中。

- decommitting：committing的反操作。
- paging file：按我的理解就是外存的交换区，用于扩展物理内存。
- memory-mapped file：当操作系统加载exe/dll文件时，不会把exe/dll文件加载到物理内存或者paging file中，而是直接将虚拟内存映射到外存中存放该exe/dll文件的位置。这样的内存区域称为memory-mapped file。
- backed：当一个虚拟内存区域被reserved，且有物理空间commit之后，就称这块虚拟内存被这块物理空间backed了。
- region：已预定（reserved）的一块虚拟内存空间，它的地址会从分配粒度（allocation granularity）边界开始，且region的大小是系统页（page）的整数倍。
- block：拥有相同保护属性（protection attributes），且被同样类型的物理存储backed的连续的页。

## 