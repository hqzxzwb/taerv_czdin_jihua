'use client';

import Link from 'next/link';
import type { CourseItem } from '@/lib/types';
import { Ruby } from './Pinyin';
import { HumButton, ToneStrip } from './Tone';

export function Example({ text, word }: { text: string; word: string }) {
  const [head, tail] = text.split('～');
  return (
    <span>
      {head}
      <b className="text-brand-deep">{word}</b>
      {tail}
    </span>
  );
}

export function WordCard({ item }: { item: CourseItem }) {
  const syl = item.s.map(([, p]) => p).filter(Boolean);
  return (
    <div className="card animate-pop p-6 text-center sm:p-8">
      <Ruby syl={item.s} size="text-5xl sm:text-6xl" />
      <div className="mt-4 text-xl font-bold">{item.g}</div>
      <div className="mt-1 font-mono text-sm text-muted">/{item.ipa.replace(/\d/g, '')}/</div>
      <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
        <ToneStrip syl={syl} />
        <HumButton syl={syl} />
      </div>
      {item.ex.length > 0 && (
        <ul className="mt-5 space-y-1.5 border-t border-line pt-4 text-left text-[15px] leading-relaxed">
          {item.ex.slice(0, 2).map((ex) => (
            <li key={ex.t}>
              <Example text={ex.t} word={item.w} />
              {ex.n && <span className="ml-1 text-muted">（{ex.n}）</span>}
            </li>
          ))}
        </ul>
      )}
      {item.eg && !item.ex.length && <div className="mt-4 text-sm text-muted">组词：{item.eg}</div>}
      {item.id !== undefined && (
        <Link href={`/dict/${item.id}`} className="mt-4 inline-block text-sm font-bold text-muted underline underline-offset-4">
          查看词典里的完整解释
        </Link>
      )}
    </div>
  );
}
