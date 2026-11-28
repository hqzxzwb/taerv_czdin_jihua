import { notFound } from 'next/navigation';
import { LessonPlayer } from '@/components/LessonPlayer';
import { findLesson, lessons } from '@/lib/course';

export function generateStaticParams() {
  return lessons.map((l) => ({ id: l.id }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const found = findLesson((await params).id);
  return { title: found ? `${found.lesson.unit.title} · ${found.lesson.title}` : '课程' };
}

export default async function LessonPage({ params }: { params: Promise<{ id: string }> }) {
  const found = findLesson((await params).id);
  if (!found) notFound();
  const { lesson, next } = found;
  const { unit, ...plain } = lesson;
  return <LessonPlayer lesson={plain} unitItems={unit.lessons.flatMap((l) => l.items)} nextId={next?.id || null} />;
}
