"use client"

import { useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { subjectService } from "@/services/subjects"
import { lessonService } from "@/services/lessons"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { BookOpen, BookText, Clock, ChevronRight } from "lucide-react"
import Link from "next/link"

export default function SubjectDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated } = useAuthStore()
  const slug = params.slug as string

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: subject } = useQuery({
    queryKey: ["subject", slug],
    queryFn: () => subjectService.getBySlug(slug),
    enabled: isAuthenticated,
  })

  const { data: lessons } = useQuery({
    queryKey: ["lessons", slug],
    queryFn: () => lessonService.getBySubject(slug),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8">
            <div className="flex items-center gap-3">
              <div
                className="flex h-14 w-14 items-center justify-center rounded-xl"
                style={{ backgroundColor: `${subject?.color || "#2563EB"}15` }}
              >
                <BookOpen className="h-7 w-7" style={{ color: subject?.color || "#2563EB" }} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-[#0F172A]">
                  {subject?.name || "Loading..."}
                </h1>
                <p className="text-sm text-gray-500">{subject?.description}</p>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <div className="mb-4 flex items-center gap-2">
              <BookText className="h-5 w-5 text-[#2563EB]" />
              <h2 className="text-lg font-semibold text-[#0F172A]">Scheme of Work</h2>
              <span className="rounded-full bg-[#2563EB]/10 px-2.5 py-0.5 text-xs font-medium text-[#2563EB]">
                {lessons?.lessons?.length || 0} topics
              </span>
            </div>
            <p className="mb-6 text-sm text-gray-500">
              Complete {subject?.name || ""} syllabus covering WAEC, NECO, GCE and JAMB standards.
              Click any topic to start learning.
            </p>
            <div className="space-y-2">
              {lessons?.lessons?.map((lesson, i) => (
                <Link
                  key={lesson.id}
                  href={`/subjects/${slug}/lessons/${lesson.slug}`}
                >
                  <Card className="cursor-pointer transition-all hover:shadow-md hover:border-[#2563EB]/30 group">
                    <CardContent className="flex items-center justify-between p-4">
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#2563EB]/10 text-sm font-bold text-[#2563EB]">
                          {i + 1}
                        </div>
                        <div>
                          <p className="font-medium text-[#0F172A] group-hover:text-[#2563EB] transition-colors">
                            {lesson.title}
                          </p>
                          {lesson.summary && (
                            <p className="mt-0.5 text-xs text-gray-500 line-clamp-1">
                              {lesson.summary}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {lesson.estimated_minutes && (
                          <span className="flex items-center gap-1 text-xs text-gray-400">
                            <Clock className="h-3 w-3" />
                            {lesson.estimated_minutes} min
                          </span>
                        )}
                        <ChevronRight className="h-4 w-4 text-gray-300 group-hover:text-[#2563EB] transition-colors" />
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
              {(!lessons?.lessons || lessons.lessons.length === 0) && (
                <div className="rounded-lg border border-dashed border-gray-200 p-12 text-center">
                  <BookText className="mx-auto h-8 w-8 text-gray-300" />
                  <p className="mt-3 text-sm text-gray-500">No topics available yet.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
