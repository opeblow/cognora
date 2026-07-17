import { api } from "./api"
import type { Subject } from "@/types"

export interface Topic {
  id: string
  title: string
  content: string | null
  content_type: string
  order_index: number | null
  lesson_title: string | null
}

export const subjectService = {
  getAll: (category?: string) =>
    api.get<{ subjects: Subject[]; total: number }>(
      `/subjects${category ? `?category=${category}` : ""}`
    ),

  getBySlug: (slug: string) => api.get<Subject>(`/subjects/${slug}`),

  getTopicsBySlug: (slug: string) =>
    api.get<{ topics: Topic[] }>(`/subjects/${slug}/topics`),
}
