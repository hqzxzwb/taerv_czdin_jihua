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
LINK_FORMAT = "%s#%s"
PY_FORMAT = re.compile(r"^([bpmfdtnlgkhjqxzcsr]|[zcs]h|ng|dd)?([aoeivuyrzm]+|ng)[nh]?[0-9]?$")


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

                # Build link (relative path only; prefix is added in JS)
                link = LINK_FORMAT % (fname.replace("\\", "/"), w.text)

                # Build meanings text (plain, for search indexing and display)
                meaning_parts = []
                for i, meaning in enumerate(w.meanings):
                    prefix = ORDERS[i] + " " if len(w.meanings) > 1 else ""
                    explanation = meaning.explanation
                    explanation = re.sub(r'<[^>]+>', '', explanation)
                    explanation = re.sub(r'\\?\[.*?\\?\]', '', explanation)
                    explanation = explanation.strip()
                    meaning_parts.append(prefix + explanation)
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

                entry = {
                    "w": word_display,      # word: erhua 儿 stored as 'ʳ', ligature with ʰ
                    "p": w.pien_ien,        # pinyin
                    "m": meaning_text,      # meaning
                    "l": link,              # link (relative path, prefix added in JS)
                    "s": sorted(source_tags),  # sources
                }
                entries.append(entry)

    return entries


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>泰如辞典</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: "Noto Serif CJK SC", "Source Han Serif SC", "SimSun", serif;
      background: #f0f4f8;
      color: #1a2433;
      min-height: 100vh;
    }

    header {
      background: #1e3a5f;
      color: #e8f0fb;
      padding: 1.2rem 1.5rem;
      display: flex;
      align-items: baseline;
      justify-content: center;
      gap: 1rem;
      flex-wrap: wrap;
    }

    header h1 {
      font-size: 1.6rem;
      font-weight: 700;
      letter-spacing: 0.05em;
    }

    header h1 a {
      color: inherit;
      text-decoration: none;
    }

    header a.old-home {
      color: #a8c4e8;
      font-size: 0.85rem;
      text-decoration: none;
    }

    header a.old-home:hover {
      text-decoration: underline;
    }

    .header-links {
      background: #1e3a5f;
      padding: 0.3rem 1rem;
      display: flex;
      justify-content: center;
      gap: 1.5rem;
      border-top: 1px solid #2d5a8e;
    }

    .header-links a {
      color: #a8c4e8;
      font-size: 0.85rem;
      text-decoration: none;
    }

    .header-links a:hover {
      text-decoration: underline;
    }

    .alpha-bar {
      background: #1e3a5f;
      padding: 0.4rem 0.5rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.25rem;
      justify-content: center;
    }

    .alpha-bar a {
      color: #a8c4e8;
      text-decoration: none;
      font-size: 1rem;
      font-family: "Consolas", "Courier New", monospace;
      padding: 0.2em 0.35em;
      border-radius: 3px;
      transition: background 0.15s, color 0.15s;
    }

    @media (hover: hover) {
      .alpha-bar a:hover {
        background: #a8c4e8;
        color: #1e3a5f;
      }
    }

    .alpha-bar a.active {
      background: #a8c4e8;
      color: #1e3a5f;
    }

    .search-bar {
      max-width: 700px;
      margin: 2rem auto 1rem;
      padding: 0 1rem;
    }

    .search-bar label {
      display: block;
      font-size: 0.85rem;
      color: #4a6a8a;
      margin-bottom: 0.4rem;
    }

    .search-row {
      display: flex;
      gap: 0.5rem;
    }

    .search-bar input {
      flex: 1;
      min-width: 0;
      padding: 0.65rem 1rem;
      font-size: 1.1rem;
      border: 2px solid #7aabcc;
      border-radius: 6px;
      background: #f8fbff;
      color: #1a2433;
      outline: none;
      transition: border-color 0.2s;
      font-family: inherit;
    }

    .search-bar input:focus {
      border-color: #1e3a5f;
    }

    #region {
      padding: 0.65rem 0.6rem;
      font-size: 0.95rem;
      border: 2px solid #7aabcc;
      border-radius: 6px;
      background: #f8fbff;
      color: #1a2433;
      outline: none;
      cursor: pointer;
      font-family: inherit;
      transition: border-color 0.2s;
    }

    #region:focus {
      border-color: #1e3a5f;
    }

    .stats {
      max-width: 700px;
      margin: 0 auto 1rem;
      padding: 0 1rem;
      font-size: 0.85rem;
      color: #4a6a8a;
    }

    #results {
      max-width: 700px;
      margin: 0 auto 3rem;
      padding: 0 1rem;
      list-style: none;
    }

    #results li {
      background: #f8fbff;
      border: 1px solid #c0d8ee;
      border-radius: 6px;
      padding: 0.9rem 1.1rem;
      margin-bottom: 0.7rem;
      line-height: 1.7;
      transition: box-shadow 0.15s;
    }

    #results li:hover {
      box-shadow: 0 2px 8px rgba(30,58,95,0.12);
    }

    .entry-word {
      font-size: 1.2rem;
      font-weight: 700;
      margin-right: 0.5rem;
    }

    .entry-word a {
      color: #1e3a5f;
      text-decoration: none;
    }

    .entry-word a:hover { text-decoration: underline; }

    .entry-pinyin {
      font-family: "Consolas", "Courier New", monospace;
      font-size: 0.9rem;
      color: #4a6a8a;
      background: none;
    }

    .entry-sources {
      display: inline-flex;
      flex-wrap: wrap;
      gap: 0.3rem;
      margin-left: 0.4rem;
      vertical-align: middle;
    }

    .entry-source-tag {
      font-size: 0.7rem;
      color: #1a3a5a;
      border-radius: 3px;
      padding: 0.05em 0.4em;
    }
    .src-如皋  { background: #d4edda; color: #1a5c2a; }
    .src-如东  { background: #d1ecf1; color: #0c5460; }
    .src-兴化  { background: #fff3cd; color: #856404; }
    .src-东台  { background: #fde8d8; color: #7a3010; }
    .src-泰兴  { background: #e2d9f3; color: #3d1a78; }
    .src-泰州  { background: #fcd8e0; color: #7a1a30; }
    .src-泰县  { background: #d8eafd; color: #1a3a7a; }
    .src-通用  { background: #e8e8e8; color: #444444; }

    .entry-meaning {
      margin-top: 0.35rem;
      font-size: 0.95rem;
      color: #1e2d3e;
    }

    u { text-decoration: underline; }

    .entry-word sub {
      vertical-align: baseline;
      font-size: 0.65em;
    }

    mark {
      background: #b3d9ff;
      color: inherit;
      border-radius: 2px;
      padding: 0 1px;
    }

    .no-results {
      text-align: center;
      color: #4a6a8a;
      padding: 3rem 1rem;
      font-size: 1rem;
    }

    footer {
      text-align: center;
      padding: 1.5rem;
      font-size: 0.8rem;
      color: #4a6a8a;
      border-top: 1px solid #c0d8ee;
    }
  </style>
</head>
<body>

<header>
  <h1><a href="https://github.com/hqzxzwb/taerv_czdin_jihua" target="_blank" rel="noopener">泰如辞典</a></h1>
</header>

<div class="header-links">
  <a href="https://hqzxzwb.github.io/taerv_czdin_jihua/home.html" target="_blank" rel="noopener">旧版主页</a>
  <a href="https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzUyNjEwMjM0OQ==&action=getalbum&album_id=2505440559352791041" target="_blank" rel="noopener">拼音方案</a>
</div>

<nav class="alpha-bar" id="alphaBar">
  <a href="#" data-letter="A">A</a>
  <a href="#" data-letter="B">B</a>
  <a href="#" data-letter="C">C</a>
  <a href="#" data-letter="D">D</a>
  <a href="#" data-letter="E">E</a>
  <a href="#" data-letter="F">F</a>
  <a href="#" data-letter="G">G</a>
  <a href="#" data-letter="H">H</a>
  <a href="#" data-letter="I">I</a>
  <a href="#" data-letter="J">J</a>
  <a href="#" data-letter="K">K</a>
  <a href="#" data-letter="L">L</a>
  <a href="#" data-letter="M">M</a>
  <a href="#" data-letter="N">N</a>
  <a href="#" data-letter="O">O</a>
  <a href="#" data-letter="P">P</a>
  <a href="#" data-letter="Q">Q</a>
  <a href="#" data-letter="R">R</a>
  <a href="#" data-letter="S">S</a>
  <a href="#" data-letter="T">T</a>
  <a href="#" data-letter="U">U</a>
  <a href="#" data-letter="V">V</a>
  <a href="#" data-letter="X">X</a>
  <a href="#" data-letter="Y">Y</a>
  <a href="#" data-letter="Z">Z</a>
</nav>

<div class="search-bar">
  <label for="q">搜索词条（支持汉字、拼音、解释）</label>
  <div class="search-row">
    <input type="search" id="q" placeholder="例：摞 / lu6 / 叠放" autocomplete="off" autofocus>
    <select id="region">
      <option value="">不限</option>
      <option value="如皋">如皋</option>
      <option value="如东">如东</option>
      <option value="兴化">兴化</option>
      <option value="东台">东台</option>
      <option value="泰兴">泰兴</option>
      <option value="泰州">泰州</option>
      <option value="泰县">泰县</option>
      <option value="通用">通用</option>
    </select>
  </div>
</div>

<p class="stats" id="stats"></p>

<ul id="results"></ul>

<footer><a href="https://github.com/hqzxzwb/taerv_czdin_jihua" target="_blank" rel="noopener">泰如辞典</a> __TIMESTAMP__</footer>

<script>
// ── Embedded dictionary data ──
const LINK_PREFIX = "https://github.com/hqzxzwb/taerv_czdin_jihua/blob/master/";
const DATA = __DATA_JSON__;

// ── Search logic ──
const input = document.getElementById('q');
const regionSelect = document.getElementById('region');
const resultsList = document.getElementById('results');
const stats = document.getElementById('stats');

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function fmtWord(raw) {
  // ʰ marks a ligature: underline the two chars before ʰ, hide ʰ itself
  let s = raw.replace(/(.)(.)ʰ/g, '<u>$1$2</u>');
  // ʳ replaces erhua 儿: render as subscript 儿
  s = s.replace(/\u02b3/g, '<sub>儿</sub>');
  return s;
}

function highlight(text, terms) {
  if (!terms.length) return text;
  const pattern = new RegExp('(' + terms.map(escapeRe).join('|') + ')', 'gi');
  // Split on HTML tags, escape and highlight only text nodes
  return text.split(/(<[^>]+>)/).map(part => {
    if (part.startsWith('<')) return part; // keep tags as-is
    const escaped = part.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    return escaped.replace(pattern, '<mark>$1</mark>');
  }).join('');
}

function score(entry, terms) {
  // Return a relevance score; higher is better
  let s = 0;
  for (const t of terms) {
    const tl = t.toLowerCase();
    const w = entry.w.replace(/\u02b0/g, '').replace(/\u02b3/g, '儿');
    const wNoR = entry.w.replace(/[\u02b0\u02b3]/g, '');
    if (w.includes(t) || wNoR.includes(t)) s += 10;
    if (entry.p.toLowerCase().includes(tl)) s += 5;
    if (entry.m.includes(t)) s += 1;
  }
  return s;
}

function search(query) {
  query = query.trim();
  if (!query && !activeLetter) {
    resultsList.innerHTML = '';
    stats.textContent = `共收录 ${DATA.length} 条词条，请输入关键词搜索或点击音序。`;
    return;
  }

  // Split on whitespace for multi-term search
  const terms = query.split(/\s+/).filter(Boolean);

  // If query is purely pinyin-like (letters + digits only), use syllable-aware matching:
  // split both query and pinyin by spaces, require query tokens to appear as a
  // consecutive subsequence in pinyin tokens where each query token is a prefix
  // of the corresponding pinyin token (e.g. "fen m" matches "fen1 men2" but not "ben fen").
  const isPinyinPhrase = /^[a-zA-Z0-9 ]+$/.test(query);
  const pinyinTerms = isPinyinPhrase ? terms.map(t => t.toLowerCase()) : null;

  const region = regionSelect.value;
  const letter = activeLetter;

  const matches = [];
  for (const entry of DATA) {
    // Filter by region
    if (region && !entry.s.includes(region)) continue;

    // Filter by initial letter of pinyin
    if (letter && entry.p[0].toUpperCase() !== letter) continue;

    const combined = entry.w.replace(/\u02b0/g, '').replace(/\u02b3/g, '儿') + ' ' + entry.p + ' ' + entry.m;
    const combinedNoR = entry.w.replace(/[\u02b0\u02b3]/g, '') + ' ' + entry.p + ' ' + entry.m;
    const combinedLower = combined.toLowerCase();
    const combinedNoRLower = combinedNoR.toLowerCase();

    // For pinyin queries, require query tokens to appear consecutively in the
    // pinyin token list, each as a prefix of the corresponding pinyin syllable.
    if (pinyinTerms) {
      const pyTokens = entry.p.toLowerCase().split(/\s+/);
      let found = false;
      for (let i = 0; i <= pyTokens.length - pinyinTerms.length; i++) {
        if (pinyinTerms.every((qt, j) => pyTokens[i + j].startsWith(qt))) {
          found = true;
          break;
        }
      }
      if (!found) continue;
    } else {
      // Non-pinyin query: check each term matches somewhere (with or without erhua 儿)
      const allMatch = terms.every(t => {
        const tl = t.toLowerCase();
        return combinedLower.includes(tl) || combinedNoRLower.includes(tl);
      });
      if (!allMatch) continue;
    }

    matches.push({ entry, s: score(entry, terms) });
  }

  // Sort by score descending, then by word length ascending
  matches.sort((a, b) => b.s - a.s || a.entry.w.length - b.entry.w.length);

  const letterHint = letter ? `【${letter}】` : '';

  if (matches.length === 0) {
    resultsList.innerHTML = '<li class="no-results">未找到相关词条。</li>';
    stats.textContent = `${letterHint}${query ? `搜索"${query}"，` : ''}共 0 条结果。`;
    return;
  }

  const limit = 200;
  const shown = matches.slice(0, limit);
  stats.textContent = `${letterHint}${query ? `搜索"${query}"，` : ''}找到 ${matches.length} 条结果${matches.length > limit ? `，显示前 ${limit} 条` : ''}。`;

  const fragment = document.createDocumentFragment();
  for (const { entry } of shown) {
    const li = document.createElement('li');

    const wordSpan = document.createElement('span');
    wordSpan.className = 'entry-word';

    const wordLink = document.createElement('a');
    wordLink.href = LINK_PREFIX + entry.l;
    wordLink.target = '_blank';
    wordLink.rel = 'noopener';
    wordLink.innerHTML = highlight(fmtWord(entry.w), terms);
    wordSpan.appendChild(wordLink);

    const pinyinCode = document.createElement('code');
    pinyinCode.className = 'entry-pinyin';
    pinyinCode.innerHTML = highlight(entry.p, terms);

    const sourcesSpan = document.createElement('span');
    sourcesSpan.className = 'entry-sources';
    for (const src of entry.s) {
      const tag = document.createElement('span');
      tag.className = 'entry-source-tag src-' + src;
      tag.textContent = src;
      sourcesSpan.appendChild(tag);
    }

    const meaningDiv = document.createElement('div');
    meaningDiv.className = 'entry-meaning';
    meaningDiv.innerHTML = highlight(entry.m, terms);

    const header = document.createElement('div');
    header.appendChild(wordSpan);
    header.appendChild(document.createTextNode(' '));
    header.appendChild(pinyinCode);
    header.appendChild(sourcesSpan);

    li.appendChild(header);
    li.appendChild(meaningDiv);
    fragment.appendChild(li);
  }

  resultsList.innerHTML = '';
  resultsList.appendChild(fragment);
}

// Alpha-bar navigation
let activeLetter = null;
document.getElementById('alphaBar').addEventListener('click', e => {
  const a = e.target.closest('a[data-letter]');
  if (!a) return;
  e.preventDefault();
  const letter = a.dataset.letter;
  if (activeLetter === letter) {
    // Click same letter again to deactivate
    activeLetter = null;
    a.classList.remove('active');
  } else {
    document.querySelectorAll('#alphaBar a.active').forEach(el => el.classList.remove('active'));
    activeLetter = letter;
    a.classList.add('active');
  }
  triggerSearch();
});

// Debounce input
let timer;
function triggerSearch() {
  clearTimeout(timer);
  timer = setTimeout(() => search(input.value), 200);
}
input.addEventListener('input', triggerSearch);
regionSelect.addEventListener('change', triggerSearch);

// Init stats
stats.textContent = `共收录 ${DATA.length} 条词条，请输入关键词搜索或点击音序。`;

// Support URL ?q= parameter
const urlParams = new URLSearchParams(window.location.search);
const initialQuery = urlParams.get('q');
if (initialQuery) {
  input.value = initialQuery;
  search(initialQuery);
}
</script>
</body>
</html>
"""


def main():
    print("Collecting dictionary entries...")
    entries = collect_all_entries()
    print(f"Collected {len(entries)} entries.")

    data_json = json.dumps(entries, ensure_ascii=False, separators=(',', ':'))

    from datetime import datetime
    from zoneinfo import ZoneInfo
    timestamp = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y年%m月%d号%-H点更新")

    html = HTML_TEMPLATE.replace('__DATA_JSON__', data_json).replace('__TIMESTAMP__', timestamp)

    out_path = os.path.join("docs", "search.html")
    os.makedirs("docs", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Written to {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
