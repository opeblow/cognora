import { api } from "./api"

export interface PracticeQuestion {
  id: string
  question: string
  options: string[]
  correct_answer: string
  explanation: string
  difficulty: string
  topic: string
}

export interface StartPracticeResponse {
  questions: PracticeQuestion[]
  total: number
  board: string
  subject: string
  year: number
}

export interface PracticeResult {
  score: number
  total: number
  percentage: number
  results: Array<{
    question_id: string
    question: string
    selected_answer: string
    correct_answer: string
    is_correct: boolean
    explanation: string
    options: string[]
  }>
}

export interface FilterOptions {
  boards: string[]
}

export const pastQuestionService = {
  getFilters: () => api.get<FilterOptions>("/past-questions/filters"),

  getSubjects: (board: string) =>
    api.get<{ subjects: string[] }>(`/past-questions/subjects/${board}`),

  getYears: (board: string) =>
    api.get<{ years: number[] }>(`/past-questions/years/${board}`),

  startPractice: (params: { board: string; subject: string; year: number; count?: number }) =>
    api.post<StartPracticeResponse>("/past-questions/start", {
      board: params.board,
      subject: params.subject,
      year: params.year,
      count: params.count ?? 20,
    }),

  submit: (questions: PracticeQuestion[], answers: Record<string, string>) =>
    api.post<PracticeResult>("/past-questions/submit", { questions, answers }),
}
