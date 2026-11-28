import Link from 'next/link';
import { HomeDash } from '@/components/HomeDash';
import { Pinyin } from '@/components/Pinyin';
import { Example } from '@/components/WordCard';
import { course } from '@/lib/course';
import { dailyEntry, store } from '@/lib/data';

export const dynamic = 'force-dynamic';

const TOOLS = [
  { href: '/pinyin', title: '拼音和声调', desc: '23 个声母、49 个韵母、7 个声调，一个个认', icon: '🔤' },
  { href: '/review', title: '复习卡片', desc: '学过的词按遗忘规律安排复习', icon: '🗂️' },
  { href: '/dict', title: '泰如词典', desc: '按汉字、拼音或意思查词', icon: '📖' },
  { href: '/zi', title: '注音器', desc: '输入一句话，看每个字泰如话怎么读', icon: '✍️' },
  { href: '/grammar', title: '语法小课', desc: '“哿”怎么问问题？“一个”为什么只说“个”？', icon: '🧩' },
];

export default function Home() {
  const daily = dailyEntry();
  const total = store().entries.length;
  const example = daily.m.flatMap((m) => m.ex).find((x) => x.includes('～') && x.length < 40);
  return (
    <div className="space-y-8">
      <HomeDash />

      <section>
        <div className="flex items-end justify-between">
          <h2 className="h2">课程</h2>
          <Link href="/learn" className="text-sm font-bold text-brand-deep">
            全部 {course.length} 个单元
          </Link>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {course.slice(0, 10).map((u) => (
            <Link key={u.id} href={`/learn#${u.id}`} className="card p-4 transition hover:-translate-y-0.5">
              <div className="text-3xl">{u.icon}</div>
              <div className="mt-2 font-black">{u.title}</div>
              <div className="mt-0.5 text-xs text-muted">{u.lessons.length} 课</div>
            </Link>
          ))}
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <Link href={`/dict/${encodeURIComponent(daily.id)}`} className="card block p-6">
          <div className="text-xs font-bold text-muted">每日一词</div>
          <div className="mt-2 flex flex-wrap items-baseline gap-3">
            <span className="text-4xl font-black">{daily.w}</span>
            <Pinyin p={daily.p} className="text-lg" />
          </div>
          <p className="mt-2 text-[15px] leading-relaxed">{daily.m[0]?.d}</p>
          {example && (
            <p className="mt-2 rounded-2xl bg-paper px-4 py-3 text-[15px]">
              <Example text={example.split('/')[0]} word={daily.w} />
            </p>
          )}
        </Link>
        <div className="grid gap-3">
          {TOOLS.map((t) => (
            <Link key={t.href} href={t.href} className="card flex items-center gap-4 p-4 transition hover:-translate-y-0.5">
              <span className="text-2xl">{t.icon}</span>
              <span>
                <span className="block font-black">{t.title}</span>
                <span className="block text-sm text-muted">{t.desc}</span>
              </span>
            </Link>
          ))}
        </div>
      </section>

      <p className="text-center text-sm text-muted">
        词典共收 {total.toLocaleString()} 条，全部来自开源项目
        <Link href="/about" className="mx-1 font-bold underline underline-offset-4">
          泰如辞典计划
        </Link>
        。
      </p>
    </div>
  );
}
