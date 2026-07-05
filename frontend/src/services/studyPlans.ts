import { api } from "./api"

export interface StudyPlanDay {
  id: string
  date: string
  subjects: string[] | null
  topics: string[] | null
  duration_minutes: number | null
  is_completed: boolean
  notes: string | null
}

export interface StudyPlan {
  id: string
  title: string
  description: string | null
  plan_type: string
  start_date: string
  end_date: string | null
  is_active: boolean
  days: StudyPlanDay[]
}

export const studyPlanService = {
  getAll: () => api.get<StudyPlan[]>("/study-planner"),

  getById: (planId: string) => api.get<StudyPlan>(`/study-planner/${planId}`),

  getToday: () => api.get<{ tasks: StudyPlanDay[] }>("/study-planner/today"),

  getCalendar: (weekStart?: string) => {
    const params = weekStart ? `?week_start=${weekStart}` : ""
    return api.get<{ days: StudyPlanDay[] }>(`/study-planner/calendar${params}`)
  },

  create: (data: {
    title: string
    description?: string
    plan_type: string
    start_date: string
    end_date?: string
    subjects: string[]
    use_ai?: boolean
  }) => api.post<StudyPlan>("/study-planner", data),

  markDayCompleted: (dayId: string) =>
    api.post<{ day: StudyPlanDay }>(`/study-planner/days/${dayId}/complete`),
}
