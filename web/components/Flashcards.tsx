'use client';

import Link from 'next/link';
import { useState } from 'react';
import { itemByKey } from '@/lib/course';
import { addXp, dueCards, gradeCard, removeCard, useProgress } from '@/lib/progress';
import { Pinyin } from './Pinyin';
import { HumButton, ToneStrip } from './Tone';

const BOX_LABEL = ['新', '刚学', '有点熟', '比较熟', '很熟', '牢固', '掌握'];

export function Flashcards() {
  const p = useProgress();
  const [shown, setShown] = useState(false);
  const due = dueCards(p);
  const all = Object.entries(p.cards);

  if (!all.length) {
    return (
      <div className="card mx-auto max-w-md p-8 text-center">
        <div className="text-5xl">🗂️</div>
        <p className="mt-4 font-bold">还没有复习卡片</p>
        <p className="mt-1 text-sm text-muted">每学完一课，这一课的词会自动变成卡片；在词典里也可以把词加进来。</p>
        <Link href="/learn" className="btn-primary mt-6">
          去学第一课
        </Link>
      </div>
    );
  }

  const current = due[0];
  const syl = current ? current[1].p.split(' ') : [];
  const item = current ? itemByKey.get(current[0]) : undefined;

  function grade(g: 'again' | 'hard' | 'good') {
    gradeCard(current[0], g);
    if (g !== 'again') addXp(2);
    setShown(false);
  }

  return (
    <div className="space-y-8">
      {current ? (
        <div className="mx-auto max-w-md">
          <p className="mb-3 text-center text-sm font-bold text-muted">今天还有 {due.length} 张</p>
          <div className="card p-8 text-center">
            <div className="text-6xl font-black">{current[1].w}</div>
            {shown ? (
              <div className="animate-pop">
                <div className="mt-4 text-xl">
                  <Pinyin p={current[1].p} />
                </div>
                <div className="mt-2 text-lg font-bold">{current[1].g}</div>
                <div className="mt-4 flex items-center justify-center gap-3">
                  <ToneStrip syl={syl} />
                  <HumButton syl={syl} />
                </div>
                {item?.ex[0] && <p className="mt-4 rounded-2xl bg-paper px-4 py-3 text-left text-[15px]">{item.ex[0].t.replace('～', current[1].w)}</p>}
              </div>
            ) : (
              <p className="mt-6 text-muted">先自己说一遍：怎么读？什么意思？</p>
            )}
          </div>
          {shown ? (
            <div className="mt-4 grid grid-cols-3 gap-3">
              <button type="button" onClick={() => grade('again')} className="btn-ghost">
                忘了
              </button>
              <button type="button" onClick={() => grade('hard')} className="btn-ghost">
                有点模糊
              </button>
              <button type="button" onClick={() => grade('good')} className="btn-primary">
                记得
              </button>
            </div>
          ) : (
            <button type="button" onClick={() => setShown(true)} className="btn-primary mt-4 w-full">
              看答案
            </button>
          )}
        </div>
      ) : (
        <div className="card mx-auto max-w-md p-8 text-center">
          <div className="text-5xl">🎉</div>
          <p className="mt-4 font-bold">今天的卡片都复习完了</p>
          <p className="mt-1 text-sm text-muted">明天再来。现在可以去学一节新课。</p>
          <Link href="/learn" className="btn-primary mt-6">
            学新课
          </Link>
        </div>
      )}

      <section>
        <h2 className="h2">全部卡片 <span className="text-sm font-normal text-muted">{all.length} 张</span></h2>
        <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {all.map(([key, c]) => (
            <div key={key} className="flex items-center gap-3 rounded-2xl bg-white px-4 py-3 ring-1 ring-line">
              <span className="text-lg font-bold">{c.w}</span>
              <Pinyin p={c.p} className="text-sm" />
              <span className="ml-auto chip">{BOX_LABEL[c.box] || '掌握'}</span>
              <button type="button" aria-label="移除" onClick={() => removeCard(key)} className="text-xl text-muted">
                ×
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
