import { API_URL } from "@/constants"

class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token))
  refreshSubscribers = []
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  let token: string | null = null
  if (typeof window !== "undefined") {
    try {
      token = localStorage.getItem("token")
    } catch {
      // localStorage may be unavailable
    }
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 30_000)
  let response: Response
  try {
    response = await fetch(`${API_URL}${endpoint}`, { ...options, headers, signal: options.signal ?? controller.signal })
  } finally {
    clearTimeout(timeout)
  }

  if (response.status === 401 && typeof window !== "undefined" && !endpoint.includes("/auth/")) {
    const refreshToken = localStorage.getItem("refreshToken")
    if (refreshToken) {
      if (!isRefreshing) {
        isRefreshing = true
        try {
          const refreshResp = await fetch(`${API_URL}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken })
          })
          
          if (refreshResp.ok) {
            const data = await refreshResp.json()
            localStorage.setItem("token", data.access_token)
            localStorage.setItem("refreshToken", data.refresh_token)
            onRefreshed(data.access_token)
          } else {
            localStorage.removeItem("token")
            localStorage.removeItem("refreshToken")
            onRefreshed("")
            window.location.href = "/login"
          }
        } catch {
          localStorage.removeItem("token")
          localStorage.removeItem("refreshToken")
          onRefreshed("")
          window.location.href = "/login"
        } finally {
          isRefreshing = false
        }
      }
      
      // Wait for refresh to complete and retry
      const newToken = await new Promise<string>((resolve) => {
        refreshSubscribers.push(resolve)
      })
      
      if (newToken) {
        headers["Authorization"] = `Bearer ${newToken}`
        const retryController = new AbortController()
        const retryTimeout = setTimeout(() => retryController.abort(), 30_000)
        try {
          response = await fetch(`${API_URL}${endpoint}`, { ...options, headers, signal: options.signal ?? retryController.signal })
        } finally {
          clearTimeout(retryTimeout)
        }
      }
    } else {
      window.location.href = "/login"
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }))
    throw new ApiError(error.detail || "Request failed", response.status)
  }

  return response.json()
}

export const api = {
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, data?: unknown) =>
    request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),
  put: <T>(endpoint: string, data?: unknown) =>
    request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    }),
  patch: <T>(endpoint: string, data?: unknown) =>
    request<T>(endpoint, {
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    }),
  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: "DELETE" }),
}
