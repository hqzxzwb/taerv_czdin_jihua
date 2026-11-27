import Link from 'next/link';
import { Syl } from '@/components/Pinyin';
import { CORE, NANTONG_CITY, sum, wan } from '@/content/census';
import { ACCESSED, REFERENCES, REF_NO, VERIFIED_LABEL } from '@/content/references';
import { store } from '@/lib/data';

export const metadata = {
  title: '泰如话的来历：和江淮官话的区别、吴语底层、移民史',
  description: '泰如话（通泰方言）从哪里来？为什么扬州人听不太懂泰州话？古浊音一律送气、六七个声调、入声分阴阳，以及它和吴语、古越语的关系，附鲁国尧、汪如东、顾黔等人的研究出处。',
  alternates: { canonical: '/origin' },
};
export const dynamic = 'force-dynamic';

function C({ id }: { id: string }) {
  return (
    <>
      {id.split(',').map((one) => (
        <sup key={one}>
          <a href={`#ref-${REF_NO.get(one)}`} className="mx-px font-mono text-[0.7em] text-brand-deep">
            [{REF_NO.get(one)}]
          </a>
        </sup>
      ))}
    </>
  );
}

const DIFFS = [
  { k: '古浊音声母', tr: '不管什么声调，一律读成送气音', other: '平声送气，仄声不送气（和普通话一样）', chars: '地白字病豆坐' },
  { k: '声调数目', tr: '六到七个：去声、入声各分阴阳两类', other: '一般五个：阴平、阳平、上声、去声、入声', chars: '' },
  { k: '入声', tr: '分阴入、阳入两个调', other: '多数只有一个入声', chars: '七八百白' },
  { k: '“我、牙、眼”的声母', tr: '保留鼻音 ng-', other: '多已脱落', chars: '我牙眼饿' },
  { k: '“万、问、晚”的声母', tr: '读唇齿音 v-', other: '多读 w-（零声母）', chars: '万问晚望' },
];

function Chars({ list }: { list: string }) {
  const { chars } = store();
  return (
    <span className="flex flex-wrap gap-x-3 gap-y-1">
      {Array.from(list).map((c) => {
        const r = chars.get(c)?.[0];
        return r ? (
          <span key={c} className="inline-flex items-baseline gap-1">
            <b>{c}</b>
            <Syl p={r.p} className="text-xs" />
          </span>
        ) : null;
      })}
    </span>
  );
}

function Words({ list }: { list: string[] }) {
  const { byWord } = store();
  return (
    <div className="flex flex-wrap gap-2">
      {list.map((w) => {
        const e = byWord.get(w)?.[0];
        if (!e) return null;
        const d = (e.m[0]?.d || '').replace(/[。；，].*$/, '').slice(0, 8);
        return (
          <Link key={w} href={`/dict/${encodeURIComponent(e.id)}`} className="rounded-xl bg-paper px-3 py-1.5 text-[15px] ring-1 ring-line hover:ring-ink/30">
            <b>{w}</b> <span className="text-sm text-muted">{d}</span>
          </Link>
        );
      })}
    </div>
  );
}

