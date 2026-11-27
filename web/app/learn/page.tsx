import { CourseMap } from '@/components/CourseMap';
import { allItems, course, lessons } from '@/lib/course';

export const metadata = { title: '课程' };

export default function LearnPage() {
  return (
    <div>
      <h1 className="h1">课程表</h1>
      <p className="mt-2 text-muted">
        {course.length} 个单元、{lessons.length} 课、{allItems.length} 个最常用的词。按顺序学最省力，也可以挑喜欢的先学。
      </p>
      <div className="mt-6">
        <CourseMap />
      </div>
    </div>
  );
}
