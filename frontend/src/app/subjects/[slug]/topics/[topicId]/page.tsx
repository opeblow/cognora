"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { lessonService } from "@/services/lessons"
import { Sidebar } from "@/components/layout/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { BookOpen, ChevronLeft, Loader2, Flag } from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"
import { issuesService } from "@/services/issues"

export default function TopicDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated } = useAuthStore()
  const slug = params.slug as string
  const topicId = params.topicId as string

  const [reportingIssue, setReportingIssue] = useState<{ sectionIndex?: number } | null>(null)
  const [issueDescription, setIssueDescription] = useState("")
  const [issueSeverity, setIssueSeverity] = useState<string>("inaccurate")

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: topicData, isLoading } = useQuery({
    queryKey: ["topic", slug, topicId],
    queryFn: () => lessonService.getTopic(slug, topicId),
    enabled: isAuthenticated,
    retry: 1,
  })

  const handleReportIssue = async () => {
    if (!issueDescription.trim()) {
      toast.error("Please describe the issue")
      return
    }
    try {
      await issuesService.create({
        content_type: "topic",
        content_id: topicId,
        section_index: reportingIssue?.sectionIndex,
        severity: issueSeverity as "typo" | "inaccurate" | "harmful" | "other",
        description: issueDescription.trim(),
      })
      toast.success("Issue reported.")
      setReportingIssue(null)
      setIssueDescription("")
      setIssueSeverity("inaccurate")
    } catch {
      toast.error("Failed to report issue.")
    }
  }

  if (!isAuthenticated) return null
  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="ml-64 flex-1 p-8">
          <div className="mx-auto max-w-4xl pt-20 text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-[#2563EB]" />
            <p className="mt-4 text-gray-500">Loading topic...</p>
          </div>
        </main>
      </div>
    )
  }

  if (!topicData) {
    return (
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="ml-64 flex-1 p-8">
          <div className="mx-auto max-w-4xl pt-20 text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-50">
              <BookOpen className="h-8 w-8 text-red-400" />
            </div>
            <h3 className="mb-2 text-lg font-semibold text-[#0F172A]">Topic not found</h3>
            <p className="mb-6 text-sm text-gray-500">This topic could not be loaded.</p>
            <Link href={`/subjects/${slug}`}>
              <Button variant="outline" className="gap-2">
                <ChevronLeft className="h-4 w-4" />
                Back to subject
              </Button>
            </Link>
          </div>
        </main>
      </div>
    )
  }

  const topic = topicData

  const sectionClass = "prose prose-sm max-w-none [&_h3]:mt-8 [&_h3]:mb-4 [&_h3]:text-xl [&_h3]:font-bold [&_h3]:text-[#0F172A] [&_h4]:mt-6 [&_h4]:mb-3 [&_h4]:text-lg [&_h4]:font-semibold [&_h4]:text-[#0F172A] [&_p]:mb-3 [&_p]:leading-relaxed [&_p]:text-gray-700 [&_ul]:mb-4 [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:space-y-1 [&_ol]:mb-4 [&_ol]:list-decimal [&_ol]:pl-6 [&_ol]:space-y-2 [&_li]:text-gray-700 [&_strong]:font-semibold [&_strong]:text-[#0F172A] [&_em]:italic [&_code]:rounded [&_code]:bg-gray-100 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:text-sm [&_code]:text-[#2563EB] [&_table]:mb-4 [&_table]:w-full [&_table]:border-collapse [&_th]:border [&_th]:border-gray-200 [&_th]:bg-gray-50 [&_th]:p-2 [&_th]:text-left [&_th]:text-sm [&_th]:font-semibold [&_td]:border [&_td]:border-gray-200 [&_td]:p-2 [&_td]:text-sm [&_pre]:mb-4 [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-gray-50 [&_pre]:p-4 [&_pre]:text-sm [&_pre]:font-mono [&_pre]:leading-relaxed [&_hr]:my-8 [&_hr]:border-gray-200"

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
              Back to {topic.subject?.name || "subject"}
            </Link>

            <div className="mt-2 flex items-center gap-3">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-lg"
                style={{ backgroundColor: `${topic.subject.color || "#2563EB"}15` }}
              >
                <BookOpen className="h-5 w-5" style={{ color: topic.subject.color || "#2563EB" }} />
              </div>
              <div>
                <h1 className="text-xl font-bold text-[#0F172A]">{topic.title}</h1>
                <p className="text-xs text-gray-400">
                  {topic.subject?.name} &middot; {topic.lesson?.title}
                </p>
              </div>
            </div>
          </div>

          <Card className="mb-6 overflow-hidden border-0 shadow-lg">
            <CardContent className="p-8">
              {topic.content ? (
                <div className={sectionClass}>
                  <div dangerouslySetInnerHTML={{ __html: topic.content }} />
                </div>
              ) : (
                <div className="py-8 text-center">
                  <BookOpen className="mx-auto h-10 w-10 text-gray-300" />
                  <p className="mt-3 text-sm text-gray-500">No content available for this topic.</p>
                </div>
              )}
              <div className="mt-6 border-t border-gray-100 pt-4 text-right">
                <button
                  onClick={() => setReportingIssue({})}
                  className="inline-flex items-center gap-1 text-xs text-gray-400 hover:text-red-500 transition-colors"
                >
                  <Flag className="h-3 w-3" />
                  Report issue
                </button>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-center">
            <Link href={`/subjects/${slug}`}>
              <Button variant="outline" size="sm" className="gap-1">
                <ChevronLeft className="h-4 w-4" />
                Back to {topic.subject?.name || "subject"}
              </Button>
            </Link>
          </div>
        </div>

        {reportingIssue !== null && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
              <h3 className="mb-4 text-lg font-semibold text-[#0F172A]">Report an Issue</h3>
              <div className="mb-4">
                <label className="mb-1 block text-xs font-medium text-gray-600">Severity</label>
                <select
                  value={issueSeverity}
                  onChange={(e) => setIssueSeverity(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 p-2 text-sm focus:border-[#2563EB] focus:outline-none"
                >
                  <option value="inaccurate">Inaccurate content</option>
                  <option value="typo">Typo / formatting</option>
                  <option value="harmful">Harmful / misleading</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="mb-1 block text-xs font-medium text-gray-600">Description</label>
                <textarea
                  value={issueDescription}
                  onChange={(e) => setIssueDescription(e.target.value)}
                  placeholder="Describe what's wrong with this content..."
                  className="h-24 w-full rounded-lg border border-gray-200 p-2 text-sm focus:border-[#2563EB] focus:outline-none"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setReportingIssue(null)
                    setIssueDescription("")
                  }}
                >
                  Cancel
                </Button>
                <Button size="sm" onClick={handleReportIssue}>
                  Submit Report
                </Button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
