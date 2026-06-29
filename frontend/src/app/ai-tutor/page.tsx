"use client"

import { useState, useRef, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import { aiService } from "@/services/ai"
import { Sidebar } from "@/components/layout/sidebar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Send, Brain, User, Sparkles, Loader2 } from "lucide-react"
import { toast } from "sonner"
import type { TutorMessage } from "@/types"

export default function AITutorPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [messages, setMessages] = useState<TutorMessage[]>([
    {
      role: "assistant",
      content: "Hi! I'm your Cognora AI tutor. I can help you with any subject for WAEC, NECO, GCE, JAMB, and Post-UTME. What would you like to learn today?",
    },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: TutorMessage = { role: "user", content: input.trim() }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const context = messages.slice(-10).map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const response = await aiService.tutor({
        message: userMessage.content,
        context,
      })

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.response },
      ])
    } catch (error: unknown) {
      const err = error as { message?: string }
      toast.error(err.message || "Failed to get response")
      if (err.message?.includes("Insufficient credits")) {
        router.push("/credits")
      }
    } finally {
      setLoading(false)
    }
  }

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex flex-1 flex-col">
        <div className="border-b border-gray-100 bg-white px-8 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#2563EB]/10">
              <Brain className="h-5 w-5 text-[#2563EB]" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-[#0F172A]">AI Tutor</h1>
              <p className="text-xs text-gray-500">1 credit per question</p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-8 py-6">
          <div className="mx-auto max-w-3xl space-y-6">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-4 ${msg.role === "user" ? "justify-end" : ""}`}
              >
                {msg.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#2563EB]/10">
                    <Sparkles className="h-4 w-4 text-[#2563EB]" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-[#2563EB] text-white"
                      : "bg-white border border-gray-100 text-[#0F172A]"
                  }`}
                >
                  <div className="prose prose-sm max-w-none">
                    {msg.content.split("\n").map((line, j) => (
                      <p key={j} className={j > 0 ? "mt-2" : ""}>
                        {line}
                      </p>
                    ))}
                  </div>
                </div>
                {msg.role === "user" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100">
                    <User className="h-4 w-4 text-gray-600" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#2563EB]/10">
                  <Sparkles className="h-4 w-4 text-[#2563EB]" />
                </div>
                <Card className="rounded-xl border border-gray-100 bg-white px-4 py-3">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Thinking...
                  </div>
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="border-t border-gray-100 bg-white px-8 py-4">
          <div className="mx-auto flex max-w-3xl gap-3">
            <Input
              placeholder="Ask me anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={loading}
              className="flex-1"
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
