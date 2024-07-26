# 【make技巧】复制文件夹下的所有文件到另一个文件夹中
## 情景描述
假设项目文件夹如下：
```
.
├── obj
│
└── src
    ├── js
    │   ├── a.js
    │   └── b.js
    ├── css
    │   ├── a.css
    │   └── b.css
    └── index.html
```
要通过makefile实现自动将src下的所有文件复制到obj文件夹中：
```
.
├── obj
│   ├── js
│   │   ├── a.js
│   │   └── b.js
│   ├── css
│   │   ├── a.css
│   │   └── b.css
│   └── index.html
│ 
└── src
    ├── js
    │   ├── a.js
    │   └── b.js
    ├── css
    │   ├── a.css
    │   └── b.css
    └── index.html
```

## 实现
```makefile
SRCDIR = ./src
OBJDIR = ./obj

SRCS = $(shell find ./tmp/ -type f)
OBJS = $(patsubst $(SRCDIR)/%, $(OBJDIR)/%, $(SRCS))

all:$(OBJS)
	@echo $^


$(OBJDIR)/%: $(SRCDIR)/% | $(dir $(OBJS))
	cp $< $(dir $@)

$(dir $(OBJS)):
	mkdir -p $@

.PHONY: clean
clean:
	rm -r $(OBJDIR)/*
```