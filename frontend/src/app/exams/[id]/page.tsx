"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useParams } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import { examService } from "@/services/exams"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { CheckCircle2, XCircle, Clock, ArrowLeft, ArrowRight, RefreshCw, Sparkles } from "lucide-react"
import { toast } from "sonner"
import type { SubmitQuizResponse, LiveQuestion } from "@/types"

export default function ExamDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated } = useAuthStore()
  const examId = params.id as string

  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [timeLeft, setTimeLeft] = useState<number | null>(null)
  const [startTime] = useState(() => Date.now())
  const [result, setResult] = useState<SubmitQuizResponse | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [fetchingLive, setFetchingLive] = useState(false)
  const mountedRef = useRef(true)
  const [examData, setExamData] = useState<{
    result_id: string
    exam: { id: string; title: string; description: string | null; exam_type: string; time_limit_minutes: number | null; pass_percentage: number | null; questions: { id: string; text: string; options: string[] }[] }
    time_limit_minutes: number
  } | null>(null)
  const [liveQuestions, setLiveQuestions] = useState<LiveQuestion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login")
      return
    }

    mountedRef.current = true
    const startExam = async () => {
      try {
        const data = await examService.start(examId)
        if (mountedRef.current) {
          setExamData(data)
          setTimeLeft(data.time_limit_minutes * 60)
        }
      } catch (err: unknown) {
        const error = err as { message?: string }
        toast.error(error.message || "Failed to start exam")
        if (error.message?.includes("Insufficient credits")) {
          router.push("/credits")
        }
      } finally {
        if (mountedRef.current) setLoading(false)
      }
    }
    startExam()
    return () => { mountedRef.current = false }
  }, [isAuthenticated, examId, router])

  const handleFetchLiveQuestions = async () => {
    if (fetchingLive) return
    setFetchingLive(true)
    try {
      const data = await examService.generateLiveQuestions(examId, 5)
      setLiveQuestions((prev) => [...prev, ...data.questions])
      toast.success(`${data.generated} new questions generated from real exam sources`)
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to fetch live questions")
    } finally {
      setFetchingLive(false)
    }
  }

  const handleAnswer = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }))
  }

  const handleSubmitRef = useRef<(() => Promise<void>) | null>(null)

  const handleSubmit = async () => {
    if (submitting || !examData) return
    setSubmitting(true)
    try {
      const res = await examService.submit(examData.result_id, {
        answers,
        time_taken_seconds: Math.floor((Date.now() - startTime) / 1000),
      })
      if (mountedRef.current) setResult(res)
    } catch (error: unknown) {
      const err = error as { message?: string }
      toast.error(err.message || "Failed to submit exam")
    } finally {
      if (mountedRef.current) setSubmitting(false)
    }
  }

  useEffect(() => { handleSubmitRef.current = handleSubmit })

  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0 || result) return
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev === null || prev <= 1) {
          clearInterval(timer)
          handleSubmitRef.current?.()
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(timer)
  }, [timeLeft, result])

  if (!isAuthenticated) return null
  if (loading) {
    return (
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="ml-64 flex-1 p-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-64 rounded bg-gray-100" />
            <div className="h-4 w-96 rounded bg-gray-100" />
            <div className="h-64 rounded-xl bg-gray-100" />
          </div>
        </main>
      </div>
    )
  }

  if (result) {
    return (
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="ml-64 flex-1 p-8">
          <div className="mx-auto max-w-2xl">
            <Card>
              <CardHeader className="text-center">
                <CardTitle>Exam Results</CardTitle>
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
                  onClick={() => router.push("/exams")}
                >
                  Back to Exams
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    )
  }

  const staticQuestions = examData?.exam?.questions || []
  const allQuestions = [
    ...staticQuestions.map((q) => ({ ...q, id: q.id, source: "static" as const })),
    ...liveQuestions.map((q) => ({ ...q, id: q.id, source: "live" as const, text: q.text, options: q.options })),
  ]
  const question = allQuestions[currentQuestion]

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-3xl">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-[#0F172A]">{examData?.exam?.title}</h1>
              <p className="text-sm text-gray-500">
                Question {currentQuestion + 1} of {allQuestions.length}
              </p>
              {question?.source === "live" && (
                <Badge variant="accent" className="mt-1 text-xs">
                  <Sparkles className="mr-1 h-3 w-3" />
                  Live (Brace API)
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={handleFetchLiveQuestions}
                disabled={fetchingLive}
                className="gap-1 text-xs"
              >
                {fetchingLive ? (
                  <RefreshCw className="h-3 w-3 animate-spin" />
                ) : (
                  <Sparkles className="h-3 w-3" />
                )}
                Fetch more questions
              </Button>
              {timeLeft !== null && (
                <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
                  <Clock className="h-4 w-4" />
                  <span className={timeLeft < 300 ? "text-red-600" : ""}>
                    {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, "0")}
                  </span>
                </div>
              )}
            </div>
          </div>

          <Progress
            value={((currentQuestion + 1) / allQuestions.length) * 100}
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
            {currentQuestion < allQuestions.length - 1 ? (
              <Button onClick={() => setCurrentQuestion((p) => p + 1)}>
                Next <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? "Submitting..." : "Submit Exam"}
              </Button>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
