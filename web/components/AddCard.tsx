'use client';

import { addCards, removeCard, useProgress } from '@/lib/progress';

export function AddCard({ w, p, g }: { w: string; p: string; g: string }) {
  const progress = useProgress();
  const key = `${w}|${p}`;
  const has = !!progress.cards[key];
  return (
    <button type="button" onClick={() => (has ? removeCard(key) : addCards([{ w, p, g }]))} className={has ? 'btn-ghost' : 'btn-primary'}>
      {has ? '已在复习卡片里' : '加入复习卡片'}
    </button>
  );
}
