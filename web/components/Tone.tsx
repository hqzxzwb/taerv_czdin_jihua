'use client';

import { hum } from '@/lib/audio';
import { TONES, toneOf } from '@/lib/tones';

export function ToneContour({ tone, size = 44 }: { tone: string; size?: number }) {
  const t = TONES[tone] || TONES['0'];
  const levels = t.levels.length === 1 ? [t.levels[0], t.levels[0]] : t.levels;
  const w = t.short ? size * 0.45 : size;
  const pad = 5;
  const y = (lv: number) => pad + ((5 - lv) / 4) * (size - pad * 2);
  const pts = levels.map((lv, i) => `${pad + (i / (levels.length - 1)) * (w - pad * 2)},${y(lv)}`).join(' ');
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-label={`${t.name}调形`}>
      {[1, 2, 3, 4, 5].map((lv) => (
        <line key={lv} x1={2} x2={size - 2} y1={y(lv)} y2={y(lv)} stroke="#EADFCB" strokeWidth={1} />
      ))}
      <polyline points={pts} fill="none" stroke={t.color} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function HumButton({ syl, label = '听声调', className = '' }: { syl: string[]; label?: string; className?: string }) {
  return (
    <button
      type="button"
      onClick={() => hum(syl)}
      className={`inline-flex min-h-[40px] items-center gap-1.5 rounded-full bg-brand-soft px-4 text-sm font-bold text-brand-deep active:scale-95 ${className}`}
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
        <path d="M3 10v4h4l5 4V6L7 10H3zm13.5 2a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z" />
      </svg>
      {label}
    </button>
  );
}

export function ToneStrip({ syl }: { syl: string[] }) {
  return (
    <span className="inline-flex items-center gap-1">
      {syl.map((p, i) => (
        <ToneContour key={i} tone={toneOf(p)} size={34} />
      ))}
    </span>
  );
}
