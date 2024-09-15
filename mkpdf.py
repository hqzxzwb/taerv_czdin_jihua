#!/usr/bin/env python3
"自动生成index.md"

import glob
import os
import re
import string
import datetime
from deploy import *

def py2ipa(py):
    syd = {
        'er': 'ɚ',
        'r(\\d)': 'ʅ\\1',
        'z(\\d)': 'ɿ\\1',
        '\\bp': 'pʰ',
        '\\bb': 'p',
        '\\bt': 'tʰ',
        '\\bd': 't',
        '\\bch': 'ʈ͡ʂʰ',
        '\\bzh': 'ʈ͡ʂ',
        '\\bsh': 'ʂ',
        '\\br': 'ɻ',
        "\\bz": "t͡s",
        "\\bc": "t͡sʰ",
        '\\bj': 't͡ɕ',
        '\\bq': 't͡ɕʰ',
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
        'eu': 'əɯ',
        'e': 'ə',
        'o': 'ɔ',
        'ii': 'iɪ',
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

def get_lines(dirs, path):
    """生成分页"""
    global count
    lines = []
    lines.append("<h2>%s</h2>\n" % path.upper())
    conts = []
    for fname in glob.glob(path+"/*.md"):
        file_content = open(fname,encoding="U8").read()
        file_content = re.sub(r"<!--\n(.*\n)*-->", "", file_content) # 移除注释
        for cont in re.findall(r"#[^#]+", file_content):
            conts.append(parse_cont(cont, fname, cz_ien))
    py0 = ""
    for w in sorted(conts, key=lambda c: c.sort_key):
        py0_first = w.py0.split(" ")[0].split("-")[0].rstrip("0123456789")
        if py0 != py0_first:
            py0 = py0_first
            lines.append(f"<h3>{py0}</h3>\n")
        link = LINK_FORMAT % (w.fname.replace("\\","/"), w.raw_word)
        if w.source:
            source = "<span class=book>%s</span>" % re.sub(r'(方言词典|方言志|方言辞典)$', '', w.source)
        else:
            source = w.source
        count += 1
        out = "<p><span class=order>%d</span> <a href=%s class=hz>%s</a> <span class=py>%s</span> <span class=ipa>/%s/</span> %s %s</p>\n" % (count, link, w.word, w.pinyin, py2ipa(w.pinyin), source, w.meaning)
        lines.append(out)
    return lines

def add_ipa(m):
    py = m.group(1)
    ipa = py2ipa(py+"0")
    return f"<td><span class=py>{py}</span> <span class=ipa>/{ipa}/</span> {m.group(2)}</td>"

def main():
    f = open("docs/pdf.html", "w", encoding="U8")
    now = datetime.datetime.now()
    html = open("template.html", encoding="U8").read().replace("%", "%%").replace("%%s", "%s") % (now.strftime("%Y年%m月%d号%H点"))
    f.write(html)
    global count
    count = 0
    for path in dirs:
        lines = get_lines(dirs, path)
        f.writelines(lines)
    f.close()
    os.system('wkhtmltopdf -B 1 -L 1 -R 1 -T 1 --enable-local-file-access --outline --disable-smart-shrinking --page-size A4 docs/pdf.html docs/泰如辞典%s.pdf' % now.strftime("%Y%m%d"))

if __name__ == "__main__":
    main()
