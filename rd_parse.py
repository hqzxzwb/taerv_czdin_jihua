#!/usr/bin/env python

import glob
import os,sys
import re

input=sys.argv[1]
f=None
for line in open(input,encoding="U8"):
    line = line.rstrip().replace("~","～")
    if not line: continue
    gs = re.findall('^(.+)【(.+)】$',line)
    if len(gs) == 1:
        #print(gs)
        if f:
            #print(file=f)
            f.close()
        py=gs[0][1].strip()
        py=re.sub('/[a-z0-8]+','',py)
        fname=re.sub("\d","",py).replace('，',' ').replace(" ","_")
        fname=os.path.join(fname[0],fname+".md")
        exist = os.path.exists(fname)
        print(fname)
        f=open(fname, mode="a",encoding="U8")
        if exist:
            print(file=f)
        print("# %s\n%s\n> 如东方言词典" % (gs[0][0], py),file=f)
    else:
        line=re.sub("\(\d\)","",line.strip()).strip().replace("例如：","\n  - ")
        print("-", line,file=f)
