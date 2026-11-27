'use client';

import Link from 'next/link';
import { lessons } from '@/lib/course';
import { DAILY_GOAL, dueCards, streak, today, useProgress } from '@/lib/progress';

export function HomeDash() {
  const p = useProgress();
  const next = lessons.find((l) => !p.lessons[l.id]) || lessons[0];
  const done = Object.keys(p.lessons).length;
  const todayXp = p.days[today()] || 0;
  const pct = Math.min(100, Math.round((todayXp / DAILY_GOAL) * 100));
  const due = dueCards(p).length;
  const started = done > 0;

  return (
    <section className="grid gap-4 md:grid-cols-5">
      <div className="card flex flex-col justify-between gap-5 bg-ink p-6 text-white md:col-span-3 md:p-8">
        <div>
          <p className="text-sm font-bold text-white/60">{started ? `已学完 ${done} / ${lessons.length} 课` : '零基础也能学'}</p>
          <h1 className="mt-2 text-3xl font-black leading-tight md:text-4xl">{started ? '接着学下去' : '今天开始，学说泰如话'}</h1>
          <p className="mt-3 text-white/70">
            {started ? `下一课：${next.unit.title} · ${next.title}` : '每课 5 分钟：先认词、看声调，再做几道小练习。'}
          </p>
        </div>
        <Link href={`/learn/${next.id}`} className="btn-primary w-full md:w-56">
          {started ? '继续学习' : '开始第一课'}
        </Link>
      </div>
      <div className="grid grid-cols-3 gap-3 md:col-span-2 md:grid-cols-1">
        <div className="card p-4">
          <div className="text-xs font-bold text-muted">今日目标</div>
          <div className="mt-1 text-2xl font-black">
            {todayXp}
            <span className="text-sm font-bold text-muted"> / {DAILY_GOAL} 分</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-line">
            <div className="h-full rounded-full bg-brand" style={{ width: `${pct}%` }} />
          </div>
        </div>
        <div className="card p-4">
          <div className="text-xs font-bold text-muted">连续学习</div>
          <div className="mt-1 text-2xl font-black">
            {streak(p)}
            <span className="text-sm font-bold text-muted"> 天</span>
          </div>
        </div>
        <Link href="/review" className="card p-4">
          <div className="text-xs font-bold text-muted">待复习</div>
          <div className="mt-1 text-2xl font-black">
            {due}
            <span className="text-sm font-bold text-muted"> 张卡片</span>
          </div>
        </Link>
      </div>
    </section>
  );
}
