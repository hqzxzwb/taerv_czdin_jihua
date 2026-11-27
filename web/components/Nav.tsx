'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const ICONS: Record<string, string> = {
  home: 'M3 11.5 12 4l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-8.5z',
  learn: 'M12 3 2 8l10 5 8-4v6h2V8L12 3zM6 12.5V17c0 1.7 2.7 3 6 3s6-1.3 6-3v-4.5l-6 3-6-3z',
  sound: 'M3 10v4h4l5 4V6L7 10H3zm13.5 2a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z',
  review: 'M12 5V2L7 6l5 4V7a5 5 0 1 1-5 5H5a7 7 0 1 0 7-7z',
  dict: 'M6 3h11a2 2 0 0 1 2 2v16H7a2 2 0 0 1-2-2V4a1 1 0 0 1 1-1zm1 15a1 1 0 0 0 0 2h10v-2H7zm2-11v2h6V7H9z',
};

const MAIN = [
  { href: '/', label: '首页', icon: 'home' },
  { href: '/learn', label: '学习', icon: 'learn' },
  { href: '/pinyin', label: '拼音', icon: 'sound' },
  { href: '/review', label: '复习', icon: 'review' },
  { href: '/dict', label: '词典', icon: 'dict' },
];

const MORE = [
  { href: '/zi', label: '注音' },
  { href: '/grammar', label: '语法' },
  { href: '/origin', label: '来历' },
  { href: '/about', label: '关于' },
];

function active(path: string, href: string) {
  return href === '/' ? path === '/' : path.startsWith(href);
}

export function Nav() {
  const path = usePathname();
  const inLesson = /^\/learn\/.+/.test(path);
  return (
    <>
      <header className="sticky top-0 z-30 border-b border-line bg-paper/90 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-5xl items-center gap-6 px-4">
          <Link href="/" className="flex items-center gap-2 text-lg font-black">
            <span className="grid h-8 w-8 place-items-center rounded-xl bg-brand text-base text-white">泰</span>
            泰如话学堂
          </Link>
          <nav className="hidden flex-1 items-center gap-1 md:flex">
            {[...MAIN, ...MORE].map((it) => (
              <Link
                key={it.href}
                href={it.href}
                className={`rounded-xl px-3 py-2 text-sm font-bold ${active(path, it.href) ? 'bg-ink text-white' : 'text-muted hover:bg-white'}`}
              >
                {it.label}
              </Link>
            ))}
          </nav>
          <nav className="ml-auto flex items-center gap-1 md:hidden">
            {MORE.map((it) => (
              <Link key={it.href} href={it.href} className={`rounded-lg px-2 py-1.5 text-sm font-bold ${active(path, it.href) ? 'text-brand-deep' : 'text-muted'}`}>
                {it.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <nav hidden={inLesson} className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-white pb-[env(safe-area-inset-bottom)] md:hidden">
        <div className="mx-auto grid max-w-lg grid-cols-5">
          {MAIN.map((it) => {
            const on = active(path, it.href);
            return (
              <Link key={it.href} href={it.href} className={`flex h-14 flex-col items-center justify-center gap-0.5 text-[11px] font-bold ${on ? 'text-brand-deep' : 'text-muted'}`}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                  <path d={ICONS[it.icon]} />
                </svg>
                {it.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
