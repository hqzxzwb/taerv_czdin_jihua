#!/usr/bin/env python3
"自动生成index.md"

import glob
import os
import re
import string
from itertools import product
from collections import namedtuple
from collections import defaultdict

Word = namedtuple('Word', ['py0', 'pinyin', 'word', 'meaning', 'source', 'fname', 'sort_key'])

ORDERS = "①②③④⑤⑥⑦⑧⑨⑩"
LINK_FORMAT = "https://github.com/hqzxzwb/taerv_czdin_jihua/blob/master/%s#%s"
PY_FORMAT = re.compile("^([bpmfdtnlgkhjqxzcsr]|[zcs]h|ng|dd)?([aoeivuyrzm]+|ng)[nh]?[0-9]?$")

FILTERED_OUT_IEN = {
    '合': 'guh7',
    '核': {'hueh8', 'veh8'},
    '烘': 'hon5',
    '期': 'ji1',
    '挨': 'ngae2',
    '什': 'shen2',
    '浇': 'xio1',
}

def write_config():
    """生成主题文件_config.yml"""
    os.system("""rm docs/*.yml docs/*.md; mkdir -p docs; cat > docs/_config.yml <<EOF
theme: jekyll-theme-cayman
title: 泰如辞典
description: `TZ="Asia/Shanghai" date +"%Y年%m月%d号%H点"`更新
EOF""")

def letter_index(dirs, out):
    """音序"""
    out.append("# 音序检索\n")
    letters = " | ".join("[%s](./%s.md)"%(d.upper(), d) for d in dirs)
    out.append("**%s**  \n" % letters)

def validate(py0, word):
    py0 = re.sub("-[a-z1-9]+", "", py0)
    py0 = re.sub(r"（.*?）|\(.*?\)|…", "", py0).strip()
    syllables = re.split("[^a-z0-9]+", py0)
    for py in syllables:
        if PY_FORMAT.match(py) is None:
            print("【%s】的拼音%s不对" % (word, py0))

def path_from_pinyin(py0):
    """获取文件路径"""
    py1 = re.sub("-[a-z1-9]+", "", py0)
    py1 = re.sub("（.*?）", "", py1).strip()
    py1 = re.sub(r"\d", "", re.sub("[^a-z1-9]+", "_", py1))
    py1 = py1.rstrip("_")
    if py1.__len__() == 0:
        print("拼音异常：%s" % py0)
        return '/unavailable@@@/'
    return os.path.join(py1[0], "%s.md" % py1)

def check_path(path, py0, word):
    """检查词语的文件名是否正确"""
    proper_path = path_from_pinyin(py0)
    if not path.endswith(proper_path):
        cmd = "meld" if os.path.exists(proper_path) else "mv"
        print("【%s】的位置不对： %s %s %s" %(word, cmd, path, proper_path))

def parse_pinyin(pinyin):
    """A B/C→AB, AC"""
    if "/" not in pinyin:
        return pinyin
    pinyin = re.sub(r"([a-z]+)(\d)/(\d)", r"\1\2/\1\3", pinyin)
    py_list = [i.split("/") for i in pinyin.split(" ")]
    return ", ".join(map(" ".join, product(*py_list)))

def parse_cont(cont, fname, cz_ien):
    """解析词条"""
    cont = cont.strip()
    fields = re.split("\n+", cont)
    raw_word = fields[0].lstrip("#").strip()
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
            meaning += example
    #例句的冒号前不显示句号
    meaning = meaning.replace("。：", "：").strip()
    py0 = pinyin.split(",")[0]
    validate(py0, raw_word)
    mixed = mix(raw_word, py0)
    sort_key = ''
    word = ''
    for cz, ien in mixed:
        sort_key += ien + ' ' + cz + ' '
        word += cz
        if ien != '' and len(cz) == 1 and cz not in cz_ien[ien.rstrip('9')]:
            print("字音未收录：【%s】中的【%s】读作【%s】" % (raw_word, cz, ien))
    return Word(py0, pinyin, word, meaning, source, fname, sort_key)

