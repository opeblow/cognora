import { describe, it, expect } from "vitest"
import {
  API_URL,
  CREDIT_COSTS,
  WEEKLY_FREE_CREDITS,
  SUBJECT_CATEGORIES,
  EXAM_TYPES,
  DIFFICULTY_LEVELS,
  ROUTES,
} from "@/constants"

describe("API_URL", () => {
  it("defaults to localhost when env var is not set", () => {
    expect(API_URL).toBe("http://localhost:8000/api")
  })
})

describe("CREDIT_COSTS", () => {
  it("has correct values", () => {
    expect(CREDIT_COSTS.AI_ASK).toBe(1)
    expect(CREDIT_COSTS.GENERATE_QUIZ).toBe(2)
    expect(CREDIT_COSTS.MOCK_EXAM).toBe(10)
  })

  it("has all required keys", () => {
    expect(Object.keys(CREDIT_COSTS)).toEqual(["AI_ASK", "GENERATE_QUIZ", "MOCK_EXAM"])
  })
})

describe("WEEKLY_FREE_CREDITS", () => {
  it("is 50", () => {
    expect(WEEKLY_FREE_CREDITS).toBe(50)
  })
})

describe("SUBJECT_CATEGORIES", () => {
  it("contains Science, Commercial, Arts", () => {
    const values = SUBJECT_CATEGORIES.map((c) => c.value)
    expect(values).toContain("Science")
    expect(values).toContain("Commercial")
    expect(values).toContain("Arts")
  })
})

describe("EXAM_TYPES", () => {
  it("contains WAEC, NECO, GCE, JAMB", () => {
    expect(EXAM_TYPES).toContain("WAEC")
    expect(EXAM_TYPES).toContain("NECO")
    expect(EXAM_TYPES).toContain("GCE")
    expect(EXAM_TYPES).toContain("JAMB")
  })
})

describe("DIFFICULTY_LEVELS", () => {
  it("contains easy, medium, hard", () => {
    const values = DIFFICULTY_LEVELS.map((d) => d.value)
    expect(values).toContain("easy")
    expect(values).toContain("medium")
    expect(values).toContain("hard")
  })
})

describe("ROUTES", () => {
  it("has correct static routes", () => {
    expect(ROUTES.HOME).toBe("/")
    expect(ROUTES.LOGIN).toBe("/login")
    expect(ROUTES.SIGNUP).toBe("/signup")
    expect(ROUTES.DASHBOARD).toBe("/dashboard")
    expect(ROUTES.SUBJECTS).toBe("/subjects")
    expect(ROUTES.QUIZZES).toBe("/quizzes")
    expect(ROUTES.EXAMS).toBe("/exams")
    expect(ROUTES.AI_TUTOR).toBe("/ai-tutor")
    expect(ROUTES.CREDITS).toBe("/credits")
    expect(ROUTES.SETTINGS).toBe("/settings")
  })

  it("generates correct dynamic routes", () => {
    expect(ROUTES.SUBJECT("mathematics")).toBe("/subjects/mathematics")
    expect(ROUTES.LESSON("physics", "kinematics")).toBe("/subjects/physics/lessons/kinematics")
    expect(ROUTES.TOPIC("chemistry", "topic-123")).toBe("/subjects/chemistry/topics/topic-123")
    expect(ROUTES.QUIZ("quiz-456")).toBe("/quizzes/quiz-456")
    expect(ROUTES.EXAM("exam-789")).toBe("/exams/exam-789")
  })
})
