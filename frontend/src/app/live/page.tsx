"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { liveService, type LiveSession } from "@/services/live"
import { subjectService } from "@/services/subjects"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Video, VideoOff, Clock, Copy, ExternalLink, Loader2 } from "lucide-react"
import { toast } from "sonner"

export default function LivePage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [showCreate, setShowCreate] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState("")
  const [topic, setTopic] = useState("")
  const [creating, setCreating] = useState(false)
  const [createdRoom, setCreatedRoom] = useState<{
    room_id: string
    provider: string
    provider_room_id: string | null
    token: string | null
  } | null>(null)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: sessions } = useQuery({
    queryKey: ["live-sessions"],
    queryFn: () => liveService.listSessions(),
    enabled: isAuthenticated,
    refetchInterval: 15000,
  })

  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => subjectService.getAll(),
    enabled: isAuthenticated,
  })

  const subjects = subjectsData?.subjects ?? []
  const sessionList = sessions ?? []

  const handleCreateRoom = async () => {
    if (!selectedSubject) {
      toast.error("Please select a subject")
      return
    }
    setCreating(true)
    try {
      const room = await liveService.createRoom({
        subject: selectedSubject,
        topic: topic.trim() || undefined,
      })
      setCreatedRoom(room)
      toast.success("Live room created!")
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to create room")
    } finally {
      setCreating(false)
    }
  }

  const copyRoomCode = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success("Copied to clipboard")
  }

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#0F172A]">Live Teaching</h1>
              <p className="mt-1 text-sm text-gray-600">Create or join live tutoring sessions with video, audio, and screen sharing</p>
            </div>
            <Button onClick={() => setShowCreate(!showCreate)} className="gap-2">
              <Video className="h-4 w-4" />
              {showCreate ? "Cancel" : "New Session"}
            </Button>
          </div>

          {showCreate && (
            <Card className="mb-6 border-[#2563EB]/20">
              <CardContent className="p-6">
                <h3 className="mb-4 font-semibold text-[#0F172A]">Create a Live Session</h3>
                <div className="space-y-3">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">Subject *</label>
                    <select
                      value={selectedSubject}
                      onChange={(e) => setSelectedSubject(e.target.value)}
                      className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm"
                    >
                      <option value="">Select a subject</option>
                      {subjects.map((s) => (
                        <option key={s.id} value={s.name}>{s.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">Topic (optional)</label>
                    <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g., Differentiation" />
                  </div>
                  <Button onClick={handleCreateRoom} disabled={creating || !selectedSubject} className="w-full">
                    {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Video className="mr-2 h-4 w-4" />}
                    Create Room
                  </Button>
                </div>

                {createdRoom && (
                  <div className="mt-4 rounded-lg bg-green-50 p-4">
                    <p className="mb-2 text-sm font-medium text-green-700">Room Created!</p>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Room ID:</span>
                        <button onClick={() => copyRoomCode(createdRoom.room_id)} className="flex items-center gap-1 text-[#2563EB] hover:underline">
                          {createdRoom.room_id} <Copy className="h-3 w-3" />
                        </button>
                      </div>
                      {createdRoom.token && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Token:</span>
                          <button onClick={() => copyRoomCode(createdRoom.token!)} className="flex items-center gap-1 text-[#2563EB] hover:underline">
                            {createdRoom.token.slice(0, 20)}... <Copy className="h-3 w-3" />
                          </button>
                        </div>
                      )}
                      <p className="text-xs text-gray-400 mt-2">
                        Share the Room ID and Token with your student to join. Video provider: {createdRoom.provider === "mock" ? "Test mode (no video)" : createdRoom.provider}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          <div className="space-y-3">
            {sessionList.map((session: LiveSession) => (
              <Card key={session.id} className="transition-shadow hover:shadow-md">
                <CardContent className="flex items-center justify-between p-5">
                  <div className="flex items-center gap-4">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${
                      session.status === "active" ? "bg-green-50" : session.status === "completed" ? "bg-gray-50" : "bg-[#2563EB]/10"
                    }`}>
                      {session.status === "active" ? (
                        <Video className="h-6 w-6 text-green-500" />
                      ) : session.status === "completed" ? (
                        <VideoOff className="h-6 w-6 text-gray-400" />
                      ) : (
                        <Video className="h-6 w-6 text-[#2563EB]" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold text-[#0F172A]">{session.subject}</h3>
                      <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                        {session.topic && <span>{session.topic}</span>}
                        <Badge variant={session.status === "active" ? "success" : session.status === "completed" ? "secondary" : "default"}>
                          {session.status}
                        </Badge>
                        {session.started_at && (
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {new Date(session.started_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {session.status === "active" && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="gap-1"
                        onClick={() => copyRoomCode(session.room_id)}
                      >
                        <Copy className="h-3 w-3" />
                        Room Code
                      </Button>
                    )}
                    {session.recording_url && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => window.open(session.recording_url!, "_blank")}
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
            {sessionList.length === 0 && !showCreate && (
              <Card>
                <CardContent className="p-12 text-center">
                  <Video className="mx-auto mb-4 h-10 w-10 text-gray-300" />
                  <h3 className="mb-2 text-lg font-semibold text-[#0F172A]">No live sessions yet</h3>
                  <p className="mb-6 text-sm text-gray-500">
                    Create a live tutoring session to teach students in real-time with video and audio.
                  </p>
                  <Button onClick={() => setShowCreate(true)} className="gap-2">
                    <Video className="h-4 w-4" />
                    Start your first session
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
