// 2020 年第七次全国人口普查常住人口（标准时点 2020-11-01 零时）。ref 指向 references.ts 里的出处。
export interface CensusRow {
  city: string;
  name: string;
  n: number;
  ref: string;
}

export const CORE: CensusRow[] = [
  { city: '泰州', name: '海陵区', n: 577016, ref: 'census-tz' },
  { city: '泰州', name: '高港区', n: 258590, ref: 'census-tz' },
  { city: '泰州', name: '姜堰区', n: 668408, ref: 'census-tz' },
  { city: '泰州', name: '兴化市', n: 1128204, ref: 'census-tz' },
  { city: '泰州', name: '泰兴市', n: 994445, ref: 'census-tz' },
  { city: '南通', name: '如皋市', n: 1238448, ref: 'census-nt' },
  { city: '南通', name: '海安市', n: 874334, ref: 'census-nt' },
  { city: '南通', name: '如东县', n: 880006, ref: 'census-nt' },
  { city: '盐城', name: '东台市', n: 888410, ref: 'census-yc' },
  { city: '盐城', name: '大丰区', n: 645603, ref: 'census-yc' },
];

export const NANTONG_CITY: CensusRow[] = [
  { city: '南通', name: '崇川区', n: 1183740, ref: 'census-nt' },
  { city: '南通', name: '通州区', n: 1258739, ref: 'census-nt' },
];

export const sum = (rows: CensusRow[]) => rows.reduce((a, r) => a + r.n, 0);
export const wan = (n: number, digits = 1) => (n / 10000).toFixed(digits);
