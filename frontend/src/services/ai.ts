import { api } from "./api"

export const aiService = {
  tutor: (data: { message: string; subject?: string; context?: { role: string; content: string }[] }) =>
    api.post<{ response: string; suggestions: string[] }>("/ai/tutor", data),

  generateQuiz: (data: { subject: string; topic: string; difficulty: string; num_questions: number }) =>
    api.post<{ title: string; questions: Record<string, unknown>[] }>("/ai/generate-quiz", data),
}
