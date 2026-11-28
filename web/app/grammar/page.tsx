import fs from 'fs';
import path from 'path';
import { Syl } from '@/components/Pinyin';

export const metadata = { title: '语法小课' };
export const dynamic = 'force-dynamic';

interface Line {
  h?: number;
  li?: number;
  t: string;
}

function Rich({ text }: { text: string }) {
  const parts = text.split(/((?:[a-z]+\d?(?:-\d)?)(?: [a-z]+\d?(?:-\d)?)*)/g);
  return (
    <>
      {parts.map((part, i) =>
        i % 2 ? (
          <span key={i}>
            {part.split(' ').map((s, k) => (
              <span key={k}>
                {k > 0 && ' '}
                <Syl p={s} />
              </span>
            ))}
          </span>
        ) : (
          part
        ),
      )}
    </>
  );
}

function Body({ lines }: { lines: Line[] }) {
  const out: React.ReactNode[] = [];
  let chips: string[] = [];
  const flush = (key: number) => {
    if (!chips.length) return;
    out.push(
      <div key={`c${key}`} className="mt-2 flex flex-wrap gap-2">
        {chips.map((c, i) => (
          <span key={i} className="rounded-xl bg-paper px-3 py-1.5 text-[15px] ring-1 ring-line">
            {c}
          </span>
        ))}
      </div>,
    );
    chips = [];
  };
  lines.forEach((l, i) => {
    if (l.h === undefined && l.li === undefined && l.t.length <= 14 && !/[。：]$/.test(l.t)) {
      chips.push(l.t);
      return;
    }
    flush(i);
    if (l.h === 1) out.push(<h3 key={i} className="mt-8 border-t border-line pt-6 text-lg font-black first:mt-0 first:border-0 first:pt-0">{l.t}</h3>);
    else if (l.h) out.push(<h4 key={i} className="mt-4 font-mono text-sm font-bold text-brand-deep">{l.t}</h4>);
    else if (l.li !== undefined)
      out.push(
        <p key={i} className={`mt-1.5 leading-relaxed ${l.li ? 'ml-5 rounded-xl bg-paper px-3 py-1.5 text-[15px]' : 'font-bold'}`}>
          <Rich text={l.t} />
        </p>,
      );
    else if (l.t !== '例：') out.push(<p key={i} className="mt-2 leading-relaxed text-ink/90"><Rich text={l.t} /></p>);
  });
  flush(lines.length);
  return <>{out}</>;
}

export default function GrammarPage() {
  const notes = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'data', 'notes.json'), 'utf8')) as { title: string; file: string; lines: Line[] }[];
  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <header>
        <h1 className="h1">语法小课</h1>
        <p className="mt-2 text-muted">泰如话和普通话最不一样的几种说法。例句里的“～”代表正在讲的那个词。</p>
      </header>
      {notes.map((n) => (
        <section key={n.title} className="card p-5 sm:p-7">
          <h2 className="h2 mb-4">{n.title}</h2>
          {n.title.includes('变调') && (
            <p className="mb-4 rounded-2xl bg-paper px-4 py-3 text-sm leading-relaxed text-muted">
              两个字连着说的时候，声调常常会变。下面是泰兴话的整理：小标题里的数字是两个字各自的调值（5 最高、1 最低），带“？”的还不确定。初学先知道有这回事，多听长辈怎么说。
            </p>
          )}
          <Body lines={n.lines} />
        </section>
      ))}
    </div>
  );
}
