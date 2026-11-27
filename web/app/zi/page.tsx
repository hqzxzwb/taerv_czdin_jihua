import { Annotator } from '@/components/Annotator';

export const metadata = { title: '注音器' };

export default function ZiPage() {
  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="h1">注音器</h1>
      <p className="mb-5 mt-2 text-muted">输入任何一句话，看看每个字用泰如话怎么读。点一个字可以听声调、看别的读音。</p>
      <Annotator />
    </div>
  );
}
