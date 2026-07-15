import { create } from "zustand"
import type { User } from "@/types"

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string, refreshToken: string) => void
  setUser: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  setAuth: (user, token, refreshToken) => {
    try {
      localStorage.setItem("token", token)
      localStorage.setItem("refreshToken", refreshToken)
    } catch {
      // localStorage may be unavailable (Safari private, quota exceeded)
    }
    set({ user, token, refreshToken, isAuthenticated: true })
  },
  setUser: (user) => set({ user }),
  logout: () => {
    try {
      localStorage.removeItem("token")
      localStorage.removeItem("refreshToken")
    } catch {
      // localStorage may be unavailable
    }
    set({ user: null, token: null, refreshToken: null, isAuthenticated: false })
  },
}))
