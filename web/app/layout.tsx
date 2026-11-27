import type { Metadata, Viewport } from 'next';
import { Nav } from '@/components/Nav';
import './globals.css';

export const metadata: Metadata = {
  title: { default: '泰如话学堂 · 从零学泰如方言', template: '%s · 泰如话学堂' },
  description: '面向零基础的泰如方言（泰州、如皋、泰兴、兴化、东台、如东、海安）学习站：分级课程、拼音与声调、练习、复习卡片、四万词条词典。',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#FBF6EC',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <Nav />
        <main className="mx-auto max-w-5xl px-4 pb-28 pt-5 md:pb-16 md:pt-8">{children}</main>
      </body>
    </html>
  );
}
