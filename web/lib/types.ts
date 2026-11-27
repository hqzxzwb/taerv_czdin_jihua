export type Syllable = [string, string];

export interface Entry {
  id: string;
  w: string;
  p: string;
  s: Syllable[];
  m: { d: string; ex: string[] }[];
  src: string[];
  c: boolean;
  ipa: Record<string, string>;
  f: string;
}

export interface CharReading {
  t: string;
  c: string;
  p: string;
  eg: string;
  n: string;
  k: string;
  ipa: string;
}

export interface CourseItem {
  w: string;
  p: string;
  g: string;
  s: Syllable[];
  ipa: string;
  defs: string[];
  ex: { t: string; n: string }[];
  eg?: string;
  id?: string;
}

export interface Lesson {
  id: string;
  title: string;
  items: CourseItem[];
}

export interface Unit {
  id: string;
  title: string;
  icon: string;
  desc: string;
  lessons: Lesson[];
}

export interface SearchHit {
  id: string;
  w: string;
  p: string;
  d: string;
}
