export interface Tone {
  n: string;
  name: string;
  levels: number[];
  short?: boolean;
  color: string;
  tip: string;
}

// 参考调值取泰兴、如皋一带的常见描写（泰兴连读变调.md 里的单字调），各地略有出入。
export const TONES: Record<string, Tone> = {
  '1': { n: '1', name: '阴平', levels: [2, 1], color: '#2F7FD1', tip: '低低地往下落，像叹一口气' },
  '2': { n: '2', name: '阳平', levels: [3, 5], color: '#2E9E6B', tip: '往上扬，像普通话的第二声' },
  '3': { n: '3', name: '上声', levels: [2, 1, 3], color: '#C98A0A', tip: '先降再升，拐个弯，像普通话的第三声' },
  '5': { n: '5', name: '阴去', levels: [4, 4], color: '#D64545', tip: '平平的、偏高，不要往下掉' },
  '6': { n: '6', name: '阳去', levels: [2, 1], color: '#7A5AC8', tip: '如皋、泰兴、泰县等多数地方读得和第 1 声一样' },
  '7': { n: '7', name: '阴入', levels: [4], short: true, color: '#D4622A', tip: '又短又急，喉咙一收就停住' },
  '8': { n: '8', name: '阳入', levels: [4, 5], short: true, color: '#B8418F', tip: '同样短促，但比第 7 声更高' },
  '9': { n: '9', name: '小称调', levels: [2, 1, 3], color: '#4C8C8C', tip: '省掉“一”留下的调：如皋像上声，泰兴像阴平，如东像阳平' },
  '0': { n: '0', name: '轻声', levels: [2], short: true, color: '#9A8F85', tip: '轻轻带过，不用力' },
};

export const TONE_ORDER = ['1', '2', '3', '5', '6', '7', '8'];

export function toneOf(syllable: string): string {
  const m = syllable.match(/(\d)(?:-\d)?$/);
  return m ? m[1] : '0';
}

export function splitTone(syllable: string): [string, string] {
  const m = syllable.match(/^(.*?)(\d(?:-\d)?)?$/);
  return m ? [m[1], m[2] || ''] : [syllable, ''];
}

export function stripTones(pinyin: string): string {
  return pinyin.replace(/\d(-\d)?/g, '');
}
