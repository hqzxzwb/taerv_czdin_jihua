#!/usr/bin/env python3
"自动生成index.md"

import glob
import os
import re

ORDERS = "⓿❶❷❸❹❺❻❼❽❾❿"
LINK_FORMAT = "https://github.com/hqzxzwb/taerv_czdin_jihua/blob/master/%s#%s"

def write_config():
    """生成主题文件_config.yml"""
    os.system("""rm -rf docs; mkdir docs; cat > docs/_config.yml <<EOF
theme: jekyll-theme-cayman
title: 泰如辞典
description: `TZ="Asia/Shanghai" date +"%Y年%m月%d号%H点"`更新
EOF""")

def get_letters(dirs):
    """音序"""
    lines = ["# 音序检索\n"]
    letters = "｜".join("[%s](#%s)"%(d.upper(), d) for d in dirs)
    lines.append("### %s\n" % letters)
    return lines

def lower_er(py0, word):
    """儿尾变小"""
    syllables = py0.split(" ")
    if "r" in syllables:
        words = list(word)
        index = 0
        while "r" in syllables[index:]:
            index = syllables.index("r", index)
            if words[index] == "儿":
                words[index] = "<sub>儿</sub>"
            index += 1
        word = "".join(words)
    return word

def check_path(path, py0, word):
    """检查词语的文件名是否正确"""
    py0 = re.sub(r"\d", "", py0.replace(" ", "_"))
    if not path.endswith("%s/%s.md" % (py0[0], py0)):
        print("【%s】不属于 %s" %(word, path))

def parse_cont(cont):
    """解析词条"""
    cont = cont.strip()
    fields = re.split("\n+", cont)
    word = fields[0].lstrip("#").strip()
    pinyin = fields[1].strip()
    meaning = ""
    show_order = cont.count("\n-") > 1
    meaning_count = 0
    example_count = 0
    for line in fields[2:]:
        if line.startswith("-"):
            example_count = 0
            meaning_count += 1
            if show_order:
                meaning += ORDERS[meaning_count]
            meaning += " " + line.replace("-", "").strip()
        else:
            example_count += 1
            meaning += "｜" if example_count > 1 else "："
            example = line.strip().replace("-", "").strip()
            if "/" in example:
                example = example.replace("/", "<sub>")+"</sub>"
            meaning += example
    return [word, pinyin, meaning]

def write_index():
    """生成主页"""
    dirs = sorted(glob.glob("?"))
    lines = get_letters(dirs)
    for path in dirs:
        lines.append("## %s\n" % path.upper())
        for fname in sorted(glob.glob(path+"/*.md")):
            conts = open(fname).read()
            for cont in re.findall(r"#[^#]+", conts):
                word, pinyin, meaning = parse_cont(cont)
                py0 = pinyin.split(",")[0]
                link = LINK_FORMAT % (fname, word)
                out = "【[%s](%s)】`%s` %s  \n" % (lower_er(py0, word), link, pinyin, meaning)
                lines.append(out)
                check_path(fname, py0, word)
        lines.append("### [▲](#音序检索)\n")
    open("docs/index.md", "w").writelines(lines)

write_config()
write_index()
