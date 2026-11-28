'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';

const SAMPLES = ['今朝', '伢儿', '没得', '耍子', '明天', '漂亮', 'ga qi', 'ngu3'];

export function SearchBox({ initial }: { initial: string }) {
  const router = useRouter();
  const [q, setQ] = useState(initial);
  const first = useRef(true);

  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    const t = setTimeout(() => router.replace(q.trim() ? `/dict?q=${encodeURIComponent(q.trim())}` : '/dict', { scroll: false }), 250);
    return () => clearTimeout(t);
  }, [q, router]);

  return (
    <>
    <div className="relative">
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="输入汉字、拼音或普通话意思，例如：今朝 / gen do / 明天"
        autoCapitalize="none"
        autoCorrect="off"
        className="h-14 w-full rounded-2xl bg-white pl-5 pr-12 text-lg ring-2 ring-line focus:outline-none focus:ring-brand"
      />
      {q && (
        <button type="button" aria-label="清空" onClick={() => setQ('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-2xl text-muted">
          ×
        </button>
      )}
    </div>
      {!q && (
        <div className="mt-4 flex flex-wrap gap-2">
          {SAMPLES.map((s) => (
            <button key={s} type="button" onClick={() => setQ(s)} className="chip hover:text-ink">
              {s}
            </button>
          ))}
        </div>
      )}
    </>
  );
}
