#!/usr/bin/env python3

import os, glob, sys
from md2pdf.core import md2pdf
from zoneinfo import ZoneInfo
from datetime import datetime

def main(output="taerv.pdf", css_file="pdf.css"):
    tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(tz)
    content = open("template.md", "r", encoding="U8").read().replace("{{DATE}}", now.strftime("%Y年%m月%d号%H点"))
    md2pdf("0.pdf", md_content=content, css_file_path=css_file)
    files = ["0.pdf"]
    index = 0
    lines = []
    for path in sorted(glob.glob("docs/[a-z].md")):
        with open(path, "r", encoding="U8") as mdfile:
            count = 0
            lines.clear()
            for line in mdfile:
                if count > 1 and not line.startswith("**"):
                    if line.startswith("##"): line = line[1:]
                    line = line.replace("<sub>儿</sub>", "𖿲")
                    if line.startswith("1."):
                        line = "<span class=order>%d</span>" % (index + 1) + line[2:]
                        index += 1
                    lines.append(line)
                count += 1
            lines.append("\n\n")
            basename = os.path.splitext(os.path.basename(path))[0] + ".pdf"
            print("生成 %s..." % (basename), flush=True)
            md2pdf(basename, md_content="\n".join(lines), css_file_path=css_file)
            files.append(basename)
    # 合并pdf
    print("合并为 %s..." % (output), flush=True)
    os.system("pdftk %s output %s" % (" ".join(files), output))

if __name__ == "__main__":
    main(*sys.argv[1:])
