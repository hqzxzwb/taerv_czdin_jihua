import { annotate } from '@/lib/data';

export async function POST(req: Request) {
  const { text } = (await req.json().catch(() => ({}))) as { text?: string };
  if (typeof text !== 'string') return Response.json({ error: 'text required' }, { status: 400 });
  return Response.json({ tokens: annotate(text.slice(0, 500)) });
}
