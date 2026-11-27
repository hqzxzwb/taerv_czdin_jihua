import type { MetadataRoute } from 'next';
import { lessons } from '@/lib/course';
import { store } from '@/lib/data';

export const dynamic = 'force-dynamic';

const BASE = 'https://tairu.ruilisi.com';

export default function sitemap(): MetadataRoute.Sitemap {
  const pages = ['', '/learn', '/pinyin', '/dict', '/zi', '/grammar', '/origin', '/about'].map((p) => ({ url: BASE + p, priority: p ? 0.8 : 1 }));
  const lessonPages = lessons.map((l) => ({ url: `${BASE}/learn/${l.id}`, priority: 0.6 }));
  const entries = store().entries.map((e) => ({ url: `${BASE}/dict/${encodeURIComponent(e.id)}`, priority: 0.5 }));
  return [...pages, ...lessonPages, ...entries];
}
