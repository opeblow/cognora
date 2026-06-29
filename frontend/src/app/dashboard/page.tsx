"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { dashboardService } from "@/services/dashboard"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { BookOpen, Brain, GraduationCap, Sparkles, TrendingUp, Clock, Zap } from "lucide-react"
import Link from "next/link"

export default function DashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login")
    }
  }, [isAuthenticated, router])

  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboardService.get,
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-6xl">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-[#0F172A]">
              Welcome back, {data?.welcome_name || user?.full_name?.split(" ")[0] || "Student"}
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              Continue your exam preparation journey
            </p>
          </div>

          {isLoading ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="h-4 w-20 rounded bg-gray-100" />
                    <div className="mt-3 h-8 w-16 rounded bg-gray-100" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <>
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-600">Credits</p>
                      <Zap className="h-4 w-4 text-yellow-500" />
                    </div>
                    <p className="mt-2 text-2xl font-bold text-[#0F172A]">
                      {data?.credits ?? 0}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">
                      {data?.weekly_credits_remaining ?? 0} weekly remaining
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-600">Streak</p>
                      <TrendingUp className="h-4 w-4 text-green-500" />
                    </div>
                    <p className="mt-2 text-2xl font-bold text-[#0F172A]">
                      {data?.learning_streak ?? 0} days
                    </p>
                    <p className="mt-1 text-xs text-gray-500">Keep it going!</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-600">Quizzes</p>
                      <BookOpen className="h-4 w-4 text-[#2563EB]" />
                    </div>
                    <p className="mt-2 text-2xl font-bold text-[#0F172A]">
                      {data?.subject_stats?.reduce((a, b) => a + b.quizzes_taken, 0) ?? 0}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">Total taken</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-600">Study Time</p>
                      <Clock className="h-4 w-4 text-[#14B8A6]" />
                    </div>
                    <p className="mt-2 text-2xl font-bold text-[#0F172A]">
                      {Math.round((data?.subject_stats?.reduce((a, b) => a + b.total_study_time_minutes, 0) ?? 0) / 60)}h
                    </p>
                    <p className="mt-1 text-xs text-gray-500">Total hours</p>
                  </CardContent>
                </Card>
              </div>

              <div className="mt-8 grid gap-6 lg:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Strong Subjects</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {data?.strong_subjects?.length ? (
                      <div className="space-y-4">
                        {data.strong_subjects.map((subject) => (
                          <div key={subject.subject_id}>
                            <div className="flex items-center justify-between text-sm">
                              <span className="font-medium text-[#0F172A]">{subject.subject_name}</span>
                              <span className="text-green-600">{subject.average_score}%</span>
                            </div>
                            <Progress value={subject.average_score} className="mt-1" indicatorClassName="bg-green-500" />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">Complete quizzes to see your strengths</p>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Weak Subjects</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {data?.weak_subjects?.length ? (
                      <div className="space-y-4">
                        {data.weak_subjects.map((subject) => (
                          <div key={subject.subject_id}>
                            <div className="flex items-center justify-between text-sm">
                              <span className="font-medium text-[#0F172A]">{subject.subject_name}</span>
                              <span className="text-red-600">{subject.average_score}%</span>
                            </div>
                            <Progress value={subject.average_score} className="mt-1" indicatorClassName="bg-red-500" />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">Complete quizzes to identify weak areas</p>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                <Link href="/ai-tutor">
                  <Card className="cursor-pointer transition-shadow hover:shadow-md">
                    <CardContent className="p-6">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#2563EB]/10">
                        <Brain className="h-6 w-6 text-[#2563EB]" />
                      </div>
                      <h3 className="mt-4 font-semibold text-[#0F172A]">AI Tutor</h3>
                      <p className="mt-1 text-sm text-gray-600">Ask anything and learn</p>
                      <Badge className="mt-3" variant="secondary">
                        1 credit per ask
                      </Badge>
                    </CardContent>
                  </Card>
                </Link>

                <Link href="/quizzes">
                  <Card className="cursor-pointer transition-shadow hover:shadow-md">
                    <CardContent className="p-6">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#14B8A6]/10">
                        <BookOpen className="h-6 w-6 text-[#14B8A6]" />
                      </div>
                      <h3 className="mt-4 font-semibold text-[#0F172A]">Practice Quizzes</h3>
                      <p className="mt-1 text-sm text-gray-600">Test your knowledge</p>
                      <Badge className="mt-3" variant="secondary">
                        2 credits per quiz
                      </Badge>
                    </CardContent>
                  </Card>
                </Link>

                <Link href="/exams">
                  <Card className="cursor-pointer transition-shadow hover:shadow-md">
                    <CardContent className="p-6">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#F59E0B]/10">
                        <GraduationCap className="h-6 w-6 text-[#F59E0B]" />
                      </div>
                      <h3 className="mt-4 font-semibold text-[#0F172A]">Mock Exams</h3>
                      <p className="mt-1 text-sm text-gray-600">Simulate real exams</p>
                      <Badge className="mt-3" variant="secondary">
                        10 credits per exam
                      </Badge>
                    </CardContent>
                  </Card>
                </Link>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
