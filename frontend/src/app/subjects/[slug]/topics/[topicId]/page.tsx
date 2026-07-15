"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter, useParams } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { lessonService } from "@/services/lessons"
import { Sidebar } from "@/components/layout/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { BookOpen, ChevronLeft, Loader2, Flag, BookText, ChevronRight, Zap, CheckCircle2, Sparkles, Brain } from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"
import { issuesService } from "@/services/issues"
import { flashcardService } from "@/services/flashcards"
import { sanitizeHtml } from "@/lib/sanitizeHtml"

export default function TopicDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated } = useAuthStore()
  const slug = params.slug as string
  const topicId = params.topicId as string
  const queryClient = useQueryClient()

  const [reportingIssue, setReportingIssue] = useState<{ sectionIndex?: number } | null>(null)
  const [issueDescription, setIssueDescription] = useState("")
  const [issueSeverity, setIssueSeverity] = useState<string>("inaccurate")
  const [activeSection, setActiveSection] = useState(0)
  const [sectionCache, setSectionCache] = useState<Record<number, string>>({})
  const [generatingSection, setGeneratingSection] = useState<number | null>(null)
  const [generatingFlashcards, setGeneratingFlashcards] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: topicData, isLoading } = useQuery({
    queryKey: ["topic", slug, topicId],
    queryFn: () => lessonService.getTopic(slug, topicId),
    enabled: isAuthenticated,
    retry: 1,
  })

  const { data: textbookPlan } = useQuery({
    queryKey: ["textbook-plan", slug, topicId],
    queryFn: () => lessonService.getTextbookPlan(slug, topicId),
    enabled: isAuthenticated && !!topicData,
  })

  const { data: textbookStatus } = useQuery({
    queryKey: ["textbook-status", slug, topicId],
    queryFn: () => lessonService.getTextbookStatus(slug, topicId),
    enabled: isAuthenticated && !!topicData,
  })

  const loadSectionContent = useCallback(async (sectionIndex: number) => {
    if (sectionCache[sectionIndex] !== undefined) return
    try {
      const resp = await lessonService.getSectionContent(slug, topicId, sectionIndex)
      if (resp.content) {
        setSectionCache(prev => ({ ...prev, [sectionIndex]: resp.content }))
      }
    } catch {
      // Section not generated yet - that's fine
    }
  }, [slug, topicId, sectionCache])

  useEffect(() => {
    if (textbookStatus) {
      textbookStatus.sections.forEach(s => {
        if (s.has_content && !sectionCache[s.index]) {
          loadSectionContent(s.index)
        }
      })
    }
  }, [textbookStatus, loadSectionContent, sectionCache])

  const generateMutation = useMutation({
    mutationFn: (sectionIndex: number) =>
      lessonService.generateSection(slug, topicId, sectionIndex),
    onSuccess: (data) => {
      setSectionCache(prev => ({ ...prev, [data.section_index]: data.content }))
      setGeneratingSection(null)
      toast.success("Section generated!")
      queryClient.invalidateQueries({ queryKey: ["textbook-status", slug, topicId] })
    },
    onError: () => {
      setGeneratingSection(null)
      toast.error("Failed to generate section. Not enough credits?")
    },
  })

  const handleGenerate = (sectionIndex: number) => {
    setGeneratingSection(sectionIndex)
    generateMutation.mutate(sectionIndex)
  }

  const flashcardMutation = useMutation({
    mutationFn: () => flashcardService.generate(topicId, 10),
    onSuccess: (data) => {
      setGeneratingFlashcards(false)
      toast.success(`Generated ${data.total || data.flashcards.length} flashcards!`)
      queryClient.invalidateQueries({ queryKey: ["flashcards"] })
    },
    onError: () => {
      setGeneratingFlashcards(false)
      toast.error("Failed to generate flashcards. Not enough credits?")
    },
  })

  const handleGenerateFlashcards = () => {
    setGeneratingFlashcards(true)
    flashcardMutation.mutate()
  }

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
  const sections = textbookPlan?.sections || []
  const generatedSections = new Set(textbookStatus?.generated_sections || [])
  const currentSectionContent = sectionCache[activeSection]

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

          {topic.content && (
            <Card className="mb-6 overflow-hidden border-0 shadow-lg">
              <CardContent className="p-8">
                <div className={sectionClass}>
                  <div dangerouslySetInnerHTML={{ __html: sanitizeHtml(topic.content) }} />
                </div>
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
          )}

          {sections.length > 0 && (
            <Card className="mb-6 overflow-hidden border-0 shadow-lg">
              <CardContent className="p-0">
                <div className="flex items-center gap-2 border-b border-gray-100 px-6 py-4">
                  <BookText className="h-5 w-5 text-[#2563EB]" />
                  <h2 className="text-lg font-semibold text-[#0F172A]">Textbook</h2>
                  <span className="rounded-full bg-[#2563EB]/10 px-2.5 py-0.5 text-xs font-medium text-[#2563EB]">
                    {generatedSections.size} / {sections.length} sections
                  </span>
                </div>

                <div className="flex flex-col sm:flex-row">
                  <div className="w-full border-r border-gray-100 sm:w-72">
                    <div className="max-h-[600px] overflow-y-auto p-2">
                      {sections.map((sec, i) => {
                        const isActive = activeSection === i
                        const isGenerated = generatedSections.has(i)
                        return (
                          <button
                            key={sec.index}
                            onClick={() => setActiveSection(i)}
                            className={`w-full rounded-lg p-3 text-left text-sm transition-colors ${
                              isActive
                                ? "bg-[#2563EB]/10 text-[#2563EB]"
                                : "text-gray-600 hover:bg-gray-50"
                            }`}
                          >
                            <div className="flex items-start gap-2">
                              <span className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${
                                isGenerated
                                  ? "bg-green-100 text-green-700"
                                  : "bg-gray-100 text-gray-400"
                              }`}>
                                {isGenerated ? <CheckCircle2 className="h-3 w-3" /> : i + 1}
                              </span>
                              <span className="font-medium">{sec.title}</span>
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  <div className="flex-1 p-6">
                    {activeSection < sections.length && (
                      <div>
                        <div className="mb-4 flex items-center justify-between">
                          <div>
                            <h3 className="text-base font-semibold text-[#0F172A]">
                              {sections[activeSection].title}
                            </h3>
                            <p className="mt-0.5 text-xs text-gray-400">
                              Section {activeSection + 1} of {sections.length}
                            </p>
                          </div>
                          {!generatedSections.has(activeSection) && (
                            <Button
                              size="sm"
                              onClick={() => handleGenerate(activeSection)}
                              disabled={generatingSection === activeSection}
                              className="gap-1.5"
                            >
                              {generatingSection === activeSection ? (
                                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              ) : (
                                <Zap className="h-3.5 w-3.5" />
                              )}
                              {generatingSection === activeSection ? "Generating..." : "Generate (1 credit)"}
                            </Button>
                          )}
                          {generatedSections.has(activeSection) && (
                            <span className="inline-flex items-center gap-1 text-xs text-green-600">
                              <CheckCircle2 className="h-3.5 w-3.5" />
                              Generated
                            </span>
                          )}
                        </div>

                        {currentSectionContent ? (
                          <div className={sectionClass}>
                            <div dangerouslySetInnerHTML={{ __html: sanitizeHtml(currentSectionContent) }} />
                          </div>
                        ) : generatedSections.has(activeSection) ? (
                          <div className="flex items-center justify-center py-12">
                            <Loader2 className="h-5 w-5 animate-spin text-[#2563EB]" />
                            <span className="ml-2 text-sm text-gray-500">Loading section...</span>
                          </div>
                        ) : (
                          <div className="flex flex-col items-center justify-center py-12 text-center">
                            <Sparkles className="mb-3 h-10 w-10 text-gray-300" />
                            <p className="text-sm text-gray-500">
                              This section hasn&apos;t been generated yet.
                            </p>
                            <p className="mt-1 text-xs text-gray-400">
                              Click &quot;Generate (1 credit)&quot; to create detailed textbook content for this section.
                            </p>
                          </div>
                        )}

                        <div className="mt-6 flex items-center justify-between border-t border-gray-100 pt-4">
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={activeSection === 0}
                            onClick={() => setActiveSection(activeSection - 1)}
                            className="gap-1"
                          >
                            <ChevronLeft className="h-4 w-4" />
                            Previous
                          </Button>
                          <span className="text-xs text-gray-400">
                            {activeSection + 1} of {sections.length}
                          </span>
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={activeSection >= sections.length - 1}
                            onClick={() => setActiveSection(activeSection + 1)}
                            className="gap-1"
                          >
                            Next
                            <ChevronRight className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card className="mb-6 overflow-hidden border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-50">
                    <Brain className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-[#0F172A]">Flashcards</h2>
                    <p className="text-xs text-gray-400">AI-generated Q&amp;A cards with spaced repetition</p>
                  </div>
                </div>
                <Button
                  size="sm"
                  onClick={handleGenerateFlashcards}
                  disabled={generatingFlashcards}
                  className="gap-1.5 bg-purple-600 hover:bg-purple-700"
                >
                  {generatingFlashcards ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Sparkles className="h-3.5 w-3.5" />
                  )}
                  {generatingFlashcards ? "Generating..." : "Generate 10 Cards (2 credits)"}
                </Button>
              </div>
              <p className="mt-3 text-sm text-gray-500">
                Flashcards help you memorize key concepts. Rate yourself after each review — the system schedules future reviews based on how well you know each card.
              </p>
              <Link href="/flashcards" className="mt-3 inline-flex items-center gap-1 text-sm text-purple-600 hover:underline">
                Go to Flashcard Review →
              </Link>
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
