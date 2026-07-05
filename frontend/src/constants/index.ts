export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export const CREDIT_COSTS = {
  AI_ASK: 1,
  GENERATE_QUIZ: 2,
  MOCK_EXAM: 10,
} as const

export const WEEKLY_FREE_CREDITS = 50

export const SUBJECT_CATEGORIES = [
  { value: "Science", label: "Science" },
  { value: "Commercial", label: "Commercial" },
  { value: "Arts", label: "Arts" },
] as const

export const EXAM_TYPES = ["WAEC", "NECO", "GCE", "JAMB"] as const

export const DIFFICULTY_LEVELS = [
  { value: "easy", label: "Easy" },
  { value: "medium", label: "Medium" },
  { value: "hard", label: "Hard" },
] as const

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  SIGNUP: "/signup",
  FORGOT_PASSWORD: "/forgot-password",
  DASHBOARD: "/dashboard",
  SUBJECTS: "/subjects",
  SUBJECT: (slug: string) => `/subjects/${slug}`,
  LESSON: (slug: string, lessonSlug: string) => `/subjects/${slug}/lessons/${lessonSlug}`,
  TOPIC: (slug: string, topicId: string) => `/subjects/${slug}/topics/${topicId}`,
  QUIZZES: "/quizzes",
  QUIZ: (id: string) => `/quizzes/${id}`,
  EXAMS: "/exams",
  EXAM: (id: string) => `/exams/${id}`,
  AI_TUTOR: "/ai-tutor",
  STUDY_PLANNER: "/study-planner",
  ANALYTICS: "/analytics",
  CREDITS: "/credits",
  SETTINGS: "/settings",
} as const
