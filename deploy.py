#!/usr/bin/env python3
"自动生成index.md"

import glob
import os
import re
import string
import shutil
import ti_fan_ien_converter
from itertools import product
from collections import namedtuple
from collections import defaultdict

CzY = namedtuple(
    'CzY',
    [
        'source',
        'pien_ien_0',
        'pien_ien',
        'raw_pien_ien',
        'text',
        'raw_text',
        'meanings',
        'fname',
        'sort_key',
        'spec',
        'mixed',
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

ORDERS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺"
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
    # '抹': 'maeh8',
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
    py0 = re.sub(r"（.*?）|\([^()]+\)|…", "", py0).strip()
    syllables = re.split("[^a-z0-9]+", py0)
    for py in syllables:
        if PY_FORMAT.match(py) is None:
            print("【%s】的拼音%s不对" % (word, py0))

def strip_tio(ien):
    return re.sub(r'\d', '', ien)

def check_path(path, mixed, word):
    """检查词语的文件名是否正确"""
    computed_path1 = "_".join([strip_tio(ien) for cz, ien, *_ in mixed if ien]) + ".md"
    if path.endswith(computed_path1):
        return
    computed_path2 = "_".join([strip_tio(ien) for cz, ien, *_ in mixed if ien][:4]) + ".md"
    if path.endswith(computed_path2):
        return
    cmd = "meld" if os.path.exists(computed_path2) else "mv"
    print("Alternative path ", computed_path1)
    print("【%s】的位置不对： %s %s %s" %(word, cmd, path, os.path.join(mixed[0][1][0], computed_path2)))

def parse_pinyin(pinyin):
    """A B/C→AB, AC"""
    if "/" not in pinyin:
        return [pinyin]
    pinyin = re.sub(r"([a-z]+)(\d)/(\d)", r"\1\2/\1\3", pinyin)
    py_list = [i.split("/") for i in pinyin.split(" ")]
    return list(map(" ".join, product(*py_list)))

meaning_pattern = r"\+ (?P<explanation>.+)\n(?P<body>(  .+\n)*)"
sub_meaning_pattern = r"(  \* (?P<source>.+)\n)?( {2,4}\+ (?P<supplement>.+)\n)?(?P<body>( {2,4}- .+\n)*)"
example_pattern = r" {2,4}- (?P<text>.+)\n"

pattern_spec1 = r"^(> (?P<source>.+)\n)?(?P<body>(.+\n)*)"
meaning_pattern_spec1 = r"- (?P<explanation>.+)\n(?P<body>(  .+\n)*)"
example_pattern_spec1 = r"  - (?P<text>.+)\n"

def parse_cont(cont, fname):
    """解析词条"""
    cont = cont.strip("\n") + "\n"
    lines = re.split("\n+", cont)
    raw_text = lines[0].lstrip("#").strip()
    raw_pien_ien = lines[1].strip().replace('ᵗ', '')
    pien_ien_list = parse_pinyin(raw_pien_ien)
    pien_ien = re.sub(r"\([^\(\)]+\)(?= |,|$)", "", ", ".join(pien_ien_list))
    pien_ien_0 = pien_ien_list[0]
    mixed = mix(raw_text, pien_ien_0)

    validate(pien_ien_0, raw_text)

    sort_key = ''
    word = ''
    for cz, ien, *_ in mixed:
        sort_key += ien + ' ' + cz + ' '
        word += cz

    prints = False

    spec_teller = lines[2]
    body = "\n".join(lines[2:])
    if prints:
        print("body", body)
    meanings = []
    source = None
    spec = 1
    message_for_failure = f"解析失败。cont = {cont}"
    if spec_teller != None and spec_teller.startswith("+"): # Spec 2
        spec = 2
        meaning_cursor = 0
        for meaning_match in re.finditer(meaning_pattern, body):
            assert meaning_cursor == meaning_match.start(), message_for_failure
            meaning_cursor = meaning_match.end()
            explanation = meaning_match.group('explanation')
            if prints:
                print("meaning_match", meaning_match)
                print("explanation", explanation)
            sub_meanings = []
            sub_meaning_cursor = 0
            sub_meaning_body = meaning_match.group('body')
            for sub_meaning_match in re.finditer(sub_meaning_pattern, sub_meaning_body):
                assert sub_meaning_cursor == sub_meaning_match.start(), message_for_failure
                sub_meaning_cursor = sub_meaning_match.end()
                examples = []
                example_cursor = 0
                example_body = sub_meaning_match.group('body')
                for example_match in re.finditer(example_pattern, example_body):
                    assert example_cursor == example_match.start(), message_for_failure
                    example_cursor = example_match.end()
                    examples.append(example_match.group('text'))
                assert example_cursor == len(example_body)
                sub_meanings.append(CzYSubMeaning(sub_meaning_match.group('source') or "", None, sub_meaning_match.group('supplement'), examples))
            assert sub_meaning_cursor == len(sub_meaning_body), message_for_failure
            meanings.append(CzYMeaning(explanation, sub_meanings))
        assert meaning_cursor == len(body), message_for_failure
    else: # Spec 1
        match = re.match(pattern_spec1, body)
        assert match.start() == 0 and match.end() == len(body), message_for_failure
        source = match.group('source')
        body = match.group('body') or ''
        if prints:
            print("match", match)
            print("body", body)
        body_cursor = 0
        for meaning_match in re.finditer(meaning_pattern_spec1, body):
            assert body_cursor == meaning_match.start(), message_for_failure
            body_cursor = meaning_match.end()
            if prints:
                print("meaning_match", meaning_match)
            examples = []
            example_cursor = 0
            example_body = meaning_match.group('body')
            for example_match in re.finditer(example_pattern_spec1, example_body):
                assert example_cursor == example_match.start(), message_for_failure
                example_cursor = example_match.end()
                examples.append(example_match.group('text'))
            assert example_cursor == len(example_body), message_for_failure
            meanings.append(CzYMeaning(meaning_match.group('explanation'), [CzYSubMeaning(source, pien_ien, None, examples)]))
        assert body_cursor == len(body), message_for_failure
    return CzY(source, pien_ien_0, pien_ien, raw_pien_ien, word, raw_text, meanings, fname, sort_key, spec, mixed)

def mix(word, pien_ien):
    word = word.replace('ʲ', '')
    pien_ien = re.sub("-[a-z1-9]+", "", pien_ien)
    pien_ien = re.sub(r"（.*?）|[…，；—]", " ", pien_ien).strip()
    char_py_list = re.split(" +", pien_ien)
    char_list = re.findall(r"[\w□](?:\wʰ)*|[，—、：；×…？\*]|（.*?）|/.+", word)
    mix = []
    pi = 0
    i = 0
    while i < len(char_list):
        char = char_list[i]
        ti_fan = defaultdict(lambda: None)
        if re.match(r'[\w□]', char[0]):
            if pi >= len(char_py_list):
                break
            pien_ien = char_py_list[pi]
            ti_fan_match = re.search(r"\(([^\(\)]+)\)$", pien_ien)
            if ti_fan_match:
                pien_ien = pien_ien[0: ti_fan_match.start()]
                for item in ti_fan_match.group(1).split(';'):
                    tis, ti_fan_ien = item.split(':')
                    if ti_fan_ien == '0':
                        ti_fan_ien = re.sub(r"\d$", "", pien_ien)
                    elif ti_fan_ien in '123456789':
                        ti_fan_ien = re.sub(r"\d$", ti_fan_ien, pien_ien)
                    for ti in tis.split(','):
                        ti_fan[ti] = ti_fan_ien
            pi += 1
            if pien_ien == 'r' and char == '儿':
                char = '<sub>儿</sub>'
            else:
                char = re.sub(r'(\w)ʰ', r'<sub>\1</sub>', char)
            mix.append((char, pien_ien, ti_fan))
        else:
            mix.append((char, '', ti_fan))
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
    for match in re.finditer(r'# (\w)ʲ(?:/\w)*\n([a-z]+\d?)', file_content):
        cz = match[1]
        ien = match[2]
        out[ien].add(cz)
        out[re.sub(r'\d', '', ien)].add(cz) # 轻声

ti_fan_ien_key = {
    '泰兴': 'txe',
    '泰县': 'tx',
    '如皋': 'rg',
}

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
                conts.append(parse_cont(cont, fname))
    out = ""
    for w in sorted(conts, key=lambda c: c.sort_key):
        check_path(w.fname, w.mixed, w.text)
        for cz, ien, *_ in w.mixed:
            # if cz == '大' and ien == 'tu6':
                # print("【%s】中的【%s】读作【%s】" % (w.raw_text, cz, ien))
            if ien != '' and cz != '□' and len(cz) == 1 and cz not in cz_ien[ien.rstrip('9')]:
                print("未登记的字音：【%s】中的【%s】读作【%s】" % (w.raw_text, cz, ien))
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
            source_set = set()
            for meaning in w.meanings:
                for sub_meaning in meaning.subs:
                    source = sub_meaning.source
                    if source:
                        source = shrink_source(source)
                        source_set.add(source)
            ti_fan_ien = {}
            for source in source_set:
                ti_fan_ien_func = getattr(ti_fan_ien_converter, source, None)
                if ti_fan_ien_func:
                    mixed = [(m[0], m[2][ti_fan_ien_key[source]] or m[1]) for m in w.mixed if m[1]]
                    ti_fan_ien[source] = " ".join([ti_fan_ien_func(cz, ien) for cz, ien in mixed])
            if ti_fan_ien:
                ti_fan_ien_md = ", ".join([f"/{ien}/<sup>{source}</sup>" for source, ien in ti_fan_ien.items()])
                pien_ien_text = f"`{w.pien_ien}` <small>{ti_fan_ien_md}</small>"
            else:
                pien_ien_text = '`' + w.pien_ien + '`'

            if len(w.meanings) > 1:
                meaning = "".join(map(lambda x: " " + ORDERS[x[0]] + " " + meaning_text(w, x[1]), enumerate(w.meanings)))
            elif len(w.meanings) == 1:
                meaning = " " + meaning_text(w, w.meanings[0])
            else:
                meaning = " "
            out = f"1. 【[{w.text}]({link})】{pien_ien_text}{meaning}  \n"
        lines.append(out)
        if count <= 20:
            sample_out.append(out)
    lines.append("**[▲](#音序检索)**  \n")
    open("docs/%s.md"%path, "w", encoding="U8").writelines(lines)

def shrink_source(source):
    return re.sub(r'(方言词典|方言志|方言辞典)\d?$', '', source)

def meaning_text(w, meaning):
    str = ""
    str = str + meaning.explanation
    for sub in sorted(meaning.subs, key = lambda x: x.supplement or ''):
        source = sub.source
        if source:
            source = shrink_source(source)
        else:
            source = ""
        supplement = sub.supplement
        if supplement:
            str = str + f"\\[{source}：{supplement}\\]"
        elif source:
            str = str + f"<sup>\\[{source}\\]</sup>"
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

def walk_sources():
    out = []
    for path in string.ascii_lowercase:
        for fname in glob.glob(path+"/*.md"):
            out.append(fname)
    return out

def main():
    dirs = string.ascii_lowercase.replace('w', '')
    write_config()
    samples = []
    cz_ien = defaultdict(lambda: set())
    parse_cz_ien("daen_cz.csv", cz_ien)
    parse_cz_ien2("用字.md", cz_ien)
    parse_cz_ien2("候选正字.md", cz_ien)
    parse_cz_ien2("suspicious_cz_baseline.md", cz_ien)
    for fname in walk_sources():
        if not re.match(r'^[a-z]+\.md$', os.path.basename(fname)):
            continue
        parse_cz_ien3(fname, cz_ien)
    for path in dirs:
        samples.append("## %s\n" % path.upper())
        write_page(dirs, path, samples, cz_ien)
        samples.append("[更多...](./%s.md)\n"%path)
        cp_pics(path)
    write_index(dirs, samples)

if __name__ == "__main__":
    main()
