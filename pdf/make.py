#!/usr/bin/env python3

import os, glob, sys, re
from md2pdf2 import md2pdf2
from zoneinfo import ZoneInfo
from datetime import datetime

dirpath = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirpath)

css_string = open("style.css", "r", encoding="utf-8").read()
css_strings = {
	"heh":css_string.replace("FONT_FAMILY", '"Noto Sans CJK SC", "Plangothic P1", "Plangothic P2", sans-serif'), 
	"son":css_string.replace("FONT_FAMILY", '"WenJin Mincho Plane 0", "WenJin Mincho Plane 2", "WenJin Mincho Plane 3", serif')
}
def main(output="taerv.pdf", stylesheets=css_strings):
    tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(tz)
    content = open("cover.md", "r", encoding="U8").read().replace("{{DATE}}", now.strftime("%Y年%m月%d号%H点"))
    md2pdf2("0.pdf", md_content=content, stylesheets=stylesheets)
    files = ["0.pdf"]
    index = 0
    lines = []
    for path in sorted(glob.glob("../docs/[a-z].md")):
        with open(path, "r", encoding="U8") as mdfile:
            count = 0
            lines.clear()
            last_py = ""
            for line in mdfile:
                if count > 1 and not line.startswith("**"):
                    if line.startswith("##"): line = line[1:]
                    line = line.replace("<sub>儿</sub>", "𖿲")
                    if line.startswith("1."):
                        line = "<span class=order>%d</span>" % (index + 1) + line[2:]
                        index += 1
                        py = re.findall(r"(?<=`)[a-z]+", line)[0]
                        if py != last_py:
                            lines.append("## %s\n" % (py))
                            last_py = py
                    lines.append(line)
                count += 1
            lines.append("\n\n")
            basename = os.path.splitext(os.path.basename(path))[0] + ".pdf"
            print("生成 %s..." % (basename), flush=True)
            md2pdf2(basename, md_content="\n".join(lines), stylesheets=stylesheets)
            files.append(basename)
    # 合并pdf
    for p in stylesheets:
        output_pdf = output.replace(".pdf", "_%s.pdf" % p)
        print("合并为 %s..." % (output_pdf), flush=True)
        os.system("pdftk %s cat output - | pdftk - update_info_utf8 info.txt output %s" % (" ".join(map(lambda f: p+f, files)), output_pdf))

if __name__ == "__main__":
    main()
