#!/usr/bin/env python3
"""把仓库根目录的词条 md / 单字 csv / 语法笔记导出为 web/data/*.json。在仓库根目录运行。"""
import csv
import glob
import json
import os
import re
import string
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import generate_search as gs  # noqa: E402
import tae_rv_ipa  # noqa: E402
import ti_fan_ien_converter as conv  # noqa: E402

OUT = os.path.join(ROOT, "web", "data")
REGIONS = ["泰兴", "如皋", "泰县", "兴化"]


def clean(text):
    text = re.sub(r"<[^>]+>", "", text or "")
    text = re.sub(r"\\?\[.*?\\?\]\(.*?\)", "", text)
    return text.strip()


def load_csv_ipa():
    """单字音表自带每个声母、韵母的音标，比按规则拼出来的更准。"""
    shen_ipa, yen_ipa = {}, {}
    with open(os.path.join(ROOT, "daen_cz.csv"), encoding="U8") as f:
        for row in csv.reader(f):
            if len(row) >= 10:
                shen_ipa.setdefault(row[2], row[8])
                yen_ipa.setdefault(row[3], row[9].replace("?", "ʔ"))
    return shen_ipa, yen_ipa


CSV_SHEN_IPA, CSV_YEN_IPA = load_csv_ipa()


def standard_ipa(ien):
    if ien == "r":
        return "˞"
    base = re.sub(r"\d$", "", ien)
    tio = ien[len(base):]
    for cut in (2, 1, 0):
        shen, yen = base[:cut], base[cut:]
        if (shen in CSV_SHEN_IPA or not shen) and yen in CSV_YEN_IPA and (cut == 0 or shen in tae_rv_ipa.tae_rv_ipa_shen):
            return CSV_SHEN_IPA.get(shen, "") + CSV_YEN_IPA[yen] + tio
    shen, gae, yen, tio = conv.parse_pien_ien(ien)
    return tae_rv_ipa.tae_rv_ipa_shen[shen] + tae_rv_ipa.tae_rv_ipa_gae[gae] + tae_rv_ipa.tae_rv_ipa_yen[yen] + tio


def join_ipa(func, syllables):
    out = []
    for cz, ien in syllables:
        ipa = func(cz, ien) if func is not standard_ipa else standard_ipa(ien)
        if ipa == "˞" and out:
            out[-1] = re.sub(r"(\d?)$", "˞\\1", out[-1], count=1)
        else:
            out.append(ipa)
    return " ".join(out)


def entry_regions(w):
    regions = set()
    names = [w.source or ""] + [s.source or "" for m in w.meanings for s in m.subs]
    for name in names:
        if name == "通用":
            regions.update(REGIONS)
        short = gs.shrink_source(name)
        if short in REGIONS:
            regions.add(short)
    return regions


def build_entries():
    entries = []
    failed = 0
    for letter in string.ascii_lowercase.replace("w", ""):
        for fname in sorted(glob.glob(os.path.join(letter, "*.md"))):
            content = open(fname, encoding="U8").read()
            content = re.sub(r"<!--\n(.*\n)*?-->(\n|$)", "", content)
            for cont in re.split(r"(?:\r?\n){2,}", content):
                if re.fullmatch(r"\s*", cont):
                    continue
                try:
                    w = gs.parse_cont(cont, fname)
                except Exception:
                    failed += 1
                    continue
                syllables = [(re.sub(r"<[^>]+>", "", cz), ien) for cz, ien, *_ in w.mixed]
                voiced = [(cz, ien) for cz, ien in syllables if ien]
                meanings = []
                sources = []
                common = False
                if w.source:
                    sources.append(w.source)
                for m in w.meanings:
                    examples = []
                    for sub in m.subs:
                        if sub.source == "通用":
                            common = True
                        elif sub.source and sub.source not in sources:
                            sources.append(sub.source)
                        for ex in sub.examples:
                            ex = re.sub(r"^例[：:]", "", clean(ex))
                            if ex:
                                examples.append(ex)
                    meanings.append({"d": clean(m.explanation), "ex": examples})
                ipa = {}
                try:
                    ipa["通用"] = join_ipa(standard_ipa, voiced)
                except Exception:
                    pass
                for region in sorted(entry_regions(w)):
                    try:
                        ipa[region] = join_ipa(getattr(conv, region), voiced)
                    except Exception:
                        pass
                entries.append({
                    "w": "".join(cz for cz, _ in syllables) or w.raw_text,
                    "p": w.pien_ien,
                    "s": [[cz, ien] for cz, ien in syllables],
                    "m": meanings,
                    "src": sources,
                    "c": common,
                    "ipa": ipa,
                    "f": fname,
                })
    entries.sort(key=lambda e: (re.sub(r"\d", "", e["p"]), e["p"], e["w"]))
    # 词条网址用“词-拼音”，不用序号：词典增删词条后序号会整体挪位，已被收录的网址就全错了。
    seen = {}
    for e in entries:
        first = e["p"].split(",")[0].strip().replace(" ", "-")
        key = re.sub(r"[^\w-]+", "", f"{e['w']}-{first}") or "x"
        seen[key] = seen.get(key, 0) + 1
        e["id"] = key if seen[key] == 1 else f"{key}-{seen[key]}"
    return entries, failed


