'use client';

import { TONES, toneOf } from './tones';

let ctx: AudioContext | null = null;

function freq(level: number) {
  return 150 * Math.pow(2, ((level - 1) / 4) * 0.75);
}

// 只哼出声调的高低走向，不是真人发音。
export function hum(syllables: string[]) {
  if (typeof window === 'undefined') return;
  const Ctor = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
  if (!Ctor) return;
  ctx = ctx || new Ctor();
  if (ctx.state === 'suspended') ctx.resume();
  let t = ctx.currentTime + 0.03;
  for (const syl of syllables) {
    const tone = TONES[toneOf(syl)] || TONES['0'];
    const dur = tone.short ? 0.16 : 0.42;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'triangle';
    const steps = tone.levels.length === 1 ? [tone.levels[0], tone.levels[0]] : tone.levels;
    steps.forEach((lv, i) => {
      const at = t + (dur * i) / (steps.length - 1);
      if (i === 0) osc.frequency.setValueAtTime(freq(lv), at);
      else osc.frequency.linearRampToValueAtTime(freq(lv), at);
    });
    const peak = toneOf(syl) === '0' ? 0.12 : 0.28;
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(peak, t + 0.03);
    gain.gain.setValueAtTime(peak, t + dur - 0.04);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(gain).connect(ctx.destination);
    osc.start(t);
    osc.stop(t + dur + 0.02);
    t += dur + 0.09;
  }
}
