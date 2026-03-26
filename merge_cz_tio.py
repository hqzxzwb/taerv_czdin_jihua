#!/usr/bin/env python3
"合并词条"

from deploy import *
from collections import defaultdict
import sys

ENTRY_PATTERN = re.compile(r'^\s*# ')
TI_FAN_PATTERN = re.compile(r'^([\w,]+):([\w /(),;]+)$')
COMMENT_PATTERN = re.compile(r'<!--\n(?:.*\n)*?-->(?:\n|$)')

def split_blocks(file_content):
  blocks = []
  split_cursor = 0
  for match in re.finditer(r"(?:\r?\n){2,}", file_content):
    blocks.append(file_content[split_cursor:match.start()])
    split_cursor = match.end()
  blocks.append(file_content[split_cursor:])
  return blocks

def parse_entry_block(block, fname):
  if not ENTRY_PATTERN.match(block):
    return None
  comments = [match.group(0).strip("\n") for match in COMMENT_PATTERN.finditer(block)]
  parseable_block = COMMENT_PATTERN.sub("", block).strip("\n")
  cont = parse_cont(parseable_block, fname)
  lines = parseable_block.splitlines()
  index = 2
  ti_fan_lines = []
  while index < len(lines) and TI_FAN_PATTERN.match(lines[index]):
    ti_fan_lines.append(lines[index])
    index += 1
  return {
    'cont': cont,
    'comments': comments,
    'ti_fan_lines': ti_fan_lines,
  }

def collect_entries(file_content, fname):
  blocks = split_blocks(file_content)
  entries = []
  for block_index, block in enumerate(blocks):
    parsed = parse_entry_block(block, fname)
    if parsed is None:
      continue
    entries.append({
      'block_index': block_index,
      'raw_block': block.strip("\n"),
      **parsed,
    })
  return blocks, entries

def merge_key(cont):
  return f"raw_text$${cont.raw_text}$$raw_pien_ien$${cont.raw_pien_ien}"

def serialize_meaning_as_spec2(meaning):
  lines = [f"+ {meaning.explanation}"]
  for sub in meaning.subs:
    if sub.source:
      lines.append(f"  * {sub.source}")
    if sub.supplement:
      lines.append(f"    + {sub.supplement}")
    for example in sub.examples:
      lines.append("  - %s" % example if not sub.source and not sub.supplement else f"    - {example}")
  return lines

def merge_group(group):
  first = group[0]
  cont0 = first['cont']
  lines = [
    f"# {cont0.raw_text}",
    cont0.raw_pien_ien,
  ]

  seen_ti_fan = set()
  for entry in group:
    for ti_fan_line in entry['ti_fan_lines']:
      if ti_fan_line not in seen_ti_fan:
        lines.append(ti_fan_line)
        seen_ti_fan.add(ti_fan_line)

  for entry in group:
    for meaning in entry['cont'].meanings:
      lines.extend(serialize_meaning_as_spec2(meaning))

  seen_comments = set()
  for entry in group:
    for comment in entry['comments']:
      if comment not in seen_comments:
        lines.append(comment)
        seen_comments.add(comment)

  return "\n".join(lines)

def duplicate_groups(entries):
  conts = defaultdict(list)
  for entry in entries:
    conts[merge_key(entry['cont'])].append(entry)
  return {key: value for key, value in conts.items() if len(value) > 1}

def txct():
  index = 1
  for fname in walk_sources():
    file_content = open(fname, encoding="U8").read()
    _, entries = collect_entries(file_content, fname)
    conts = duplicate_groups(entries)
    for key, value in conts.items():
      print(f"====同形词条====")
      for entry in value:
        print(index, '\t', (entry['cont'], entry['block_index'], entry['raw_block']))
      index += 1

def main():
  for fname in walk_sources():
    file_content = open(fname, encoding="U8").read()
    blocks, entries = collect_entries(file_content, fname)
    conts = duplicate_groups(entries)
    if not conts:
      continue

    first_indexes = {}
    removed_indexes = set()
    merged_blocks = {}
    for group in conts.values():
      first_index = group[0]['block_index']
      first_indexes[first_index] = group
      merged_blocks[first_index] = merge_group(group)
      for entry in group[1:]:
        removed_indexes.add(entry['block_index'])

    out_blocks = []
    for block_index, block in enumerate(blocks):
      if block_index in first_indexes:
        out_blocks.append(merged_blocks[block_index])
      elif block_index in removed_indexes:
        continue
      else:
        out_blocks.append(block.strip("\n"))

    file_content = "\n\n".join(block for block in out_blocks if block.strip()) + "\n"
    open(fname, "w", encoding="U8").write(file_content)

if __name__ == '__main__':
  globals()['main' if len(sys.argv) <= 1 else sys.argv[1]]()
