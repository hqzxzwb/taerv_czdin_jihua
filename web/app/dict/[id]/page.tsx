import Link from 'next/link';
import { notFound } from 'next/navigation';
import { AddCard } from '@/components/AddCard';
import { Pinyin, Ruby } from '@/components/Pinyin';
import { HumButton, ToneStrip } from '@/components/Tone';
import { Example } from '@/components/WordCard';
import { firstDef, hit, store } from '@/lib/data';

export const dynamic = 'force-dynamic';

const REPO = 'https://github.com/hqzxzwb/taerv_czdin_jihua/blob/master/';

function get(id: string) {
  const n = Number(id);
  return Number.isInteger(n) ? store().entries[n] : undefined;
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const e = get((await params).id);
  return e ? { title: `${e.w} ${e.p}`, description: firstDef(e, 120) } : { title: '词典' };
}

export default async function EntryPage({ params }: { params: Promise<{ id: string }> }) {
  const e = get((await params).id);
  if (!e) notFound();
  const { byWord, entries } = store();
  const first = e.p.split(',')[0].trim();
  const voiced = e.s.filter(([, p]) => p);
  const firstSyl = first.split(/\s+/);
  const aligned = voiced.length === firstSyl.length;
  const syl = aligned ? firstSyl : [];
  const twins = (byWord.get(e.w) || []).filter((x) => x.id !== e.id).map(hit);
  const related: ReturnType<typeof hit>[] = [];
  if (Array.from(e.w).length <= 2) {
    for (const x of entries) {
      if (related.length >= 12) break;
      if (x.w !== e.w && x.w.includes(e.w) && x.w.length <= 5) related.push(hit(x));
    }
  }
  const regions = Object.entries(e.ipa);

  return (
    <article className="mx-auto max-w-3xl space-y-6">
      <Link href="/dict" className="text-sm font-bold text-muted">
        ← 返回词典
      </Link>

      <header className="card p-6 text-center sm:p-8">
        {aligned ? <Ruby syl={e.s.map(([c, p]) => [c, p])} size="text-5xl sm:text-6xl" /> : <div className="text-5xl font-black">{e.w}</div>}
        <div className="mt-3 text-lg">
          <Pinyin p={e.p} />
        </div>
        {syl.length > 0 && (
          <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
            <ToneStrip syl={syl} />
            <HumButton syl={syl} />
          </div>
        )}
        <div className="mt-5">
          <AddCard w={e.w} p={first} g={firstDef(e, 24)} />
        </div>
      </header>

      <section className="card p-6">
        <h2 className="h2">解释</h2>
        <ol className="mt-3 space-y-4">
          {e.m.map((m, i) => (
            <li key={i} className="flex gap-3">
              <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-full bg-ink text-xs font-bold text-white">{i + 1}</span>
              <div className="min-w-0">
                <p className="leading-relaxed">{m.d}</p>
                {m.ex.length > 0 && (
                  <ul className="mt-2 space-y-1.5">
                    {m.ex.map((ex, k) => {
                      const [text, note] = ex.split('/');
                      return (
                        <li key={k} className="rounded-xl bg-paper px-3 py-2 text-[15px] leading-relaxed">
                          {text.includes('～') && text.split('～').length === 2 ? <Example text={text} word={e.w} /> : text.replaceAll('～', e.w)}
                          {note && <span className="ml-1 text-muted">（{note}）</span>}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            </li>
          ))}
        </ol>
      </section>

      {regions.length > 0 && (
        <section className="card p-6">
          <h2 className="h2">各地读音（国际音标）</h2>
          <p className="mt-1 text-sm text-muted">按拼音自动换算，数字是声调类别。“通用”是拼音方案本身的读法。</p>
          <dl className="mt-3 grid gap-2 sm:grid-cols-2">
            {regions.map(([region, ipa]) => (
              <div key={region} className="flex items-baseline gap-3 rounded-xl bg-paper px-3 py-2">
                <dt className="w-10 shrink-0 text-sm font-bold text-muted">{region}</dt>
                <dd className="font-mono">/{ipa}/</dd>
              </div>
            ))}
          </dl>
        </section>
      )}

      {(e.src.length > 0 || e.c) && (
        <section className="flex flex-wrap items-center gap-2 text-sm">
          <span className="font-bold text-muted">出处</span>
          {e.c && <span className="chip">各地通用</span>}
          {e.src.map((s) => (
            <span key={s} className="chip">
              {s}
            </span>
          ))}
          <a href={REPO + e.f} target="_blank" rel="noreferrer" className="ml-auto font-bold text-muted underline underline-offset-4">
            查看 / 改进这个词条
          </a>
        </section>
      )}

      {[
        { title: '同一个写法的其他词条', list: twins },
        { title: `含有“${e.w}”的词`, list: related },
      ].map(
        (g) =>
          g.list.length > 0 && (
            <section key={g.title}>
              <h2 className="h2">{g.title}</h2>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                {g.list.map((h) => (
                  <Link key={h.id} href={`/dict/${h.id}`} className="rounded-2xl bg-white px-4 py-3 ring-1 ring-line hover:ring-ink/30">
                    <span className="font-black">{h.w}</span> <Pinyin p={h.p} className="text-sm" />
                    <span className="mt-0.5 block truncate text-sm text-muted">{h.d}</span>
                  </Link>
                ))}
              </div>
            </section>
          ),
      )}
    </article>
  );
}
