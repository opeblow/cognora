import { api } from "./api"
import type { Quiz, QuizDetail, SubmitQuizResponse, QuizAttempt } from "@/types"

export const quizService = {
  getAll: (subjectId?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    if (subjectId) params.set("subject_id", subjectId)
    return api.get<{ quizzes: Quiz[]; total: number }>(`/quizzes?${params}`)
  },

  getById: (id: string) => api.get<QuizDetail>(`/quizzes/${id}`),

  submit: (quizId: string, data: { session_id: string; answers: Record<string, string>; time_taken_seconds: number }) =>
    api.post<SubmitQuizResponse>(`/quizzes/${quizId}/submit`, data),

  getMyAttempts: () => api.get<{ attempts: QuizAttempt[]; total: number }>("/quizzes/attempts/mine"),
}
