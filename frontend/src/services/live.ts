import { api } from "./api"

export interface LiveRoom {
  room_id: string
  provider: string
  provider_room_id: string | null
  token: string | null
  status: string
  created_at: string
}

export interface LiveSession {
  id: string
  room_id: string
  subject: string
  topic: string | null
  status: string
  provider: string
  recording_url: string | null
  started_at: string | null
  ended_at: string | null
  created_at: string
}

export const liveService = {
  createRoom: (data: { subject: string; topic?: string; student_id?: string }) =>
    api.post<LiveRoom>("/live/rooms", data),

  getRoom: (roomId: string) =>
    api.get<LiveSession>(`/live/rooms/${roomId}`),

  startSession: (roomId: string) =>
    api.post<LiveSession>(`/live/rooms/${roomId}/start`),

  endSession: (roomId: string, recordingUrl?: string) =>
    api.post<LiveSession>(`/live/rooms/${roomId}/end`, { recording_url: recordingUrl }),

  listSessions: (role = "tutor", skip = 0, limit = 50) => {
    const params = new URLSearchParams({ role, skip: String(skip), limit: String(limit) })
    return api.get<LiveSession[]>(`/live?${params}`)
  },
}
