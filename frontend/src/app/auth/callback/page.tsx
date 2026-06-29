"use client"

import { Suspense, useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import { authService } from "@/services/auth"
import { Loader2 } from "lucide-react"

function CallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { setAuth } = useAuthStore()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = searchParams.get("token")
    const refreshToken = searchParams.get("refresh_token")

    if (token && refreshToken) {
      localStorage.setItem("token", token)
      localStorage.setItem("refreshToken", refreshToken)

      authService.getMe()
        .then((user) => {
          setAuth(
            {
              id: user.id,
              email: user.email,
              full_name: user.full_name,
              avatar_url: user.avatar_url,
              is_verified: user.is_verified,
              credits: user.credits,
              learning_streak: user.learning_streak,
            },
            token,
            refreshToken
          )
          router.push("/dashboard")
        })
        .catch(() => {
          setError("Failed to complete authentication")
        })
    } else {
      setError("Invalid authentication response")
    }
  }, [searchParams, router, setAuth])

  return (
    <div className="flex min-h-screen items-center justify-center">
      {error ? (
        <div className="text-center">
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => router.push("/login")}
            className="mt-4 text-sm font-medium text-[#2563EB] hover:text-[#1d4ed8]"
          >
            Back to login
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-gray-600">
          <Loader2 className="h-5 w-5 animate-spin" />
          Completing sign in...
        </div>
      )}
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2 text-gray-600">
          <Loader2 className="h-5 w-5 animate-spin" />
          Loading...
        </div>
      </div>
    }>
      <CallbackContent />
    </Suspense>
  )
}
