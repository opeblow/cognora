"use client"

import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { studyGroupService, type StudyGroup, type StudyGroupMessage } from "@/services/studyGroups"
import { subjectService } from "@/services/subjects"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Users, MessageCircle, Plus, X, Loader2, Send, Search,
  ChevronDown, ChevronUp, Trash2, LogOut, UserPlus,
} from "lucide-react"
import { toast } from "sonner"

export default function StudyGroupsPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { user, isAuthenticated } = useAuthStore()

  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [selectedSubject, setSelectedSubject] = useState("")
  const [maxMembers, setMaxMembers] = useState(10)
  const [creating, setCreating] = useState(false)

  const [browseSubject, setBrowseSubject] = useState("")
  const [searchQuery, setSearchQuery] = useState("")

  const [activeGroupId, setActiveGroupId] = useState<string | null>(null)
  const [messageInput, setMessageInput] = useState("")
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data: myGroupsData, refetch: refetchMyGroups } = useQuery({
    queryKey: ["study-groups", "my"],
    queryFn: () => studyGroupService.getMyGroups(),
    enabled: isAuthenticated,
  })

  const { data: browseData, refetch: refetchBrowse } = useQuery({
    queryKey: ["study-groups", "browse", browseSubject],
    queryFn: () => studyGroupService.browse(browseSubject || undefined),
    enabled: isAuthenticated,
  })

  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => subjectService.getAll(),
    enabled: isAuthenticated,
  })

  const { data: groupDetail } = useQuery({
    queryKey: ["study-group", activeGroupId],
    queryFn: () => studyGroupService.getById(activeGroupId!),
    enabled: isAuthenticated && !!activeGroupId,
  })

  const { data: messagesData, refetch: refetchMessages } = useQuery({
    queryKey: ["study-group-messages", activeGroupId],
    queryFn: () => studyGroupService.getMessages(activeGroupId!),
    enabled: isAuthenticated && !!activeGroupId,
    refetchInterval: activeGroupId ? 10000 : false,
  })

  const myGroups = myGroupsData?.groups ?? []
  const browseGroups = browseGroupsFiltered(browseData?.groups ?? [], searchQuery)
  const subjects = subjectsData?.subjects ?? []
  const messages = messagesData?.messages ?? []

  const joinMutation = useMutation({
    mutationFn: (groupId: string) => studyGroupService.join(groupId),
    onSuccess: () => {
      toast.success("Joined group!")
      refetchMyGroups()
      refetchBrowse()
      queryClient.invalidateQueries({ queryKey: ["study-groups"] })
    },
    onError: (err: unknown) => {
      const e = err as { detail?: string; message?: string }
      toast.error(e.detail || e.message || "Failed to join")
    },
  })

  const leaveMutation = useMutation({
    mutationFn: (groupId: string) => studyGroupService.leave(groupId),
    onSuccess: () => {
      toast.success("Left group")
      if (activeGroupId) setActiveGroupId(null)
      refetchMyGroups()
      refetchBrowse()
      queryClient.invalidateQueries({ queryKey: ["study-groups"] })
    },
    onError: (err: unknown) => {
      const e = err as { detail?: string; message?: string }
      toast.error(e.detail || e.message || "Failed to leave")
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (groupId: string) => studyGroupService.delete(groupId),
    onSuccess: () => {
      toast.success("Group deleted")
      setActiveGroupId(null)
      queryClient.invalidateQueries({ queryKey: ["study-groups"] })
      refetchMyGroups()
      refetchBrowse()
    },
    onError: (err: unknown) => {
      const e = err as { detail?: string; message?: string }
      toast.error(e.detail || e.message || "Failed to delete")
    },
  })

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error("Please enter a group name")
      return
    }
    setCreating(true)
    try {
      await studyGroupService.create({
        name: name.trim(),
        subject: selectedSubject || undefined,
        description: description.trim() || undefined,
        max_members: maxMembers,
      })
      toast.success("Study group created!")
      setShowCreate(false)
      setName("")
      setDescription("")
      setSelectedSubject("")
      setMaxMembers(10)
      refetchMyGroups()
    } catch (err: unknown) {
      const e = err as { detail?: string; message?: string }
      toast.error(e.detail || e.message || "Failed to create group")
    } finally {
      setCreating(false)
    }
  }

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !activeGroupId || sending) return
    setSending(true)
    try {
      await studyGroupService.sendMessage(activeGroupId, messageInput.trim())
      setMessageInput("")
      refetchMessages()
    } catch (err: unknown) {
      const e = err as { detail?: string; message?: string }
      toast.error(e.detail || e.message || "Failed to send message")
    } finally {
      setSending(false)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const isMemberOf = (groupId: string) =>
    myGroups.some((g) => g.id === groupId)

  const myGroupIds = new Set(myGroups.map((g) => g.id))

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#0F172A]">Study Groups</h1>
              <p className="mt-1 text-sm text-gray-600">Create or join groups to study together</p>
            </div>
            <Button onClick={() => setShowCreate(!showCreate)} className="gap-2">
              {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              {showCreate ? "Cancel" : "Create Group"}
            </Button>
          </div>

          {showCreate && (
            <Card className="mb-6 border-[#2563EB]/20">
              <CardContent className="p-6">
                <h3 className="mb-4 font-semibold text-[#0F172A]">Create a Study Group</h3>
                <div className="space-y-3">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">Group Name *</label>
                    <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., JAMB Math Prep" />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">Description</label>
                    <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What will this group study?" />
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
                      <label className="mb-1 block text-sm font-medium text-gray-700">Max Members</label>
                      <Input
                        type="number"
                        min={2}
                        max={50}
                        value={maxMembers}
                        onChange={(e) => setMaxMembers(parseInt(e.target.value) || 10)}
                      />
                    </div>
                  </div>
                  <Button onClick={handleCreate} disabled={creating || !name.trim()} className="w-full">
                    {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Users className="mr-2 h-4 w-4" />}
                    Create Group
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeGroupId && groupDetail ? (
            <Card className="mb-6">
              <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#2563EB]/10">
                    <Users className="h-5 w-5 text-[#2563EB]" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-[#0F172A]">{groupDetail.name}</h2>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      {groupDetail.subject && <Badge variant="secondary">{groupDetail.subject}</Badge>}
                      <span>{groupDetail.member_count}/{groupDetail.max_members} members</span>
                      {groupDetail.creator_name && <span>Created by {groupDetail.creator_name}</span>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {groupDetail.creator_id === user?.id && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => {
                        if (confirm("Delete this group?")) deleteMutation.mutate(groupDetail.id)
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                  {isMemberOf(groupDetail.id) && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => leaveMutation.mutate(groupDetail.id)}
                    >
                      <LogOut className="mr-1 h-4 w-4" />
                      Leave
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" onClick={() => setActiveGroupId(null)}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {groupDetail.description && (
                <div className="border-b border-gray-100 px-6 py-3 text-sm text-gray-600">
                  {groupDetail.description}
                </div>
              )}

              <div className="max-h-[300px] overflow-y-auto px-6 py-4">
                <div className="space-y-3">
                  {messages.map((msg) => (
                    <div key={msg.id} className="flex gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#2563EB]/10 text-xs font-semibold text-[#2563EB]">
                        {msg.full_name?.charAt(0) || "?"}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-baseline gap-2">
                          <span className="text-sm font-medium text-[#0F172A]">{msg.full_name || "User"}</span>
                          <span className="text-xs text-gray-400">{formatTime(msg.created_at)}</span>
                        </div>
                        <p className="mt-0.5 text-sm text-gray-700 break-words">{msg.content}</p>
                      </div>
                    </div>
                  ))}
                  {messages.length === 0 && (
                    <p className="py-8 text-center text-sm text-gray-400">No messages yet. Say hello!</p>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </div>

              {isMemberOf(groupDetail.id) && (
                <div className="border-t border-gray-100 px-6 py-3">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Type a message..."
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                      disabled={sending}
                    />
                    <Button onClick={handleSendMessage} disabled={!messageInput.trim() || sending} size="icon">
                      {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          ) : null}

          {myGroups.length > 0 && (
            <div className="mb-8">
              <h2 className="mb-3 text-lg font-semibold text-[#0F172A]">My Groups</h2>
              <div className="space-y-3">
                {myGroups.map((group) => (
                  <Card
                    key={group.id}
                    className="cursor-pointer transition-shadow hover:shadow-md"
                    onClick={() => setActiveGroupId(group.id)}
                  >
                    <CardContent className="flex items-center justify-between p-5">
                      <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#2563EB]/10">
                          <Users className="h-6 w-6 text-[#2563EB]" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-[#0F172A]">{group.name}</h3>
                          <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                            {group.subject && <Badge variant="secondary">{group.subject}</Badge>}
                            <span>{group.member_count}/{group.max_members} members</span>
                          </div>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setActiveGroupId(group.id) }}>
                        Open
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          <div>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-[#0F172A]">Browse Groups</h2>
            </div>
            <div className="mb-4 flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Search groups..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              <select
                value={browseSubject}
                onChange={(e) => setBrowseSubject(e.target.value)}
                className="flex h-10 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm"
              >
                <option value="">All subjects</option>
                {subjects.map((s) => (
                  <option key={s.id} value={s.name}>{s.name}</option>
                ))}
              </select>
            </div>

            <div className="space-y-3">
              {browseGroups.map((group) => (
                <Card
                  key={group.id}
                  className="cursor-pointer transition-shadow hover:shadow-md"
                  onClick={() => !myGroupIds.has(group.id) && joinMutation.mutate(group.id)}
                >
                  <CardContent className="flex items-center justify-between p-5">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#14B8A6]/10">
                        <Users className="h-6 w-6 text-[#14B8A6]" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-[#0F172A]">{group.name}</h3>
                        {group.description && (
                          <p className="mt-0.5 text-xs text-gray-500 line-clamp-1">{group.description}</p>
                        )}
                        <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                          {group.subject && <Badge variant="secondary">{group.subject}</Badge>}
                          <span>{group.member_count}/{group.max_members} members</span>
                          {group.creator_name && <span>by {group.creator_name}</span>}
                        </div>
                      </div>
                    </div>
                    {myGroupIds.has(group.id) ? (
                      <Badge variant="secondary" className="text-[#14B8A6]">Joined</Badge>
                    ) : group.member_count >= group.max_members ? (
                      <Badge variant="secondary">Full</Badge>
                    ) : (
                      <Button variant="ghost" size="sm" className="gap-1">
                        <UserPlus className="h-4 w-4" />
                        Join
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
              {browseGroups.length === 0 && (
                <Card>
                  <CardContent className="p-12 text-center">
                    <Users className="mx-auto mb-4 h-10 w-10 text-gray-300" />
                    <h3 className="mb-2 text-lg font-semibold text-[#0F172A]">No groups found</h3>
                    <p className="text-sm text-gray-500">
                      {searchQuery || browseSubject ? "Try different filters" : "Be the first to create a study group!"}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function browseGroupsFiltered(groups: StudyGroup[], query: string): StudyGroup[] {
  if (!query.trim()) return groups
  const q = query.toLowerCase()
  return groups.filter(
    (g) =>
      g.name.toLowerCase().includes(q) ||
      (g.description && g.description.toLowerCase().includes(q)) ||
      (g.subject && g.subject.toLowerCase().includes(q))
  )
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffMin = Math.floor(diffMs / 60000)
    if (diffMin < 1) return "just now"
    if (diffMin < 60) return `${diffMin}m ago`
    const diffHr = Math.floor(diffMin / 60)
    if (diffHr < 24) return `${diffHr}h ago`
    return d.toLocaleDateString()
  } catch {
    return ""
  }
}
