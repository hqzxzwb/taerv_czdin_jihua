'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { allItems } from '@/lib/course';
import { addCards, addXp, finishLesson } from '@/lib/progress';
import { buildSteps, checkTyped, shuffle, type Step } from '@/lib/quiz';
import type { CourseItem, Lesson } from '@/lib/types';
import { Pinyin, Ruby } from './Pinyin';
import { ToneContour } from './Tone';
import { WordCard } from './WordCard';

type Verdict = null | { ok: boolean; note?: string };

function Choice({ step, picked, verdict, onPick }: { step: Extract<Step, { kind: 'choice' }>; picked: string | null; verdict: Verdict; onPick: (k: string) => void }) {
  const big = step.variant === 'meaning' || step.variant === 'pinyin' || step.variant === 'tone';
  return (
    <div className="animate-pop">
      <h2 className="h2 text-center">{step.title}</h2>
      <div className="card mx-auto mt-4 max-w-md p-6 text-center">
        {step.variant === 'tone' ? (
          <Ruby syl={step.item.s.map(([c, p], i) => [c, i === step.focus ? p.replace(/\d.*$/, '') + '?' : ''] as [string, string])} size="text-5xl" />
        ) : (
          <div className={big ? 'text-5xl font-black' : 'text-2xl font-bold leading-relaxed'}>{step.prompt}</div>
        )}
        {step.variant === 'meaning' && (
          <div className="mt-2">
            <Pinyin p={step.item.p} />
          </div>
        )}
        {step.variant === 'cloze' && <div className="mt-2 text-sm text-muted">选一个词填进横线</div>}
      </div>
      <div className="mx-auto mt-5 grid max-w-md grid-cols-1 gap-3 sm:grid-cols-2">
        {step.options.map((o) => {
          const isAnswer = o.key === step.answer;
          const chosen = picked === o.key;
          let tone = 'bg-white ring-line hover:ring-ink/30';
          if (verdict && isAnswer) tone = 'bg-ok-soft ring-ok text-ok';
          else if (verdict && chosen) tone = 'bg-bad-soft ring-bad text-bad animate-shake';
          else if (chosen) tone = 'bg-brand-soft ring-brand';
          return (
            <button
              key={o.key}
              type="button"
              disabled={!!verdict}
              onClick={() => onPick(o.key)}
              className={`flex min-h-[60px] items-center justify-center gap-3 rounded-2xl px-4 py-3 text-lg font-bold ring-2 transition ${tone}`}
            >
              {o.tone && <ToneContour tone={o.tone} size={36} />}
              {step.variant === 'pinyin' ? <Pinyin p={o.label} /> : o.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Match({ items, onMiss, onDone }: { items: CourseItem[]; onMiss: () => void; onDone: () => void }) {
  const left = useMemo(() => shuffle(items), [items]);
  const right = useMemo(() => shuffle(items), [items]);
  const [a, setA] = useState<string | null>(null);
  const [b, setB] = useState<string | null>(null);
  const [done, setDone] = useState<string[]>([]);
  const [wrong, setWrong] = useState(false);

  useEffect(() => {
    if (!a || !b) return;
    if (a === b) {
      const next = [...done, a];
      setDone(next);
      setA(null);
      setB(null);
      if (next.length === items.length) onDone();
      return;
    }
    setWrong(true);
    onMiss();
    const t = setTimeout(() => {
      setWrong(false);
      setA(null);
      setB(null);
    }, 450);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [a, b]);

  const cell = (key: string, on: boolean) =>
    `min-h-[56px] rounded-2xl px-3 py-2 text-base font-bold ring-2 transition ${
      done.includes(key) ? 'bg-ok-soft text-ok ring-ok opacity-60' : on ? (wrong ? 'bg-bad-soft ring-bad animate-shake' : 'bg-brand-soft ring-brand') : 'bg-white ring-line'
    }`;

  return (
    <div className="animate-pop">
      <h2 className="h2 text-center">连一连：词和意思配对</h2>
      <div className="mx-auto mt-5 grid max-w-md grid-cols-2 gap-3">
        <div className="grid gap-3">
          {left.map((it) => (
            <button key={it.w} type="button" disabled={done.includes(it.w)} onClick={() => setA(it.w)} className={cell(it.w, a === it.w) + ' text-xl'}>
              {it.w}
            </button>
          ))}
        </div>
        <div className="grid gap-3">
          {right.map((it) => (
            <button key={it.w} type="button" disabled={done.includes(it.w)} onClick={() => setB(it.w)} className={cell(it.w, b === it.w)}>
              {it.g}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function Stars({ n }: { n: number }) {
  return (
    <div className="flex justify-center gap-2 text-5xl">
      {[1, 2, 3].map((i) => (
        <span key={i} className={i <= n ? 'text-[#EAB13B]' : 'text-line'}>
          ★
        </span>
      ))}
    </div>
  );
}

export function LessonPlayer({ lesson, unitItems, nextId }: { lesson: Lesson; unitItems: CourseItem[]; nextId: string | null }) {
  const [steps, setSteps] = useState<Step[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [picked, setPicked] = useState<string | null>(null);
  const [typed, setTyped] = useState('');
  const [verdict, setVerdict] = useState<Verdict>(null);
  const [matched, setMatched] = useState(false);
  const [mistakes, setMistakes] = useState(0);
  const [stars, setStars] = useState(0);
  const [retried, setRetried] = useState<number[]>([]);

  useEffect(() => {
    setSteps(buildSteps(lesson.items, unitItems, allItems));
  }, [lesson, unitItems]);

  if (!steps) return <div className="py-24 text-center text-muted">正在准备这一课…</div>;

  const step = steps[idx];
  const finished = idx >= steps.length;

  if (finished) {
    return (
      <div className="mx-auto max-w-md animate-pop py-6 text-center">
        <Stars n={stars} />
        <h1 className="h1 mt-4">学完啦！</h1>
        <p className="mt-2 text-muted">
          这一课学了 {lesson.items.length} 个词，得到 {10 + stars * 5} 分。它们已经放进复习卡片，明天记得来复习。
        </p>
        <div className="card mt-6 divide-y divide-line text-left">
          {lesson.items.map((it) => (
            <div key={it.w + it.p} className="flex items-center justify-between gap-3 px-4 py-3">
              <span className="text-lg font-bold">{it.w}</span>
              <Pinyin p={it.p} className="text-sm" />
              <span className="ml-auto text-sm text-muted">{it.g}</span>
            </div>
          ))}
        </div>
        <div className="mt-6 grid gap-3">
          {nextId && (
            <Link href={`/learn/${nextId}`} className="btn-primary">
              下一课
            </Link>
          )}
          <Link href="/learn" className="btn-ghost">
            回到课程表
          </Link>
        </div>
      </div>
    );
  }

  function miss() {
    setMistakes((m) => m + 1);
  }

  function check() {
    if (step.kind === 'choice' && picked) {
      const ok = picked === step.answer;
      if (!ok) miss();
      setVerdict({ ok });
    } else if (step.kind === 'type') {
      const res = checkTyped(typed, step.item.p);
      if (res === 'wrong') miss();
      setVerdict({ ok: res !== 'wrong', note: res === 'toneless' ? '拼对了！再留意一下声调数字。' : undefined });
    }
  }

  function advance() {
    let queue = steps!;
    if (verdict && !verdict.ok && step.kind === 'choice' && !retried.includes(idx)) {
      setRetried([...retried, queue.length]);
      queue = [...queue, { ...step, options: shuffle(step.options) }];
      setSteps(queue);
    }
    const next = idx + 1;
    if (next >= queue.length) {
      const earned = mistakes === 0 ? 3 : mistakes <= 3 ? 2 : 1;
      setStars(earned);
      addXp(10 + earned * 5);
      finishLesson(lesson.id, earned);
      addCards(lesson.items);
    }
    setIdx(next);
    setPicked(null);
    setTyped('');
    setVerdict(null);
    setMatched(false);
  }

  const canCheck = (step.kind === 'choice' && !!picked) || (step.kind === 'type' && typed.trim().length > 0);
  const showContinue = step.kind === 'learn' || !!verdict || (step.kind === 'match' && matched);

  return (
    <div className="pb-36">
      <div className="flex items-center gap-3">
        <Link href="/learn" aria-label="退出" className="grid h-10 w-10 place-items-center rounded-full text-2xl text-muted hover:bg-white">
          ×
        </Link>
        <div className="h-3 flex-1 overflow-hidden rounded-full bg-line">
          <div className="h-full rounded-full bg-brand transition-all" style={{ width: `${(idx / steps.length) * 100}%` }} />
        </div>
      </div>

      <div className="mx-auto mt-6 max-w-xl">
        {step.kind === 'learn' && (
          <>
            <p className="mb-3 text-center text-sm font-bold text-muted">新词 · 先看一看、听一听声调</p>
            <WordCard key={step.item.w + idx} item={step.item} />
          </>
        )}
        {step.kind === 'choice' && <Choice key={idx} step={step} picked={picked} verdict={verdict} onPick={setPicked} />}
        {step.kind === 'match' && <Match key={idx} items={step.items} onMiss={miss} onDone={() => setMatched(true)} />}
        {step.kind === 'type' && (
          <div className="animate-pop">
            <h2 className="h2 text-center">用拼音把它写出来</h2>
            <div className="card mx-auto mt-4 max-w-md p-6 text-center">
              <div className="text-5xl font-black">{step.item.w}</div>
              <div className="mt-2 text-muted">{step.item.g}</div>
            </div>
            <input
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && canCheck && !verdict && check()}
              disabled={!!verdict}
              placeholder="例如 gen1 do（声调数字可以先不写）"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck={false}
              className="mx-auto mt-5 block h-14 w-full max-w-md rounded-2xl bg-white px-4 text-center font-mono text-xl ring-2 ring-line focus:outline-none focus:ring-brand"
            />
            {!verdict && (
              <button type="button" onClick={() => { miss(); setVerdict({ ok: false }); }} className="mx-auto mt-3 block text-sm font-bold text-muted underline underline-offset-4">
                不会，看答案
              </button>
            )}
          </div>
        )}
      </div>

      <div className={`fixed inset-x-0 bottom-0 z-40 border-t pb-[env(safe-area-inset-bottom)] ${verdict ? (verdict.ok ? 'border-ok bg-ok-soft' : 'border-bad bg-bad-soft') : 'border-line bg-white'}`}>
        <div className="mx-auto flex max-w-xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center">
          <div className="min-h-[24px] flex-1 text-[15px]">
            {verdict?.ok && <b className="text-ok">答对了！{verdict.note}</b>}
            {verdict && !verdict.ok && step.kind !== 'learn' && step.kind !== 'match' && (
              <span className="text-bad">
                <b>正确答案：</b>
                <span className="font-bold text-ink">{step.item.w}</span> <Pinyin p={step.item.p} /> <span className="text-ink">— {step.item.g}</span>
              </span>
            )}
          </div>
          {showContinue ? (
            <button type="button" onClick={advance} className="btn-primary sm:w-40">
              继续
            </button>
          ) : (
            step.kind !== 'match' && (
              <button type="button" onClick={check} disabled={!canCheck} className="btn-primary sm:w-40">
                检查
              </button>
            )
          )}
        </div>
      </div>
    </div>
  );
}
