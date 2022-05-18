#!/usr/bin/env python

import glob
import os,sys
import re

input=sys.argv[1]
f=None
for line in open(input,encoding="utf-8-sig"):
    line = line.strip().replace("~","～")
    if not line: continue
    gs = re.findall('^【(.+)】(.+)$',line)[::-1]
    if len(gs) == 1:
        #print(gs)
        if f:
            #print(file=f)
            f.close()
        line=gs[0][1].strip()
        py=re.findall('^[a-z1-8/ ]*',line)[0]
        line=line[len(py):].strip()
        py=py.strip()
        fname=re.sub("/[a-z1-8]+", "", py)
        fname=re.sub("[^a-z1-8]+", "_", fname)
        fname=re.sub("\d","",fname)
        fname = fname.rstrip("_")
        fname=os.path.join(fname[0],fname+".md")
        exist = os.path.exists(fname)
        #print(fname)
        f=open(fname, mode="a",encoding="U8")
        if exist:
            print(file=f)
        print("# %s\n%s" % (gs[0][0], py),file=f)
        if line:
            line=re.sub("（\d）","\n- ",line.strip()).strip("\n- ").replace("例如：","\n  - ").replace("：","\n  - ")
            print("-", line,file=f)
    else:
        print(line, "解析失败")
