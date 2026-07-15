import { api } from "./api"
import type { AuthResponse } from "@/types"

export const authService = {
  signup: (data: { email: string; password: string; full_name: string }) =>
    api.post<AuthResponse>("/auth/signup", data),

  login: (data: { email: string; password: string }) =>
    api.post<AuthResponse>("/auth/login", data),

  verifyEmail: (token: string) =>
    api.post<{ message: string }>("/auth/verify-email", { token }),

  forgotPassword: (email: string) =>
    api.post<{ message: string }>("/auth/forgot-password", { email }),

  resetPassword: (data: { token: string; password: string }) =>
    api.post<{ message: string }>("/auth/reset-password", data),

  refreshToken: (refresh_token: string) =>
    api.post<{ access_token: string; refresh_token: string }>("/auth/refresh", { refresh_token }),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post<{ message: string }>("/auth/change-password", data),

  getMe: () => api.get<{ id: string; email: string; full_name: string; avatar_url: string | null; is_verified: boolean; credits: number; learning_streak: number }>("/auth/me"),
}
