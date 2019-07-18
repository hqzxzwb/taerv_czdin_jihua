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

def lower_er(pys, word):
    """儿尾变小"""
    if "r" in pys:
        words = list(word)
        index = 0
        while "r" in pys[index:]:
            index = pys.index("r", index)
            if words[index] == "儿":
                words[index] = "<sub>儿</sub>"
            index += 1
        word = "".join(words)
    return word

def check_path(path, py, word):
    """检查词语的文件名是否正确"""
    py = re.sub(r"\d", "", py.replace(" ", "_"))
    if not path.endswith("%s/%s.md" % (py[0], py)):
        print("【%s】不属于%s" %(word, path))

write_config()
DIRS = sorted(glob.glob("?"))
LINES = get_letters(DIRS)

for d in DIRS:
    LINES.append("## %s\n" % d.upper())
    for f in sorted(glob.glob(d+"/*.md")):
        conts = open(f).read()
        for cont in conts.split("#"):
            if cont:
                cont = cont.strip()
                fs = re.split("\n+", cont)
                py = fs[1].split(",")[0]
                check_path(f, py, fs[0])
                link = LINK_FORMAT % (f, fs[0])
                out = "【[%s](%s)】`%s` " % (lower_er(py.split(" "), fs[0]), link, fs[1])
                meanings = cont.count("\n-")
                meaning = 0
                example_count = 0
                for line in fs[2:]:
                    if line.startswith("-"):
                        meaning += 1
                        if meanings > 1:
                            out += ORDERS[meaning]
                        out += " " + line.replace("-", "").strip()
                    else:
                        example_count += 1
                        out += "｜" if example_count > 1 else "："
                        example = line.strip().replace("-", "").strip()
                        if "/" in example:
                            example = example.replace("/", "<sub>")+"</sub>"
                        out += example
                LINES.append(out+"  \n")
    LINES.append("### [▲](#音序检索)\n")
open("docs/index.md", "w").writelines(LINES)
