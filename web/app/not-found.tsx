import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="py-24 text-center">
      <h1 className="h1">没有找到这一页</h1>
      <Link href="/" className="btn-primary mt-6">
        回首页
      </Link>
    </div>
  );
}
