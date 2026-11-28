import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import { Syl } from '@/components/Pinyin';
import { HumButton, ToneContour } from '@/components/Tone';
import { store } from '@/lib/data';
import { TONES, TONE_ORDER } from '@/lib/tones';

export const metadata = { title: '拼音和声调' };
export const dynamic = 'force-dynamic';

interface Sound {
  k: string;
  ipa: string;
  ex: { c: string; p: string }[];
}

const INITIAL_NOTES: Record<string, string> = {
  v: '上牙轻碰下唇，像英语 very 开头的音。普通话里没有。',
  ng: '把“昂 ang”结尾的鼻音搬到字的开头：我 ngu3、爱 ngae5。',
  zh: '翘舌。如皋、泰兴、泰县等不少地方读成平舌的 z。',
  ch: '翘舌。不少地方读成平舌的 c。',
  sh: '翘舌。不少地方读成平舌的 s。',
};

const FINAL_NOTES: Record<string, string> = {
  ae: '嘴比“诶”张得大一点：街 gae1。',
  o: '嘴张圆、不滑动：老 lo3。',
  u: '比普通话的 u 松一点：我 ngu3。',
  v: '嘴唇保持 v 的样子拖长当韵母：主 zhv3。',
  eu: '从“呃”滑向不圆唇的“乌”：头 teu2。',
  z: '就是普通话 zi、ci、si 里的那个 i：子 zz3。',
  r: '就是普通话 zhi、chi、shi 里的那个 i：是 shr6。',
  y: '就是普通话的 ü。',
};

function SoundCard({ s, note }: { s: Sound; note?: string }) {
  return (
    <div className="rounded-2xl bg-white p-3 ring-1 ring-line">
      <div className="flex items-baseline justify-between gap-2">
        <span className="font-mono text-xl font-black">{s.k}</span>
        <span className="font-mono text-sm text-muted">[{s.ipa}]</span>
      </div>
      <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1">
        {s.ex.map((e) => (
          <span key={e.c + e.p} className="inline-flex items-baseline gap-1">
            <span className="text-lg font-bold">{e.c}</span>
            <Syl p={e.p} className="text-xs" />
          </span>
        ))}
      </div>
      {note && <p className="mt-2 text-xs leading-relaxed text-muted">{note}</p>}
    </div>
  );
}

export default function PinyinPage() {
  const sounds = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'data', 'sounds.json'), 'utf8')) as { initials: Sound[]; finals: Sound[] };
  const order = ['b', 'p', 'm', 'f', 'v', 'd', 't', 'n', 'l', 'z', 'c', 's', 'zh', 'ch', 'sh', 'r', 'j', 'q', 'x', 'g', 'k', 'h', 'ng'];
  const initials = [...sounds.initials].sort((a, b) => order.indexOf(a.k) - order.indexOf(b.k));
  const groups = [
    { title: '普通韵母', hint: '嘴巴张开直接读。', list: sounds.finals.filter((f) => !/[nh]$/.test(f.k)) },
    { title: '鼻化韵母', hint: 'aen、in、un 这一类：气从鼻子和嘴巴一起出来，舌头不用顶上去。', list: sounds.finals.filter((f) => /n$/.test(f.k) && f.ipa.includes('̃')) },
    { title: '后鼻音韵母', hint: 'an、en、on 这一类：结尾是 -ng，和普通话的 ang、eng、ong 差不多。', list: sounds.finals.filter((f) => /n$/.test(f.k) && !f.ipa.includes('̃')) },
    { title: '入声韵母', hint: '结尾写 h：读得很短，喉咙一下子关住。普通话里没有，是泰如话最有特色的音。', list: sounds.finals.filter((f) => /h$/.test(f.k)) },
  ];
  const chars = [...store().chars.values()].flat();
  const toneExamples = (t: string) => {
    const out: { c: string; p: string }[] = [];
    for (const c of chars) {
      if (out.length >= 5) break;
      if (c.p.endsWith(t) && !c.n && c.c.length === 1 && !out.some((o) => o.c === c.c)) out.push({ c: c.c, p: c.p });
    }
    return out;
  };

  return (
    <div className="space-y-10">
      <header>
        <h1 className="h1">拼音和声调</h1>
        <p className="mt-2 max-w-2xl text-muted">
          泰如话用一套专门的拼音来记音：字母表示声母和韵母，后面的数字表示声调，比如“今朝” <Syl p="gen1" /> <Syl p="do" />。学会它，词典里四万多个词你都能读出来。
        </p>
      </header>

      <section>
        <h2 className="h2">一、七个声调</h2>
        <p className="mt-1 text-sm text-muted">
          数字 1、2、3、5、6、7、8 各代表一个声调（没有第 4 声）。点“听”可以听到声调高低的走向——那是电脑哼出来的调子，不是真人读音。
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {TONE_ORDER.map((t) => {
            const tone = TONES[t];
            const ex = toneExamples(t);
            return (
              <div key={t} className="card p-4">
                <div className="flex items-center gap-3">
                  <ToneContour tone={t} size={52} />
                  <div className="flex-1">
                    <div className="font-black" style={{ color: tone.color }}>
                      第 {t} 声 · {tone.name}
                    </div>
                    <div className="text-xs text-muted">参考调值 {tone.levels.join('')}</div>
                  </div>
                  <HumButton syl={[`a${t}`]} label="听" />
                </div>
                <p className="mt-3 text-sm leading-relaxed">{tone.tip}</p>
                <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1">
                  {ex.map((e) => (
                    <span key={e.c} className="inline-flex items-baseline gap-1">
                      <span className="text-lg font-bold">{e.c}</span>
                      <Syl p={e.p} className="text-xs" />
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <div className="card p-4 text-sm leading-relaxed">
            <b>没有数字 = 轻声。</b>轻轻带过就好，比如“桌子” <Syl p="zhuah7" /> <Syl p="zz" /> 的“子”。
          </div>
          <div className="card p-4 text-sm leading-relaxed">
            <b>数字 9 是“小称调”。</b>“一个”常常省掉“一”只说“个” <Syl p="gu9" />，这时“个”要变调。各地变法不同，详见
            <Link href="/grammar" className="font-bold text-brand-deep"> 语法小课</Link>。
          </div>
        </div>
        <p className="mt-3 text-xs text-muted">调值以泰兴、如皋一带的常见读法为参考，各县市之间略有出入，以当地长辈的读法为准。</p>
      </section>

      <section>
        <h2 className="h2">二、{initials.length} 个声母</h2>
        <p className="mt-1 text-sm text-muted">大部分和普通话拼音读法一样。要特别留意的有说明。方括号里是国际音标。</p>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {initials.map((s) => (
            <SoundCard key={s.k} s={s} note={INITIAL_NOTES[s.k]} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="h2">三、韵母</h2>
        {groups.map((g) => (
          <div key={g.title} className="mt-5">
            <h3 className="font-black">
              {g.title} <span className="ml-1 text-sm font-normal text-muted">{g.list.length} 个</span>
            </h3>
            <p className="mt-1 text-sm text-muted">{g.hint}</p>
            <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {g.list.map((s) => (
                <SoundCard key={s.k} s={s} note={FINAL_NOTES[s.k]} />
              ))}
            </div>
          </div>
        ))}
      </section>

      <div className="text-center">
        <Link href="/learn" className="btn-primary">
          学会了，去上课
        </Link>
      </div>
    </div>
  );
}
