#!/usr/bin/env python

import glob
import os,sys
import re

f=None
for line in open(sys.argv[1],encoding="utf-8-sig"):
	line = line.strip().replace("~","～").replace(" --  -- ","——").replace("★","").replace("▲","").replace("...","…")
	if not line: continue
	if line.startswith("【"):
		if f:
			#print(file=f)
			f.close()
		hz, py = re.findall('^【(.+)】(.+)$',line)[0]
		#print(hz,py)
		hz = re.sub("[\-\+\=\*\?]", "", hz)
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
	else:
		print("# %s\n%s\n> 东台方言词典" % (hz, py),file=f)
		line = line.replace("/","｜")
		line=re.sub("[①-⑳]","\n- ",line.strip()).strip("\n- ").replace("例如：","\n  - ").replace("：","\n  - ")
		print("-", line,file=f)
