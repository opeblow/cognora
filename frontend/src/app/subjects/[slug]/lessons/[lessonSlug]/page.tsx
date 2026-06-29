"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { lessonService } from "@/services/lessons"
import { subjectService } from "@/services/subjects"
import { Sidebar } from "@/components/layout/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { BookOpen, ChevronLeft, ChevronRight, Clock } from "lucide-react"
import Link from "next/link"

export default function LessonDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated } = useAuthStore()
  const slug = params.slug as string
  const lessonSlug = params.lessonSlug as string
  const [activeTopic, setActiveTopic] = useState<number>(0)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: subject } = useQuery({
    queryKey: ["subject", slug],
    queryFn: () => subjectService.getBySlug(slug),
    enabled: isAuthenticated,
  })

  const { data: lesson, isLoading } = useQuery({
    queryKey: ["lesson", slug, lessonSlug],
    queryFn: () => lessonService.getBySlug(slug, lessonSlug),
    enabled: isAuthenticated,
  })

  const { data: allLessons } = useQuery({
    queryKey: ["lessons", slug],
    queryFn: () => lessonService.getBySubject(slug),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) return null

  const topics = lesson?.topics || []
  const currentTopic = topics[activeTopic]
  const currentIndex = allLessons?.lessons?.findIndex(l => l.slug === lessonSlug) ?? -1
  const prevLesson = currentIndex > 0 ? allLessons?.lessons?.[currentIndex - 1] : null
  const nextLesson = currentIndex < (allLessons?.lessons?.length ?? 0) - 1 ? allLessons?.lessons?.[currentIndex + 1] : null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-6">
            <Link
              href={`/subjects/${slug}`}
              className="mb-4 inline-flex items-center gap-1 text-sm text-[#2563EB] hover:underline"
            >
              <ChevronLeft className="h-4 w-4" />
              Back to {subject?.name || "Subject"}
            </Link>

            <div className="mt-2 flex items-center gap-3">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-lg"
                style={{ backgroundColor: `${subject?.color || "#2563EB"}15` }}
              >
                <BookOpen className="h-5 w-5" style={{ color: subject?.color || "#2563EB" }} />
              </div>
              <div>
                <h1 className="text-xl font-bold text-[#0F172A]">{lesson?.title}</h1>
                {lesson?.estimated_minutes && (
                  <span className="flex items-center gap-1 text-xs text-gray-400">
                    <Clock className="h-3 w-3" />
                    {lesson.estimated_minutes} min
                  </span>
                )}
              </div>
            </div>
          </div>

          {topics.length > 0 && (
            <div className="mb-6 flex flex-wrap gap-2">
              {topics.map((topic, i) => (
                <button
                  key={topic.id}
                  onClick={() => setActiveTopic(i)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    activeTopic === i
                      ? "bg-[#2563EB] text-white"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {topic.title}
                </button>
              ))}
            </div>
          )}

          <Card className="mb-6 overflow-hidden border-0 shadow-lg">
            <CardContent className="p-0">
              {currentTopic?.content ? (
                <div className="prose prose-sm max-w-none p-8 [&_h3]:mt-6 [&_h3]:mb-3 [&_h3]:text-lg [&_h3]:font-bold [&_h3]:text-[#0F172A] [&_h4]:mt-4 [&_h4]:mb-2 [&_h4]:text-base [&_h4]:font-semibold [&_h4]:text-[#0F172A] [&_p]:mb-3 [&_p]:leading-relaxed [&_p]:text-gray-700 [&_ul]:mb-4 [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:space-y-1 [&_ol]:mb-4 [&_ol]:list-decimal [&_ol]:pl-6 [&_ol]:space-y-2 [&_li]:text-gray-700 [&_strong]:font-semibold [&_strong]:text-[#0F172A] [&_em]:italic [&_code]:rounded [&_code]:bg-gray-100 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:text-sm [&_code]:text-[#2563EB] [&_table]:mb-4 [&_table]:w-full [&_table]:border-collapse [&_th]:border [&_th]:border-gray-200 [&_th]:bg-gray-50 [&_th]:p-2 [&_th]:text-left [&_th]:text-sm [&_th]:font-semibold [&_td]:border [&_td]:border-gray-200 [&_td]:p-2 [&_td]:text-sm">
                  <div dangerouslySetInnerHTML={{ __html: currentTopic.content }} />
                </div>
              ) : lesson?.content ? (
                <div className="prose prose-sm max-w-none p-8 prose-headings:text-[#0F172A] prose-p:text-gray-700 prose-li:text-gray-700">
                  <div dangerouslySetInnerHTML={{ __html: lesson.content }} />
                </div>
              ) : (
                <div className="p-8 text-center text-gray-500">
                  {isLoading ? "Loading..." : "No content available yet."}
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex items-center justify-between gap-4">
            <div>
              {prevLesson && (
                <Link href={`/subjects/${slug}/lessons/${prevLesson.slug}`}>
                  <Button variant="outline" className="gap-1">
                    <ChevronLeft className="h-4 w-4" />
                    {prevLesson.title}
                  </Button>
                </Link>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">
                {currentTopic ? `Topic ${activeTopic + 1} of ${topics.length}` : ""}
              </span>
            </div>
            <div>
              {topics.length > 0 && activeTopic < topics.length - 1 && (
                <Button onClick={() => setActiveTopic(activeTopic + 1)} className="gap-1">
                  Next: {topics[activeTopic + 1].title}
                  <ChevronRight className="h-4 w-4" />
                </Button>
              )}
              {nextLesson && activeTopic >= topics.length - 1 && (
                <Link href={`/subjects/${slug}/lessons/${nextLesson.slug}`}>
                  <Button className="gap-1">
                    Next: {nextLesson.title}
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
