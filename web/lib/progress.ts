'use client';

import { useSyncExternalStore } from 'react';

export interface Card {
  w: string;
  p: string;
  g: string;
  box: number;
  due: number;
}

export interface Progress {
  xp: number;
  days: Record<string, number>;
  lessons: Record<string, number>;
  cards: Record<string, Card>;
}

const KEY = 'tairu.v1';
const EMPTY: Progress = { xp: 0, days: {}, lessons: {}, cards: {} };
export const DAILY_GOAL = 30;
const INTERVALS = [0, 1, 2, 4, 8, 16, 32];

let cache: Progress | null = null;
const listeners = new Set<() => void>();

function load(): Progress {
  if (cache) return cache;
  try {
    cache = { ...EMPTY, ...JSON.parse(localStorage.getItem(KEY) || '{}') };
  } catch {
    cache = EMPTY;
  }
  return cache!;
}

function save(next: Progress) {
  cache = next;
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {}
  listeners.forEach((fn) => fn());
}

export function today(offset = 0) {
  const d = new Date(Date.now() + offset * 86400000);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function dayNumber() {
  const d = new Date();
  return Math.floor(new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() / 86400000);
}

export function useProgress(): Progress {
  return useSyncExternalStore(
    (fn) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    load,
    () => EMPTY,
  );
}

export function addXp(n: number) {
  const p = load();
  save({ ...p, xp: p.xp + n, days: { ...p.days, [today()]: (p.days[today()] || 0) + n } });
}

export function finishLesson(id: string, stars: number) {
  const p = load();
  save({ ...p, lessons: { ...p.lessons, [id]: Math.max(stars, p.lessons[id] || 0) } });
}

export function addCards(items: { w: string; p: string; g: string }[]) {
  const p = load();
  const cards = { ...p.cards };
  for (const it of items) {
    const key = `${it.w}|${it.p}`;
    if (!cards[key]) cards[key] = { w: it.w, p: it.p, g: it.g, box: 1, due: dayNumber() + 1 };
  }
  save({ ...p, cards });
}

export function removeCard(key: string) {
  const p = load();
  const cards = { ...p.cards };
  delete cards[key];
  save({ ...p, cards });
}

export function gradeCard(key: string, grade: 'again' | 'hard' | 'good') {
  const p = load();
  const card = p.cards[key];
  if (!card) return;
  const box = grade === 'again' ? 1 : grade === 'hard' ? card.box : Math.min(card.box + 1, INTERVALS.length - 1);
  const due = dayNumber() + (grade === 'again' ? 0 : INTERVALS[box]);
  save({ ...p, cards: { ...p.cards, [key]: { ...card, box, due } } });
}

export function dueCards(p: Progress): [string, Card][] {
  const now = dayNumber();
  return Object.entries(p.cards).filter(([, c]) => c.due <= now);
}

export function streak(p: Progress): number {
  let n = 0;
  for (let i = p.days[today()] ? 0 : -1; p.days[today(i)]; i--) n++;
  return n;
}

export function resetProgress() {
  save(EMPTY);
}
