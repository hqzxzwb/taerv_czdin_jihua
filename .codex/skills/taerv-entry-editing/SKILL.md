---
name: taerv-entry-editing
description: Use when editing or adding dictionary entries in the taerv_czdin_jihua project, especially when handling entry structure, definition bullets, reference-book markers, and formatting conventions across existing files.
---

# Taerv Entry Editing

Use this skill when modifying this repository's dictionary entry files.

## Editing principle

Check the surrounding file and entry before editing. This project currently has two marker styles, and both are valid in existing files:

- Legacy style: use `>` for reference-book lines and `-` for definition lines.
- Newer style: use `*` for reference-book lines and `+` for definition lines.

When editing an existing entry, keep the local style consistent. Do not mix the two marker styles within the same entry unless the user explicitly asks for normalization or conversion.

## Entry skeleton

Typical entry structure:

```md
# 中文词条
zhon1 ven2
txe:zhon1 ven1
> 参考文献
- 义项一
  - 例句一/例句解释
  - 例句二
- 义项二
```

The same structure may also appear in newer files as:

```md
# 中文词条
zhon1 ven2
txe:zhon1 ven1
+ 义项一
  * 通用
    - 例句一
  * 参考文献
    - 例句二
+ 义项二
  * 参考文献
    + 补充说明
```

There should be no blank line between adjacent entries.

## Pronunciation line

The line immediately after `# 中文词条` is the main normalized pronunciation line.

- If one written form has multiple pronunciations but the meaning is the same, separate whole readings with `,`.
- If only one character within the word has multiple readings, separate those variants with `/`.
- If the written form, pronunciation, and meaning all differ, split them into separate entries rather than merging them.
- If there is a multi-character contracted reading, add `ʰ` after every contracted character except the first.

## Local pronunciation and irregular reading notes

In principle, systematic local sound differences should be normalized into the repository's standard phonology before being placed on the main pronunciation line.

- If a locality has a structured alternate reading worth preserving, add an extra pronunciation line such as `txe:`, `xh:`, `dt:`, `rg:`, `rd:`, `tz:` directly below the main pronunciation line.
- Use these prefixed lines for actual alternate pronunciations, not for general commentary.
- If the source uses a special local reading, a special written form, or a form whose sound or character choice should not replace the normalized main line, record that as a note in the body instead of rewriting the main pronunciation line.

Common note styles seen in the repository include:

- `泰兴方言辞典作“着”`
- `东台音hu1 in1。`
- `（原文作“䐥”，音不合）`
- `也作“……”`

Put such notes near the relevant义项、例句或参考书信息, and match the surrounding file's style. Existing files use plain lines, indented continuation lines, `+` note lines, and sometimes HTML comments.

## Definitions and sources

- Each义项 occupies one bullet line.
- Reference-book lines usually sit immediately under the relevant义项.
- In legacy-style entries, the source often appears once near the top of the entry.
- In newer-style entries, each义项 often carries its own `* 参考文献` line.
- In newer-style entries, `* 通用` is a special marker meaning that this义项 is used across localities. It applies only to the current义项, not to the whole entry.
- If several sources support the same义项, list them separately instead of merging names into one line.
- Put `* 通用` before book-source lines when both appear under the same义项.

## Example sentences

Example sentences are child bullets under the relevant义项.

- Use full-width `～` to stand for the current headword, no matter how many characters the headword has.
- If an example has an explanation, separate example and explanation with `/`.
- Keep each example on its own bullet line.
- Examples that are generally used across localities should go under `* 通用`.
- Examples quoted from a specific source should stay under that source line instead of under `* 通用`.
- Quoted examples from books can be kept with Chinese quotation marks and citation in the same line if the surrounding file does that.
- If an example is really a usage note rather than a full sentence, keep the repository's existing style instead of forcing complete-sentence prose.

## IPA generation

- A义项 marked with `* 通用` will cause deploy-time IPA generation for every currently supported locality converter.
- Existing newer-style义项 with no source line remain valid, but they are not automatically treated as `通用`.

## Textual notes from sources

This repository often preserves source-level remarks when useful for later review.

- Prefer trusting the source's pronunciation over its written form when the two conflict.
- If the source's graph form is questionable, keep the normalized headword and record the source form in a note.
- If the source reflects only a local irregular reading, mention it in a note or locality-prefixed pronunciation line rather than replacing the normalized main reading.

## Before finishing

Quick check:

- Marker style matches nearby entries.
- Pronunciation line is normalized unless a locality-prefixed line is intentionally added.
- Local special readings and source-specific forms are preserved in notes when needed.
- Example lines stay under the correct义项.
- No accidental blank lines were introduced between entries.
- Keep the file's trailing newline. Do not remove the final newline at end of file.
