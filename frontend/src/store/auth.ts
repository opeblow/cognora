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
    localStorage.setItem("token", token)
    localStorage.setItem("refreshToken", refreshToken)
    set({ user, token, refreshToken, isAuthenticated: true })
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem("token")
    localStorage.removeItem("refreshToken")
    set({ user: null, token: null, refreshToken: null, isAuthenticated: false })
  },
}))
