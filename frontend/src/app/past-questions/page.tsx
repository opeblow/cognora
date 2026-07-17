"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery, useMutation } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { pastQuestionService, type PracticeQuestion, type PracticeResult } from "@/services/pastQuestions"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Loader2, CheckCircle2, XCircle, ArrowRight, RotateCcw, ChevronLeft, Globe } from "lucide-react"
import { toast } from "sonner"

type View = "setup" | "practice" | "results"

export default function PastQuestionsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [view, setView] = useState<View>("setup")
  const [board, setBoard] = useState("")
  const [subject, setSubject] = useState("")
  const [year, setYear] = useState("")
  const [practiceQuestions, setPracticeQuestions] = useState<PracticeQuestion[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<PracticeResult | null>(null)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: filters } = useQuery({
    queryKey: ["pq-filters"],
    queryFn: () => pastQuestionService.getFilters(),
    enabled: isAuthenticated,
  })

  const { data: subjectsData, isLoading: subjectsLoading } = useQuery({
    queryKey: ["pq-subjects", board],
    queryFn: () => pastQuestionService.getSubjects(board),
    enabled: isAuthenticated && !!board,
  })

  const { data: yearsData, isLoading: yearsLoading } = useQuery({
    queryKey: ["pq-years", board],
    queryFn: () => pastQuestionService.getYears(board),
    enabled: isAuthenticated && !!board,
  })

  const subjects = subjectsData?.subjects ?? []
  const years = yearsData?.years ?? []

  const startPractice = useMutation({
    mutationFn: () => pastQuestionService.startPractice({
      board,
      subject,
      year: parseInt(year),
      count: 20,
    }),
    onSuccess: (data) => {
      if (data.questions.length === 0) {
        toast.error("No questions found. Try a different subject or year.")
        return
      }
      setPracticeQuestions(data.questions)
      setCurrentIndex(0)
      setAnswers({})
      setResult(null)
      setView("practice")
      toast.success(`Loaded ${data.questions.length} questions from the web`)
    },
    onError: () => toast.error("Failed to fetch questions. Check your connection."),
  })

  const submitPractice = useMutation({
    mutationFn: () => pastQuestionService.submit(practiceQuestions, answers),
    onSuccess: (data) => {
      setResult(data)
      setView("results")
    },
    onError: () => toast.error("Failed to submit answers"),
  })

  const handleAnswer = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }))
  }

  const currentQ = practiceQuestions[currentIndex]

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8 flex-1">
        <div className="mx-auto max-w-3xl">

          {view === "setup" && (
            <>
              <div className="mb-8">
                <h1 className="text-2xl font-bold text-[#0F172A]">Past Questions</h1>
                <p className="mt-1 text-sm text-gray-600">Real WAEC, NECO, JAMB & GCE questions fetched from the web</p>
              </div>

              <Card className="border-[#2563EB]/20">
                <CardContent className="p-6">
                  <div className="space-y-5">

                    <div>
                      <label className="mb-1.5 block text-sm font-medium text-[#0F172A]">Exam Board</label>
                      <select
                        value={board}
                        onChange={(e) => { setBoard(e.target.value); setSubject(""); setYear(""); }}
                        className="w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm text-[#0F172A]"
                      >
                        <option value="">Select exam board</option>
                        {(filters?.boards ?? []).map((b) => (
                          <option key={b} value={b}>{b}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="mb-1.5 block text-sm font-medium text-[#0F172A]">Subject</label>
                      <select
                        value={subject}
                        onChange={(e) => { setSubject(e.target.value); setYear(""); }}
                        disabled={!board}
                        className="w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm text-[#0F172A] disabled:opacity-50"
                      >
                        <option value="">{board ? (subjectsLoading ? "Loading subjects..." : "Select subject") : "Select board first"}</option>
                        {subjects.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="mb-1.5 block text-sm font-medium text-[#0F172A]">Year</label>
                      <select
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        disabled={!subject}
                        className="w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm text-[#0F172A] disabled:opacity-50"
                      >
                        <option value="">{subject ? (yearsLoading ? "Loading years..." : "Select year") : "Select subject first"}</option>
                        {years.map((y) => (
                          <option key={y} value={String(y)}>{y}</option>
                        ))}
                      </select>
                    </div>

                    <Button
                      className="w-full gap-2"
                      size="lg"
                      disabled={!board || !subject || !year || startPractice.isPending}
                      onClick={() => startPractice.mutate()}
                    >
                      {startPractice.isPending ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Fetching questions from the web...
                        </>
                      ) : (
                        <>
                          <Globe className="h-4 w-4" />
                          Start Practice
                        </>
                      )}
                    </Button>

                    {startPractice.isPending && (
                      <p className="text-center text-xs text-gray-500">
                        Searching for real {board} {subject} {year} past questions...
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {view === "practice" && currentQ && (
            <div className="mx-auto max-w-2xl">
              <div className="mb-6 flex items-center justify-between">
                <Button variant="ghost" size="sm" onClick={() => setView("setup")}>
                  <ChevronLeft className="mr-1 h-4 w-4" /> Back
                </Button>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{board}</Badge>
                  <Badge variant="outline">{subject}</Badge>
                  <Badge variant="secondary">{year}</Badge>
                </div>
                <span className="text-sm text-gray-500">
                  {currentIndex + 1}/{practiceQuestions.length}
                </span>
              </div>

              <div className="mb-4 h-2 w-full rounded-full bg-gray-100">
                <div
                  className="h-2 rounded-full bg-[#2563EB] transition-all"
                  style={{ width: `${((currentIndex + 1) / practiceQuestions.length) * 100}%` }}
                />
              </div>

              <Card className="mb-6">
                <CardContent className="p-6">
                  {currentQ.topic && (
                    <Badge variant="outline" className="mb-3 text-xs">{currentQ.topic}</Badge>
                  )}
                  <p className="text-lg font-medium text-[#0F172A]">{currentQ.question}</p>
                  <div className="mt-6 space-y-3">
                    {currentQ.options.map((opt, i) => {
                      const letter = String.fromCharCode(65 + i)
                      const isSelected = answers[currentQ.id] === letter
                      return (
                        <button
                          key={i}
                          onClick={() => handleAnswer(currentQ.id, letter)}
                          className={`flex w-full items-center gap-3 rounded-lg border p-3 text-left text-sm transition-colors ${
                            isSelected
                              ? "border-[#2563EB] bg-[#2563EB]/5 text-[#2563EB]"
                              : "border-gray-200 bg-white text-[#0F172A] hover:border-gray-300"
                          }`}
                        >
                          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-current text-xs font-bold">
                            {letter}
                          </span>
                          {opt}
                        </button>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  disabled={currentIndex === 0}
                  onClick={() => setCurrentIndex((i) => i - 1)}
                >
                  Previous
                </Button>
                {currentIndex < practiceQuestions.length - 1 ? (
                  <Button className="flex-1 gap-2" onClick={() => setCurrentIndex((i) => i + 1)}>
                    Next <ArrowRight className="h-4 w-4" />
                  </Button>
                ) : (
                  <Button
                    className="flex-1 gap-2"
                    onClick={() => submitPractice.mutate()}
                    disabled={submitPractice.isPending || Object.keys(answers).length < practiceQuestions.length}
                  >
                    {submitPractice.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                    Submit ({Object.keys(answers).length}/{practiceQuestions.length})
                  </Button>
                )}
              </div>
            </div>
          )}

          {view === "results" && result && (
            <div className="mx-auto max-w-2xl">
              <Card className="mb-6 border-[#2563EB]/20 bg-[#2563EB]/5">
                <CardContent className="p-6 text-center">
                  <h2 className="text-3xl font-bold text-[#0F172A]">{result.percentage}%</h2>
                  <p className="mt-1 text-sm text-gray-600">
                    You got {result.score} out of {result.total} correct
                  </p>
                  <div className="mt-4 flex justify-center gap-3">
                    <Button variant="outline" onClick={() => { setView("setup"); setResult(null); }}>
                      New Practice
                    </Button>
                    <Button onClick={() => startPractice.mutate()} disabled={startPractice.isPending} className="gap-2">
                      {startPractice.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCcw className="h-4 w-4" />}
                      Try Again (New Questions)
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <div className="space-y-3">
                {result.results.map((r, i) => (
                  <Card key={i} className={r.is_correct ? "border-green-200" : "border-red-200"}>
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        {r.is_correct ? (
                          <CheckCircle2 className="h-5 w-5 shrink-0 text-green-500 mt-0.5" />
                        ) : (
                          <XCircle className="h-5 w-5 shrink-0 text-red-500 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm font-medium text-[#0F172A]">{r.question}</p>
                          <div className="mt-2 space-y-1">
                            {r.options.map((opt, j) => {
                              const letter = String.fromCharCode(65 + j)
                              const isThis = r.selected_answer === letter
                              const isCorrect = r.correct_answer === letter
                              return (
                                <p key={j} className={`text-xs ${
                                  isCorrect ? "text-green-600 font-semibold" :
                                  isThis && !isCorrect ? "text-red-600 line-through" :
                                  "text-gray-500"
                                }`}>
                                  {letter}) {opt}
                                  {isCorrect && " ✓"}
                                  {isThis && !isCorrect && " ✗"}
                                </p>
                              )
                            })}
                          </div>
                          {r.explanation && (
                            <p className="mt-2 text-xs text-gray-500 italic">{r.explanation}</p>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  )
}
