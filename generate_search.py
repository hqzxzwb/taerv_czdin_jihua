#!/usr/bin/env python3
"""
Generate docs/search.html - a static search page for the Taerv dialect dictionary.
Supports searching by word (Chinese characters), pinyin, and explanation text.
"""

import glob
import json
import os
import re
import string
import subprocess

# Reuse parsing logic from deploy.py
from itertools import product
from collections import namedtuple

CzY = namedtuple(
    'CzY',
    [
        'source',
        'ti_fan_pien_ien',
        'pien_ien',
        'raw_pien_ien',
        'text',
        'raw_text',
        'meanings',
        'fname',
        'sort_key',
        'spec',
        'mixed',
    ]
)
CzYMeaning = namedtuple('CzYMeaning', ['explanation', 'subs'])
CzYSubMeaning = namedtuple('CzYSubMeaning', ['source', 'pien_ien', 'supplement', 'examples'])

ORDERS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚"
LINK_PREFIX = "https://github.com/hqzxzwb/taerv_czdin_jihua/blob/master/"
PY_FORMAT = re.compile(r"^([bpmfdtnlgkhjqxzcsr]|[zcs]h|ng|dd)?([aoeivuyrzm]+|ng)[nh]?[0-9]?$")
SOURCE_NAMES = ["如皋", "如东", "兴化", "东台", "泰兴", "泰州", "泰县", "通用"]
SOURCE_NAME_TO_ID = {name: i for i, name in enumerate(SOURCE_NAMES)}
DEFAULT_SOURCE_ID = SOURCE_NAME_TO_ID["通用"]


def parse_pinyin(pinyin):
    """A B/C → AB, AC"""
    if "/" not in pinyin:
        return [pinyin]
    pinyin = re.sub(r"([a-z]+)(\d)/(\d)", r"\1\2/\1\3", pinyin)
    py_list = [i.split("/") for i in pinyin.split(" ")]
    return list(map(" ".join, product(*py_list)))


def strip_tio(ien):
    return re.sub(r'\d', '', ien)


def mix(word, pien_ien):
    word = word.replace('ʲ', '')
    pien_ien = re.sub(r"-[a-z1-9]+", "", pien_ien)
    pien_ien = re.sub(r"（.*?）|[…，；—]", " ", pien_ien).strip()
    char_py_list = re.split(r" +", pien_ien)
    char_list = re.findall(r"[\w□](?:\wʰ)*|[，—、：；×…？\*]|（.*?）|/.+", word)
    result = []
    pi = 0
    i = 0
    while i < len(char_list):
        char = char_list[i]
        if re.match(r'[\w□]', char[0]):
            if pi >= len(char_py_list):
                break
            py = char_py_list[pi]
            pi += 1
            if py == 'r' and char == '儿':
                char = '<sub>儿</sub>'
            else:
                char = re.sub(r'(\w)ʰ', r'<sub>\1</sub>', char)
            result.append((char, py))
        else:
            result.append((char, ''))
        i += 1
    return result


meaning_pattern = r"\+ (?P<explanation>.+)\n(?P<body>(  .+\n)*)"
sub_meaning_pattern = r"(  \* (?P<source>.+)\n)?( {2,4}\+ (?P<supplement>.+)\n)?(?P<body>( {2,4}- .+\n)*)"
example_pattern = r" {2,4}- (?P<text>.+)\n"
pattern_spec1 = r"^(> (?P<source>.+)\n)?(?P<body>(.+\n)*)"
meaning_pattern_spec1 = r"- (?P<explanation>.+)\n(?P<body>(  .+\n)*)"
example_pattern_spec1 = r"  - (?P<text>.+)\n"


