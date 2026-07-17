"use client"

import { useEffect, useState, useMemo } from "react"
import { useRouter } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { studyPlanService, type StudyPlan, type StudyPlanDay } from "@/services/studyPlans"
import { subjectService, type Topic } from "@/services/subjects"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import {
  Sparkles, Calendar, CheckCircle2, Circle, Clock, BookOpen,
  Plus, ChevronLeft, ChevronRight, Loader2, Trash2, ChevronDown,
  ChevronUp, ArrowLeft, Coffee,
} from "lucide-react"
import { toast } from "sonner"

export default function StudyPlannerPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [planTitle, setPlanTitle] = useState("")
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([])
  const [durationDays, setDurationDays] = useState("14")
  const [hoursPerDay, setHoursPerDay] = useState("2")
  const [creating, setCreating] = useState(false)
  const [weekOffset, setWeekOffset] = useState(0)
  const [selectedTopics, setSelectedTopics] = useState<Record<string, string[]>>({})
  const [expandedSubject, setExpandedSubject] = useState<string | null>(null)
  const [viewingPlan, setViewingPlan] = useState<StudyPlan | null>(null)

  const weekStartStr = useMemo(() => {
    const d = new Date()
    d.setDate(d.getDate() + weekOffset * 7 - d.getDay() + 1)
    return d.toISOString().split("T")[0]
  }, [weekOffset])

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: plans } = useQuery({
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
  const planList = Array.isArray(plans)
    ? (plans as StudyPlan[])
    : ((plans as unknown as { plans?: StudyPlan[] })?.plans ?? [])
  const today = todayTasks as { tasks: StudyPlanDay[] } | undefined

  const { data: calendarData } = useQuery({
    queryKey: ["study-plans", "calendar", weekStartStr],
    queryFn: () => studyPlanService.getCalendar(weekStartStr),
    enabled: isAuthenticated,
  })

  const calendarDays = (calendarData as { days?: StudyPlanDay[] } | undefined)?.days ?? []

  const { data: topicsData, isLoading: topicsLoading } = useQuery({
    queryKey: ["subject-topics", expandedSubject],
    queryFn: () => {
      const subj = subjects.find((s) => s.name === expandedSubject)
      return subj ? subjectService.getTopicsBySlug(subj.slug) : { topics: [] as Topic[] }
    },
    enabled: !!expandedSubject,
  })

  const availableTopics = (topicsData as { topics?: Topic[] } | undefined)?.topics ?? []

  const toggleSubject = (name: string) => {
    setSelectedSubjects((prev) => {
      const next = prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
      if (!next.includes(name)) {
        setSelectedTopics((prev) => {
          const copy = { ...prev }
          delete copy[name]
          return copy
        })
        if (expandedSubject === name) setExpandedSubject(null)
      }
      return next
    })
  }

  const toggleTopic = (subject: string, topicTitle: string) => {
    setSelectedTopics((prev) => {
      const current = prev[subject] || []
      const next = current.includes(topicTitle)
        ? current.filter((t) => t !== topicTitle)
        : [...current, topicTitle]
      return { ...prev, [subject]: next }
    })
  }

  const markComplete = useMutation({
    mutationFn: (dayId: string) => studyPlanService.markDayCompleted(dayId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["study-plans"] })
      queryClient.invalidateQueries({ queryKey: ["study-plans", "today"] })
      queryClient.invalidateQueries({ queryKey: ["study-plans", "calendar"] })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success("Day marked as completed!")
    },
    onError: (err: Error) => toast.error(err.message || "Failed to update"),
  })

  const deletePlan = useMutation({
    mutationFn: (planId: string) => studyPlanService.deletePlan(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["study-plans"] })
      queryClient.invalidateQueries({ queryKey: ["study-plans", "today"] })
      queryClient.invalidateQueries({ queryKey: ["study-plans", "calendar"] })
      toast.success("Plan deleted")
      if (viewingPlan) setViewingPlan(null)
    },
    onError: (err: Error) => toast.error(err.message || "Failed to delete plan"),
  })

  const handleCreatePlan = async () => {
    if (!planTitle.trim() || selectedSubjects.length === 0) {
      toast.error("Please enter a title and select at least one subject")
      return
    }
    const hours = parseFloat(hoursPerDay)
    if (isNaN(hours) || hours < 0.5 || hours > 12) {
      toast.error("Hours per day must be between 0.5 and 12")
      return
    }

    const topicsForPlan: Record<string, string[]> = {}
    for (const subj of selectedSubjects) {
      const picked = selectedTopics[subj]
      if (picked && picked.length > 0) {
        topicsForPlan[subj] = picked
      }
    }

    setCreating(true)
    try {
      await studyPlanService.create({
        title: planTitle.trim(),
        plan_type: "custom",
        start_date: new Date().toISOString().split("T")[0],
        end_date: new Date(Date.now() + (parseInt(durationDays) || 14) * 86400000).toISOString().split("T")[0],
        subjects: selectedSubjects,
        hours_per_day: hours,
        subject_topics: Object.keys(topicsForPlan).length > 0 ? topicsForPlan : undefined,
      })
      toast.success("Study plan created!")
      setShowCreate(false)
      resetForm()
      queryClient.invalidateQueries({ queryKey: ["study-plans"] })
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to create plan")
    } finally {
      setCreating(false)
    }
  }

  const resetForm = () => {
    setPlanTitle("")
    setSelectedSubjects([])
    setSelectedTopics({})
    setDurationDays("14")
    setHoursPerDay("2")
    setExpandedSubject(null)
  }

  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStartStr + "T00:00:00")
    d.setDate(d.getDate() + i)
    return d
  })

  if (!isAuthenticated) return null

  if (viewingPlan) {
    return (
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
          <div className="mx-auto max-w-4xl">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Button variant="ghost" size="icon" onClick={() => setViewingPlan(null)}>
                  <ArrowLeft className="h-5 w-5" />
                </Button>
                <div>
                  <h1 className="text-2xl font-bold text-[#0F172A]">{viewingPlan.title}</h1>
                  <p className="mt-1 text-sm text-gray-600">
                    {viewingPlan.start_date} â€” {viewingPlan.end_date} Â· {viewingPlan.days?.length ?? 0} days
                  </p>
                </div>
              </div>
              <Button
                variant="outline"
                className="gap-2 text-red-600 hover:text-red-700"
                onClick={() => {
                  if (confirm("Delete this study plan? This cannot be undone.")) {
                    deletePlan.mutate(viewingPlan.id)
                  }
                }}
              >
                <Trash2 className="h-4 w-4" />
                Delete Plan
              </Button>
            </div>

            {viewingPlan.days && viewingPlan.days.length > 0 && (
              <div className="space-y-3">
                {viewingPlan.days.map((day) => {
                  const dateObj = new Date(day.date + "T00:00:00")
                  const dayName = dateObj.toLocaleDateString("en-NG", { weekday: "long", month: "short", day: "numeric" })
                  const hasBreak = day.topics?.some((t) => t.startsWith("---")) ?? false
                  const focusTip = day.notes?.replace("Focus tip: ", "") ?? null
                  return (
                    <Card key={day.id} className={`transition-shadow ${day.is_completed ? "opacity-60" : "hover:shadow-md"}`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <button onClick={() => markComplete.mutate(day.id)}>
                                {day.is_completed ? (
                                  <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />
                                ) : (
                                  <Circle className="h-5 w-5 text-gray-300 shrink-0" />
                                )}
                              </button>
                              <span className={`text-sm font-semibold ${day.is_completed ? "text-gray-400 line-through" : "text-[#0F172A]"}`}>
                                {dayName}
                              </span>
                              <Badge variant="secondary" className="text-xs">
                                {day.duration_minutes} min
                              </Badge>
                            </div>
                            <div className="ml-8 space-y-1">
                              {day.topics?.map((topic, i) => {
                                if (topic.startsWith("---")) {
                                  return (
                                    <div key={i} className="flex items-center gap-1.5 py-0.5">
                                      <Coffee className="h-3 w-3 text-orange-400" />
                                      <span className="text-xs text-orange-500 font-medium">{topic.replace("--- ", "").replace(" ---", "")}</span>
                                    </div>
                                  )
                                }
                                return (
                                  <p key={i} className={`text-sm ${day.is_completed ? "text-gray-400" : "text-gray-700"}`}>
                                    {topic}
                                  </p>
                                )
                              })}
                              {focusTip && (
                                <p className="text-xs text-[#2563EB] italic mt-2">{focusTip}</p>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            )}
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#0F172A]">Study Planner</h1>
              <p className="mt-1 text-sm text-gray-600">Plan, track, and optimize your exam preparation</p>
            </div>
            <Button onClick={() => { setShowCreate(!showCreate); if (showCreate) resetForm() }} className="gap-2">
              <Plus className="h-4 w-4" />
              {showCreate ? "Cancel" : "New Plan"}
            </Button>
          </div>

          {showCreate && (
            <Card className="mb-6 border-[#2563EB]/20">
              <CardContent className="p-6">
                <h3 className="mb-4 font-semibold text-[#0F172A]">Create Study Plan</h3>
                <div className="space-y-4">
                  <Input value={planTitle} onChange={(e) => setPlanTitle(e.target.value)} placeholder="Plan title (e.g., JAMB Prep)" />

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Duration (days)</label>
                      <Input type="number" value={durationDays} onChange={(e) => setDurationDays(e.target.value)} min={1} max={365} />
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Hours per day</label>
                      <Input type="number" value={hoursPerDay} onChange={(e) => setHoursPerDay(e.target.value)} min={0.5} max={12} step={0.5} />
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

                  {selectedSubjects.length > 0 && (
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Select topics per subject (optional â€” we&apos;ll pick the best ones if you skip this)
                      </label>
                      {selectedSubjects.map((subj) => (
                        <div key={subj} className="rounded-lg border border-gray-100 bg-gray-50/50">
                          <button
                            className="flex w-full items-center justify-between px-3 py-2 text-sm font-medium text-[#0F172A]"
                            onClick={() => setExpandedSubject(expandedSubject === subj ? null : subj)}
                          >
                            <span className="flex items-center gap-2">
                              {subj}
                              {selectedTopics[subj] && selectedTopics[subj].length > 0 && (
                                <Badge variant="secondary" className="text-xs">{selectedTopics[subj].length} selected</Badge>
                              )}
                            </span>
                            {expandedSubject === subj ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                          </button>
                          {expandedSubject === subj && (
                            <div className="border-t border-gray-100 px-3 py-2">
                              {topicsLoading ? (
                                <p className="text-xs text-gray-400">Loading topics...</p>
                              ) : availableTopics.length === 0 ? (
                                <p className="text-xs text-gray-400">No topics available for this subject yet.</p>
                              ) : (
                                <div className="flex flex-wrap gap-1.5">
                                  {availableTopics.map((t) => {
                                    const isSelected = selectedTopics[subj]?.includes(t.title) ?? false
                                    return (
                                      <button
                                        key={t.id}
                                        onClick={() => toggleTopic(subj, t.title)}
                                        className={`rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${
                                          isSelected
                                            ? "bg-[#14B8A6] text-white"
                                            : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-100"
                                        }`}
                                      >
                                        {t.title}
                                      </button>
                                    )
                                  })}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

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
                            {task.subjects?.join(", ")}
                          </p>
                          {task.topics && task.topics.length > 0 && (
                            <div className="mt-0.5">
                              {task.topics.filter(t => !t.startsWith("---")).slice(0, 3).map((t, i) => (
                                <p key={i} className="text-xs text-gray-500">{t}</p>
                              ))}
                              {task.topics.filter(t => !t.startsWith("---")).length > 3 && (
                                <p className="text-xs text-gray-400">+{task.topics.filter(t => !t.startsWith("---")).length - 3} more</p>
                              )}
                            </div>
                          )}
                          {task.duration_minutes && (
                            <p className="flex items-center gap-1 text-xs text-gray-400 mt-1">
                              <Clock className="h-3 w-3" /> {task.duration_minutes} min total
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
                    {weekDays[0].toLocaleDateString("en-NG", { month: "short", day: "numeric" })} â€” {weekDays[6].toLocaleDateString("en-NG", { month: "short", day: "numeric" })}
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
                  const dayTasks = calendarDays.filter((d) => d.date?.startsWith(dateStr))
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
              const allSubjects = [...new Set(plan.days?.flatMap((d) => d.subjects ?? []) ?? [])]
              return (
                <Card key={plan.id} className="transition-shadow hover:shadow-md cursor-pointer" onClick={() => setViewingPlan(plan)}>
                  <CardContent className="flex items-center justify-between p-5">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#F59E0B]/10">
                        <BookOpen className="h-6 w-6 text-[#F59E0B]" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-[#0F172A]">{plan.title}</h3>
                        <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                          <Badge variant="secondary">{plan.plan_type}</Badge>
                          <span>{totalDays} days</span>
                          <span>{completedDays} completed</span>
                          {allSubjects.length > 0 && (
                            <span className="text-gray-400">Â· {allSubjects.join(", ")}</span>
                          )}
                        </div>
                        <Progress value={totalDays > 0 ? (completedDays / totalDays) * 100 : 0} className="mt-2 w-48" />
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="shrink-0"
                      onClick={(e) => {
                        e.stopPropagation()
                        if (confirm("Delete this study plan?")) {
                          deletePlan.mutate(plan.id)
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4 text-gray-400 hover:text-red-500" />
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
            {planList.length === 0 && !showCreate && (
              <Card>
                <CardContent className="p-12 text-center">
                  <Calendar className="mx-auto mb-4 h-10 w-10 text-gray-300" />
                  <h3 className="mb-2 text-lg font-semibold text-[#0F172A]">No study plans yet</h3>
                  <p className="mb-6 text-sm text-gray-500">Create a structured study plan with timed sessions and focus tips.</p>
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
