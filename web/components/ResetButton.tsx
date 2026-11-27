'use client';

import { useState } from 'react';
import { resetProgress } from '@/lib/progress';

export function ResetButton() {
  const [asking, setAsking] = useState(false);
  const [done, setDone] = useState(false);
  if (done) return <p className="text-sm text-muted">已清空。</p>;
  if (!asking)
    return (
      <button type="button" onClick={() => setAsking(true)} className="btn-ghost">
        清空我的学习记录
      </button>
    );
  return (
    <div className="flex flex-wrap items-center gap-3">
      <span className="text-sm">分数、星星和复习卡片都会删掉，确定吗？</span>
      <button type="button" onClick={() => { resetProgress(); setDone(true); }} className="btn bg-bad text-white">
        确定清空
      </button>
      <button type="button" onClick={() => setAsking(false)} className="btn-ghost">
        不了
      </button>
    </div>
  );
}