def parse_cont(cont, fname):
    """Parse a single dictionary entry."""
    cont = cont.strip("\n") + "\n"
    lines = re.split("\n+", cont)
    raw_text = lines[0].lstrip("#").strip()
    raw_pien_ien = lines[1].strip().replace('ᵗ', '')
    pien_ien_list = parse_pinyin(raw_pien_ien)
    pien_ien = re.sub(r"\([^\(\)]+\)(?= |,|$)", "", ", ".join(pien_ien_list))
    pien_ien_0 = pien_ien_list[0]
    ti_fan_pien_ien = {}
    index = 2
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^([\w,]+):([\w /(),;]+)$", line)
        if match:
            for ti_fan in match[1].split(','):
                ti_fan_pien_ien[ti_fan] = match[2]
            index += 1
        else:
            break

    try:
        mixed = mix(raw_text, pien_ien_0)
    except Exception:
        mixed = []

    sort_key = ''
    word = ''
    for cz, ien, *_ in mixed:
        if ien:
            sort_key += ien + ' ' + cz + ' '
        word += cz

    spec_teller = lines[index] if index < len(lines) else None
    body = "\n".join(lines[index:])
    meanings = []
    source = None
    spec = 1
    message_for_failure = f"Parse failed. cont = {cont[:80]}"

    try:
        if spec_teller is not None and spec_teller.startswith("+"):  # Spec 2
            spec = 2
            meaning_cursor = 0
            for meaning_match in re.finditer(meaning_pattern, body):
                assert meaning_cursor == meaning_match.start(), message_for_failure
                meaning_cursor = meaning_match.end()
                explanation = meaning_match.group('explanation')
                sub_meanings = []
                sub_meaning_cursor = 0
                sub_meaning_body = meaning_match.group('body')
                for sub_meaning_match in re.finditer(sub_meaning_pattern, sub_meaning_body):
                    if sub_meaning_match.start() == sub_meaning_match.end():
                        continue
                    assert sub_meaning_cursor == sub_meaning_match.start(), message_for_failure
                    sub_meaning_cursor = sub_meaning_match.end()
                    examples = []
                    example_cursor = 0
                    example_body = sub_meaning_match.group('body')
                    for example_match in re.finditer(example_pattern, example_body):
                        assert example_cursor == example_match.start(), message_for_failure
                        example_cursor = example_match.end()
                        examples.append(example_match.group('text'))
                    assert example_cursor == len(example_body)
                    sub_meanings.append(CzYSubMeaning(
                        sub_meaning_match.group('source') or "",
                        None,
                        sub_meaning_match.group('supplement'),
                        examples
                    ))
                assert sub_meaning_cursor == len(sub_meaning_body), message_for_failure
                meanings.append(CzYMeaning(explanation, sub_meanings))
            assert meaning_cursor == len(body), message_for_failure
        else:  # Spec 1
            match = re.match(pattern_spec1, body)
            source = match.group('source') if match else None
            body = match.group('body') or '' if match else body
            body_cursor = 0
            for meaning_match in re.finditer(meaning_pattern_spec1, body):
                assert body_cursor == meaning_match.start(), message_for_failure
                body_cursor = meaning_match.end()
                examples = []
                example_cursor = 0
                example_body = meaning_match.group('body')
                for example_match in re.finditer(example_pattern_spec1, example_body):
                    assert example_cursor == example_match.start(), message_for_failure
                    example_cursor = example_match.end()
                    examples.append(example_match.group('text'))
                assert example_cursor == len(example_body), message_for_failure
                meanings.append(CzYMeaning(
                    meaning_match.group('explanation'),
                    [CzYSubMeaning(source, pien_ien, None, examples)]
                ))
            assert body_cursor == len(body), message_for_failure
    except (AssertionError, AttributeError, IndexError):
        pass  # Silently skip malformed entries

    return CzY(source, ti_fan_pien_ien, pien_ien, raw_pien_ien, word, raw_text,
               meanings, fname, sort_key, spec, mixed)


def shrink_source(source):
    return re.sub(r'(方言词典|方言志|方言辞典)\d?$', '', source)


def build_meaning_text(meanings, spec):
    """Build plain-text explanation for a list of meanings."""
    parts = []
    for i, meaning in enumerate(meanings):
        prefix = ORDERS[i] + " " if len(meanings) > 1 else ""
        explanation = meaning.explanation
        # Strip markdown formatting
        explanation = re.sub(r'<[^>]+>', '', explanation)
        explanation = re.sub(r'\[.*?\]', '', explanation)
        explanation = explanation.strip()
        parts.append(prefix + explanation)
    return "  ".join(parts)


