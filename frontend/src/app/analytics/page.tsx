"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { dashboardService } from "@/services/dashboard"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { BarChart3, TrendingUp, TrendingDown, BookOpen } from "lucide-react"

export default function AnalyticsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data } = useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboardService.get,
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) return null

  const allStats = data?.subject_stats || []
  const strong = data?.strong_subjects || []
  const weak = data?.weak_subjects || []

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-6xl">
          <h1 className="text-2xl font-bold text-[#0F172A]">Analytics</h1>
          <p className="mt-1 text-sm text-gray-600">
            Track your learning progress and performance
          </p>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-[#2563EB]" />
                  Subject Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                {allStats.length > 0 ? (
                  <div className="space-y-6">
                    {allStats.map((stat) => (
                      <div key={stat.subject_id}>
                        <div className="mb-1 flex items-center justify-between text-sm">
                          <span className="font-medium text-[#0F172A]">
                            {stat.subject_name}
                          </span>
                          <span
                            className={
                              stat.average_score >= 70
                                ? "text-green-600"
                                : stat.average_score >= 50
                                ? "text-yellow-600"
                                : "text-red-600"
                            }
                          >
                            {stat.average_score}%
                          </span>
                        </div>
                        <Progress
                          value={stat.average_score}
                          className="h-2.5"
                          indicatorClassName={
                            stat.average_score >= 70
                              ? "bg-green-500"
                              : stat.average_score >= 50
                              ? "bg-yellow-500"
                              : "bg-red-500"
                          }
                        />
                        <div className="mt-1 flex gap-4 text-xs text-gray-500">
                          <span>{stat.quizzes_taken} quizzes</span>
                          <span>{stat.lessons_completed} lessons</span>
                          <span>{Math.round(stat.total_study_time_minutes / 60)}h studied</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">
                    Complete quizzes and lessons to see your performance data.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  Strong Subjects
                </CardTitle>
              </CardHeader>
              <CardContent>
                {strong.length > 0 ? (
                  <div className="space-y-4">
                    {strong.map((s) => (
                      <div key={s.subject_id} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <BookOpen className="h-4 w-4 text-green-500" />
                          <span className="text-sm text-[#0F172A]">{s.subject_name}</span>
                        </div>
                        <span className="text-sm font-medium text-green-600">{s.average_score}%</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No data yet</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingDown className="h-5 w-5 text-red-500" />
                  Weak Subjects
                </CardTitle>
              </CardHeader>
              <CardContent>
                {weak.length > 0 ? (
                  <div className="space-y-4">
                    {weak.map((s) => (
                      <div key={s.subject_id} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <BookOpen className="h-4 w-4 text-red-500" />
                          <span className="text-sm text-[#0F172A]">{s.subject_name}</span>
                        </div>
                        <span className="text-sm font-medium text-red-600">{s.average_score}%</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No data yet</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
