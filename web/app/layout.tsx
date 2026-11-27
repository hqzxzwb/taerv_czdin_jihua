import type { Metadata, Viewport } from 'next';
import { Nav } from '@/components/Nav';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL('https://tairu.ruilisi.com'),
  keywords: ['泰如话', '泰如方言', '通泰方言', '泰州话', '兴化话', '泰兴话', '东台话', '大丰话', '海安话', '如皋话', '如东话', '江淮官话', '方言学习', '方言词典'],
  openGraph: { siteName: '泰如话学堂', locale: 'zh_CN', type: 'website' },
  verification: { other: { 'baidu-site-verification': 'codeva-ful4ysntkY' } },
  title: { default: '泰如话学堂 · 从零学泰如方言', template: '%s · 泰如话学堂' },
  description: '面向零基础的泰如方言（泰州、兴化、泰兴、东台、大丰、海安、如皋、如东）学习站：分级课程、拼音与声调、练习、复习卡片、四万词条词典。',
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
        <main className="mx-auto max-w-5xl px-4 pb-8 pt-5 md:pt-8">{children}</main>
        <footer className="mx-auto max-w-5xl px-4 pb-28 text-center text-xs text-muted md:pb-10">
          <a href="https://beian.miit.gov.cn/" target="_blank" rel="noreferrer" className="hover:underline">
            苏ICP备19037090号
          </a>
        </footer>
      </body>
    </html>
  );
}