def encode_sources(source_tags):
    """Encode source names to compact numeric IDs for smaller JSON payload."""
    return sorted({SOURCE_NAME_TO_ID.get(tag, DEFAULT_SOURCE_ID) for tag in source_tags})


def collect_all_entries():
    """Parse all source .md files and return list of entry dicts for JSON embedding."""
    dirs = string.ascii_lowercase.replace('w', '')
    entries = []

    for path in dirs:
        for fname in glob.glob(os.path.join(path, "*.md")):
            file_content = open(fname, encoding="U8").read()
            # Remove comments
            file_content = re.sub(r"<!--\n(.*\n)*?-->(\n|$)", "", file_content)
            for cont in re.split(r"(?:\r?\n){2,}", file_content):
                if re.fullmatch(r'\s*', cont):
                    continue
                try:
                    w = parse_cont(cont, fname)
                except Exception:
                    continue

                # Build meanings text (plain, for search indexing and display)
                meaning_parts = []
                for i, meaning in enumerate(w.meanings):
                    prefix = ORDERS[i] + " " if len(w.meanings) > 1 else ""
                    explanation = meaning.explanation
                    explanation = re.sub(r'<[^>]+>', '', explanation)
                    explanation = re.sub(r'\\?\[.*?\\?\]', '', explanation)
                    explanation = explanation.strip()
                    examples = []
                    for sub in meaning.subs:
                        for ex in sub.examples:
                            if not ex:
                                continue
                            ex = ex.strip()
                            if not ex:
                                continue
                            ex = re.sub(r'<[^>]+>', '', ex)
                            ex = re.sub(r'\\?\[.*?\\?\]', '', ex)
                            ex = re.sub(r'^例[：:]', '', ex)
                            ex = ex.strip()
                            if ex:
                                ex = ex.replace('{', '').replace('}', '')
                                examples.append(ex)
                    example_text = f"{{{'；'.join(examples)}}}" if examples else ""
                    meaning_parts.append(prefix + explanation + example_text)
                meaning_text = "  ".join(meaning_parts)

                # Build source tags for display
                source_tags = set()
                if w.source:
                    source_tags.add(shrink_source(w.source))
                for meaning in w.meanings:
                    for sub in meaning.subs:
                        if sub.source:
                            source_tags.add(shrink_source(sub.source))

                # Build display word from mixed: erhua '儿' (pinyin=r) stored as '儿ʳ', JS renders 儿 as subscript
                word_display = ''
                for cz, ien, *_ in w.mixed:
                    raw_cz = re.sub(r'<sub>(.*?)</sub>', r'\1ʰ', cz)  # restore ʰ notation
                    if ien == 'r' and '儿' in cz:
                        word_display += '\u02b3'  # ʳ (U+02B3) replaces erhua 儿
                    else:
                        word_display += raw_cz
                if not word_display:
                    word_display = w.raw_text

                # Compress pinyin for JSON payload: remove spaces between tone digit and next syllable initial.
                pinyin_compact = re.sub(r'([0-9])\s+([A-Za-z])', r'\1\2', w.pien_ien)

                entry = [
                    word_display,          # [0] word: erhua 儿 stored as 'ʳ', ligature with ʰ
                    pinyin_compact,        # [1] compact pinyin (render-side restores syllable spaces)
                    meaning_text,          # [2] meaning
                    w.raw_text,            # [3] raw_text (used to build link in JS)
                    encode_sources(source_tags),  # [4] sources encoded as numeric IDs
                ]
                entries.append(entry)

    return entries


