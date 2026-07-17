"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { lobbyService } from "@/services/lobbies"
import { subjectService } from "@/services/subjects"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Users, MessageCircle, Plus, X, Loader2 } from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"

export default function LobbiesPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState("")
  const [selectedSubject, setSelectedSubject] = useState("")
  const [topic, setTopic] = useState("")
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: lobbiesData, refetch } = useQuery({
    queryKey: ["lobbies"],
    queryFn: () => lobbyService.getAll(),
    enabled: isAuthenticated,
    refetchInterval: 30000,
  })

  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => subjectService.getAll(),
    enabled: isAuthenticated,
  })

  const lobbies = lobbiesData?.lobbies ?? []
  const subjects = subjectsData?.subjects ?? []

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error("Please enter a lobby name")
      return
    }
    setCreating(true)
    try {
      const lobby = await lobbyService.create({
        name: name.trim(),
        subject: selectedSubject || undefined,
        topic: topic.trim() || undefined,
      })
      toast.success("Study lobby created!")
      setShowCreate(false)
      setName("")
      setSelectedSubject("")
      setTopic("")
      refetch()
      router.push(`/lobbies/${lobby.id}`)
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to create lobby")
    } finally {
      setCreating(false)
    }
  }

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#0F172A]">Study Groups</h1>
              <p className="mt-1 text-sm text-gray-600">Join or create study lobbies to learn together</p>
            </div>
            <Button onClick={() => setShowCreate(!showCreate)} className="gap-2">
              {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              {showCreate ? "Cancel" : "Create Lobby"}
            </Button>
          </div>

          {showCreate && (
            <Card className="mb-6 border-[#2563EB]/20">
              <CardContent className="p-6">
                <h3 className="mb-4 font-semibold text-[#0F172A]">Create a Study Lobby</h3>
                <div className="space-y-3">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">Lobby Name *</label>
                    <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Math JAMB Prep Group" />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Subject</label>
                      <select
                        value={selectedSubject}
                        onChange={(e) => setSelectedSubject(e.target.value)}
                        className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm"
                      >
                        <option value="">Any subject</option>
                        {subjects.map((s) => (
                          <option key={s.id} value={s.name}>{s.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Topic (optional)</label>
                      <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g., Quadratic Equations" />
                    </div>
                  </div>
                  <Button onClick={handleCreate} disabled={creating || !name.trim()} className="w-full">
                    {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <MessageCircle className="mr-2 h-4 w-4" />}
                    Create Lobby
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="space-y-3">
            {lobbies.map((lobby) => (
              <Link key={lobby.id} href={`/lobbies/${lobby.id}`}>
                <Card className="cursor-pointer transition-shadow hover:shadow-md">
                  <CardContent className="flex items-center justify-between p-5">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#14B8A6]/10">
                        <Users className="h-6 w-6 text-[#14B8A6]" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-[#0F172A]">{lobby.name}</h3>
                        <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                          {lobby.subject && <Badge variant="secondary">{lobby.subject}</Badge>}
                          {lobby.topic && <span>{lobby.topic}</span>}
                          <span>{lobby.max_participants} max</span>
                        </div>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      Join
                    </Button>
                  </CardContent>
                </Card>
              </Link>
            ))}
            {lobbies.length === 0 && (
              <Card>
                <CardContent className="p-12 text-center">
                  <Users className="mx-auto mb-4 h-10 w-10 text-gray-300" />
                  <h3 className="mb-2 text-lg font-semibold text-[#0F172A]">No active study groups</h3>
                  <p className="mb-6 text-sm text-gray-500">Create one and invite friends to study together!</p>
                  <Button onClick={() => setShowCreate(true)} className="gap-2">
                    <Plus className="h-4 w-4" />
                    Create the first lobby
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
