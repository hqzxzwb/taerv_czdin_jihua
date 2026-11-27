'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Syl } from './Pinyin';
import { HumButton } from './Tone';

interface Token {
  text: string;
  kind: 'word' | 'char' | 'plain';
  syl: [string, string][];
  id?: string;
  alts?: { p: string; eg: string; n: string }[];
}

const SAMPLES = ['今朝落雨，我俫明朝再家去。', '伢儿，哿曾吃夜饭？', '这块的烧饼蛮好吃。'];

export function Annotator() {
  const [text, setText] = useState('');
  const [tokens, setTokens] = useState<Token[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);
  const [open, setOpen] = useState<number | null>(null);

  async function run(value: string) {
    if (!value.trim()) return;
    setBusy(true);
    setFailed(false);
    setOpen(null);
    try {
      const res = await fetch('/api/annotate', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ text: value }) });
      if (!res.ok) throw new Error(String(res.status));
      setTokens((await res.json()).tokens);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  const picked = open !== null && tokens ? tokens[open] : null;

  return (
    <div className="space-y-4">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        maxLength={500}
        placeholder="在这里输入或粘贴一句话…"
        className="block w-full rounded-2xl bg-white p-4 text-lg leading-relaxed ring-2 ring-line focus:outline-none focus:ring-brand"
      />
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" onClick={() => run(text)} disabled={busy || !text.trim()} className="btn-primary">
          {busy ? '正在注音…' : '注音'}
        </button>
        {SAMPLES.map((s) => (
          <button key={s} type="button" onClick={() => { setText(s); run(s); }} className="chip hover:text-ink">
            {s}
          </button>
        ))}
      </div>
      {failed && <p className="text-sm text-bad">没连上服务器，请稍后再试一次。</p>}
      {tokens && (
        <div className="card p-5 sm:p-6">
          <div className="flex flex-wrap items-end gap-x-1 gap-y-4">
            {tokens.map((t, i) =>
              t.kind === 'plain' ? (
                <span key={i} className="pb-1 text-2xl text-muted">
                  {t.text}
                </span>
              ) : (
                <button
                  key={i}
                  type="button"
                  onClick={() => setOpen(open === i ? null : i)}
                  className={`inline-flex items-end gap-1 rounded-xl px-1.5 py-1 ${open === i ? 'bg-brand-soft' : t.kind === 'word' ? 'bg-paper' : ''} ${t.alts && t.alts.length > 1 ? 'underline decoration-dotted decoration-muted underline-offset-8' : ''}`}
                >
                  {t.syl.map(([c, p], k) => (
                    <span key={k} className="inline-flex flex-col items-center leading-tight">
                      <Syl p={p} className="text-sm" />
                      <span className="text-3xl font-bold">{c}</span>
                    </span>
                  ))}
                </button>
              ),
            )}
          </div>
          {picked && (
            <div className="mt-5 rounded-2xl bg-paper p-4 text-sm">
              <div className="flex flex-wrap items-center gap-3">
                <b className="text-lg">{picked.text}</b>
                <HumButton syl={picked.syl.map(([, p]) => p)} />
                {picked.id !== undefined && (
                  <Link href={`/dict/${encodeURIComponent(picked.id)}`} className="font-bold text-brand-deep">
                    查词典
                  </Link>
                )}
              </div>
              {picked.alts && picked.alts.length > 1 && (
                <ul className="mt-3 space-y-1">
                  {picked.alts.map((a) => (
                    <li key={a.p}>
                      <Syl p={a.p} /> <span className="text-muted">{[a.eg, a.n].filter(Boolean).join(' · ')}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          <p className="mt-5 text-xs leading-relaxed text-muted">
            浅色底的是词典里查到的整个词，其余按单字表逐字标注，多音字只取第一个读音（带虚线的字点开可以看其他读音）。机器标注难免有错，只当参考。
          </p>
        </div>
      )}
    </div>
  );
}
