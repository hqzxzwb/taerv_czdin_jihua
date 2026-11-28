// 全站引用的文献只在这里登记一次，页面和文档都从这里取，编号按本表顺序。
// verified：full = 读过原文；reprint = 读的是转载；abstract = 只读到摘要或二手转述；data = 统计数据
export interface Reference {
  id: string;
  kind: '论文' | '专著' | '学位论文' | '官方统计' | '统计转载' | '百科' | '报道';
  cite: string;
  url?: string;
  verified: 'full' | 'reprint' | 'abstract' | 'data';
  note?: string;
}

export const ACCESSED = '2026-11-27';

export const REFERENCES: Reference[] = [
  { id: 'lu-history', kind: '论文', cite: '鲁国尧. 泰州方音史与通泰方言史研究[M]//鲁国尧语言学论文集. 南京: 江苏教育出版社, 2003.', url: 'https://nantonghua.net/archives/5548/', verified: 'reprint', note: '读的是“下篇一”的网络转录，未核对原书页码。' },
  { id: 'lu-survey', kind: '论文', cite: '鲁国尧. 通泰方言研究史脞述[J/OL].', url: 'https://www.aisixiang.com/data/137953.html', verified: 'reprint', note: '原刊未核对。' },
  { id: 'lu-tongyu', kind: '论文', cite: '鲁国尧. 客、赣、通泰方言源于南朝通语说[J/OL].', url: 'http://nantonghua.net/archives/2560/', verified: 'reprint', note: '读的是第二部分的转录，原刊未核对。' },
  { id: 'wang', kind: '论文', cite: '汪如东. 通泰方言的吴语底层及历史层次[J/OL].', url: 'http://nantonghua.net/archives/7084/', verified: 'reprint', note: '原刊刊期未核对。' },
  { id: 'gu-tone', kind: '论文', cite: '顾黔. 通泰方言声调的历史演变[J]. 南京师大学报(社会科学版), 1993(2).', url: 'http://rwtz.t56.net/index.php?a=show&c=index&catid=12&id=4125&m=content', verified: 'abstract', note: '只读到转载页的摘要。' },
  { id: 'gu-book', kind: '专著', cite: '顾黔. 通泰方言音韵研究[M]. 南京: 南京大学出版社, 2001.', verified: 'abstract', note: '未读到原书，内容据维基百科和鲁国尧序言的转述。' },
  { id: 'you', kind: '论文', cite: '游汝杰. 吴语地理在历史上的演变[J]. 中国语文研究, 2001(1).', url: 'https://www.cuhk.edu.hk/ics/clrc/scl_12/you.pdf', verified: 'abstract' },
  { id: 'zhengzhang', kind: '论文', cite: '郑张尚芳. 古吴越地名中的侗台语成分[J]. 民族语文, 1990(6).', verified: 'abstract', note: '据维基百科“古越语”条目转述。' },
  { id: 'rusheng', kind: '学位论文', cite: '江淮官话入声研究[D]. 2007.', url: 'https://wap.cnki.net/touch/web/Dissertation/Article/10032-2007162154.nh.html', verified: 'abstract', note: '只读到知网摘要，作者和授予单位未核对。' },
  { id: 'atlas', kind: '专著', cite: '中国社会科学院, 澳大利亚人文科学院. 中国语言地图集[M]. 香港: 朗文出版(远东)有限公司, 1987.', verified: 'abstract', note: '未读到原书，分片方案据百科转述；第二版（商务印书馆, 2012）的泰如片人口数未查到。' },
  { id: 'wiki-tongtai', kind: '百科', cite: '维基百科. 通泰方言[EB/OL].', url: 'https://zh.wikipedia.org/zh-cn/通泰方言', verified: 'full', note: '条目本身被标注缺少文内引注。' },
  { id: 'wiki-jianghuai', kind: '百科', cite: '维基百科. 江淮官话[EB/OL].', url: 'https://zh.wikipedia.org/zh-hans/江淮官话', verified: 'abstract' },
  { id: 'wiki-yue', kind: '百科', cite: '维基百科. 古越语[EB/OL].', url: 'https://zh.wikipedia.org/zh-hans/古越语', verified: 'abstract' },
  { id: 'wiki-en', kind: '百科', cite: 'Wikipedia. Tong-Tai Mandarin[EB/OL].', url: 'https://en.wikipedia.org/wiki/Tong-Tai_Mandarin', verified: 'abstract' },
  { id: 'baike-dongtai', kind: '百科', cite: '百度百科. 东台话[EB/OL].', url: 'https://baike.baidu.com/item/%E4%B8%9C%E5%8F%B0%E8%AF%9D/8965743', verified: 'full' },
  { id: 'baike-tairu', kind: '百科', cite: '百度百科. 江淮官话泰如片[EB/OL].', url: 'https://baike.baidu.com/item/%E6%B1%9F%E6%B7%AE%E5%AE%98%E8%AF%9D%E6%B3%B0%E5%A6%82%E7%89%87/12016644', verified: 'abstract', note: '页面无法直接打开，数字据搜索摘要；不同版本分别写 1200 万和 1300 万。' },
  { id: 'xhby', kind: '报道', cite: '新华报业网. 跟着“苏超”去读城｜为啥扬州人不懂泰州话，却错把盐城人当“老乡”？[EB/OL].', url: 'https://www.xhby.net/content/s68d0c8dce4b0b65f07c3af57.html', verified: 'abstract' },
  { id: 'census-nt', kind: '官方统计', cite: '南通市统计局. 南通市第七次全国人口普查公报(第二号)——地区人口情况[R]. 2021-05-24.', url: 'http://tjj.nantong.gov.cn/ntstj/tjgb/content/bee00145-67eb-4189-9208-8d1aa20d9e2c.html', verified: 'data' },
  { id: 'census-tz', kind: '统计转载', cite: '泰州市及海陵区、高港区、姜堰区、兴化市、泰兴市第七次全国人口普查公报[R]. 2021.', url: 'https://tjgb.hongheiku.com/11453.html', verified: 'data', note: '读的是第三方网站转载，未打开统计局原文核对。' },
  { id: 'census-yc', kind: '统计转载', cite: '盐城市第七次全国人口普查公报(分区县数据)[R]. 2021.', url: 'https://www.phsb.com/html/680/679432.html', verified: 'data', note: '读的是第三方网站转载，未打开统计局原文核对。' },
  { id: 'huji-dt', kind: '统计转载', cite: '东台市历年国民经济和社会发展统计公报(户籍人口、常住人口)[R].', url: 'https://www.hongheiku.com/lishishuju/21687.html', verified: 'data', note: '第三方网站汇总。' },
  { id: 'repo', kind: '专著', cite: 'hqzxzwb 等. 泰如辞典计划(taerv_czdin_jihua)[DB/OL]. GitHub.', url: 'https://github.com/hqzxzwb/taerv_czdin_jihua', verified: 'full', note: '本站例字读音（daen_cz.csv）和例词（词条文件）的来源。' },
];

export const REF_NO = new Map(REFERENCES.map((r, i) => [r.id, i + 1]));

export const VERIFIED_LABEL: Record<Reference['verified'], string> = {
  full: '已读原文',
  reprint: '读的是转载',
  abstract: '只读到摘要或转述',
  data: '统计数据',
};
