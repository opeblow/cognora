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
  time_limit_minutes: number | null
  total_questions: number | null
  pass_percentage: number | null
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
  content_type?: string
  order_index: number | null
  lesson_title?: string | null
}

export interface LessonDetail extends Lesson {
  content: string | null
  topics: Topic[]
}

export interface TopicDetail {
  id: string
  title: string
  content: string | null
  has_expanded: boolean
  lesson: {
    id: string
    title: string
    slug: string
  }
  subject: {
    id: string
    name: string
    slug: string
    color: string | null
  }
  all_topics: Topic[]
}

export interface ExpandResponse {
  content: string
  expanded: boolean
  subject?: string
  topic?: string
}

export interface TutorMessage {
  role: "user" | "assistant"
  content: string
}

// ===== Textbook Section Types (Lazy Loading) =====

export interface SectionPlan {
  index: number
  title: string
  focus: string
}

export interface TextbookPlanResponse {
  topic_id: string
  topic_title: string
  subject_name: string
  total_sections: number
  sections: SectionPlan[]
}

export interface SectionContent {
  index: number
  title: string
  content: string
  has_content: boolean
}

export interface TextbookStatusResponse {
  topic_id: string
  total_sections: number
  generated_sections: number[]
  sections: SectionContent[]
}

export interface GenerateSectionResponse {
  section_index: number
  total_sections: number
  content: string
  section_title: string
  has_more: boolean
}

export interface LiveQuestion {
  id: string
  text: string
  options: string[]
  correct_answer: string
  explanation: string
  difficulty: string
  cognitive_level: string
}
