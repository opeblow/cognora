"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { flashcardService, type Flashcard } from "@/services/flashcards"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Brain, ChevronLeft, Sparkles, Trash2, RotateCcw, Clock, RefreshCw } from "lucide-react"
import { toast } from "sonner"

type View = "list" | "review"

export default function FlashcardsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const [view, setView] = useState<View>("list")
  const [reviewCard, setReviewCard] = useState<Flashcard | null>(null)
  const [showAnswer, setShowAnswer] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [reviewedCount, setReviewedCount] = useState(0)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: allCards, refetch } = useQuery({
    queryKey: ["flashcards"],
    queryFn: () => flashcardService.getAll(),
    enabled: isAuthenticated,
  })

  const { data: dueCards } = useQuery({
    queryKey: ["flashcards", "due"],
    queryFn: () => flashcardService.getAll(undefined, true),
    enabled: isAuthenticated,
  })

  const cards = allCards?.flashcards ?? []
  const due = dueCards?.flashcards ?? []
  const dueCount = due.length

  const startReview = () => {
    if (due.length === 0) {
      toast("No cards due for review right now. Come back later!")
      return
    }
    setReviewCard(due[0])
    setShowAnswer(false)
    setReviewedCount(0)
    setView("review")
  }

  const handleReview = async (quality: number) => {
    if (!reviewCard || submitting) return
    setSubmitting(true)
    try {
      await flashcardService.review(reviewCard.id, quality)
      const remaining = due.filter((c) => c.id !== reviewCard.id)
      setReviewedCount((prev) => prev + 1)
      if (remaining.length > 0) {
        setReviewCard(remaining[0])
        setShowAnswer(false)
      } else {
        toast.success("All due cards reviewed!")
        setView("list")
        setReviewCard(null)
        queryClient.invalidateQueries({ queryKey: ["flashcards"] })
        queryClient.invalidateQueries({ queryKey: ["flashcards", "due"] })
      }
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to record review")
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await flashcardService.delete(id)
      toast.success("Card deleted")
      queryClient.invalidateQueries({ queryKey: ["flashcards"] })
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to delete card")
    }
  }

  const handleDeleteAll = async () => {
    if (!confirm("Delete all flashcards? This cannot be undone.")) return
    try {
      await flashcardService.deleteAll()
      toast.success("All flashcards deleted")
      queryClient.invalidateQueries({ queryKey: ["flashcards"] })
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to delete flashcards")
    }
  }

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-4xl">
          {view === "list" && (
            <>
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-[#0F172A]">Flashcards</h1>
                  <p className="mt-1 text-sm text-gray-600">Spaced repetition for effective memorization</p>
                </div>
                <div className="flex items-center gap-3">
                  {cards.length > 0 && (
                    <>
                      <Button variant="outline" onClick={() => router.push("/subjects")} className="gap-2">
                        <RefreshCw className="h-4 w-4" />
                        Switch Topic
                      </Button>
                      <Button variant="outline" onClick={handleDeleteAll} className="gap-2 text-red-600 hover:text-red-700">
                        <Trash2 className="h-4 w-4" />
                        Clear All
                      </Button>
                    </>
                  )}
                  <Button onClick={startReview} className="gap-2" disabled={dueCount === 0}>
                    <Brain className="h-4 w-4" />
                    Review Due ({dueCount})
                  </Button>
                </div>
              </div>

              {dueCount > 0 && (
                <Card className="mb-6 border-[#2563EB]/20 bg-[#2563EB]/5">
                  <CardContent className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-3">
                      <RotateCcw className="h-5 w-5 text-[#2563EB]" />
                      <div>
                        <p className="text-sm font-medium text-[#0F172A]">{dueCount} cards due for review</p>
                        <p className="text-xs text-gray-500">Space them out for best retention</p>
                      </div>
                    </div>
                    <Button size="sm" onClick={startReview}>
                      Start Review
                    </Button>
                  </CardContent>
                </Card>
              )}

              <div className="space-y-3">
                {cards.map((card) => {
                  const isDue = due.some((d) => d.id === card.id)
                  return (
                    <Card key={card.id} className={`transition-shadow hover:shadow-md ${isDue ? "border-[#2563EB]/30" : ""}`}>
                      <CardContent className="p-5">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <p className="font-medium text-[#0F172A]">{card.question}</p>
                            <p className="mt-1 text-sm text-gray-500 line-clamp-2">{card.answer}</p>
                            <div className="mt-2 flex flex-wrap items-center gap-2">
                              {card.tags && (
                                <Badge variant="secondary" className="text-xs">{card.tags}</Badge>
                              )}
                              {card.difficulty && (
                                <Badge variant={card.difficulty === "hard" ? "destructive" : card.difficulty === "easy" ? "success" : "default"}>
                                  {card.difficulty}
                                </Badge>
                              )}
                              {isDue && (
                                <Badge variant="accent" className="text-xs">
                                  Due now
                                </Badge>
                              )}
                              {card.interval_days > 0 && (
                                <span className="flex items-center gap-1 text-xs text-gray-400">
                                  <Clock className="h-3 w-3" />
                                  {card.interval_days}d interval
                                </span>
                              )}
                            </div>
                          </div>
                          <Button variant="ghost" size="icon" onClick={() => handleDelete(card.id)}>
                            <Trash2 className="h-4 w-4 text-gray-400 hover:text-red-500" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
                {cards.length === 0 && (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <Brain className="mx-auto mb-4 h-10 w-10 text-gray-300" />
                      <h3 className="mb-2 text-lg font-semibold text-[#0F172A]">No flashcards yet</h3>
                      <p className="mb-6 text-sm text-gray-500">
                        Generate flashcards from any topic page to start reviewing with spaced repetition.
                      </p>
                      <Button variant="outline" onClick={() => router.push("/subjects")} className="gap-2">
                        <Sparkles className="h-4 w-4" />
                        Browse Subjects
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </div>
            </>
          )}

          {view === "review" && reviewCard && (
            <div className="mx-auto max-w-2xl">
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <h1 className="text-xl font-bold text-[#0F172A]">Review Flashcards</h1>
                  <p className="text-sm text-gray-500">{dueCount} cards due</p>
                </div>
                <Button variant="outline" size="sm" onClick={() => { setView("list"); setReviewCard(null) }}>
                  <ChevronLeft className="mr-1 h-4 w-4" /> Back
                </Button>
              </div>

              <Progress value={(reviewedCount / dueCount) * 100} className="mb-6" />

              <Card className="mb-6 min-h-[300px]">
                <CardContent className="p-8">
                  <div className="mb-4 flex items-center justify-between">
                    <Badge variant="outline">Question</Badge>
                    <span className="text-xs text-gray-400">
                      {reviewedCount + 1} of {dueCount}
                    </span>
                  </div>
                  <p className="text-lg font-medium text-[#0F172A]">{reviewCard.question}</p>

                  {showAnswer && (
                    <>
                      <hr className="my-6 border-gray-100" />
                      <div className="mb-4 flex items-center justify-between">
                        <Badge variant="success">Answer</Badge>
                      </div>
                      <p className="text-gray-700">{reviewCard.answer}</p>
                    </>
                  )}
                </CardContent>
              </Card>

              {!showAnswer ? (
                <Button className="w-full" size="lg" onClick={() => setShowAnswer(true)}>
                  Show Answer
                </Button>
              ) : (
                <div>
                  <p className="mb-3 text-center text-sm text-gray-500">How well did you remember?</p>
                  <div className="grid grid-cols-6 gap-2">
                    <Button variant="outline" onClick={() => handleReview(0)} disabled={submitting} className="flex-col py-4 text-xs">
                      <span className="text-lg">0</span>
                      <span>Blackout</span>
                    </Button>
                    <Button variant="outline" onClick={() => handleReview(1)} disabled={submitting} className="flex-col py-4 text-xs">
                      <span className="text-lg">1</span>
                      <span>Wrong</span>
                    </Button>
                    <Button variant="outline" onClick={() => handleReview(2)} disabled={submitting} className="flex-col py-4 text-xs">
                      <span className="text-lg">2</span>
                      <span>Hard</span>
                    </Button>
                    <Button variant="outline" onClick={() => handleReview(3)} disabled={submitting} className="flex-col py-4 text-xs">
                      <span className="text-lg">3</span>
                      <span>Good</span>
                    </Button>
                    <Button variant="outline" onClick={() => handleReview(4)} disabled={submitting} className="flex-col py-4 text-xs">
                      <span className="text-lg">4</span>
                      <span>Easy</span>
                    </Button>
                    <Button variant="default" onClick={() => handleReview(5)} disabled={submitting} className="flex-col py-4 text-xs">
                      <span className="text-lg">5</span>
                      <span>Perfect</span>
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
