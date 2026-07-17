"use client"

import { useEffect, useState, useRef, useCallback } from "react"
import { useRouter, useParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { lobbyService, type LobbyMessage } from "@/services/lobbies"
import { Sidebar } from "@/components/layout/sidebar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Send, Users, Sparkles, ChevronLeft, Loader2 } from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"

export default function LobbyDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { user, isAuthenticated } = useAuthStore()
  const lobbyId = params.id as string

  const [messages, setMessages] = useState<LobbyMessage[]>([])
  const [input, setInput] = useState("")
  const [connected, setConnected] = useState(false)
  const [sending, setSending] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const reconnectAttemptRef = useRef(0)

  const { data: lobby, isLoading } = useQuery({
    queryKey: ["lobby", lobbyId],
    queryFn: () => lobbyService.getById(lobbyId),
    enabled: isAuthenticated,
  })

  const { data: history } = useQuery({
    queryKey: ["lobby-history", lobbyId],
    queryFn: () => lobbyService.getHistory(lobbyId),
    enabled: isAuthenticated,
  })

  const initializedRef = useRef(false)
  useEffect(() => {
    if (history?.messages && !initializedRef.current) {
      setMessages(history.messages)
      initializedRef.current = true
    }
  }, [history])

  const connectWs = useCallback(() => {
    if (!lobbyId || !lobby?.is_active) return
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return
    }

    const ws = new WebSocket(`${WS_URL}/api/lobbies/${lobbyId}/ws`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      reconnectAttemptRef.current = 0
      ws.send(JSON.stringify({
        username: user?.full_name || "Anonymous",
        user_id: user?.id,
      }))
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === "message") {
          setMessages((prev) => [...prev, {
            id: data.id,
            lobby_id: lobbyId,
            user_id: data.user_id,
            username: data.username,
            content: data.content,
            is_ai_response: data.is_ai_response,
            created_at: data.created_at,
          }])
        }
      } catch {
        // ignore malformed messages
      }
    }

    ws.onerror = () => {
      setConnected(false)
    }

    ws.onclose = () => {
      setConnected(false)
      const attempt = reconnectAttemptRef.current
      const delay = Math.min(1000 * Math.pow(2, attempt), 30000)
      reconnectAttemptRef.current = attempt + 1
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectTimeoutRef.current = null
        connectWs()
      }, delay)
    }
  }, [lobbyId, lobby?.is_active, user])

  useEffect(() => {
    if (lobby?.is_active) {
      connectWs()
    }
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      reconnectAttemptRef.current = 0
      if (wsRef.current) {
        wsRef.current.onclose = null
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [lobbyId, lobby?.is_active, connectWs])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = () => {
    if (!input.trim() || sending || !wsRef.current) return
    setSending(true)
    try {
      wsRef.current.send(JSON.stringify({ content: input.trim() }))
      setInput("")
    } catch {
      toast.error("Failed to send message")
    } finally {
      setSending(false)
    }
  }

  if (!isAuthenticated) return null
  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
          <div className="mx-auto max-w-4xl pt-20 text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-[#14B8A6]" />
            <p className="mt-4 text-gray-500">Loading lobby...</p>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 flex flex-1 flex-col pt-14 lg:pt-0">
        <div className="border-b border-gray-100 bg-white px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link href="/lobbies">
                <Button variant="ghost" size="icon">
                  <ChevronLeft className="h-4 w-4" />
                </Button>
              </Link>
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#14B8A6]/10">
                <Users className="h-5 w-5 text-[#14B8A6]" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-[#0F172A]">{lobby?.name || "Study Lobby"}</h1>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  {lobby?.subject && <Badge variant="secondary">{lobby.subject}</Badge>}
                  {lobby?.topic && <span>{lobby.topic}</span>}
                  <span className={`flex items-center gap-1 ${connected ? "text-green-600" : "text-red-500"}`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
                    {connected ? "Connected" : "Disconnected"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-8 py-6">
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-3 ${msg.username === "System" ? "justify-center" : msg.is_ai_response ? "" : ""}`}>
                {msg.username === "System" ? (
                  <div className="rounded-full bg-gray-100 px-4 py-1 text-xs text-gray-500">{msg.content}</div>
                ) : (
                  <div className={`flex gap-3 max-w-[80%] ${msg.is_ai_response ? "items-start" : ""}`}>
                    {msg.is_ai_response && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#14B8A6]/10">
                        <Sparkles className="h-4 w-4 text-[#14B8A6]" />
                      </div>
                    )}
                    <div className={`rounded-xl px-4 py-3 ${msg.is_ai_response ? "border border-gray-100 bg-white" : "bg-white border border-gray-100"}`}>
                      <p className="text-xs font-medium text-[#14B8A6]">{msg.username}</p>
                      <p className="mt-1 text-sm text-[#0F172A]">{msg.content}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="border-t border-gray-100 bg-white px-8 py-4">
          <div className="mx-auto flex max-w-3xl gap-3">
            <Input
              placeholder="Type a message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={!connected}
            />
            <Button onClick={sendMessage} disabled={!input.trim() || !connected || sending}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="mt-1 text-center text-xs text-gray-400">
            AI moderator joins after 3 messages to keep discussions productive
          </p>
        </div>
      </main>
    </div>
  )
}