export default function OriginPage() {
  return (
    <article className="mx-auto max-w-3xl space-y-6 leading-relaxed">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: '泰如话的来历',
            inLanguage: 'zh-CN',
            about: ['泰如话', '通泰方言', '江淮官话', '吴语'],
            mainEntityOfPage: 'https://tairu.ruilisi.com/origin',
            publisher: { '@type': 'Organization', name: '泰如话学堂', url: 'https://tairu.ruilisi.com' },
            citation: REFERENCES.map((r) => ({ '@type': 'CreativeWork', name: r.cite, ...(r.url ? { url: r.url } : {}) })),
          }),
        }}
      />
      <header>
        <h1 className="h1">泰如话的来历</h1>
        <p className="mt-2 text-muted">它从哪里来？为什么扬州人听不太懂泰州话？和吴语、古越语又是什么关系？这一页把学者们的研究讲给你听，每个说法后面都注明是谁说的。</p>
      </header>

      <section className="card space-y-3 p-6">
        <h2 className="h2">一、先说结论</h2>
        <ul className="list-disc space-y-2 pl-5">
          <li>在方言分类上，泰如话（学界也叫“通泰方言”）算<b>江淮官话</b>的一支，叫“泰如片”，和南京、扬州、合肥所在的“洪巢片”，以及湖北一带的“黄孝片”并列。<C id="atlas,wiki-jianghuai" /></li>
          <li>但它是江淮官话里<b>最特别</b>的一片：声母、声调、词汇上有一批特点，洪巢片没有，反而和江南的吴语、江西的赣语、客家话相通。<C id="wiki-tongtai,lu-tongyu" /></li>
          <li>主流的解释是：这片土地上古时候说的是吴语，后来北方移民带来的话盖在上面，吴语沉到了“底层”。所以泰如话是<b>北方话的骨架、吴语的底子</b>。<C id="lu-history,wang" /></li>
          <li>说泰如话的人在<b>一千万上下</b>：光是泰州、兴化、姜堰、泰兴、如皋、海安、如东、东台、大丰这十个核心县市区，2020 年常住人口就有 815 万；算上南通市区和在外地的同乡，各家估计在 1100 万到 1300 万之间。详见下面第二节。</li>
        </ul>
      </section>

      <section className="card space-y-4 p-6">
        <h2 className="h2">二、有多少人说泰如话</h2>
        <p>
          <b>方法：</b>没有哪次普查直接数过“说泰如话的人”，所以用“通行地区的常住人口”来推算上限。数据取 2020 年第七次全国人口普查（标准时点 2020 年 11 月 1 日零时）各县市区公报。
        </p>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[420px] text-left text-[15px]">
            <caption className="mb-2 text-left text-sm font-bold text-muted">表 1　泰如话核心通行区的常住人口（2020 年）</caption>
            <thead>
              <tr className="border-b border-line text-sm text-muted">
                <th className="py-1.5 pr-3 font-bold">地级市</th>
                <th className="py-1.5 pr-3 font-bold">县市区</th>
                <th className="py-1.5 pr-3 text-right font-bold">常住人口</th>
                <th className="py-1.5 font-bold">出处</th>
              </tr>
            </thead>
            <tbody>
              {CORE.map((r) => (
                <tr key={r.name} className="border-b border-line/60">
                  <td className="py-1.5 pr-3 text-muted">{r.city}</td>
                  <td className="py-1.5 pr-3 font-bold">{r.name}</td>
                  <td className="py-1.5 pr-3 text-right font-mono">{r.n.toLocaleString()}</td>
                  <td className="py-1.5">
                    <C id={r.ref} />
                  </td>
                </tr>
              ))}
              <tr className="font-black">
                <td className="py-2 pr-3" colSpan={2}>
                  合计（A）
                </td>
                <td className="py-2 pr-3 text-right font-mono">{sum(CORE).toLocaleString()}</td>
                <td />
              </tr>
            </tbody>
          </table>
        </div>
        <ul className="list-disc space-y-2 pl-5">
          <li>
            <b>A = {wan(sum(CORE))} 万。</b>这十个县市区是泰如话的核心通行区。
          </li>
          <li>
            <b>B = 南通市区 {wan(sum(NANTONG_CITY))} 万</b>（崇川 {wan(NANTONG_CITY[0].n)} 万、通州 {wan(NANTONG_CITY[1].n)} 万）。
            <C id="census-nt" />
            南通话一般也划在泰如片的东区。
            <C id="wiki-tongtai" />
          </li>
          <li>
            <b>A + B = {wan(sum(CORE) + sum(NANTONG_CITY), 0)} 万。</b>
          </li>
          <li>
            没算进去的：扬中、江都东部等地（没查到数字）；以及在外地的同乡。东台 2021 年户籍人口 105.46 万，常住只有 88.84 万。
            <C id="huji-dt" />
          </li>
          <li>
            别处给的总数：维基百科 1137 万（2004 年）
            <C id="wiki-tongtai" />
            ，百度百科 1200 万或 1300 万
            <C id="baike-tairu" />
            。
          </li>
        </ul>
        <p>
          <b>结论：</b>说泰如话的人在<b>一千万上下</b>。
        </p>
        <p className="text-sm text-muted">
          <b>局限：</b>这是“通行地区住了多少人”，不等于“多少人会说”。城里的孩子很多已经只说普通话；如东南部、东台东部有说吴语的乡镇，大丰北部靠近盐城话；这几项会让实际人数低于表里的数字，但没有可用的统计来量化。网上“约 120 万”的数字说的只是东台话一种
          <C id="baike-dongtai" />
          ，不是泰如话的总数。
        </p>
      </section>

      <section className="card space-y-4 p-6">
        <h2 className="h2">三、和江淮官话其他地方有什么不一样</h2>
        <p>下面“洪巢片”一栏说的是南京、扬州一带的一般情况。例字的读音直接取自本项目的单字音表<C id="repo" />，分片特点据<C id="wiki-tongtai,wiki-jianghuai" />。</p>
        <div className="space-y-3">
          {DIFFS.map((d) => (
            <div key={d.k} className="rounded-2xl bg-paper p-4">
              <div className="font-black">{d.k}</div>
              <div className="mt-2 grid gap-2 text-[15px] sm:grid-cols-2">
                <div>
                  <span className="mr-2 rounded-md bg-brand px-1.5 py-0.5 text-xs font-bold text-white">泰如片</span>
                  {d.tr}
                </div>
                <div>
                  <span className="mr-2 rounded-md bg-ink px-1.5 py-0.5 text-xs font-bold text-white">洪巢片</span>
                  {d.other}
                </div>
              </div>
              {d.chars && (
                <div className="mt-3">
                  <Chars list={d.chars} />
                </div>
              )}
            </div>
          ))}
        </div>
        <p>
          第一条最要紧，学者拿它当泰如片的“身份证”。古代的浊音声母（像“地、白、字”的声母），普通话和扬州话里平声字送气、仄声字不送气，所以“地”读 d-；泰如话不分平仄一律送气，“地”读 <Syl p="ti6" />，声母是 t-。全国这样读的还有客家话、赣语和徽语。<C id="lu-tongyu,lu-survey" />
        </p>
        <p>
          另外，泰如话多数地方有“支微入鱼”（一部分 -ei 类的字读成 -y 类，比如“水”白读 <Syl p="xy3" />、“嘴”白读 <Syl p="jy3" />），这也是吴语常见、洪巢片不见的现象；“三、南、山”一类字的韵母分法也和吴语、赣语一致。<C id="wiki-tongtai" />
        </p>
        <p className="text-sm text-muted">
          要说明的是，“入声分阴阳”并不是泰如片独有，洪巢片里盐城、阜宁一带和安徽庐江也分；而且在读书音的影响下，泰如话里仄声不送气的读法正在变多，西边比东边更明显。<C id="wiki-jianghuai,rusheng,gu-tone" />
        </p>
      </section>

      <section className="card space-y-3 p-6">
        <h2 className="h2">四、它是怎么来的</h2>
        <ol className="space-y-3">
          {[
            ['先秦到汉', '这一带春秋时属吴国，后来归越、归楚。语言学家鲁国尧提出“吴方言本北抵淮河”：那时吴语的北界不在长江，而在淮河，江淮之间说的是吴语一类的话。', 'lu-history,lu-survey'],
            ['四世纪', '西晋末年“永嘉之乱”，大批北方人南渡，江淮之间的话开始变成北方话的样子。鲁国尧的说法是：通泰方言是三、四世纪北方方言的“后裔”，而带着吴方言的底层。', 'lu-history'],
            ['隋唐到宋元', '据汪如东的研究，到隋代，江北沿江的扬州、泰州、如皋一带仍有吴语。此后安史之乱、唐末战乱、两宋之交又有几波北人南下，官话在江淮一步步站稳。', 'wang,xhby'],
            ['明初', '洪武年间有大批苏州一带的移民迁入江北。汪如东认为这对通泰方言里吴语成分的保存影响很大。', 'wang'],
            ['为什么留得住', '泰如地区偏在东边海角，过去交通不便、人口流动少，话变得慢；南京、扬州是商业和战事的要冲，向北方话靠拢得快。所以同属江淮官话，泰如片留下的老底子最多。', 'wang,lu-history'],
          ].map(([t, d, refs]) => (
            <li key={t} className="flex gap-3">
              <span className="mt-0.5 w-24 shrink-0 text-sm font-black text-brand-deep">{t}</span>
              <span>
                {d}
                <C id={refs} />
              </span>
            </li>
          ))}
        </ol>
        <p>
          鲁国尧还提出过一个更大的假说：通泰方言、客家话、赣语同出一源，都来自南朝时的通用语。依据是三者都把古浊音读成送气音，入声的调值格局也相似。这个说法有学者不同意，认为送气相同只是碰巧类型一样，目前<b>还没有定论</b>。<C id="lu-tongyu,lu-survey" />
        </p>
      </section>

      <section className="card space-y-4 p-6">
        <h2 className="h2">五、吴语留下的痕迹</h2>
        <p>汪如东拿苏州话和海安话对比，举出了一批两地相同、而一般官话不说的词。<C id="wang" />下面这些在本站词典里都能查到，点开可以看原始词条：</p>
        <Words list={['推板', '蛮好', '落雨', '眼热', '新妇', '济手', '掇', '壮', '猛', '挜', '吼', '捅', '汏']} />
        <p>词典里还能查到一批吴语区同样常说的词（这一组是本站自己的判断，没有文献出处）：</p>
        <Words list={['辰光', '交关', '日脚', '夜饭', '囥', '晏', '揩', '适意']} />
        <p>
          语音上，除了上面说的鼻音声母 ng-、唇齿音 v-，还有两点和吴语相近：一是“三 <Syl p="saen1" />、南 <Syl p="nun2" />”这类字读成鼻化元音，不带 -n 尾；二是很多字有“白读”和“文读”两种读法，白读往往更接近吴语，文读则跟着北方话走。<C id="wang" />
        </p>
      </section>

      <section className="card space-y-3 p-6">
        <h2 className="h2">六、古越语呢？</h2>
        <p>
          古越语是先秦时江南百越人说的话，不是汉语。学者（如郑张尚芳、游汝杰）研究的主要是它在<b>吴语、闽语、粤语</b>里留下的痕迹，比如一些讲不出汉语来历的地名和口语词；游汝杰认为，秦汉时吴语区乡间住的还是百越人，说的是越语。<C id="zhengzhang,you,wiki-yue" />
        </p>
        <p>
          泰如地区先秦属吴、越之地，底层又是吴语，所以推想它<b>间接</b>带有一些古越语的成分，是说得通的。但要老实说：我们目前<b>没有查到</b>专门论证“泰如话里有古越语底层”的研究，也举不出可靠的例词。这一条现在只能算合理的推测，不能当成定论。
        </p>
      </section>

      <section className="card space-y-3 p-6">
        <h2 className="h2">七、所以，它算不算江淮官话？</h2>
        <p>
          算，但要加一句“很不一样的一支”。按《中国语言地图集》的分法它属于江淮官话；可是和扬州话相比，声母、声调、词汇的差别大到互相听起来吃力。<C id="wiki-en,xhby" />把它理解成“站在官话和吴语之间的话”，大概最贴切。
        </p>
        <p className="text-sm text-muted">这一页是根据公开的论文和资料整理的，不是定论。发现有不准确的地方，欢迎指正。</p>
      </section>

      <section>
        <h2 className="h2">参考文献</h2>
        <p className="mt-1 text-sm text-muted">网络资料的访问日期均为 {ACCESSED}。每条后面标了我们实际读到的程度，没读到原文的不冒充读过。</p>
        <ol className="mt-3 space-y-2 text-sm">
          {REFERENCES.map((r, i) => (
            <li key={r.id} id={`ref-${i + 1}`} className="flex scroll-mt-20 gap-2">
              <span className="w-8 shrink-0 font-mono text-muted">[{i + 1}]</span>
              <span>
                {r.cite}{' '}
                {r.url && (
                  <a href={r.url} target="_blank" rel="noreferrer" className="break-all underline underline-offset-4">
                    {r.url}
                  </a>
                )}
                <span className="ml-2 rounded-md bg-paper px-1.5 py-0.5 text-xs text-muted ring-1 ring-line">
                  {r.kind} · {VERIFIED_LABEL[r.verified]}
                </span>
                {r.note && <span className="mt-0.5 block text-xs text-muted">{r.note}</span>}
              </span>
            </li>
          ))}
        </ol>
      </section>
    </article>
  );
}
