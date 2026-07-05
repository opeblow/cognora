import { api } from "./api"

export interface Lobby {
  id: string
  name: string
  subject: string | null
  topic: string | null
  created_by: string
  max_participants: number
  is_active: boolean
  created_at: string
}

export interface LobbyMessage {
  id: string
  lobby_id: string
  user_id: string | null
  username: string | null
  content: string
  is_ai_response: boolean
  created_at: string
}

export const lobbyService = {
  getAll: (skip = 0, limit = 50) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
    return api.get<{ lobbies: Lobby[]; total: number }>(`/lobbies?${params}`)
  },

  getById: (lobbyId: string) =>
    api.get<Lobby>(`/lobbies/${lobbyId}`),

  create: (data: { name: string; subject?: string; topic?: string; max_participants?: number }) =>
    api.post<Lobby>("/lobbies", data),

  getHistory: (lobbyId: string, limit = 100) =>
    api.get<{ messages: LobbyMessage[] }>(`/lobbies/${lobbyId}/history?limit=${limit}`),

  close: (lobbyId: string) =>
    api.post<{ message: string }>(`/lobbies/${lobbyId}/close`),
}
