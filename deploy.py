#!/usr/bin/env python3
"自动生成index.md"

import glob
import os
import re
import string
import shutil
from itertools import product
from collections import namedtuple
from collections import defaultdict

CzY = namedtuple(
    'CzY',
    [
        'source',
        'pien_ien_0',
        'pien_ien',
        'text',
        'raw_text',
        'meanings',
        'fname',
        'sort_key',
        'spec',
    ]
)
CzYMeaning = namedtuple(
    'CzYMeaning',
    [
        'explanation',
        'subs',
    ]
)
CzYSubMeaning = namedtuple(
    'CzYSubMeaning',
    [
        'source',
        'pien_ien',
        'supplement',
        'examples',
    ]
)

ORDERS = "①②③④⑤⑥⑦⑧⑨⑩"
LINK_FORMAT = "https://github.com/hqzxzwb/taerv_czdin_jihua/blob/master/%s#%s"
PY_FORMAT = re.compile("^([bpmfdtnlgkhjqxzcsr]|[zcs]h|ng|dd)?([aoeivuyrzm]+|ng)[nh]?[0-9]?$")

FILTERED_OUT_IEN = {
    '炸': {'chaeh8', 'shaeh8'},
    '秸': 'gae1',
    '合': 'guh7',
    '歪': 'huae1',
    '核': {'hueh8', 'veh8'},
    '烘': 'hon5',
    '期': 'ji1',
    '挨': 'ngae2',
    '呆': 'ngae2',
    '什': 'shen2',
    '敌': 'vaeh8',
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

def strip_tio(ien):
    return re.sub(r'\d', '', ien)

def check_path(path, mixed, word):
    """检查词语的文件名是否正确"""
    computed_path1 = "_".join([strip_tio(ien) for cz, ien in mixed if ien]) + ".md"
    if path.endswith(computed_path1):
        return
    computed_path2 = "_".join([strip_tio(ien) for cz, ien in mixed if ien][:4]) + ".md"
    if path.endswith(computed_path2):
        return
    cmd = "meld" if os.path.exists(computed_path2) else "mv"
    print("Alternative path ", computed_path1)
    print("【%s】的位置不对： %s %s %s" %(word, cmd, path, os.path.join(mixed[0][1][0], computed_path2)))

def parse_pinyin(pinyin):
    """A B/C→AB, AC"""
    if "/" not in pinyin:
        return pinyin
    pinyin = re.sub(r"([a-z]+)(\d)/(\d)", r"\1\2/\1\3", pinyin)
    py_list = [i.split("/") for i in pinyin.split(" ")]
    return ", ".join(map(" ".join, product(*py_list)))

meaning_pattern = r"\+ (?P<explanation>.+)\n(?P<body>(  .+\n)*)"
sub_meaning_pattern = r"(  \* (?P<source>.+)\n)?(    \+ (?P<supplement>.+)\n)?(?P<body>(    .+\n)*)"
example_pattern = r"    - (?P<text>.+)\n"

pattern_spec1 = r"^(> (?P<source>.+)\n)?(?P<body>(.+\n)*)"
meaning_pattern_spec1 = r"- (?P<explanation>.+)\n(?P<body>(  .+\n)*)"
example_pattern_spec1 = r"  - (?P<text>.+)\n"

def parse_cont(cont, fname, cz_ien):
    """解析词条"""
    cont = cont.strip("\n") + "\n"
    lines = re.split("\n+", cont)
    raw_word = lines[0].lstrip("#").strip()
    pien_ien = parse_pinyin(lines[1].strip())
    pien_ien_0 = pien_ien.split(",")[0]
    mixed = mix(raw_word, pien_ien_0)

    validate(pien_ien_0, raw_word)

    sort_key = ''
    word = ''
    for cz, ien in mixed:
        sort_key += ien + ' ' + cz + ' '
        word += cz
        # if cz == '混':
            # print("【%s】中的【%s】读作【%s】" % (raw_word, cz, ien))
        if ien != '' and cz != '□' and len(cz) == 1 and cz not in cz_ien[ien.rstrip('9')]:
            print("未登记的字音：【%s】中的【%s】读作【%s】" % (raw_word, cz, ien))
    check_path(fname, mixed, word)

    prints = False

    spec_teller = lines[2]
    body = "\n".join(lines[2:])
    if prints:
        print("body", body)
    meanings = []
    source = None
    spec = 1
    if spec_teller != None and spec_teller.startswith("+"): # Spec 2
        spec = 2
        for meaning_match in re.finditer(meaning_pattern, body):
            explanation = meaning_match.group('explanation')
            if prints:
                print("meaning_match", meaning_match)
                print("explanation", explanation)
            sub_meanings = []
            for sub_meaning_match in re.finditer(sub_meaning_pattern, meaning_match.group('body')):
                examples = []
                for example_match in re.finditer(example_pattern, sub_meaning_match.group('body')):
                    examples.append(example_match.group('text'))
                sub_meanings.append(CzYSubMeaning(sub_meaning_match.group('source') or "", None, sub_meaning_match.group('supplement'), examples))
            meanings.append(CzYMeaning(explanation, sub_meanings))
    else: # Spec 1
        match = re.match(pattern_spec1, body)
        source = match.group('source')
        if prints:
            print("match", match)
            print("body", match.group('body'))
        for meaning_match in re.finditer(meaning_pattern_spec1, match.group('body') or ''):
            if prints:
                print("meaning_match", meaning_match)
            examples = []
            for example_match in re.finditer(example_pattern_spec1, meaning_match.group('body')):
                examples.append(example_match.group('text'))
            meanings.append(CzYMeaning(meaning_match.group('explanation'), [CzYSubMeaning(source, pien_ien, None, examples)]))
    return CzY(source, pien_ien_0, pien_ien, word, raw_word, meanings, fname, sort_key, spec)

def mix(word, py):
    word = word.rstrip('ʲ')
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
            if pi >= len(char_py_list):
                break
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
        raise Exception("【%s】(%s)跟拼音(%s)不对应" % (word, char_list, char_py_list))
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
    while True:
        line = io.readline().rstrip('\n')
        if not line:
            break
        split = line.split(',')
        cz = split[1]
        ien = (split[2] + split[3] + split[4]).replace('vv', 'v').rstrip('0')

        # 单音化
        ien_filter = FILTERED_OUT_IEN.get(cz)
        if ien == ien_filter: continue
        if type(ien_filter) == set and ien in ien_filter: continue

        out[ien].add(cz)
        out[strip_tio(ien)].add(cz) # 轻声
        # print("line ", line, " cz ", cz, " ien ", ien)

def parse_cz_ien2(f, out):
    io = open(f, encoding="U8")
    while True:
        line = io.readline()
        if not line:
            break
        line = line.rstrip('\n')
        match = re.match(r'^# (\w) ([a-z0-9, ]+)$', line)
        if match:
            cz = match[1]
            ienList = re.split(r", ?", match[2])
            # print("line ", line, " cz ", cz, " ien ", ienList)
            for ien in ienList:
                out[ien].add(cz)
                out[re.sub(r'\d', '', ien)].add(cz) # 轻声

def parse_cz_ien3(f, out):
    io = open(f, encoding="U8")
    file_content = io.read()
    for match in re.finditer(r'# (\w)ʲ\n([a-z]+\d?)', file_content):
        cz = match[1]
        ien = match[2]
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
        file_content = open(fname,encoding="U8").read()
        file_content = re.sub(r"<!--\n(.*\n)*?-->(\n|$)", "", file_content) # 移除注释
        for cont in re.split(r"(?:\r?\n){2,}", file_content):
            if not re.fullmatch(r'\s*', cont):
                conts.append(parse_cont(cont, fname, cz_ien))
    out = ""
    for w in sorted(conts, key=lambda c: c.sort_key):
        link = LINK_FORMAT % (w.fname.replace("\\","/"), w.text)
        if w.spec == 1:
            source = w.source
            if source:
                source = " <sup>[%s]</sup>" % shrink_source(source)
            else:
                source = ""
            count += 1
            if len(w.meanings) > 1:
                meaning = "".join(map(lambda x: " " + ORDERS[x[0]] + " " + meaning_text_spec1(x[1]), enumerate(w.meanings)))
            elif len(w.meanings) == 1:
                meaning = " " + meaning_text_spec1(w.meanings[0])
            else:
                meaning = " "
            out = f"1. 【[{w.text}]({link})】`{w.pien_ien}`{source}{meaning}  \n"
        else:
            if len(w.meanings) > 1:
                meaning = "".join(map(lambda x: " " + ORDERS[x[0]] + " " + meaning_text(x[1]), enumerate(w.meanings)))
            elif len(w.meanings) == 1:
                meaning = " " + meaning_text(w.meanings[0])
            else:
                meaning = " "
            out = f"1. 【[{w.text}]({link})】`{w.pien_ien}`{meaning}  \n"
        lines.append(out)
        if count <= 20:
            sample_out.append(out)
    lines.append("**[▲](#音序检索)**  \n")
    open("docs/%s.md"%path, "w", encoding="U8").writelines(lines)

def shrink_source(source):
    return re.sub(r'(方言词典|方言志|方言辞典)$', '', source)

def meaning_text(meaning):
    str = ""
    source = "".join(f"\\[{shrink_source(sub.source)}\\]" for sub in meaning.subs if sub and sub.source)
    if source:
        str = "<sup>" + source + "</sup>"
    str = str + meaning.explanation
    for sub in meaning.subs:
        supplement = sub.supplement
        if supplement:
            str = str + f"\\[{shrink_source(sub.source)}：{supplement}\\]"
    if any(sub.examples for sub in meaning.subs):
        str = str.rstrip('。') + "："
        for sub in meaning.subs:
            source = sub.source
            if source:
                source = "<sup>\\[" + shrink_source(source) + "\\]</sup>"
            else:
                source = ""
            for example in sub.examples:
                str = str + example + source + "｜"
        str = str.rstrip("｜")
    return str

def meaning_text_spec1(meaning):
    str = meaning.explanation
    if len(meaning.subs[0].examples) != 0:
        str = str.rstrip('。')
        str = str + "：" + "｜".join(meaning.subs[0].examples)
    return str

def cp_pics(path):
    for fname in glob.glob(path+"/*.png"):
        shutil.copyfile(fname, "docs/"+os.path.basename(fname))

dirs = string.ascii_lowercase.replace('w', '')
write_config()
samples = []
cz_ien = defaultdict(lambda: set())
parse_cz_ien("daen_cz.csv", cz_ien)
parse_cz_ien2("用字.md", cz_ien)
parse_cz_ien2("候选正字.md", cz_ien)
parse_cz_ien2("suspicious_cz_baseline.md", cz_ien)
for path in dirs:
    for fname in glob.glob(path+"/*.md"):
        if not re.match(r'^[a-z]+\.md$', os.path.basename(fname)):
            continue
        parse_cz_ien3(fname, cz_ien)
for path in dirs:
    samples.append("## %s\n" % path.upper())
    write_page(dirs, path, samples, cz_ien)
    samples.append("[更多...](./%s.md)\n"%path)
    cp_pics(path)
write_index(dirs, samples)
