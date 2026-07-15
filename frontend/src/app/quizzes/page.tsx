"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { quizService } from "@/services/quizzes"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileQuestion, Clock } from "lucide-react"
import Link from "next/link"

export default function QuizzesPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["quizzes"],
    queryFn: () => quizService.getAll(),
    enabled: isAuthenticated,
    staleTime: 60000,
  })

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-4xl">
          <h1 className="text-2xl font-bold text-[#0F172A]">Practice Quizzes</h1>
          <p className="mt-1 text-sm text-gray-600">
            Test your knowledge with subject-specific quizzes
          </p>

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
