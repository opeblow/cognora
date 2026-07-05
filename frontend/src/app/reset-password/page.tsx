"use client"

import { useState, useEffect, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { authService } from "@/services/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles, Loader2, Eye, EyeOff, CheckCircle2 } from "lucide-react"
import { toast } from "sonner"
import Link from "next/link"

function ResetPasswordForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get("token")

  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (!token) {
      toast.error("Invalid reset link")
    }
  }, [token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token) {
      toast.error("Missing reset token")
      return
    }
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters")
      return
    }
    if (password !== confirmPassword) {
      toast.error("Passwords do not match")
      return
    }
    setSubmitting(true)
    try {
      await authService.resetPassword({ token, password })
      setSuccess(true)
      toast.success("Password reset successfully!")
    } catch (err: unknown) {
      const error = err as { message?: string }
      toast.error(error.message || "Failed to reset password")
    } finally {
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC]">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <CheckCircle2 className="mx-auto mb-4 h-12 w-12 text-green-500" />
            <h2 className="mb-2 text-xl font-bold text-[#0F172A]">Password Reset Complete</h2>
            <p className="mb-6 text-sm text-gray-500">Your password has been successfully reset.</p>
            <Button className="w-full" onClick={() => router.push("/login")}>
              Sign In
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC]">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <h2 className="mb-2 text-xl font-bold text-[#0F172A]">Invalid Link</h2>
            <p className="mb-6 text-sm text-gray-500">This password reset link is invalid or has expired.</p>
            <Button className="w-full" onClick={() => router.push("/forgot-password")}>
              Request New Link
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC]">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[#2563EB]">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <CardTitle>Reset your password</CardTitle>
          <p className="mt-2 text-sm text-gray-500">Enter your new password below.</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Input
                type={showPassword ? "text" : "password"}
                placeholder="New password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={submitting}
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            <Input
              type="password"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={submitting}
            />
            <Button type="submit" className="w-full" disabled={submitting || !password || !confirmPassword}>
              {submitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Reset Password
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-gray-500">
            <Link href="/login" className="text-[#2563EB] hover:underline">Back to sign in</Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC]">
        <Loader2 className="h-8 w-8 animate-spin text-[#2563EB]" />
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  )
}