def build_chars():
    chars = []
    with open("daen_cz.csv", encoding="U8") as f:
        for row in csv.reader(f):
            if len(row) < 10:
                continue
            trad, simp, shen, yen, tio, words, note, cat, ipa_s, ipa_y = row[:10]
            chars.append({"t": trad, "c": simp, "p": shen + yen + tio, "eg": words, "n": note, "k": cat, "ipa": ipa_s + ipa_y})
    return chars


def split_example(text, word):
    text = text.strip()
    note = ""
    if "/" in text:
        text, note = text.split("/", 1)
    return {"t": text.strip(), "n": note.strip()}


def pick_examples(entry_list, word):
    seen, out = set(), []
    for e in entry_list:
        for m in e["m"]:
            for raw in m["ex"]:
                for part in re.split(r"[｜|]", raw):
                    ex = split_example(part, word)
                    t = ex["t"]
                    if t.count("～") != 1 or not 5 <= len(t) <= 26 or t in seen:
                        continue
                    if re.search(r"[《》（）()\[\]A-Za-z肏屄屌卵屎尿嫖婊死杀奸赌骚]", t):
                        continue
                    seen.add(t)
                    out.append(ex)
    out.sort(key=lambda ex: abs(len(ex["t"]) - 11))
    return out[:3]


