import { api } from "./api"

export interface StudyGroup {
  id: string
  name: string
  description: string | null
  subject: string | null
  creator_id: string
  max_members: number
  is_active: boolean
  created_at: string
  member_count: number
  creator_name: string | null
}

export interface StudyGroupMember {
  id: string
  user_id: string
  role: string
  joined_at: string
  full_name: string | null
}

export interface StudyGroupDetail extends StudyGroup {
  members: StudyGroupMember[]
}

export interface StudyGroupMessage {
  id: string
  group_id: string
  user_id: string
  content: string
  created_at: string
  full_name: string | null
}

export const studyGroupService = {
  getMyGroups: () =>
    api.get<{ groups: StudyGroup[]; total: number }>("/study-groups"),

  browse: (subject?: string) => {
    const params = subject ? `?subject=${encodeURIComponent(subject)}` : ""
    return api.get<{ groups: StudyGroup[]; total: number }>(`/study-groups/browse${params}`)
  },

  getById: (groupId: string) =>
    api.get<StudyGroupDetail>(`/study-groups/${groupId}`),

  create: (data: { name: string; subject?: string; description?: string; max_members?: number }) =>
    api.post<StudyGroup>("/study-groups", data),

  join: (groupId: string) =>
    api.post<{ message: string; group_id: string }>(`/study-groups/${groupId}/join`),

  leave: (groupId: string) =>
    api.post<{ message: string; group_id: string }>(`/study-groups/${groupId}/leave`),

  getMessages: (groupId: string, offset = 0, limit = 50) =>
    api.get<{ messages: StudyGroupMessage[]; total: number }>(
      `/study-groups/${groupId}/messages?offset=${offset}&limit=${limit}`
    ),

  sendMessage: (groupId: string, content: string) =>
    api.post<StudyGroupMessage>(`/study-groups/${groupId}/messages`, { content }),

  delete: (groupId: string) =>
    api.delete<{ message: string; group_id: string }>(`/study-groups/${groupId}`),
}
