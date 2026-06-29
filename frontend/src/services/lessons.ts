import { api } from "./api"
import type { Lesson, LessonDetail } from "@/types"

export const lessonService = {
  getBySubject: (subjectSlug: string) =>
    api.get<{ lessons: Lesson[] }>(`/subjects/${subjectSlug}/lessons`),

  getBySlug: (subjectSlug: string, lessonSlug: string) =>
    api.get<LessonDetail>(`/subjects/${subjectSlug}/lessons/${lessonSlug}`),
}
