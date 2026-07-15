"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { studyPlanService, type StudyPlan, type StudyPlanDay } from "@/services/studyPlans"
import { subjectService } from "@/services/subjects"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { Sparkles, Calendar, CheckCircle2, Circle, Clock, BookOpen, Plus, ChevronLeft, ChevronRight, Loader2 } from "lucide-react"
import { toast } from "sonner"

export default function StudyPlannerPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [planTitle, setPlanTitle] = useState("")
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([])
  const [durationDays, setDurationDays] = useState("14")
  const [useAI, setUseAI] = useState(false)
  const [creating, setCreating] = useState(false)
  const [weekOffset, setWeekOffset] = useState(0)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: plans, refetch } = useQuery({
    queryKey: ["study-plans"],
    queryFn: () => studyPlanService.getAll(),
    enabled: isAuthenticated,
  })

  const { data: todayTasks } = useQuery({
    queryKey: ["study-plans", "today"],
    queryFn: () => studyPlanService.getToday(),
    enabled: isAuthenticated,
  })

  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => subjectService.getAll(),
    enabled: isAuthenticated,
  })

  const subjects = subjectsData?.subjects ?? []
  const planList = Array.isArray(plans) ? (plans as StudyPlan[]) : []
  const today = todayTasks as { tasks: StudyPlanDay[] } | undefined

  const weekStart = new Date()
  weekStart.setDate(weekStart.getDate() + weekOffset * 7 - weekStart.getDay() + 1)

  const { data: calendarData } = useQuery({
    queryKey: ["study-plans", "calendar", weekStart.toISOString()],
    queryFn: () => studyPlanService.getCalendar(weekStart.toISOString().split("T")[0]),
    enabled: isAuthenticated,
  })

  const calendarDays = (calendarData as { days: StudyPlanDay[] } | undefined)?.days ?? []

  const toggleSubject = (name: string) => {
    setSelectedSubjects((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    )
  }

  const markComplete = useMutation({
    mutationFn: (dayId: string) => studyPlanService.markDayCompleted(dayId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["study-plans"] })
      toast.success("Day marked as completed!")
    },
    onError: (err: Error) => toast.error(err.message || "Failed to update"),
  })

  const handleCreatePlan = async () => {
    if (!planTitle.trim() || selectedSubjects.length === 0) {
      toast.error("Please enter a title and select at least one subject")
      return
    }
    setCreating(true)
    try {
      await studyPlanService.create({
        title: planTitle.trim(),
        plan_type: "custom",
        start_date: new Date().toISOString().split("T")[0],
        end_date: new Date(Date.now() + (parseInt(durationDays) || 14) * 86400000).toISOString().split("T")[0],
        subjects: selectedSubjects,
        use_ai: useAI,
      })
      toast.success("Study plan created!")
      setShowCreate(false)
      setPlanTitle("")
      setSelectedSubjects([])
      refetch()
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to create plan")
    } finally {
      setCreating(false)
    }
  }

  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStart)
    d.setDate(d.getDate() + i)
    return d
  })

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#0F172A]">Study Planner</h1>
              <p className="mt-1 text-sm text-gray-600">Plan, track, and optimize your exam preparation</p>
            </div>
            <Button onClick={() => setShowCreate(!showCreate)} className="gap-2">
              <Plus className="h-4 w-4" />
              {showCreate ? "Cancel" : "New Plan"}
            </Button>
          </div>

          {showCreate && (
            <Card className="mb-6 border-[#2563EB]/20">
              <CardContent className="p-6">
                <h3 className="mb-4 font-semibold text-[#0F172A]">Create Study Plan</h3>
                <div className="space-y-3">
                  <Input value={planTitle} onChange={(e) => setPlanTitle(e.target.value)} placeholder="Plan title (e.g., JAMB Prep)" />
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Duration (days)</label>
                      <Input type="number" value={durationDays} onChange={(e) => setDurationDays(e.target.value)} min={1} max={365} />
                    </div>
                    <div className="flex items-end pb-2">
                      <label className="flex items-center gap-2 text-sm">
                        <input type="checkbox" checked={useAI} onChange={(e) => setUseAI(e.target.checked)} className="rounded" />
                        Generate with AI
                      </label>
                    </div>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">Subjects</label>
                    <div className="flex flex-wrap gap-2">
                      {subjects.map((s) => (
                        <button
                          key={s.id}
                          onClick={() => toggleSubject(s.name)}
                          className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                            selectedSubjects.includes(s.name)
                              ? "bg-[#2563EB] text-white"
                              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                          }`}
                        >
                          {s.name}
                        </button>
                      ))}
                    </div>
                  </div>
                  <Button onClick={handleCreatePlan} disabled={creating || !planTitle.trim() || selectedSubjects.length === 0} className="w-full">
                    {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                    Create Plan
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {today?.tasks && today.tasks.length > 0 && (
            <Card className="mb-6 border-[#14B8A6]/20 bg-[#14B8A6]/5">
              <CardContent className="p-5">
                <div className="mb-3 flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-[#14B8A6]" />
                  <h3 className="font-semibold text-[#0F172A]">Today&apos;s Tasks</h3>
                </div>
                <div className="space-y-2">
                  {today.tasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between rounded-lg bg-white p-3">
                      <div className="flex items-center gap-3">
                        <button onClick={() => markComplete.mutate(task.id)}>
                          {task.is_completed ? (
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                          ) : (
                            <Circle className="h-5 w-5 text-gray-300" />
                          )}
                        </button>
                        <div>
                          <p className={`text-sm font-medium ${task.is_completed ? "text-gray-400 line-through" : "text-[#0F172A]"}`}>
                            {task.subjects?.join(", ")} — {task.topics?.join(", ")}
                          </p>
                          {task.duration_minutes && (
                            <p className="flex items-center gap-1 text-xs text-gray-400">
                              <Clock className="h-3 w-3" /> {task.duration_minutes} min
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Weekly Overview</span>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="icon" onClick={() => setWeekOffset(weekOffset - 1)}>
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm font-normal text-gray-500">
                    {weekDays[0].toLocaleDateString("en-NG", { month: "short", day: "numeric" })} — {weekDays[6].toLocaleDateString("en-NG", { month: "short", day: "numeric" })}
                  </span>
                  <Button variant="ghost" size="icon" onClick={() => setWeekOffset(weekOffset + 1)}>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-2">
                {weekDays.map((day) => {
                  const dateStr = day.toISOString().split("T")[0]
                  const dayTasks = calendarDays.filter((d) => d.date.startsWith(dateStr))
                  const isToday = new Date().toISOString().split("T")[0] === dateStr
                  const completed = dayTasks.filter((d) => d.is_completed).length
                  return (
                    <div key={dateStr} className={`rounded-lg border p-2 ${isToday ? "border-[#2563EB] bg-[#2563EB]/5" : "border-gray-100"}`}>
                      <p className={`text-center text-xs font-medium ${isToday ? "text-[#2563EB]" : "text-gray-500"}`}>
                        {day.toLocaleDateString("en-NG", { weekday: "short" })}
                      </p>
                      <p className={`text-center text-lg font-bold ${isToday ? "text-[#2563EB]" : "text-[#0F172A]"}`}>
                        {day.getDate()}
                      </p>
                      {dayTasks.length > 0 && (
                        <div className="mt-1 text-center">
                          <Badge variant={completed === dayTasks.length ? "success" : "secondary"} className="text-[10px]">
                            {completed}/{dayTasks.length}
                          </Badge>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          <div className="space-y-3">
            {planList.map((plan) => {
              const totalDays = plan.days?.length ?? 0
              const completedDays = plan.days?.filter((d) => d.is_completed).length ?? 0
              return (
                <Card key={plan.id}>
                  <CardContent className="flex items-center justify-between p-5">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#F59E0B]/10">
                        <BookOpen className="h-6 w-6 text-[#F59E0B]" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-[#0F172A]">{plan.title}</h3>
                        <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                          <Badge variant="secondary">{plan.plan_type}</Badge>
                          <span>{totalDays} days</span>
                          <span>{completedDays} completed</span>
                        </div>
                        <Progress value={totalDays > 0 ? (completedDays / totalDays) * 100 : 0} className="mt-2 w-48" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
            {planList.length === 0 && !showCreate && (
              <Card>
                <CardContent className="p-12 text-center">
                  <Calendar className="mx-auto mb-4 h-10 w-10 text-gray-300" />
                  <h3 className="mb-2 text-lg font-semibold text-[#0F172A]">No study plans yet</h3>
                  <p className="mb-6 text-sm text-gray-500">Create a structured study plan with AI recommendations for exam preparation.</p>
                  <Button onClick={() => setShowCreate(true)} className="gap-2">
                    <Sparkles className="h-4 w-4" />
                    Create your first plan
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
