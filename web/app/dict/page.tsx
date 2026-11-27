import Link from 'next/link';
import { Pinyin } from '@/components/Pinyin';
import { SearchBox } from '@/components/SearchBox';
import { hit, search, store } from '@/lib/data';
import type { SearchHit } from '@/lib/types';

export const metadata = { title: '词典' };
export const dynamic = 'force-dynamic';

function Row({ h }: { h: SearchHit }) {
  return (
    <Link href={`/dict/${h.id}`} className="block rounded-2xl bg-white px-4 py-3 ring-1 ring-line transition hover:ring-ink/30">
      <div className="flex flex-wrap items-baseline gap-x-3">
        <span className="text-xl font-black">{h.w}</span>
        <Pinyin p={h.p} className="text-sm" />
      </div>
      <p className="mt-1 text-sm leading-relaxed text-muted">{h.d}</p>
    </Link>
  );
}

export default async function DictPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const q = ((await searchParams).q || '').slice(0, 40);
  const results = q ? search(q) : [];
  const { entries } = store();
  const pool = entries.filter((e) => e.c);
  const day = Math.floor(Date.now() / 86400000);
  const picks = q ? [] : Array.from({ length: 9 }, (_, i) => hit(pool[(day * 7 + i * 13) % pool.length]));

  return (
    <div>
      <h1 className="h1">泰如词典</h1>
      <p className="mb-4 mt-2 text-muted">收词 {entries.length.toLocaleString()} 条，可以按汉字、拼音（带不带声调都行）或普通话意思来查。</p>
      <SearchBox initial={q} />
      {!q && (
        <>
          <h2 className="h2 mt-8">随便看看</h2>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {picks.map((h) => (
              <Row key={h.id} h={h} />
            ))}
          </div>
        </>
      )}
      {q && (
        <>
          <p className="mt-4 text-sm text-muted">{results.length ? `找到 ${results.length}${results.length >= 60 ? '+' : ''} 条` : '没有找到。换个写法，或者试试用普通话的意思来查。'}</p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {results.map((h) => (
              <Row key={h.id} h={h} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
