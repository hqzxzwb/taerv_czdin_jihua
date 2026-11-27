import Link from 'next/link';
import { ResetButton } from '@/components/ResetButton';
import { store } from '@/lib/data';

export const metadata = { title: '关于' };
export const dynamic = 'force-dynamic';

export default function AboutPage() {
  const { entries } = store();
  const counts = new Map<string, number>();
  for (const e of entries) for (const s of e.src) counts.set(s, (counts.get(s) || 0) + 1);
  const sources = [...counts.entries()].filter(([, n]) => n >= 100).sort((a, b) => b[1] - a[1]);
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="h1">关于泰如话学堂</h1>

      <section className="card space-y-3 p-6 leading-relaxed">
        <h2 className="h2">泰如话是什么</h2>
        <p>泰如话是江淮官话的一支，主要在江苏的泰州、兴化、姜堰、泰兴、东台、大丰、海安、如皋、如东一带使用。这些地方 2020 年的常住人口合计约 815 万，算上南通市区和在外地的同乡，说泰如话的人在一千万上下。它保留了入声，“今天”说“今朝”，“小孩”说“伢儿”，“没有”说“没得”。</p>
        <p>
          以其中的东台话为例：它通行于盐城东台市全境，以及相邻的大丰区南部、海安市东南角、兴化市东北角，单这一种就有一百多万人说（百度百科的数字是约 120 万）。东台话保留了阴入、阳入两个入声调；境内沿范公堤又分台城、堤东、堤西、街唐四片，各片声母韵母略有差别，但互相通话没有障碍。
          <a href="https://baike.baidu.com/item/%E4%B8%9C%E5%8F%B0%E8%AF%9D/8965743" target="_blank" rel="noreferrer" className="ml-1 text-sm text-muted underline underline-offset-4">
            （据百度百科“东台话”）
          </a>
        </p>
        <p>
          它虽然归在江淮官话里，却和南京、扬州的话差别很大：古浊音一律读送气音、有六到七个声调、入声分阴阳，词汇里还留着不少吴语的底子。
          <Link href="/origin" className="ml-1 font-bold text-brand-deep underline underline-offset-4">
            详细的来历看这里
          </Link>
        </p>
        <p>这个网站想帮从零开始的孩子和大人，用每天几分钟的时间，把家乡话一点点捡回来。</p>
      </section>

      <section className="card space-y-3 p-6 leading-relaxed">
        <h2 className="h2">内容从哪里来</h2>
        <p>
          全部词条、拼音、例句和语法笔记都来自开源项目
          <a href="https://github.com/hqzxzwb/taerv_czdin_jihua" target="_blank" rel="noreferrer" className="mx-1 font-bold text-brand-deep underline underline-offset-4">
            泰如辞典计划（taerv_czdin_jihua）
          </a>
          ，由 hqzxzwb、HISAHARA、osfans 等贡献者多年整理。课程里的每一个词都能在词典里查到原始词条；我们只做了挑选、分级和练习。
        </p>
        <p>词典目前收词 {entries.length.toLocaleString()} 条，主要参考：</p>
        <div className="flex flex-wrap gap-2">
          {sources.map(([s, n]) => (
            <span key={s} className="chip">
              {s} · {n.toLocaleString()}
            </span>
          ))}
        </div>
        <p>发现词条有错，欢迎到上面的项目里提 Issue 或直接修改。</p>
      </section>

      <section className="card space-y-3 p-6 leading-relaxed">
        <h2 className="h2">几件要说清楚的事</h2>
        <ul className="list-disc space-y-2 pl-5">
          <li><b>没有真人录音。</b>“听声调”播放的是电脑哼出来的高低走向，帮你抓住调子，不能代替真人发音。最好的老师是家里说泰如话的长辈。</li>
          <li><b>各地读法不完全一样。</b>拼音记录的是各地通用的“标准音系”，声调调值以泰兴、如皋一带为参考。词条页列出了泰兴、兴化、如皋、泰县的换算读音。</li>
          <li><b>学习记录只存在这台设备的浏览器里</b>，不用注册，也不会上传。换手机或清浏览器数据后会重新开始。</li>
        </ul>
        <ResetButton />
      </section>
    </div>
  );
}
