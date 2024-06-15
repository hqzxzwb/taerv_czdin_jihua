#!/usr/bin/env python3
"自动生成index.md"

import glob
import os
import re
import string
from itertools import product
import datetime
from deploy import *

html = """<html lang="zh-CN">
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta charset="UTF-8">
    <title>泰如辞典</title>
    <style>
        @font-face {
            font-family: "LXGW WenKai";
            src: url("/usr/share/fonts/TTF/LXGWWenKai-Regular.ttf")
        }
        @font-face {
            font-family: "Charis SIL";
            src: url("/usr/share/fonts/TTF/CharisSIL-Regular.ttf")
        }
        @font-face {
            font-family: "MiSans";
            src: url("/usr/share/fonts/TTF/MiSans-Regular.ttf");
            src: url("/usr/share/fonts/TTF/MiSans L3.ttf");
        }
        body {font-family: "LXGW WenKai";}
        h2 {page-break-before: always;}
        .order {font-size: 60%%;}
        .hz {font-family: "MiSans"; text-decoration: none; color: black;}
        .py {font-size: 90%%; color: green;}
        .ipa {font-size: 90%%; font-family: "Charis SIL";}
        .meaning {}
        .book {font-size: 70%%; color: gray;}
    </style>
</head>
<body>
      <h2 class=hz style="page-break-before: avoid;">泰如辞典</h1>
      <p>%s</p>
      <p><a href="https://hqzxzwb.github.io/taerv_czdin_jihua/">在线辞典</a></p>
      <p><a href="https://dict.taerv.cn/">泰如字典</a></p>
<p>韵母</p>
      <img src="image003.jpg"></img>
<p>声调</p>
      <img src="image004.jpg"></img>
""" % (datetime.datetime.now().strftime("%Y年%m月%d号%H点"))

def py2ipa(py):
    syd = {
        'er': 'ɚ',
        'r(\\d)': 'ʅ\\1',
        'z(\\d)': 'ɿ\\1',
        '\\bp': 'pʰ',
        '\\bb': 'p',
        '\\bt': 'tʰ',
        '\\bd': 't',
        '\\bch': 'tʂʰ',
        '\\bzh': 'tʂ',
        '\\bsh': 'ʂ',
        '\\br': 'ɻ',
        "\\bz": "ʦ",
        "\\bc": "ʦʰ",
        '\\bj': 'ʨ',
        '\\bq': 'ʨʰ',
        '\\bx': 'ɕ',
        '\\bk': 'kʰ',
        '\\bg': 'k',
        '\\bng': 'ŋ',
        '\\bh': 'x',
        '(ʂ|ʂʰ)(\\d)': '\\1ʅ\\2',
        "([aeiouy])h": '\\1ʔ',
        "h": "ʰ",
        'v': 'ʋ',
        'z': 'ɿ',
        'ae': 'ɛ',
        'r': 'ʅ',
        'eu': 'əʊ',
        'e': 'ə',
        'o': 'ɔ',
        'ii': 'i',
        '([iuɛ])n': '\\1̃',
        '([aəɔ])n': '\\1ŋ',
        'a([^ŋʔ])': 'ɑ\\1',
        'i([ʔ̃])': 'ɪ\\1',
        'u(\\b|[\\dʔ̃])': 'ʊ\\1',
        'iəŋ': 'iŋ',
        '0': '',
        '([\\d-]+)': '<sup>\\1</sup>',
    }
    for key, value in syd.items():
        py = re.sub(key, value, py)
    return py

def write_page(dirs, path, f):
    """生成分页"""
    global count
    lines = []
    lines.append("<h2>%s</h2>\n" % path.upper())
    conts = []
    for fname in glob.glob(path+"/*.md"):
        for cont in re.findall(r"#[^#]+", open(fname,encoding="U8").read()):
            conts.append(parse_cont(cont, fname, cz_ien))
    py0 = ""
    for w in sorted(conts, key=lambda c: c.sort_key):
        py0_first = w.py0.split(" ")[0].split("-")[0].rstrip("0123456789")
        if py0 != py0_first:
            py0 = py0_first
            lines.append(f"<h3>{py0}</h3>\n")
        link = LINK_FORMAT % (w.fname.replace("\\","/"), w.raw_word)
        if w.source:
            source = "<span class=book>%s</span> " % re.sub(r'(方言词典|方言志)$', '', w.source)
        else:
            source = w.source
        count += 1
        out = "<p><span class=order>%d</span>&nbsp;<a href=%s class=hz>%s</a>&nbsp;<span class=py>%s</span> <span class=ipa>/%s/</span> %s<span class=meaning>%s</span></p>\n" % (count, link, w.word, w.pinyin, py2ipa(w.pinyin), source, w.meaning)
        lines.append(out)
    f.writelines(lines)

f = open("docs/index.html", "w", encoding="U8")
f.write(html)
count = 0
for path in dirs:
    write_page(dirs, path, f)
f.close()
os.chdir("docs")
os.system("wkhtmltopdf -B 0 -L 0 -R 0 -T 0 --enable-local-file-access --outline --page-width 100 --page-height 180 ./index.html 泰如辞典%s.pdf" % datetime.datetime.now().strftime("%Y%m%d"))
