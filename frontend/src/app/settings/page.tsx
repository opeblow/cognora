"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { authService } from "@/services/auth"
import { toast } from "sonner"
import { User, Shield } from "lucide-react"

const passwordSchema = z.object({
  current_password: z.string().min(1, "Current password is required"),
  new_password: z.string().min(8, "New password must be at least 8 characters"),
})

type PasswordForm = z.infer<typeof passwordSchema>

export default function SettingsPage() {
  const router = useRouter()
  const { isAuthenticated, user } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
  })

  const onChangePassword = async (data: PasswordForm) => {
    try {
      await authService.changePassword(data)
      toast.success("Password changed successfully")
      reset()
    } catch (error: unknown) {
      const err = error as { message?: string }
      toast.error(err.message || "Failed to change password")
    }
  }

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-2xl">
          <h1 className="text-2xl font-bold text-[#0F172A]">Settings</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your account settings
          </p>

          <div className="mt-8 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5 text-[#2563EB]" />
                  Profile
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label>Name</Label>
                    <p className="mt-1 text-sm font-medium text-[#0F172A]">
                      {user?.full_name}
                    </p>
                  </div>
                  <div>
                    <Label>Email</Label>
                    <p className="mt-1 text-sm font-medium text-[#0F172A]">
                      {user?.email}
                    </p>
                  </div>
                  <div>
                    <Label>Account Status</Label>
                    <p className="mt-1 text-sm font-medium text-green-600">
                      {user?.is_verified ? "Verified" : "Not verified"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-[#2563EB]" />
                  Change Password
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit(onChangePassword)} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current_password">Current Password</Label>
                    <Input
                      id="current_password"
                      type="password"
                      {...register("current_password")}
                    />
                    {errors.current_password && (
                      <p className="text-xs text-red-500">{errors.current_password.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new_password">New Password</Label>
                    <Input
                      id="new_password"
                      type="password"
                      {...register("new_password")}
                    />
                    {errors.new_password && (
                      <p className="text-xs text-red-500">{errors.new_password.message}</p>
                    )}
                  </div>
                  <Button type="submit">Update Password</Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
