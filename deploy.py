#!/usr/bin/env python3
"自动生成index.md"

import glob
import os
import re
from itertools import product

ORDERS = "①②③④⑤⑥⑦⑧⑨⑩"
LINK_FORMAT = "https://github.com/hqzxzwb/taerv_czdin_jihua/blob/master/%s#%s"
PY_FORMAT = re.compile("^([bpmfdtnlgkhjqxzcsr]|[zcs]h|ng|dd)?([aoeivuyrzm]+|ng)[nh]?[0-8]?$")

def write_config():
    """生成主题文件_config.yml"""
    os.system("""rm docs/*.yml docs/*.md; mkdir -p docs; cat > docs/_config.yml <<EOF
theme: jekyll-theme-cayman
title: 泰如辞典
description: `TZ="Asia/Shanghai" date +"%Y年%m月%d号%H点"`更新
EOF""")

def get_letters(dirs):
    """音序"""
    lines = ["# 音序检索\n"]
    letters = " | ".join("[%s](#%s)"%(d.upper(), d) for d in dirs)
    lines.append("**%s**  \n" % letters)
    return lines

def validate(py0, word):
    py0 = re.sub("-[a-z1-8]+", "", py0)
    py0 = re.sub("（.*?）", "", py0).strip()
    py0 = re.sub("\(.*?\)", "", py0).strip()
    syllables = re.split("[^a-z0-8]+", py0)
    s=re.sub("[，—、：；×…？\*]","",word)
    s=re.sub("（.*?）","",s)
    s=re.sub("/.+", "", s)
    if len(s) != len(syllables):
        print("%s 【%s】(%d)跟拼音(%d)不对应" % (get_path(py0), word, len(s), len(syllables)))
    for py in syllables:
        if PY_FORMAT.match(py) is None:
            print("【%s】的拼音%s不对" % (word, py0))

def lower_er(py0, word):
    """儿尾变小"""
    syllables = py0.split(" ")
    validate(py0, word)
    if "r" in syllables:
        words = list(word)
        index = 0
        while "r" in syllables[index:]:
            index = syllables.index("r", index)
            if index >= len(words):
                print("【%s】跟拼音%s不对应" % (word, py0))
            elif words[index] == "儿":
                words[index] = "<sub>儿</sub>"
            index += 1
        word = "".join(words)
    return word

def get_path(py0):
    """获取文件路径"""
    py0 = re.sub("-[a-z1-8]+", "", py0)
    py0 = re.sub("（.*?）", "", py0).strip()
    py0 = re.sub(r"\d", "", re.sub("[^a-z1-8]+", "_", py0))
    py0 = py0.rstrip("_")
    return os.path.join(py0[0], "%s.md" % py0)

def check_path(path, py0, word):
    """检查词语的文件名是否正确"""
    should_path = get_path(py0)
    if not path.endswith(should_path):
        cmd = "meld" if os.path.exists(should_path) else "mv"
        print("【%s】的位置不对： %s %s %s" %(word, cmd, path, should_path))

def parse_pinyin(pinyin):
    """A B/C→AB, AC"""
    if "/" not in pinyin:
        return pinyin
    pinyin = re.sub("([a-z]+)(\d)/(\d)", "\\1\\2/\\1\\3", pinyin)
    py_list = [i.split("/") for i in pinyin.split(" ")]
    return ", ".join(map(" ".join, product(*py_list)))

def parse_cont(cont, fname):
    """解析词条"""
    cont = cont.strip()
    fields = re.split("\n+", cont)
    word = fields[0].lstrip("#").strip()
    pinyin = parse_pinyin(fields[1].strip())
    meaning = ""
    source = ""
    show_order = cont.count("\n-") > 1
    meaning_count = 0
    example_count = 0
    for line in fields[2:]:
        if line.startswith("-"):
            example_count = 0
            if show_order:
                meaning += " " + ORDERS[meaning_count]
                meaning_count += 1
            meaning += " " + line.replace("-", "").strip()
        elif line.startswith(">"):
            source = line.lstrip(">").strip()
        else:
            example_count += 1
            meaning += "｜" if example_count > 1 else "："
            example = line.strip().replace("-", "").strip()
            # ~ if "/" in example:
                # ~ example = example.replace("/", "<sub>")+"</sub>"
            meaning += example
    #例句的冒号前不显示句号
    meaning = meaning.replace("。：", "：").replace("~", "～").strip()
    py0 = pinyin.split(",")[0]
    return [py0, pinyin, word, meaning, source, fname]

def get_key(cont):
    """词条排序"""
    key = cont[0].split(" ")[0] + cont[2][0]+ ("2" if len(cont[2]) > 1 else "1")
    #print(key)
    return key

def write_index():
    """生成主页"""
    dirs = sorted(glob.glob("?"))
    lines = get_letters(dirs)
    count = 0
    for path in dirs:
        lines.append("## %s\n" % path.upper())
        conts = []
        for fname in sorted(glob.glob(path+"/*.md")):
            for cont in re.findall(r"#[^#]+", open(fname,encoding="U8").read()):
                conts.append(parse_cont(cont, fname))
        for py0, pinyin, word, meaning, source, fname in sorted(conts, key=get_key):
            check_path(fname, py0, word)
            link = LINK_FORMAT % (fname.replace("\\","/"), word)
            if source:
                source = "<sup>[%s]</sup> " % source.rstrip("方言词典").rstrip("方言志")
            count += 1
            out = "<sub>%d</sub>【[%s](%s)】`%s` %s%s  \n" % (count, lower_er(py0, word), link, pinyin, source, meaning)
            lines.append(out)
            #check_path(fname, py0, word)
        lines.append("**[▲](#音序检索)**  \n")
    open("docs/index.md", "w", encoding="U8").writelines(lines)

write_config()
write_index()
