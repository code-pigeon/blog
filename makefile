# makefile方案3
SHELL := /usr/bin/bash
PARSER := cmark
TEMPLATE_RENDERER := ./template_renderer

MARKDOWN_DIR := ./md
MIDDLE_DIR := ./middle
HTML_DIR := ./docs
CSS_DIR := ./css
JS_DIR := ./js

MD_FILES := $(shell find $(MARKDOWN_DIR) -type f)
# MD_FILES := $(filter-out %, $(FILES))
MIDDLE_TARGETS := $(patsubst $(MARKDOWN_DIR)/%.md,$(MIDDLE_DIR)/%.middle.html,$(MD_FILES))
HTML_TARGETS := $(patsubst $(MARKDOWN_DIR)/%.md,$(HTML_DIR)/%.html,$(MD_FILES))

MARKDOWN_SUB_DIR := $(shell find $(MARKDOWN_DIR) -type d)
MIDDLE_SUB_DIR := $(patsubst $(MARKDOWN_DIR)/%,$(MIDDLE_DIR)/%,$(MARKDOWN_SUB_DIR))
HTML_SUB_DIR := $(patsubst $(MARKDOWN_DIR)/%,$(HTML_DIR)/%,$(MARKDOWN_SUB_DIR))


define render_template
@$(TEMPLATE_RENDERER) \
		./web_skeleton/skeleton.html $(2) \
		-v title=$(shell basename $(2) .html) \
		-f markdown_file.html=$(1)  \
		-v index.html=$(call calculate_relative_path,$(dir $(2)), $(HTML_DIR)/index.html) \
		-v toc.html=$(call calculate_relative_path,$(dir $(2)), $(HTML_DIR)/目录.html) \
		-v index.css=$(call calculate_relative_path,$(dir $(2)),$(CSS_DIR)/index.css) \
		-v toc.js=$(call calculate_relative_path,$(dir $(2)),$(JS_DIR)/toc.js) \
		-v code_highlight.css=$(call calculate_relative_path,$(dir $@),$(CSS_DIR)/code_highlight.css)
endef

calculate_relative_path = $(shell realpath --relative-to=$(1) $(2))

all: $(HTML_TARGETS) $(HTML_DIR)/目录.html 

# //////////////////////////////////////////////////////////////////////////////////////////

# ----- <begin> 目录.html ------

$(MARKDOWN_DIR)/目录.md:./web_skeleton/目录.md $(filter-out ./md/目录.md,$(MD_FILES))
	@echo make 目录.md
	cat $< <(python3 make_toc.py $(HTML_DIR)) > $@
# 	cat ./web_skeleton/目录.md <(python3 make_toc.py ./html) > ./md/目录.md

$(MIDDLE_DIR)/目录.middle.html: $(MARKDOWN_DIR)/目录.md
	@echo building 目录.middle.html
	$(PARSER) $< > $@

$(HTML_DIR)/目录.html:$(MIDDLE_DIR)/目录.middle.html
	@echo 开始将$< 渲染成 $@
	$(call render_template,"$<",$@)

# ----- <end> 目录.html ------

# //////////////////////////////////////////////////////////////////////////////////////////

$(HTML_DIR)/%.html:$(MIDDLE_DIR)/%.middle.html | $(HTML_SUB_DIR)
	@echo 开始将$< 渲染成 $@
	$(call render_template,"$<",$@)

middle: $(MIDDLE_TARGETS)

$(MIDDLE_DIR)/%.middle.html: $(MARKDOWN_DIR)/%.md | $(MIDDLE_SUB_DIR)
	$(PARSER) $< > $@


$(MIDDLE_SUB_DIR):
	mkdir -p $(MIDDLE_SUB_DIR)

$(HTML_SUB_DIR):
	mkdir -p $(HTML_SUB_DIR)


.PHONY: clean
clean:
	rm -r $(HTML_DIR)/*
	rm -r $(MIDDLE_DIR)/*

.PHONY: toc
toc:
	rm $(MARKDOWN_DIR)/目录.md
# 	rm $(MIDDLE_DIR)/目录.middle.html


.PHONY: test
test:
	@echo 测试-------------- ------------------
	@echo $(MARKDOWN_SUB_DIR)
	@echo $(HTML_SUB_DIR)
