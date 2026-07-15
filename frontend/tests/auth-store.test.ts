import { describe, it, expect, beforeEach } from "vitest"
import { useAuthStore } from "@/store/auth"
import type { User } from "@/types"

const mockUser: User = {
  id: "user-1",
  email: "test@example.com",
  full_name: "Test User",
  is_verified: true,
  credits: 50,
  learning_streak: 3,
  avatar_url: null,
}

describe("useAuthStore", () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
    })
    localStorage.clear()
  })

  it("starts unauthenticated", () => {
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.user).toBeNull()
  })

  it("setAuth sets user and tokens", () => {
    useAuthStore.getState().setAuth(mockUser, "token-123", "refresh-456")
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(true)
    expect(state.user).toEqual(mockUser)
    expect(state.token).toBe("token-123")
    expect(state.refreshToken).toBe("refresh-456")
  })

  it("setAuth persists tokens to localStorage", () => {
    useAuthStore.getState().setAuth(mockUser, "token-abc", "refresh-def")
    expect(localStorage.getItem("token")).toBe("token-abc")
    expect(localStorage.getItem("refreshToken")).toBe("refresh-def")
  })

  it("setUser updates user without changing tokens", () => {
    useAuthStore.getState().setAuth(mockUser, "token-1", "refresh-1")
    const updatedUser = { ...mockUser, full_name: "Updated Name" }
    useAuthStore.getState().setUser(updatedUser)
    const state = useAuthStore.getState()
    expect(state.user?.full_name).toBe("Updated Name")
    expect(state.token).toBe("token-1")
  })

  it("logout clears everything", () => {
    useAuthStore.getState().setAuth(mockUser, "token-x", "refresh-y")
    useAuthStore.getState().logout()
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(localStorage.getItem("token")).toBeNull()
  })
})