def build_course(entries, chars):
    by_word = {}
    for e in entries:
        by_word.setdefault(e["w"], []).append(e)
    by_char = {}
    for c in chars:
        by_char.setdefault(c["c"], []).append(c)
    units, errors = [], []
    for line in open(os.path.join(ROOT, "web", "content", "course.txt"), encoding="U8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith("U "):
            uid, title, icon, desc = line[2:].split("|")
            units.append({"id": uid, "title": title, "icon": icon, "desc": desc, "lessons": []})
            continue
        if line.startswith("L "):
            unit = units[-1]
            unit["lessons"].append({"id": f"{unit['id']}-{len(unit['lessons']) + 1}", "title": line[2:], "items": []})
            continue
        is_char = line.startswith("=")
        word, pinyin, gloss = line.lstrip("=").split("|")
        item = {"w": word, "p": pinyin, "g": gloss, "ex": [], "defs": []}
        same = by_word.get(word, [])
        exact = [e for e in same if pinyin in [r.strip() for r in e["p"].split(",")]]
        if is_char:
            hit = [c for c in by_char.get(word, []) if c["p"] == pinyin]
            if not hit:
                errors.append(f"单字表里没有 {word} {pinyin}")
                continue
            item["eg"] = hit[0]["eg"]
            item["s"] = [[word, pinyin]]
            item["ipa"] = standard_ipa(pinyin)
            exact = exact or [e for e in same if re.sub(r"\d", "", e["p"]) == re.sub(r"\d", "", pinyin)]
        else:
            if not exact:
                have = "; ".join(e["p"] for e in same) or "无此词"
                errors.append(f"词典里没有 {word} {pinyin}（现有：{have}）")
                continue
            best = max(exact, key=lambda e: (len(e["src"]) + (5 if e["c"] else 0), sum(len(m["ex"]) for m in e["m"])))
            syll = pinyin.split(" ")
            chars_only = [cz for cz, ien in best["s"] if ien]
            if len(chars_only) != len(syll):
                errors.append(f"{word} {pinyin} 字数与音节数不一致")
                continue
            item["s"] = [[cz, ien] for cz, ien in zip(chars_only, syll)]
            item["ipa"] = join_ipa(standard_ipa, [(cz, ien) for cz, ien in item["s"]])
        if exact:
            best = max(exact, key=lambda e: (len(e["src"]) + (5 if e["c"] else 0), sum(len(m["ex"]) for m in e["m"])))
            item["id"] = best["id"]
            item["defs"] = [m["d"] for m in best["m"][:3] if m["d"]]
            item["ex"] = pick_examples(exact, word)
        units[-1]["lessons"][-1]["items"].append(item)
    if errors:
        print("\n".join(errors))
        sys.exit(f"课程里有 {len(errors)} 个词条对不上词典，构建中止")
    return units


def build_sounds():
    """每个声母、韵母各取几个常用字做例字（单字表按常用度排序）。"""
    initials, finals = {}, {}
    seen_i, seen_f = {}, {}
    with open("daen_cz.csv", encoding="U8") as f:
        for row in csv.reader(f):
            if len(row) < 10:
                continue
            _, simp, shen, yen, tio, words, note, cat, ipa_s, ipa_y = row[:10]
            if not tio or tio == "0" or note or cat or len(simp) != 1:
                continue
            ex = {"c": simp, "p": shen + yen + tio}
            if shen and len(initials.setdefault(shen, {"ipa": ipa_s, "ex": []})["ex"]) < 4 and simp not in seen_i.setdefault(shen, set()):
                initials[shen]["ex"].append(ex)
                seen_i[shen].add(simp)
            if len(finals.setdefault(yen, {"ipa": ipa_y.replace("?", "ʔ"), "ex": []})["ex"]) < 4 and simp not in seen_f.setdefault(yen, set()):
                finals[yen]["ex"].append(ex)
                seen_f[yen].add(simp)
    return {
        "initials": [{"k": k, **v} for k, v in initials.items()],
        "finals": [{"k": k, **v} for k, v in finals.items() if len(v["ex"]) >= 2],
    }


def build_notes():
    notes = []
    for title, fname in [("语法与词法", "语法与词法.md"), ("泰兴连读变调", "泰兴连读变调.md")]:
        lines = []
        for raw in open(fname, encoding="U8"):
            raw = raw.rstrip("\n")
            if not raw.strip():
                continue
            head = re.match(r"^(#+) *(.*)$", raw)
            if head:
                lines.append({"h": len(head.group(1)), "t": head.group(2)})
                continue
            item = re.match(r"^(\s*)- (.*)$", raw)
            if item:
                lines.append({"li": len(item.group(1).replace("\t", "  ")) // 2, "t": item.group(2)})
            else:
                lines.append({"t": raw.strip()})
        notes.append({"title": title, "file": fname, "lines": lines})
    return notes


def main():
    os.makedirs(OUT, exist_ok=True)
    entries, failed = build_entries()
    chars = build_chars()
    course = build_course(entries, chars)
    json.dump(course, open(os.path.join(OUT, "course.json"), "w", encoding="U8"), ensure_ascii=False, separators=(",", ":"))
    json.dump(build_sounds(), open(os.path.join(OUT, "sounds.json"), "w", encoding="U8"), ensure_ascii=False, separators=(",", ":"))
    json.dump(build_notes(), open(os.path.join(OUT, "notes.json"), "w", encoding="U8"), ensure_ascii=False, separators=(",", ":"))
    print(f"course: units={len(course)} lessons={sum(len(u['lessons']) for u in course)} items={sum(len(l['items']) for u in course for l in u['lessons'])}")
    json.dump(entries, open(os.path.join(OUT, "entries.json"), "w", encoding="U8"), ensure_ascii=False, separators=(",", ":"))
    json.dump(chars, open(os.path.join(OUT, "chars.json"), "w", encoding="U8"), ensure_ascii=False, separators=(",", ":"))
    print(f"entries={len(entries)} failed={failed} chars={len(chars)}")


if __name__ == "__main__":
    main()
