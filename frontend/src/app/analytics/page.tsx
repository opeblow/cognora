"use client"

import { useEffect, useMemo } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { dashboardService } from "@/services/dashboard"
import { quizService } from "@/services/quizzes"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  BarChart3,
  TrendingUp,
  Clock,
  Zap,
  Target,
  BookOpen,
  AlertTriangle,
  Trophy,
  Flame,
  Brain,
  CheckCircle2,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react"

const BLUE = "#2563EB"
const TEAL = "#14B8A6"
const AMBER = "#F59E0B"
const RED = "#EF4444"
const GREEN = "#22C55E"

function scoreColor(score: number) {
  if (score >= 70) return GREEN
  if (score >= 50) return AMBER
  return RED
}

function scoreLevel(score: number) {
  if (score >= 80) return "Excellent"
  if (score >= 70) return "Good"
  if (score >= 50) return "Needs Work"
  return "At Risk"
}

function readinessLabel(score: number) {
  if (score >= 80) return "Ready"
  if (score >= 65) return "Almost There"
  if (score >= 50) return "Developing"
  return "Not Ready"
}

export default function AnalyticsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: dashboardData } = useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboardService.get,
    enabled: isAuthenticated,
  })

  const { data: attemptsData } = useQuery({
    queryKey: ["quiz-attempts"],
    queryFn: quizService.getMyAttempts,
    enabled: isAuthenticated,
  })

  const allStats = useMemo(() => dashboardData?.subject_stats || [], [dashboardData])
  const strongSubjects = useMemo(() => dashboardData?.strong_subjects || [], [dashboardData])
  const weakSubjects = useMemo(() => dashboardData?.weak_subjects || [], [dashboardData])
  const streak = dashboardData?.learning_streak || 0

  const attempts = useMemo(() => {
    if (!attemptsData?.attempts) return []
    return [...attemptsData.attempts]
      .filter((a) => a.percentage != null && a.completed_at)
      .sort((a, b) => new Date(a.completed_at!).getTime() - new Date(b.completed_at!).getTime())
  }, [attemptsData])

  const totalQuizzes = useMemo(
    () => allStats.reduce((sum, s) => sum + s.quizzes_taken, 0),
    [allStats]
  )

  const avgScore = useMemo(() => {
    if (allStats.length === 0) return 0
    return Math.round(allStats.reduce((sum, s) => sum + s.average_score, 0) / allStats.length)
  }, [allStats])

  const totalStudyMinutes = useMemo(
    () => allStats.reduce((sum, s) => sum + s.total_study_time_minutes, 0),
    [allStats]
  )
  const studyHours = (totalStudyMinutes / 60).toFixed(1)

  const performanceScore = useMemo(() => {
    const scoreComponent = avgScore * 0.5
    const streakComponent = Math.min(streak * 5, 25)
    const quizComponent = Math.min(totalQuizzes * 2, 25)
    return Math.round(scoreComponent + streakComponent + quizComponent)
  }, [avgScore, streak, totalQuizzes])

  const last10 = useMemo(() => attempts.slice(-10), [attempts])

  const weeklyActivity = useMemo(() => {
    const dayMap: Record<string, number> = {}
    for (let i = 6; i >= 0; i--) {
      const d = new Date()
      d.setDate(d.getDate() - i)
      const key = d.toISOString().slice(0, 10)
      dayMap[key] = 0
    }
    for (const a of attempts) {
      if (!a.completed_at) continue
      const key = a.completed_at.slice(0, 10)
      if (key in dayMap) dayMap[key]++
    }
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    const today = new Date()
    const todayIdx = today.getDay()
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date()
      d.setDate(d.getDate() - (6 - i))
      const key = d.toISOString().slice(0, 10)
      return { label: dayNames[(todayIdx - 6 + i + 7) % 7], count: dayMap[key] || 0 }
    })
  }, [attempts])

  const maxBarCount = useMemo(
    () => Math.max(...last10.map((a) => parseInt(a.score || "0")), 1),
    [last10]
  )

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-6xl">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-[#0F172A]">Analytics Dashboard</h1>
            <p className="mt-1 text-sm text-gray-500">
              Track your learning progress, performance trends, and areas to improve
            </p>
          </div>

          {/* Summary Stats */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Total Quizzes</p>
                    <p className="mt-1 text-3xl font-bold text-[#0F172A]">{totalQuizzes}</p>
                    <p className="mt-1 text-xs text-gray-400">Across {allStats.length} subjects</p>
                  </div>
                  <div className="rounded-xl bg-[#2563EB]/10 p-3">
                    <BarChart3 className="h-6 w-6 text-[#2563EB]" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Average Score</p>
                    <div className="mt-1 flex items-baseline gap-2">
                      <p className="text-3xl font-bold text-[#0F172A]">{avgScore}%</p>
                      <Badge variant={avgScore >= 70 ? "success" : avgScore >= 50 ? "default" : "destructive"}>
                        {scoreLevel(avgScore)}
                      </Badge>
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14B8A6]/10 p-3">
                    <Target className="h-6 w-6 text-[#14B8A6]" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Study Hours</p>
                    <p className="mt-1 text-3xl font-bold text-[#0F172A]">{studyHours}h</p>
                    <p className="mt-1 text-xs text-gray-400">
                      {totalStudyMinutes.toLocaleString()} minutes total
                    </p>
                  </div>
                  <div className="rounded-xl bg-[#F59E0B]/10 p-3">
                    <Clock className="h-6 w-6 text-[#F59E0B]" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Current Streak</p>
                    <div className="mt-1 flex items-baseline gap-2">
                      <p className="text-3xl font-bold text-[#0F172A]">{streak}</p>
                      <span className="text-sm text-gray-400">days</span>
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#EF4444]/10 p-3">
                    <Flame className="h-6 w-6 text-[#EF4444]" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Performance Score + Exam Readiness */}
          <div className="grid gap-4 lg:grid-cols-3 mb-8">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="h-5 w-5" style={{ color: AMBER }} />
                  Performance Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-8">
                  <div className="relative flex-shrink-0">
                    <svg viewBox="0 0 120 120" className="h-32 w-32 -rotate-90">
                      <circle
                        cx="60"
                        cy="60"
                        r="52"
                        fill="none"
                        stroke="#E5E7EB"
                        strokeWidth="10"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="52"
                        fill="none"
                        stroke={scoreColor(performanceScore)}
                        strokeWidth="10"
                        strokeDasharray={`${(performanceScore / 100) * 326.7} 326.7`}
                        strokeLinecap="round"
                        className="transition-all duration-700"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-3xl font-bold text-[#0F172A]">{performanceScore}</span>
                      <span className="text-xs text-gray-400">/100</span>
                    </div>
                  </div>
                  <div className="flex-1 space-y-3">
                    <div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Score Average (50%)</span>
                        <span className="font-medium" style={{ color: scoreColor(avgScore) }}>
                          {Math.round(avgScore * 0.5)} pts
                        </span>
                      </div>
                      <Progress
                        value={avgScore}
                        className="h-2 mt-1"
                        indicatorClassName="bg-[#2563EB]"
                      />
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Streak Bonus (25%)</span>
                        <span className="font-medium" style={{ color: TEAL }}>
                          {Math.min(streak * 5, 25)} pts
                        </span>
                      </div>
                      <Progress
                        value={Math.min(streak * 5, 25)}
                        max={25}
                        className="h-2 mt-1"
                        indicatorClassName="bg-[#14B8A6]"
                      />
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Quiz Volume (25%)</span>
                        <span className="font-medium" style={{ color: AMBER }}>
                          {Math.min(totalQuizzes * 2, 25)} pts
                        </span>
                      </div>
                      <Progress
                        value={Math.min(totalQuizzes * 2, 25)}
                        max={25}
                        className="h-2 mt-1"
                        indicatorClassName="bg-[#F59E0B]"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" style={{ color: scoreColor(avgScore) }} />
                  Exam Readiness
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center text-center">
                  <div
                    className="mb-3 flex h-20 w-20 items-center justify-center rounded-full"
                    style={{ backgroundColor: `${scoreColor(avgScore)}15` }}
                  >
                    {avgScore >= 70 ? (
                      <CheckCircle2 className="h-10 w-10" style={{ color: scoreColor(avgScore) }} />
                    ) : avgScore >= 50 ? (
                      <Target className="h-10 w-10" style={{ color: scoreColor(avgScore) }} />
                    ) : (
                      <AlertTriangle className="h-10 w-10" style={{ color: RED }} />
                    )}
                  </div>
                  <Badge
                    variant={
                      avgScore >= 70 ? "success" : avgScore >= 50 ? "default" : "destructive"
                    }
                    className="mb-2 text-sm px-3 py-1"
                  >
                    {readinessLabel(avgScore)}
                  </Badge>
                  <p className="text-sm text-gray-500 mb-4">
                    {avgScore >= 70
                      ? "You're well prepared! Keep up the momentum."
                      : avgScore >= 50
                      ? "You're getting there. Focus on weak areas."
                      : "More practice needed. Review fundamentals."}
                  </p>
                  <div className="w-full space-y-2">
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Subjects covered</span>
                      <span className="font-medium text-[#0F172A]">{allStats.length}</span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Quizzes completed</span>
                      <span className="font-medium text-[#0F172A]">{totalQuizzes}</span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Study time</span>
                      <span className="font-medium text-[#0F172A]">{studyHours}h</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Performance Trend */}
          {last10.length > 0 && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-[#2563EB]" />
                  Performance Trend (Last {last10.length} Quizzes)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-end gap-2 h-48">
                  {last10.map((attempt, i) => {
                    const pct = parseInt(attempt.percentage || "0")
                    const scoreVal = parseInt(attempt.score || "0")
                    const height = maxBarCount > 0 ? (scoreVal / maxBarCount) * 100 : 0
                    return (
                      <div key={attempt.id} className="flex flex-1 flex-col items-center gap-1">
                        <span className="text-[10px] font-medium text-gray-500">{pct}%</span>
                        <div className="w-full flex items-end" style={{ height: "140px" }}>
                          <div
                            className="w-full rounded-t-md transition-all duration-500 hover:opacity-80"
                            style={{
                              height: `${Math.max(height, 4)}%`,
                              backgroundColor: scoreColor(pct),
                            }}
                            title={`${attempt.quiz?.title || "Quiz"}: ${pct}%`}
                          />
                        </div>
                        <span className="text-[10px] text-gray-400 mt-1 truncate max-w-full">
                          {attempt.completed_at
                            ? new Date(attempt.completed_at).toLocaleDateString("en-US", {
                                month: "short",
                                day: "numeric",
                              })
                            : ""}
                        </span>
                      </div>
                    )
                  })}
                </div>
                <div className="mt-3 flex items-center justify-center gap-4 text-xs text-gray-400">
                  <span className="flex items-center gap-1">
                    <span className="inline-block h-2 w-2 rounded-sm" style={{ backgroundColor: GREEN }} />
                    70%+
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="inline-block h-2 w-2 rounded-sm" style={{ backgroundColor: AMBER }} />
                    50-69%
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="inline-block h-2 w-2 rounded-sm" style={{ backgroundColor: RED }} />
                    &lt;50%
                  </span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Subject Breakdown + Topic Mastery */}
          <div className="grid gap-4 lg:grid-cols-2 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-[#2563EB]" />
                  Subject Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                {allStats.length > 0 ? (
                  <div className="space-y-5">
                    {allStats
                      .slice()
                      .sort((a, b) => b.average_score - a.average_score)
                      .map((stat) => (
                        <div key={stat.subject_id}>
                          <div className="mb-1.5 flex items-center justify-between">
                            <span className="text-sm font-medium text-[#0F172A]">
                              {stat.subject_name}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-400">
                                {stat.quizzes_taken} quizzes
                              </span>
                              <span
                                className="text-sm font-semibold"
                                style={{ color: scoreColor(stat.average_score) }}
                              >
                                {stat.average_score}%
                              </span>
                            </div>
                          </div>
                          <div className="relative h-3 w-full overflow-hidden rounded-full bg-gray-100">
                            <div
                              className="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
                              style={{
                                width: `${stat.average_score}%`,
                                backgroundColor: scoreColor(stat.average_score),
                              }}
                            />
                          </div>
                          <div className="mt-1 flex gap-3 text-[11px] text-gray-400">
                            <span>{stat.lessons_completed} lessons</span>
                            <span>{Math.round(stat.total_study_time_minutes / 60)}h studied</span>
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">
                    Start taking quizzes to see your subject breakdown.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" style={{ color: TEAL }} />
                  Topic Mastery
                </CardTitle>
              </CardHeader>
              <CardContent>
                {allStats.length > 0 ? (
                  <div className="space-y-4">
                    {[
                      {
                        label: "Mastered",
                        filter: (s: (typeof allStats)[0]) => s.average_score >= 80,
                        color: GREEN,
                        icon: <Trophy className="h-4 w-4" />,
                        desc: "Strong understanding",
                      },
                      {
                        label: "Proficient",
                        filter: (s: (typeof allStats)[0]) => s.average_score >= 70 && s.average_score < 80,
                        color: BLUE,
                        icon: <CheckCircle2 className="h-4 w-4" />,
                        desc: "Good grasp",
                      },
                      {
                        label: "Learning",
                        filter: (s: (typeof allStats)[0]) => s.average_score >= 50 && s.average_score < 70,
                        color: AMBER,
                        icon: <Target className="h-4 w-4" />,
                        desc: "Needs more practice",
                      },
                      {
                        label: "Needs Work",
                        filter: (s: (typeof allStats)[0]) => s.average_score < 50,
                        color: RED,
                        icon: <AlertTriangle className="h-4 w-4" />,
                        desc: "Focus required",
                      },
                    ].map((level) => {
                      const items = allStats.filter(level.filter)
                      if (items.length === 0) return null
                      return (
                        <div
                          key={level.label}
                          className="rounded-lg border p-3"
                          style={{ borderColor: `${level.color}30` }}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <div style={{ color: level.color }}>{level.icon}</div>
                            <span className="text-sm font-semibold text-[#0F172A]">
                              {level.label}
                            </span>
                            <Badge variant="secondary" className="ml-auto text-[10px]">
                              {items.length}
                            </Badge>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {items.map((s) => (
                              <span
                                key={s.subject_id}
                                className="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium"
                                style={{
                                  backgroundColor: `${level.color}12`,
                                  color: level.color,
                                }}
                              >
                                {s.subject_name}
                                <span className="ml-1 text-gray-400">{s.average_score}%</span>
                              </span>
                            ))}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">
                    Complete lessons and quizzes to track topic mastery.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Weekly Activity + Weak Areas */}
          <div className="grid gap-4 lg:grid-cols-2 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-[#F59E0B]" />
                  Weekly Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-7 gap-2">
                  {weeklyActivity.map((day) => {
                    const intensity = day.count === 0 ? 0 : day.count <= 2 ? 1 : day.count <= 4 ? 2 : 3
                    const bgColors = ["#E5E7EB", "#BBF7D0", "#22C55E", "#15803D"]
                    const textColors = ["#9CA3AF", "#166534", "#166534", "#fff"]
                    return (
                      <div key={day.label} className="flex flex-col items-center gap-1.5">
                        <div
                          className="h-14 w-full rounded-lg transition-all"
                          style={{ backgroundColor: bgColors[intensity] }}
                          title={`${day.label}: ${day.count} quiz${day.count !== 1 ? "zes" : ""}`}
                        />
                        <span
                          className="text-xs font-medium"
                          style={{ color: textColors[intensity] }}
                        >
                          {day.label}
                        </span>
                      </div>
                    )
                  })}
                </div>
                <div className="mt-4 flex items-center justify-between text-xs text-gray-400">
                  <span>Less active</span>
                  <div className="flex items-center gap-1">
                    <div className="h-3 w-3 rounded-sm bg-gray-200" />
                    <div className="h-3 w-3 rounded-sm bg-[#BBF7D0]" />
                    <div className="h-3 w-3 rounded-sm bg-[#22C55E]" />
                    <div className="h-3 w-3 rounded-sm bg-[#15803D]" />
                  </div>
                  <span>Most active</span>
                </div>
                <div className="mt-3 rounded-lg bg-gray-50 p-3 text-center">
                  <p className="text-sm font-medium text-[#0F172A]">
                    {weeklyActivity.filter((d) => d.count > 0).length} of 7 active days
                  </p>
                  <p className="text-xs text-gray-400">
                    {weeklyActivity.reduce((s, d) => s + d.count, 0)} quizzes this week
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" style={{ color: RED }} />
                  Weak Areas & Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                {weakSubjects.length > 0 ? (
                  <div className="space-y-3">
                    {weakSubjects.map((s) => {
                      const urgency = s.average_score < 30 ? "high" : s.average_score < 50 ? "medium" : "low"
                      const urgencyColor = urgency === "high" ? RED : urgency === "medium" ? AMBER : BLUE
                      const suggestion =
                        s.average_score < 30
                          ? "Review lessons and retake basic quizzes"
                          : s.average_score < 50
                          ? "Focus on foundational topics and practice more"
                          : "Take targeted quizzes to strengthen this area"
                      return (
                        <div
                          key={s.subject_id}
                          className="rounded-lg border border-gray-100 p-3"
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-[#0F172A]">
                                {s.subject_name}
                              </span>
                              <Badge
                                variant={
                                  urgency === "high"
                                    ? "destructive"
                                    : urgency === "medium"
                                    ? "accent"
                                    : "default"
                                }
                                className="text-[10px]"
                              >
                                {urgency} priority
                              </Badge>
                            </div>
                            <span
                              className="text-sm font-semibold"
                              style={{ color: urgencyColor }}
                            >
                              {s.average_score}%
                            </span>
                          </div>
                          <Progress
                            value={s.average_score}
                            className="h-1.5 mt-1.5 mb-2"
                            indicatorClassName={`bg-${urgency === "high" ? "[#EF4444]" : urgency === "medium" ? "[#F59E0B]" : "[#2563EB]"}`}
                          />
                          <div className="flex items-center gap-1.5 text-xs text-gray-500">
                            <ArrowUpRight className="h-3 w-3" style={{ color: urgencyColor }} />
                            <span>{suggestion}</span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : weakSubjects.length === 0 && allStats.length > 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <div className="mb-3 rounded-full bg-[#22C55E]/10 p-3">
                      <Trophy className="h-8 w-8 text-[#22C55E]" />
                    </div>
                    <p className="text-sm font-medium text-[#0F172A]">Looking Great!</p>
                    <p className="text-xs text-gray-400 mt-1">
                      No weak subjects detected. Keep up the excellent work!
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">
                    Complete more quizzes to get weak area recommendations.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Strong Subjects */}
          {strongSubjects.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-[#22C55E]" />
                  Strong Subjects
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {strongSubjects.map((s) => (
                    <div
                      key={s.subject_id}
                      className="flex items-center gap-3 rounded-lg border border-green-100 bg-green-50/50 p-3"
                    >
                      <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-[#22C55E]/10">
                        <TrendingUp className="h-5 w-5 text-[#22C55E]" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[#0F172A]">{s.subject_name}</p>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-[#22C55E]">
                            {s.average_score}%
                          </span>
                          <span className="text-[11px] text-gray-400">
                            {s.quizzes_taken} quizzes
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}
