import glob,re

for fname in sorted(glob.glob("?/*.md")):
    fs = re.split("\n{2,}",open(fname,encoding="U8").read().strip())
    words = list()
    for i in fs:
        if i not in words:
            words.append(i)
    open(fname,mode="w",encoding="U8").write("\n\n".join(words)+"\n")
