import { TONES, splitTone, toneOf } from '@/lib/tones';

export function Syl({ p, className = '' }: { p: string; className?: string }) {
  const [base, tone] = splitTone(p);
  const color = TONES[toneOf(p)]?.color;
  return (
    <span className={`font-mono font-semibold ${className}`} style={{ color }}>
      {base}
      {tone && <sup className="ml-px text-[0.65em]">{tone}</sup>}
    </span>
  );
}

export function Pinyin({ p, className = '' }: { p: string; className?: string }) {
  const parts = p.split(/(\s+|,\s*|\/)/);
  return (
    <span className={className}>
      {parts.map((part, i) =>
        /^[a-z]+\d?(-\d)?$/i.test(part) ? <Syl key={i} p={part} /> : <span key={i} className="text-muted">{part}</span>,
      )}
    </span>
  );
}

export function Ruby({ syl, size = 'text-4xl' }: { syl: [string, string][]; size?: string }) {
  return (
    <span className="inline-flex flex-wrap items-end justify-center gap-x-2 gap-y-1">
      {syl.map(([c, p], i) => (
        <span key={i} className="inline-flex flex-col items-center leading-tight">
          <span className="h-5 text-sm">{p ? <Syl p={p} /> : null}</span>
          <span className={`${size} font-black`}>{c}</span>
        </span>
      ))}
    </span>
  );
}
