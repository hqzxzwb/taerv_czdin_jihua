import Link from 'next/link';
import { Syl } from '@/components/Pinyin';
import { store } from '@/lib/data';

export const metadata = { title: '泰如话的来历', description: '泰如话从哪里来，和江淮官话其他地方的话有什么不一样，和吴语、古越语是什么关系。' };
export const dynamic = 'force-dynamic';

const SOURCES = [
  { t: '鲁国尧《通泰方言研究史脞述》', u: 'https://www.aisixiang.com/data/137953.html' },
  { t: '鲁国尧：通泰方言是古代北方方言的“后裔”而具有吴方言的底层（转录）', u: 'https://nantonghua.net/archives/5548/' },
  { t: '鲁国尧《客、赣、通泰方言源于南朝通语说（二）》', u: 'http://nantonghua.net/archives/2560/' },
  { t: '汪如东《通泰方言的吴语底层及历史层次》', u: 'http://nantonghua.net/archives/7084/' },
  { t: '顾黔《通泰方言声调的历史演变》', u: 'http://rwtz.t56.net/index.php?a=show&c=index&catid=12&id=4125&m=content' },
  { t: '游汝杰《吴语地理在历史上的演变》', u: 'https://www.cuhk.edu.hk/ics/clrc/scl_12/you.pdf' },
  { t: '维基百科“通泰方言”', u: 'https://zh.wikipedia.org/zh-cn/通泰方言' },
  { t: '维基百科“江淮官话”', u: 'https://zh.wikipedia.org/zh-hans/江淮官话' },
  { t: '维基百科“古越语”', u: 'https://zh.wikipedia.org/zh-hans/古越语' },
  { t: 'Wikipedia: Tong-Tai Mandarin', u: 'https://en.wikipedia.org/wiki/Tong-Tai_Mandarin' },
  { t: '百度百科“东台话”', u: 'https://baike.baidu.com/item/%E4%B8%9C%E5%8F%B0%E8%AF%9D/8965743' },
  { t: '新华报业：为啥扬州人不懂泰州话', u: 'https://www.xhby.net/content/s68d0c8dce4b0b65f07c3af57.html' },
  { t: '《江淮官话入声研究》（学位论文摘要）', u: 'https://wap.cnki.net/touch/web/Dissertation/Article/10032-2007162154.nh.html' },
];

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
          <Link key={w} href={`/dict/${e.id}`} className="rounded-xl bg-paper px-3 py-1.5 text-[15px] ring-1 ring-line hover:ring-ink/30">
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
      <header>
        <h1 className="h1">泰如话的来历</h1>
        <p className="mt-2 text-muted">它从哪里来？为什么扬州人听不太懂泰州话？和吴语、古越语又是什么关系？这一页把学者们的研究讲给你听，每个说法后面都注明是谁说的。</p>
      </header>

      <section className="card space-y-3 p-6">
        <h2 className="h2">一、先说结论</h2>
        <ul className="list-disc space-y-2 pl-5">
          <li>在方言分类上，泰如话（学界也叫“通泰方言”）算<b>江淮官话</b>的一支，叫“泰如片”，和南京、扬州、合肥所在的“洪巢片”，以及湖北一带的“黄孝片”并列。</li>
          <li>但它是江淮官话里<b>最特别</b>的一片：声母、声调、词汇上有一批特点，洪巢片没有，反而和江南的吴语、江西的赣语、客家话相通。</li>
          <li>主流的解释是：这片土地上古时候说的是吴语，后来北方移民带来的话盖在上面，吴语沉到了“底层”。所以泰如话是<b>北方话的骨架、吴语的底子</b>。</li>
          <li>使用人口约一千一百万（2004 年的数字），分布在泰州、兴化、姜堰、泰兴、东台、大丰、海安、如皋、如东、南通等地。</li>
        </ul>
      </section>

      <section className="card space-y-4 p-6">
        <h2 className="h2">二、和江淮官话其他地方有什么不一样</h2>
        <p>下面“洪巢片”一栏说的是南京、扬州一带的一般情况。例字的读音直接取自本站的单字音表，你可以自己对一对。</p>
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
          第一条最要紧，学者拿它当泰如片的“身份证”。古代的浊音声母（像“地、白、字”的声母），普通话和扬州话里平声字送气、仄声字不送气，所以“地”读 d-；泰如话不分平仄一律送气，“地”读 <Syl p="ti6" />，声母是 t-。全国这样读的还有客家话、赣语和徽语。
        </p>
        <p>
          另外，泰如话多数地方有“支微入鱼”（一部分 -ei 类的字读成 -y 类，比如“水”白读 <Syl p="xy3" />、“嘴”白读 <Syl p="jy3" />），这也是吴语常见、洪巢片不见的现象；“三、南、山”一类字的韵母分法也和吴语、赣语一致。
        </p>
        <p className="text-sm text-muted">
          要说明的是，“入声分阴阳”并不是泰如片独有，洪巢片里盐城、阜宁一带和安徽庐江也分；而且在读书音的影响下，泰如话里仄声不送气的读法正在变多，西边比东边更明显。
        </p>
      </section>

      <section className="card space-y-3 p-6">
        <h2 className="h2">三、它是怎么来的</h2>
        <ol className="space-y-3">
          {[
            ['先秦到汉', '这一带春秋时属吴国，后来归越、归楚。语言学家鲁国尧提出“吴方言本北抵淮河”：那时吴语的北界不在长江，而在淮河，江淮之间说的是吴语一类的话。'],
            ['四世纪', '西晋末年“永嘉之乱”，大批北方人南渡，江淮之间的话开始变成北方话的样子。鲁国尧的说法是：通泰方言是三、四世纪北方方言的“后裔”，而带着吴方言的底层。'],
            ['隋唐到宋元', '据汪如东的研究，到隋代，江北沿江的扬州、泰州、如皋一带仍有吴语。此后安史之乱、唐末战乱、两宋之交又有几波北人南下，官话在江淮一步步站稳。'],
            ['明初', '洪武年间有大批苏州一带的移民迁入江北。汪如东认为这对通泰方言里吴语成分的保存影响很大；地方谱牒的统计也显示，明以后迁入泰州的家族里相当一部分来自吴语区。'],
            ['为什么留得住', '泰如地区偏在东边海角，过去交通不便、人口流动少，话变得慢；南京、扬州是商业和战事的要冲，向北方话靠拢得快。所以同属江淮官话，泰如片留下的老底子最多。'],
          ].map(([t, d]) => (
            <li key={t} className="flex gap-3">
              <span className="mt-0.5 w-24 shrink-0 text-sm font-black text-brand-deep">{t}</span>
              <span>{d}</span>
            </li>
          ))}
        </ol>
        <p>
          鲁国尧还提出过一个更大的假说：通泰方言、客家话、赣语同出一源，都来自南朝时的通用语。依据是三者都把古浊音读成送气音，入声的调值格局也相似。这个说法有学者不同意，认为送气相同只是碰巧类型一样，目前<b>还没有定论</b>。
        </p>
      </section>

      <section className="card space-y-4 p-6">
        <h2 className="h2">四、吴语留下的痕迹</h2>
        <p>汪如东拿苏州话和海安话对比，举出了一批两地相同、而一般官话不说的词。下面这些在本站词典里都能查到，点开可以看原始词条：</p>
        <Words list={['推板', '蛮好', '落雨', '眼热', '新妇', '济手', '掇', '壮', '猛', '挜', '吼', '捅', '汏']} />
        <p>词典里还能查到一批吴语区同样常说的词：</p>
        <Words list={['辰光', '交关', '日脚', '夜饭', '囥', '晏', '揩', '适意']} />
        <p>
          语音上，除了上面说的鼻音声母 ng-、唇齿音 v-，还有两点和吴语相近：一是“三 <Syl p="saen1" />、南 <Syl p="nun2" />”这类字读成鼻化元音，不带 -n 尾；二是很多字有“白读”和“文读”两种读法，白读往往更接近吴语，文读则跟着北方话走。
        </p>
      </section>

      <section className="card space-y-3 p-6">
        <h2 className="h2">五、古越语呢？</h2>
        <p>
          古越语是先秦时江南百越人说的话，不是汉语。学者（如郑张尚芳、游汝杰）研究的主要是它在<b>吴语、闽语、粤语</b>里留下的痕迹，比如一些讲不出汉语来历的地名和口语词；游汝杰认为，秦汉时吴语区乡间住的还是百越人，说的是越语。
        </p>
        <p>
          泰如地区先秦属吴、越之地，底层又是吴语，所以推想它<b>间接</b>带有一些古越语的成分，是说得通的。但要老实说：我们目前<b>没有查到</b>专门论证“泰如话里有古越语底层”的研究，也举不出可靠的例词。这一条现在只能算合理的推测，不能当成定论。
        </p>
      </section>

      <section className="card space-y-3 p-6">
        <h2 className="h2">六、所以，它算不算江淮官话？</h2>
        <p>
          算，但要加一句“很不一样的一支”。按《中国语言地图集》的分法它属于江淮官话；可是和扬州话相比，声母、声调、词汇的差别大到互相听起来吃力。把它理解成“站在官话和吴语之间的话”，大概最贴切。
        </p>
        <p className="text-sm text-muted">这一页是根据公开的论文和资料整理的，不是定论。发现有不准确的地方，欢迎指正。</p>
      </section>

      <section>
        <h2 className="h2">参考资料</h2>
        <ul className="mt-3 list-disc space-y-1.5 pl-5 text-sm">
          {SOURCES.map((s) => (
            <li key={s.u}>
              <a href={s.u} target="_blank" rel="noreferrer" className="underline underline-offset-4">
                {s.t}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </article>
  );
}