def mix(word, py):
    py = re.sub("-[a-z1-9]+", "", py)
    py = re.sub(r"（.*?）|\(.*?\)|…", "", py).strip()
    char_py_list = re.split("[^a-z0-9]+", py)
    char_list = re.findall(r"[\w□](?:\wʰ)*|[，—、：；×…？\*]|（.*?）|/.+", word)
    mix = []
    pi = 0
    i = 0
    while i < len(char_list):
        char = char_list[i]
        if re.match(r'[\w□]', char[0]):
            py = char_py_list[pi]
            pi += 1
            if py == 'r' and char == '儿':
                char = '<sub>儿</sub>'
            else:
                char = re.sub(r'(\w)ʰ', r'<sub>\1</sub>', char)
            mix.append((char, py))
        else:
            mix.append((char, ''))
        i += 1
    if pi != len(char_py_list) or i != len(char_list):
        print("【%s】(%s)跟拼音(%s)不对应" % (word, char_list, char_py_list))
    return mix

def write_index(dirs, examples):
    """生成主页"""
    lines = []
    letter_index(dirs, lines)
    f = open("docs/index.md", "w", encoding="U8")
    f.writelines(lines)
    f.writelines(examples)

def parse_cz_ien(f, out):
    io = open(f, encoding="U8")
    io.readline()
    while True:
        line = io.readline().rstrip('\n')
        if not line:
            break
        split = line.split(',')
        cz = split[2]
        ien = (split[3] + split[4] + split[5]).replace('vv', 'v').rstrip('0')

        # 单音化
        ien_filter = FILTERED_OUT_IEN.get(cz)
        if ien == ien_filter: continue
        if type(ien_filter) == set and ien in ien_filter: continue

        out[ien].add(cz)
        out[re.sub(r'\d', '', ien)].add(cz) # 轻声
        # print("line ", line, " cz ", cz, " ien ", ien)

def parse_cz_ien2(f, out):
    io = open(f, encoding="U8")
    while True:
        line = io.readline()
        if not line:
            break
        line = line.rstrip('\n')
        match = re.match(r'^# (\w) ([a-z]+\d?)$', line)
        if match:
            cz = match[1]
            ien = match[2]
            # print("line ", line, " cz ", cz, " ien ", ien)
            out[ien].add(cz)
            out[re.sub(r'\d', '', ien)].add(cz) # 轻声

def write_page(dirs, path, sample_out, cz_ien):
    """生成分页"""
    count = 0
    lines = []
    letter_index(dirs, lines)
    lines.append("## %s\n" % path.upper())
    conts = []
    for fname in glob.glob(path+"/*.md"):
        for cont in re.findall(r"#[^#]+", open(fname,encoding="U8").read()):
            conts.append(parse_cont(cont, fname, cz_ien))
    for w in sorted(conts, key=lambda c: c.sort_key):
        check_path(w.fname, w.py0, w.word)
        link = LINK_FORMAT % (w.fname.replace("\\","/"), w.word)
        if w.source:
            source = "<sup>[%s]</sup> " % re.sub(r'(方言词典|方言志|方言辞典)$', '', w.source)
        else:
            source = w.source
        count += 1
        out = "1. 【[%s](%s)】`%s` %s%s  \n" % (w.word, link, w.pinyin, source, w.meaning)
        lines.append(out)
        if count <= 20:
            sample_out.append(out)
    lines.append("**[▲](#音序检索)**  \n")
    open("docs/%s.md"%path, "w", encoding="U8").writelines(lines)

dirs = string.ascii_lowercase.replace('w', '')
write_config()
samples = []
cz_ien = defaultdict(lambda: set())
parse_cz_ien("daen_cz.csv", cz_ien)
parse_cz_ien2("用字.md", cz_ien)
for path in dirs:
    samples.append("## %s\n" % path.upper())
    write_page(dirs, path, samples, cz_ien)
    samples.append("[更多...](./%s.md)\n"%path)
write_index(dirs, samples)
