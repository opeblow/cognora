import { api } from "./api"
import type {
  Lesson, LessonDetail, Topic, TopicDetail, ExpandResponse,
  TextbookPlanResponse, TextbookStatusResponse, SectionContent, GenerateSectionResponse,
} from "@/types"

export const lessonService = {
  getBySubject: (subjectSlug: string) =>
    api.get<{ lessons: Lesson[] }>(`/subjects/${subjectSlug}/lessons`),

  getBySlug: (subjectSlug: string, lessonSlug: string) =>
    api.get<LessonDetail>(`/subjects/${subjectSlug}/lessons/${lessonSlug}`),

  getTopicsBySubject: (subjectSlug: string) =>
    api.get<{ topics: Topic[] }>(`/subjects/${subjectSlug}/topics`),

  getTopic: (subjectSlug: string, topicId: string) =>
    api.get<TopicDetail>(`/subjects/${subjectSlug}/topics/${topicId}`),

  expandTopic: (subjectSlug: string, topicId: string) =>
    api.post<ExpandResponse>(`/subjects/${subjectSlug}/topics/${topicId}/expand`),

  // ===== Textbook Section (Lazy Loading) =====

  getTextbookPlan: (subjectSlug: string, topicId: string) =>
    api.get<TextbookPlanResponse>(`/subjects/${subjectSlug}/topics/${topicId}/textbook/plan`),

  getTextbookStatus: (subjectSlug: string, topicId: string) =>
    api.get<TextbookStatusResponse>(`/subjects/${subjectSlug}/topics/${topicId}/textbook/status`),

  getSectionContent: (subjectSlug: string, topicId: string, sectionIndex: number) =>
    api.get<SectionContent>(`/subjects/${subjectSlug}/topics/${topicId}/textbook/sections/${sectionIndex}`),

  generateSection: (subjectSlug: string, topicId: string, sectionIndex: number, regenerate = false) =>
    api.post<GenerateSectionResponse>(
      `/subjects/${subjectSlug}/topics/${topicId}/textbook/sections/${sectionIndex}/generate`,
      { regenerate }
    ),
}