def get_recent_entries(limit=10):
    """Get recently modified entries using git log -p, detecting actual changes."""
    try:
        # Get recently modified .md files with their diffs
        result = subprocess.run(
            ['git', 'log', '-p', '--pretty=format:%H%n%s', '-20', '--',
             'a/', 'b/', 'c/', 'd/', 'e/', 'f/', 'g/', 'h/', 'i/', 'j/', 'k/', 'l/', 'm/', 'n/', 'o/', 'p/', 'q/', 'r/', 's/', 't/', 'u/', 'v/', 'x/', 'y/', 'z/'],
            capture_output=True, text=True, timeout=1000
        )
        if result.returncode != 0:
            return []
        
        # Parse git log output to extract modified entries
        modified_entries_texts = set()  # Track which entry texts were modified
        current_file = None
        in_diff = False
        diff_content = []
        
        for line in result.stdout.split('\n'):
            # Detect diff start
            if line.startswith('diff --git'):
                in_diff = True
                diff_content = [line]
            elif in_diff:
                diff_content.append(line)
                # Look for lines that were changed (added or removed) in the entry structure
                if line.startswith('+# ') or line.startswith('-# '):
                    # Entry heading changed
                    modified_entries_texts.add(line[3:].strip())
                elif line.startswith('+') and not line.startswith('+++'):
                    # Any content addition - mark as modified
                    if line.strip() != '+':
                        pass  # Keep looking
                elif line.startswith('-') and not line.startswith('---'):
                    # Any content removal - mark as modified
                    if line.strip() != '-':
                        pass  # Keep looking
        
        # Better approach: parse all recent commits' diffs and find entries that changed
        # Use git show to get the actual modified lines and extract entry names
        recent_entries_list = []
        
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%H', '--diff-filter=M', '-20', '--',
             'a/', 'b/', 'c/', 'd/', 'e/', 'f/', 'g/', 'h/', 'i/', 'j/', 'k/', 'l/', 'm/', 'n/', 'o/', 'p/', 'q/', 'r/', 's/', 't/', 'u/', 'v/', 'x/', 'y/', 'z/'],
            capture_output=True, text=True, timeout=1000
        )
        commits = result.stdout.strip().split('\n')
        
        # For each commit, find modified entries
        processed_entries = set()  # Track to avoid duplicates
        for commit_hash in commits[:20]:
            if not commit_hash:
                continue
                
            # Get list of modified files in this commit
            file_result = subprocess.run(
                ['git', 'show', '--name-only', '--pretty=format:', commit_hash],
                capture_output=True, text=True, timeout=5
            )
            if file_result.returncode != 0:
                continue
            
            for fname in file_result.stdout.strip().split('\n'):
                if not fname.endswith('.md'):
                    continue
                
                # Get the diff for this file
                diff_result = subprocess.run(
                    ['git', 'show', f'{commit_hash}:{fname}'],
                    capture_output=True, text=True, timeout=5
                )
                if diff_result.returncode != 0:
                    continue
                
                current_content = diff_result.stdout
                current_content = re.sub(r"<!--\n(.*\n)*?-->(\n|$)", "", current_content)
                
                # Get previous version
                prev_result = subprocess.run(
                    ['git', 'show', f'{commit_hash}~1:{fname}'],
                    capture_output=True, text=True, timeout=5
                )
                prev_content = prev_result.stdout if prev_result.returncode == 0 else ""
                prev_content = re.sub(r"<!--\n(.*\n)*?-->(\n|$)", "", prev_content)
                
                # Parse both versions
                current_entries = {}
                for cont in re.split(r"(?:\r?\n){2,}", current_content):
                    if re.fullmatch(r'\s*', cont):
                        continue
                    try:
                        w = parse_cont(cont, fname)
                        current_entries[w.raw_text] = (cont, w)
                    except Exception:
                        continue
                
                prev_entries = {}
                for cont in re.split(r"(?:\r?\n){2,}", prev_content):
                    if re.fullmatch(r'\s*', cont):
                        continue
                    try:
                        w = parse_cont(cont, fname)
                        prev_entries[w.raw_text] = cont
                    except Exception:
                        continue
                
                # Find changed entries
                for raw_text in current_entries:
                    entry_key = (fname, raw_text)
                    if entry_key in processed_entries:
                        continue
                    
                    if raw_text not in prev_entries or current_entries[raw_text][0] != prev_entries[raw_text]:
                        processed_entries.add(entry_key)
                        cont, w = current_entries[raw_text]
                        
                        # Build meanings text
                        meaning_parts = []
                        for i, meaning in enumerate(w.meanings):
                            prefix = ORDERS[i] + " " if len(w.meanings) > 1 else ""
                            explanation = meaning.explanation
                            explanation = re.sub(r'<[^>]+>', '', explanation)
                            explanation = re.sub(r'\\?\[.*?\\?\]', '', explanation)
                            explanation = explanation.strip()
                            examples = []
                            for sub in meaning.subs:
                                for ex in sub.examples:
                                    if not ex:
                                        continue
                                    ex = ex.strip()
                                    if not ex:
                                        continue
                                    ex = re.sub(r'<[^>]+>', '', ex)
                                    ex = re.sub(r'\\?\[.*?\\?\]', '', ex)
                                    ex = re.sub(r'^例[：:]', '', ex)
                                    ex = ex.strip()
                                    if ex:
                                        ex = ex.replace('{', '').replace('}', '')
                                        examples.append(ex)
                            example_text = f"{{{'；'.join(examples)}}}" if examples else ""
                            meaning_parts.append(prefix + explanation + example_text)
                        meaning_text = "  ".join(meaning_parts)
                        
                        # Build source tags
                        source_tags = set()
                        if w.source:
                            source_tags.add(shrink_source(w.source))
                        for meaning in w.meanings:
                            for sub in meaning.subs:
                                if sub.source:
                                    source_tags.add(shrink_source(sub.source))
                        
                        # Build display word
                        word_display = ''
                        for cz, ien, *_ in w.mixed:
                            raw_cz = re.sub(r'<sub>(.*?)</sub>', r'\1ʰ', cz)
                            if ien == 'r' and '儿' in cz:
                                word_display += '\u02b3'
                            else:
                                word_display += raw_cz
                        if not word_display:
                            word_display = w.raw_text

                        pinyin_compact = re.sub(r'([0-9])\s+([A-Za-z])', r'\1\2', w.pien_ien)
                        
                        entry = [
                            word_display,
                            pinyin_compact,
                            meaning_text,
                            w.raw_text,
                            encode_sources(source_tags),
                        ]
                        recent_entries_list.append(entry)
                        
                        if len(recent_entries_list) >= limit:
                            break
                
                if len(recent_entries_list) >= limit:
                    break
            
            if len(recent_entries_list) >= limit:
                break
        
        return recent_entries_list[:limit]
    except Exception as e:
        print(f"Warning: Could not get recent entries: {e}")
        return []


TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "search_template.html")


def load_html_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()



def main():
    print("Collecting dictionary entries...")
    entries = collect_all_entries()
    print(f"Collected {len(entries)} entries.")

    print("Collecting recently modified entries...")
    recent_entries = get_recent_entries()
    print(f"Collected {len(recent_entries)} recent entries.")

    # Find indices of recent entries in the full entries list
    # Build a map from (word, pinyin) to indices for matching
    entry_key_to_indices = {}
    for i, entry in enumerate(entries):
        key = (entry[0], entry[1])  # (word, pinyin)
        if key not in entry_key_to_indices:
            entry_key_to_indices[key] = []
        entry_key_to_indices[key].append(i)
    
    recent_indices = []
    for recent_entry in recent_entries:
        key = (recent_entry[0], recent_entry[1])
        if key in entry_key_to_indices:
            # Use the first matching index
            idx = entry_key_to_indices[key][0]
            recent_indices.append(idx)
    
    data_json = json.dumps(entries, ensure_ascii=False, separators=(',', ':'))
    recent_data_json = json.dumps(recent_indices, ensure_ascii=False, separators=(',', ':'))
    source_names_json = json.dumps(SOURCE_NAMES, ensure_ascii=False, separators=(',', ':'))

    from datetime import datetime
    from zoneinfo import ZoneInfo
    timestamp = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y年%m月%d号%-H点更新")

    html = load_html_template().replace('__DATA_JSON__', data_json).replace('__RECENT_DATA_JSON__', recent_data_json).replace('__SOURCE_NAMES_JSON__', source_names_json).replace('__TIMESTAMP__', timestamp)

    out_path = os.path.join("docs", "search.html")
    os.makedirs("docs", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Written to {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
