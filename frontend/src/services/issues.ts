import { api } from "./api"

export interface CreateIssueRequest {
  content_type: string
  content_id: string
  section_index?: number
  severity: "typo" | "inaccurate" | "harmful" | "other"
  description: string
}

export interface IssueResponse {
  id: string
  status: string
  message: string
}

export interface IssueListItem {
  id: string
  content_type: string
  severity: string
  description: string
  status: string
  ai_response: string | null
  created_at: string | null
}

export const issuesService = {
  create: (data: CreateIssueRequest) =>
    api.post<IssueResponse>("/issues", data),

  list: (skip = 0, limit = 20) =>
    api.get<{ issues: IssueListItem[] }>(`/issues?skip=${skip}&limit=${limit}`),
}
