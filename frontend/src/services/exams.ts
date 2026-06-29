import { api } from "./api"
import type { Exam, StartExamResponse, SubmitQuizResponse, ExamResult } from "@/types"

export const examService = {
  getAll: (subjectId?: string, examType?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    if (subjectId) params.set("subject_id", subjectId)
    if (examType) params.set("exam_type", examType)
    return api.get<{ exams: Exam[]; total: number }>(`/exams?${params}`)
  },

  start: (examId: string) =>
    api.post<StartExamResponse>(`/exams/${examId}/start`),

  submit: (resultId: string, data: { answers: Record<string, string>; time_taken_seconds: number }) =>
    api.post<SubmitQuizResponse>(`/exams/results/${resultId}/submit`, data),

  getMyResults: () => api.get<{ results: ExamResult[]; total: number }>("/exams/results/mine"),
}
