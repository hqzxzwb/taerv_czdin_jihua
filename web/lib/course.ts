import raw from '@/data/course.json';
import type { CourseItem, Lesson, Unit } from './types';

export const course = raw as unknown as Unit[];

export const lessons: (Lesson & { unit: Unit })[] = course.flatMap((u) => u.lessons.map((l) => ({ ...l, unit: u })));

export const allItems: CourseItem[] = lessons.flatMap((l) => l.items);

export function cardKey(item: { w: string; p: string }) {
  return `${item.w}|${item.p}`;
}

export const itemByKey = new Map(allItems.map((i) => [cardKey(i), i]));

export function findLesson(id: string) {
  const idx = lessons.findIndex((l) => l.id === id);
  return idx < 0 ? null : { lesson: lessons[idx], next: lessons[idx + 1] || null };
}
