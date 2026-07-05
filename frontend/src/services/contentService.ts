import { api } from "./api"

export interface TopicContent {
  id: string
  title: string
  html_content: string
  sections: TextbookSection[]
}

export interface TextbookSection {
  id: string
  title: string
  content: string
  section_index: number
  word_count: number | null
  is_generated: boolean
}

export interface TopicProgress {
  topic_id: string
  completed: boolean
  sections_read: number[]
  total_sections: number
  exercises_attempted: number
  exercises_passed: number
  deep_dives_completed: string[]
  last_position: string
  time_spent_seconds: number
}

export interface SyllabusInfo {
  exam_board: string
  subject: string
  year: string
  modules: SyllabusModule[]
}

export interface SyllabusModule {
  id: string
  title: string
  weight_in_exam: number
  topics: SyllabusTopic[]
}

export interface SyllabusTopic {
  id: string
  title: string
  examination_focus: string[]
  typical_question_style: string
  difficulty_rating: string
}

export const contentService = {
  getTopic: (topicId: string) =>
    api.get<TopicContent>(`/content/topics/${topicId}`),

  getTopicProgress: (topicId: string) =>
    api.get<TopicProgress>(`/content/topics/${topicId}/progress`),

  updateTopicProgress: (topicId: string, update: Partial<TopicProgress>) =>
    api.patch<TopicProgress>(`/content/topics/${topicId}/progress`, update),

  getSyllabus: (examBoard: string, subject: string) =>
    api.get<SyllabusInfo>(`/content/syllabus/${examBoard}/${subject}`),

  verifyAlignment: (topicId: string) =>
    api.get<{ aligned: boolean; coverage: number; uncovered_areas: unknown[] }>(
      `/content/topics/${topicId}/alignment`
    ),
}
