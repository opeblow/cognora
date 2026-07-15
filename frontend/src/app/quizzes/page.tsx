"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery, useMutation } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { quizService } from "@/services/quizzes"
import { subjectService } from "@/services/subjects"
import { aiService } from "@/services/ai"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileQuestion, Clock, Sparkles, Loader2 } from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"
import { DIFFICULTY_LEVELS } from "@/constants"

export default function QuizzesPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [showGenerate, setShowGenerate] = useState(false)
  const [subject, setSubject] = useState("")
  const [topic, setTopic] = useState("")
  const [difficulty, setDifficulty] = useState("medium")
  const [numQuestions, setNumQuestions] = useState(5)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["quizzes"],
    queryFn: () => quizService.getAll(),
    enabled: isAuthenticated,
    staleTime: 60000,
  })

  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => subjectService.getAll(),
    enabled: isAuthenticated,
  })

  const generateMutation = useMutation({
    mutationFn: () => aiService.generateQuiz({ subject, topic, difficulty, num_questions: numQuestions }),
    onSuccess: (data) => {
      toast.success(`Generated quiz: ${data.title}`)
      setShowGenerate(false)
      setSubject("")
      setTopic("")
      queryClient.invalidateQueries({ queryKey: ["quizzes"] })
    },
    onError: () => {
      toast.error("Failed to generate quiz. Not enough credits?")
    },
  })

  const queryClient = useQueryClient()

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-4xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#0F172A]">Practice Quizzes</h1>
              <p className="mt-1 text-sm text-gray-600">
                Test your knowledge with subject-specific quizzes
              </p>
            </div>
            <Button onClick={() => setShowGenerate(!showGenerate)} className="gap-1.5">
              <Sparkles className="h-4 w-4" />
              Generate Quiz
            </Button>
          </div>

          {showGenerate && (
            <Card className="mt-4 border-0 shadow-lg">
              <CardContent className="p-6">
                <h3 className="mb-4 text-sm font-semibold text-[#0F172A]">AI-Generated Quiz</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="mb-1 block text-xs font-medium text-gray-600">Subject</label>
                    <select
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                      className="w-full rounded-lg border border-gray-200 p-2 text-sm focus:border-[#2563EB] focus:outline-none"
                    >
                      <option value="">Select subject</option>
                      {subjectsData?.subjects?.map((s) => (
                        <option key={s.id} value={s.name}>{s.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-gray-600">Topic</label>
                    <input
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g. Quadratic Equations"
                      className="w-full rounded-lg border border-gray-200 p-2 text-sm focus:border-[#2563EB] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-gray-600">Difficulty</label>
                    <select
                      value={difficulty}
                      onChange={(e) => setDifficulty(e.target.value)}
                      className="w-full rounded-lg border border-gray-200 p-2 text-sm focus:border-[#2563EB] focus:outline-none"
                    >
                      {DIFFICULTY_LEVELS.map((d) => (
                        <option key={d.value} value={d.value}>{d.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-gray-600">Questions</label>
                    <select
                      value={numQuestions}
                      onChange={(e) => setNumQuestions(Number(e.target.value))}
                      className="w-full rounded-lg border border-gray-200 p-2 text-sm focus:border-[#2563EB] focus:outline-none"
                    >
                      {[3, 5, 10, 15, 20].map((n) => (
                        <option key={n} value={n}>{n} questions</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="mt-4 flex justify-end gap-2">
                  <Button variant="outline" size="sm" onClick={() => setShowGenerate(false)}>Cancel</Button>
                  <Button
                    size="sm"
                    onClick={() => generateMutation.mutate()}
                    disabled={!subject || !topic || generateMutation.isPending}
                    className="gap-1.5"
                  >
                    {generateMutation.isPending ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Sparkles className="h-3.5 w-3.5" />
                    )}
                    {generateMutation.isPending ? "Generating..." : `Generate (${numQuestions > 5 ? Math.ceil(numQuestions / 5) : 2} credits)`}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="mt-6 space-y-3">
            {isLoading && (
              <div className="animate-pulse space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="h-20 rounded-xl bg-gray-100" />
                ))}
              </div>
            )}
            {!isLoading && data?.quizzes?.map((quiz) => (
              <Link key={quiz.id} href={`/quizzes/${quiz.id}`}>
                <Card className="cursor-pointer transition-shadow hover:shadow-md">
                  <CardContent className="flex items-center justify-between p-5">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#2563EB]/10">
                        <FileQuestion className="h-6 w-6 text-[#2563EB]" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-[#0F172A]">{quiz.title}</h3>
                        <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                          {quiz.difficulty && (
                            <Badge variant={quiz.difficulty === "easy" ? "success" : quiz.difficulty === "hard" ? "destructive" : "default"}>
                              {quiz.difficulty}
                            </Badge>
                          )}
                          {quiz.time_limit_minutes && (
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {quiz.time_limit_minutes} min
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      Start Quiz
                    </Button>
                  </CardContent>
                </Card>
              </Link>
            ))}
            {!isLoading && !isFetching && (!data?.quizzes || data.quizzes.length === 0) && (
              <Card>
                <CardContent className="p-8 text-center">
                  <p className="text-gray-500">No quizzes available yet.</p>
                  <p className="mt-1 text-sm text-gray-400">Click &quot;Generate Quiz&quot; to create one with AI.</p>
                </CardContent>
              </Card>
            )}
            {isFetching && !isLoading && (
              <div className="animate-pulse space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="h-20 rounded-xl bg-gray-100" />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
