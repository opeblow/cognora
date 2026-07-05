import { api } from "./api"

export interface AudioUploadResult {
  id: string
  processing_status: string
  message: string
}

export interface AudioStatus {
  id: string
  transcript: string | null
  ai_feedback: string | null
  processing_status: string
}

export const audioService = {
  upload: (file: File) => {
    const formData = new FormData()
    formData.append("file", file)
    return api.post<AudioUploadResult>("/audio/upload", formData)
  },

  getStatus: (audioId: string) =>
    api.get<AudioStatus>(`/audio/${audioId}/status`),
}
