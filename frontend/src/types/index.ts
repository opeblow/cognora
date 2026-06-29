export interface User {
  id: string
  email: string
  full_name: string
  avatar_url: string | null
  is_verified: boolean
  credits: string
  learning_streak: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface Subject {
  id: string
  name: string
  slug: string
  description: string | null
  category: string
  icon: string | null
  color: string | null
}

export interface Quiz {
  id: string
  subject_id: string
  title: string
  description: string | null
  difficulty: string | null
  time_limit_minutes: string | null
  pass_percentage: string | null
  subject?: Subject
}

export interface Question {
  id: string
  text: string
  options: string[]
  order_index: string | null
  question_type: string
  correct_answer?: string
  explanation?: string
}

export interface QuizDetail extends Quiz {
  questions: Question[]
}

export interface QuizAttempt {
  id: string
  quiz_id: string
  score: string | null
  total: string | null
  percentage: string | null
  time_taken_seconds: string | null
  completed_at: string | null
  quiz?: Quiz
}

export interface SubmitQuizResponse {
  score: number
  total: number
  percentage: number
  passed: boolean
  answers: AnswerDetail[]
}

export interface AnswerDetail {
  question_id: string
  question_text: string
  selected_answer: string
  correct_answer: string
  is_correct: boolean
  explanation: string | null
}

export interface Exam {
  id: string
  subject_id: string
  title: string
  description: string | null
  exam_type: string
  year: string | null
  time_limit_minutes: string | null
  total_questions: string | null
  pass_percentage: string | null
  subject?: Subject
}

export interface StartExamResponse {
  result_id: string
  exam: {
    id: string
    title: string
    description: string | null
    exam_type: string
    year: string | null
    time_limit_minutes: string | null
    pass_percentage: string | null
    questions: Question[]
  }
  time_limit_minutes: number
}

export interface ExamResult {
  id: string
  exam_id: string
  score: string | null
  total: string | null
  percentage: string | null
  time_taken_seconds: string | null
  status: string
  started_at: string
  completed_at: string | null
  exam?: Exam
}

export interface DashboardData {
  welcome_name: string
  credits: number
  weekly_credits_remaining: number
  learning_streak: number
  recent_activity: Record<string, unknown>[]
  progress_overview: SubjectStat[]
  subject_stats: SubjectStat[]
  strong_subjects: SubjectStat[]
  weak_subjects: SubjectStat[]
}

export interface SubjectStat {
  subject_id: string
  subject_name: string
  lessons_completed: number
  quizzes_taken: number
  average_score: number
  total_study_time_minutes: number
}

export interface CreditBalance {
  credits: number
  weekly_credits_used: number
  weekly_credits_total: number
  transactions: CreditTransaction[]
}

export interface CreditTransaction {
  id: string
  amount: string
  transaction_type: string
  description: string | null
  created_at: string
}

export interface StudyPlan {
  id: string
  title: string
  description: string | null
  plan_type: string
  start_date: string
  end_date: string | null
  is_active: string
  days: StudyPlanDay[]
}

export interface StudyPlanDay {
  id: string
  date: string
  subjects: string[] | null
  topics: string[] | null
  duration_minutes: string | null
  is_completed: string
  notes: string | null
}

export interface Lesson {
  id: string
  title: string
  slug: string
  summary: string | null
  order_index: number | null
  estimated_minutes: number | null
}

export interface Topic {
  id: string
  title: string
  content: string | null
  order_index: number | null
}

export interface LessonDetail extends Lesson {
  content: string | null
  topics: Topic[]
}

export interface TutorMessage {
  role: "user" | "assistant"
  content: string
}
