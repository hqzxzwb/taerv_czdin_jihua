#!/usr/bin/env python3

import glob, re, os

os.system("""rm -rf docs; mkdir docs; cat > docs/_config.yml <<EOF
theme: jekyll-theme-cayman
title: 泰如辞典
description: `TZ="Asia/Shanghai" date +"%Y年%m月%d号%H点"`更新
EOF""")

orders="⓿❶❷❸❹❺❻❼❽❾❿"
txtfiles = []
target=open("docs/index.md", "w")
print("# 音序检索", file=target)
print ("### %s" % "｜".join("[%s](#%s)"%(d.strip("/").upper(), d.strip("/")) for d in sorted(glob.glob("?/"))), file=target)
for d in sorted(glob.glob("?/")):
	letter=d.strip("/").upper()
	print("## %s" % letter, file=target)
	for f in sorted(glob.glob(d+"*.md")):
		conts = open(f).read()
		link_format="https://github.com/hqzxzwb/taerv_czdin_jihua/blob/master/%s#%s"
		for cont in conts.split("#"):
			if cont:
				cont = cont.strip()
				fs=re.split("\n+", cont)
				link_md = re.sub("\d", "", fs[1].split(", ")[0].replace(" ", "_"))
				if not f.endswith(link_md+".md"): print("【%s】不属于%s" %(fs[0], f))
				link=link_format % (f, fs[0])
				out="【[%s](%s)】`%s` " % (fs[0], link, fs[1])
				meanings=cont.count("\n-")
				meaning = 0
				example_count = 0
				for line in fs[2:]:
					if line.startswith("-"):
						meaning+=1
						if meanings > 1:
							out+= orders[meaning]
						out+=" " + line.replace("-", "").strip()
					else:
						example_count += 1
						out+= "｜" if example_count > 1 else "："
						example=line.strip().replace("-", "").strip()
						if "/" in example:
							example=example.replace("/", "<sub>")+"</sub>"
						out+=example
				print(out+"  ", file=target)
	print("### [▲](#音序检索)", file=target)
