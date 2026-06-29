import { api } from "./api"
import type { Subject } from "@/types"

export const subjectService = {
  getAll: (category?: string) =>
    api.get<{ subjects: Subject[]; total: number }>(
      `/subjects${category ? `?category=${category}` : ""}`
    ),

  getBySlug: (slug: string) => api.get<Subject>(`/subjects/${slug}`),
}
