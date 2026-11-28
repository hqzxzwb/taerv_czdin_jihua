'use client';

import Link from 'next/link';
import { course, lessons } from '@/lib/course';
import { useProgress } from '@/lib/progress';

export function CourseMap() {
  const p = useProgress();
  const nextId = (lessons.find((l) => !p.lessons[l.id]) || lessons[0]).id;
  return (
    <div className="space-y-6">
      {course.map((u, ui) => {
        const done = u.lessons.filter((l) => p.lessons[l.id]).length;
        return (
          <section key={u.id} id={u.id} className="card scroll-mt-20 p-5 sm:p-6">
            <div className="flex items-center gap-4">
              <span className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-paper text-3xl">{u.icon}</span>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold text-muted">第 {ui + 1} 单元</div>
                <h2 className="h2">{u.title}</h2>
                <p className="text-sm text-muted">{u.desc}</p>
              </div>
              <span className="chip shrink-0">
                {done}/{u.lessons.length}
              </span>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {u.lessons.map((l) => {
                const stars = p.lessons[l.id] || 0;
                const isNext = l.id === nextId;
                return (
                  <Link
                    key={l.id}
                    href={`/learn/${l.id}`}
                    className={`flex min-h-[72px] items-center gap-3 rounded-2xl px-4 py-3 ring-2 transition ${
                      isNext ? 'bg-brand-soft ring-brand' : stars ? 'bg-ok-soft/50 ring-ok/30' : 'bg-white ring-line hover:ring-ink/20'
                    }`}
                  >
                    <div className="min-w-0 flex-1">
                      <div className="font-black">{l.title}</div>
                      <div className="truncate text-sm text-muted">{l.items.map((i) => i.w).join(' ')}</div>
                    </div>
                    {stars ? (
                      <span className="shrink-0 text-[#EAB13B]">{'★'.repeat(stars)}<span className="text-line">{'★'.repeat(3 - stars)}</span></span>
                    ) : (
                      isNext && <span className="shrink-0 rounded-full bg-brand px-3 py-1 text-xs font-bold text-white">开始</span>
                    )}
                  </Link>
                );
              })}
            </div>
          </section>
        );
      })}
    </div>
  );
}
