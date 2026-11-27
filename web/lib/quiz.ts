import type { CourseItem } from './types';
import { TONE_ORDER, splitTone, stripTones, toneOf } from './tones';

export interface Option {
  key: string;
  label: string;
  pinyin?: string;
  tone?: string;
}

export type Step =
  | { kind: 'learn'; item: CourseItem }
  | { kind: 'choice'; variant: 'meaning' | 'word' | 'pinyin' | 'cloze' | 'tone'; item: CourseItem; title: string; prompt: string; focus?: number; options: Option[]; answer: string }
  | { kind: 'match'; items: CourseItem[] }
  | { kind: 'type'; item: CourseItem };

export function shuffle<T>(list: T[]): T[] {
  const a = [...list];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function distractors(item: CourseItem, pools: CourseItem[][], field: 'g' | 'w', n = 3): CourseItem[] {
  const out: CourseItem[] = [];
  const used = new Set([item[field], item.w + item.g]);
  for (const pool of pools) {
    for (const cand of shuffle(pool)) {
      if (out.length >= n) return out;
      if (used.has(cand[field]) || cand.w === item.w || cand.g === item.g) continue;
      used.add(cand[field]);
      out.push(cand);
    }
  }
  return out;
}

function pinyinVariants(item: CourseItem, pools: CourseItem[][]): string[] {
  const syl = item.p.split(' ');
  const out = new Set<string>();
  const toned = syl.map((s, i) => (/\d/.test(s) ? i : -1)).filter((i) => i >= 0);
  let guard = 0;
  while (out.size < 2 && toned.length && guard++ < 30) {
    const i = toned[Math.floor(Math.random() * toned.length)];
    const [base] = splitTone(syl[i]);
    const current = toneOf(syl[i]);
    const entering = /h$/.test(base);
    const choices = (entering ? ['7', '8'] : ['1', '2', '3', '5', '6']).filter((t) => t !== current);
    const next = [...syl];
    next[i] = base + choices[Math.floor(Math.random() * choices.length)];
    out.add(next.join(' '));
  }
  for (const pool of pools) {
    for (const cand of shuffle(pool)) {
      if (out.size >= 3) break;
      if (cand.p !== item.p && cand.p.split(' ').length === syl.length && stripTones(cand.p) !== stripTones(item.p)) out.add(cand.p);
    }
  }
  return [...out].slice(0, 3);
}

function meaningStep(item: CourseItem, pools: CourseItem[][]): Step {
  const opts = [item, ...distractors(item, pools, 'g')];
  return { kind: 'choice', variant: 'meaning', item, title: '这个词是什么意思？', prompt: item.w, options: shuffle(opts.map((o) => ({ key: o.g, label: o.g }))), answer: item.g };
}

function wordStep(item: CourseItem, pools: CourseItem[][]): Step {
  const opts = [item, ...distractors(item, pools, 'w')];
  return { kind: 'choice', variant: 'word', item, title: '泰如话怎么说？', prompt: item.g, options: shuffle(opts.map((o) => ({ key: o.w, label: o.w, pinyin: o.p }))), answer: item.w };
}

function pinyinStep(item: CourseItem, pools: CourseItem[][]): Step {
  const opts = [item.p, ...pinyinVariants(item, pools)];
  return { kind: 'choice', variant: 'pinyin', item, title: '选出正确的拼音', prompt: item.w, options: shuffle(opts.map((p) => ({ key: p, label: p, pinyin: p }))), answer: item.p };
}

function clozeStep(item: CourseItem, pools: CourseItem[][]): Step | null {
  if (!item.ex.length) return null;
  const ex = item.ex[Math.floor(Math.random() * item.ex.length)];
  const opts = [item, ...distractors(item, pools, 'w')];
  return { kind: 'choice', variant: 'cloze', item, title: '把句子补完整', prompt: ex.t.replace('～', '＿＿'), options: shuffle(opts.map((o) => ({ key: o.w, label: o.w }))), answer: item.w };
}

function toneStep(item: CourseItem): Step | null {
  const idx = item.s.findIndex(([, p]) => /[1235678]$/.test(p));
  if (idx < 0) return null;
  const answer = toneOf(item.s[idx][1]);
  const twin = answer === '1' ? '6' : answer === '6' ? '1' : '';
  const others = shuffle(TONE_ORDER.filter((t) => t !== answer && t !== twin)).slice(0, 3);
  return {
    kind: 'choice',
    variant: 'tone',
    item,
    focus: idx,
    title: `“${item.s[idx][0]}”读第几声？`,
    prompt: item.w,
    options: shuffle([answer, ...others]).map((t) => ({ key: t, label: `第 ${t} 声`, tone: t })),
    answer,
  };
}

// 和普通话写法、意思都一样的词，问“什么意思”等于白问，只练读音。
function soundOnly(item: CourseItem) {
  return item.g === item.w;
}

export function buildSteps(items: CourseItem[], unitItems: CourseItem[], all: CourseItem[]): Step[] {
  const pools = [items, unitItems, all];
  const steps: Step[] = [];
  for (let i = 0; i < items.length; i += 3) {
    const group = items.slice(i, i + 3);
    group.forEach((item) => steps.push({ kind: 'learn', item }));
    shuffle(group).forEach((item, k) => {
      if (soundOnly(item)) steps.push((k % 2 && toneStep(item)) || pinyinStep(item, pools));
      else steps.push((i / 3 + k) % 2 ? wordStep(item, pools) : meaningStep(item, pools));
    });
  }
  const round: Step[] = [];
  shuffle(items).forEach((item, k) => {
    const cloze = clozeStep(item, pools);
    const tone = toneStep(item);
    const recall = soundOnly(item) ? null : k % 2 ? meaningStep(item, pools) : wordStep(item, pools);
    const pick = [pinyinStep(item, pools), cloze, tone, recall].filter(Boolean) as Step[];
    round.push(pick[k % pick.length]);
    if (cloze && pick[k % pick.length] !== cloze) round.push(cloze);
  });
  steps.push(...round.slice(0, Math.max(items.length, 6)));
  const matchable = items.filter((item) => !soundOnly(item));
  if (matchable.length >= 4) steps.push({ kind: 'match', items: shuffle(matchable).slice(0, 5) });
  shuffle(items)
    .slice(0, 2)
    .forEach((item) => steps.push({ kind: 'type', item }));
  return steps;
}

export function checkTyped(input: string, answer: string): 'exact' | 'toneless' | 'wrong' {
  const norm = (s: string) => s.toLowerCase().replace(/[\s,]/g, '');
  if (norm(input) === norm(answer)) return 'exact';
  if (norm(stripTones(input)) === norm(stripTones(answer))) return 'toneless';
  return 'wrong';
}
