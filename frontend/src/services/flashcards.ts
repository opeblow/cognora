import { api } from "./api"

export interface Flashcard {
  id: string
  question: string
  answer: string
  difficulty: string | null
  tags: string | null
  topic_id: string | null
  section_index: number | null
  next_review_at: string | null
  ease_factor: number
  interval_days: number
  repetitions: number
}

export interface ReviewResult {
  id: string
  next_review_at: string | null
  interval_days: number
  ease_factor: number
  repetitions: number
}

export const flashcardService = {
  getAll: (topicId?: string, dueOnly = false, skip = 0, limit = 50) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
    if (topicId) params.set("topic_id", topicId)
    if (dueOnly) params.set("due_only", "true")
    return api.get<{ flashcards: Flashcard[]; total: number }>(`/flashcards?${params}`)
  },

  review: (flashcardId: string, quality: number) =>
    api.post<ReviewResult>(`/flashcards/${flashcardId}/review`, { quality }),

  generate: (topicId: string, count = 10) =>
    api.post<{ flashcards: Flashcard[]; total: number }>("/flashcards/generate", { topic_id: topicId, count }),

  delete: (flashcardId: string) =>
    api.delete<{ message: string }>(`/flashcards/${flashcardId}`),

  deleteAll: () =>
    api.delete<{ message: string; deleted: number }>("/flashcards"),
}
