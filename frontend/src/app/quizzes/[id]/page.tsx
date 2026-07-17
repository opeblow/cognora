"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { quizService } from "@/services/quizzes"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { CheckCircle2, XCircle, Clock, ArrowLeft, ArrowRight } from "lucide-react"
import { toast } from "sonner"
import type { SubmitQuizResponse } from "@/types"

export default function QuizDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated } = useAuthStore()
  const quizId = params.id as string

  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [startTime] = useState(() => Date.now())
  const [result, setResult] = useState<SubmitQuizResponse | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const mountedRef = useRef(true)
  const submittedRef = useRef(false)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
    return () => { mountedRef.current = false }
  }, [isAuthenticated, router])

  const { data: quiz, isLoading } = useQuery({
    queryKey: ["quiz", quizId],
    queryFn: () => quizService.getById(quizId),
    enabled: isAuthenticated,
  })

  const sessionId = quiz?.session_id ?? null

  const timeLimit = quiz?.time_limit_minutes ? Math.min(quiz.time_limit_minutes, 6) * 60 : null
  const timeLeft = timeLimit !== null ? Math.max(0, timeLimit - elapsed) : null

  const handleAnswer = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }))
  }

  const handleSubmitRef = useRef<(() => Promise<void>) | null>(null)

  const handleSubmit = async () => {
    if (submitting || !sessionId || submittedRef.current) return
    submittedRef.current = true
    setSubmitting(true)
    try {
      const res = await quizService.submit(quizId, {
        session_id: sessionId,
        answers,
        time_taken_seconds: Math.floor((Date.now() - startTime) / 1000),
      })
      if (mountedRef.current) setResult(res)
    } catch (error: unknown) {
      submittedRef.current = false
      const err = error as { message?: string }
      toast.error(err.message || "Failed to submit quiz")
      if (err.message?.includes("Insufficient credits")) {
        router.push("/credits")
      }
    } finally {
      if (mountedRef.current) setSubmitting(false)
    }
  }

  useEffect(() => { handleSubmitRef.current = handleSubmit })

  useEffect(() => {
    if (timeLimit === null || result) return
    const timer = setInterval(() => {
      setElapsed((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [timeLimit, result])

  useEffect(() => {
    if (timeLimit !== null && elapsed >= timeLimit && !submittedRef.current) {
      handleSubmitRef.current?.()
    }
  }, [elapsed, timeLimit])

  if (!isAuthenticated) return null

  const questions = quiz?.questions || []
  const question = questions[currentQuestion]

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
          <div className="mx-auto max-w-3xl">
            <div className="mb-6">
              <div className="h-8 w-64 animate-pulse rounded bg-gray-200" />
              <div className="mt-2 h-4 w-48 animate-pulse rounded bg-gray-200" />
            </div>
            <div className="animate-pulse space-y-4">
              <div className="flex items-center justify-center rounded-xl bg-gray-100 p-12">
                <div className="text-center">
                  <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-[#2563EB]" />
                  <p className="mt-4 text-sm text-gray-500">
                    Loading quiz...
                  </p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (result) {
    return (
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
          <div className="mx-auto max-w-2xl">
            <Card>
              <CardHeader className="text-center">
                <CardTitle>Quiz Results</CardTitle>
                <div className="mt-4">
                  <div className="text-5xl font-bold text-[#0F172A]">
                    {result.percentage}%
                  </div>
                  <p className="mt-2 text-sm text-gray-500">
                    {result.score} / {result.total} correct
                  </p>
                  <Badge
                    className="mt-3"
                    variant={result.passed ? "success" : "destructive"}
                  >
                    {result.passed ? "PASSED" : "FAILED"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {result.answers.map((answer, i) => (
                  <div
                    key={answer.question_id}
                    className={`rounded-lg border p-4 ${
                      answer.is_correct
                        ? "border-green-200 bg-green-50"
                        : "border-red-200 bg-red-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {answer.is_correct ? (
                        <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-green-600" />
                      ) : (
                        <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
                      )}
                      <div>
                        <p className="font-medium text-[#0F172A]">
                          {i + 1}. {answer.question_text}
                        </p>
                        <p className="mt-1 text-sm text-gray-600">
                          Your answer: {answer.selected_answer}
                        </p>
                        {!answer.is_correct && (
                          <p className="text-sm text-green-600">
                            Correct: {answer.correct_answer}
                          </p>
                        )}
                        {answer.explanation && (
                          <p className="mt-2 text-sm text-gray-500">
                            {answer.explanation}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                <Button
                  className="mt-4 w-full"
                  onClick={() => router.push("/quizzes")}
                >
                  Back to Quizzes
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-3xl">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-[#0F172A]">{quiz?.title}</h1>
              <p className="text-sm text-gray-500">
                Question {currentQuestion + 1} of {questions.length}
              </p>
            </div>
            {timeLeft !== null && (
              <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
                <Clock className="h-4 w-4" />
                <span>
                  {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, "0")}
                </span>
              </div>
            )}
          </div>

          <Progress
            value={((currentQuestion + 1) / questions.length) * 100}
            className="mb-6"
          />

          {question && (
            <Card>
              <CardContent className="p-6">
                <h2 className="text-lg font-medium text-[#0F172A]">
                  {question.text}
                </h2>
                <RadioGroup
                  className="mt-6 space-y-3"
                  value={answers[question.id] || ""}
                  onValueChange={(value) => handleAnswer(question.id, value)}
                >
                  {question.options.map((option) => (
                    <div
                      key={option}
                      className="flex items-center space-x-3 rounded-lg border border-gray-100 p-4 transition-colors hover:bg-gray-50 has-data-[state=checked]:border-[#2563EB] has-data-[state=checked]:bg-[#2563EB]/5"
                    >
                      <RadioGroupItem value={option} id={option} />
                      <Label htmlFor={option} className="flex-1 cursor-pointer text-sm">
                        {option}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </CardContent>
            </Card>
          )}

          <div className="mt-6 flex items-center justify-between">
            <Button
              variant="outline"
              onClick={() => setCurrentQuestion((p) => Math.max(0, p - 1))}
              disabled={currentQuestion === 0}
            >
              <ArrowLeft className="mr-2 h-4 w-4" /> Previous
            </Button>
            {currentQuestion < questions.length - 1 ? (
              <Button
                onClick={() => setCurrentQuestion((p) => p + 1)}
              >
                Next <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? "Submitting..." : "Submit Quiz"}
              </Button>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
