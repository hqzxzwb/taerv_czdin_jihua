import fs from 'fs';
import path from 'path';
import type { CharReading, Entry, SearchHit } from './types';
import { stripTones } from './tones';

interface Indexed {
  e: Entry;
  toneless: string;
  compact: string;
  full: string;
}

interface Store {
  entries: Entry[];
  index: Indexed[];
  byWord: Map<string, Entry[]>;
  chars: Map<string, CharReading[]>;
  maxWord: number;
}

const g = globalThis as unknown as { __tairu?: Store };

function read<T>(name: string): T {
  return JSON.parse(fs.readFileSync(path.join(process.cwd(), 'data', name), 'utf8')) as T;
}

export function store(): Store {
  if (g.__tairu) return g.__tairu;
  const entries = read<Entry[]>('entries.json');
  const byWord = new Map<string, Entry[]>();
  const index = entries.map((e) => {
    const list = byWord.get(e.w);
    if (list) list.push(e);
    else byWord.set(e.w, [e]);
    const toneless = stripTones(e.p).toLowerCase();
    return { e, toneless, compact: toneless.replace(/[\s,]/g, ''), full: e.p.toLowerCase().replace(/\s/g, '') };
  });
  const chars = new Map<string, CharReading[]>();
  for (const c of read<CharReading[]>('chars.json')) {
    for (const key of new Set([c.c, c.t])) {
      const list = chars.get(key);
      if (list) list.push(c);
      else chars.set(key, [c]);
    }
  }
  g.__tairu = { entries, index, byWord, chars, maxWord: 6 };
  return g.__tairu;
}

export function firstDef(e: Entry, max = 60): string {
  const d = e.m.map((m) => m.d).filter(Boolean).join('；');
  return d.length > max ? d.slice(0, max) + '…' : d;
}

export function hit(e: Entry): SearchHit {
  return { id: e.id, w: e.w, p: e.p, d: firstDef(e) };
}

export function search(raw: string, limit = 60): SearchHit[] {
  const q = raw.trim().toLowerCase();
  if (!q) return [];
  const { index } = store();
  const latin = /^[a-z0-9\s,]+$/.test(q);
  const scored: [number, Entry][] = [];
  if (latin) {
    const hasTone = /\d/.test(q);
    const qc = q.replace(/[\s,]/g, '');
    for (const it of index) {
      const target = hasTone ? it.full : it.compact;
      let score = 0;
      if (target === qc || target.split(',').includes(qc)) score = 100;
      else if (target.startsWith(qc)) score = 70;
      else if (!hasTone && it.toneless.split(/[\s,]+/).includes(q)) score = 50;
      if (score) scored.push([score - it.e.w.length, it.e]);
    }
  } else {
    for (const it of index) {
      const w = it.e.w;
      let score = 0;
      if (w === q) score = 100;
      else if (w.startsWith(q)) score = 80;
      else if (w.includes(q)) score = 60;
      else if (it.e.m.some((m) => m.d.includes(q))) score = it.e.m[0]?.d.startsWith(q) ? 45 : 30;
      if (score) scored.push([score - w.length + Math.min(it.e.src.length, 5), it.e]);
    }
  }
  scored.sort((a, b) => b[0] - a[0] || a[1].id - b[1].id);
  return scored.slice(0, limit).map(([, e]) => hit(e));
}

export interface Token {
  text: string;
  kind: 'word' | 'char' | 'plain';
  syl: [string, string][];
  id?: number;
  alts?: { p: string; eg: string; n: string }[];
}

// 先按词典最长匹配取词的读音，其余逐字查单字音表。
export function annotate(text: string): Token[] {
  const { byWord, chars, maxWord } = store();
  const cps = Array.from(text);
  const out: Token[] = [];
  let i = 0;
  while (i < cps.length) {
    let matched = false;
    for (let len = Math.min(maxWord, cps.length - i); len >= 2; len--) {
      const word = cps.slice(i, i + len).join('');
      const list = byWord.get(word);
      if (!list) continue;
      const e = list.reduce((a, b) => (b.src.length + (b.c ? 5 : 0) > a.src.length + (a.c ? 5 : 0) ? b : a));
      const first = e.p.split(',')[0].trim().split(/\s+/);
      const voiced = e.s.filter(([, p]) => p);
      if (voiced.length !== first.length || voiced.length !== len) continue;
      out.push({ text: word, kind: 'word', id: e.id, syl: voiced.map(([c], k) => [c, first[k]]) });
      i += len;
      matched = true;
      break;
    }
    if (matched) continue;
    const ch = cps[i];
    const readings = chars.get(ch);
    if (readings) {
      const uniq = readings.filter((r, k) => readings.findIndex((x) => x.p === r.p) === k);
      out.push({ text: ch, kind: 'char', syl: [[ch, uniq[0].p]], alts: uniq.map((r) => ({ p: r.p, eg: r.eg, n: r.n })) });
    } else {
      const last = out[out.length - 1];
      if (last && last.kind === 'plain') last.text += ch;
      else out.push({ text: ch, kind: 'plain', syl: [] });
    }
    i++;
  }
  return out;
}

export function dailyEntry(): Entry {
  const { entries } = store();
  const pool = entries.filter((e) => e.c && e.m.some((m) => m.ex.length) && e.w.length <= 4);
  const day = Math.floor((Date.now() + 8 * 3600 * 1000) / 86400000);
  return pool[day % pool.length];
}
