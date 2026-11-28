import { Flashcards } from '@/components/Flashcards';

export const metadata = { title: '复习' };

export default function ReviewPage() {
  return (
    <div>
      <h1 className="h1">复习卡片</h1>
      <p className="mb-6 mt-2 text-muted">记得的词隔得越来越久才再出现，忘了的词马上再来一遍。</p>
      <Flashcards />
    </div>
  );
}
