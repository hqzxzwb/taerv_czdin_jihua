#!/usr/bin/env python3
"合并词条"

from deploy import *
from collections import defaultdict
import sys

def conts_from_content(fc1, fname):
  conts = defaultdict(lambda: list())
  split_cursor = 0
  for cont_match in re.finditer(r"(?:\r?\n){2,}", fc1 + "\n\n"):
    cont_text = fc1[split_cursor: cont_match.start()]
    if not re.fullmatch(r'\s*', cont_text):
      cont = parse_cont(cont_text, fname)
      range = (split_cursor, cont_match.start())
      split_cursor = cont_match.end()
      conts[f"raw_text$${cont.raw_text}$$raw_pien_ien$${cont.raw_pien_ien}"].append((cont, range))
  return conts

def txct():
  for fname in walk_sources():
    file_content = open(fname,encoding="U8").read()
    fc1 = re.sub(r"<!--\n(.*\n)*?-->(\n|$)", "", file_content) # 移除注释
    conts = conts_from_content(fc1, fname)
    for key, value in conts.items():
      if len(value) > 1:
        print(f"====同形词条====")
        for cont in value:
          print(cont)

def main():
  for fname in walk_sources():
    file_content = open(fname,encoding="U8").read()
    fc1 = re.sub(r"<!--\n(.*\n)*?-->(\n|$)", "", file_content) # 移除注释
    replaceable = len(file_content) == len(fc1)
    conts = conts_from_content(fc1, fname)

    ranges_to_delete = []

    for key, value in conts.items():
      value = [it for it in value if value[0].spec == 1]
      if len(value) > 1:
        cont0 = value[0][0]
        if file_content[-1] != '\n':
          file_content += '\n'
        file_content += '\n'
        file_content += (f"# {cont0.raw_text}\n")
        file_content += (f"{cont0.raw_pien_ien}\n")
        for cont, r in value:
          if replaceable:
            ranges_to_delete.append(r)
          for meaning in cont.meanings:
            file_content += (f"+ {meaning.explanation}\n")
            if cont.source:
              file_content += (f"  * {cont.source}\n")
            sub_meaning = meaning.subs[0]
            for example in sub_meaning.examples:
              file_content += (f"    - {example}\n")

    ranges_to_delete.sort(key=lambda r: r[0])
    file_content = remove_matches(file_content, ranges_to_delete)

    open(fname, "w").write(file_content)

def remove_matches(sentence, matches):
    result = []
    i = 0
    for x, y in matches:
        result.append(sentence[i:x])
        i = y
    result.append(sentence[i:])

    return "".join(result)

if __name__ == '__main__':
  globals()[sys.argv[1] or 'main']()
