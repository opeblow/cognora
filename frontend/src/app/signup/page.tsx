"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { authService } from "@/services/auth"
import { useAuthStore } from "@/store/auth"
import { BookOpen } from "lucide-react"
import { toast } from "sonner"
import { motion } from "motion/react"

const signupSchema = z
  .object({
    full_name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Enter a valid email"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })

type SignupForm = z.infer<typeof signupSchema>

export default function SignupPage() {
  const router = useRouter()
  const { setAuth } = useAuthStore()
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupForm>({
    resolver: zodResolver(signupSchema),
  })

  const onSubmit = async (data: SignupForm) => {
    setLoading(true)
    try {
      const response = await authService.signup({
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      })
      setAuth(response.user, response.access_token, response.refresh_token)
      toast.success("Account created! Check your email to verify.")
      router.push("/dashboard")
    } catch (error: unknown) {
      const err = error as { message?: string }
      toast.error(err.message || "Failed to create account")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center px-6">
      <motion.div
        className="w-full max-w-sm"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
      >
        {/* Logo */}
        <div className="mb-10">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-amber flex items-center justify-center rounded-sm">
              <BookOpen className="w-4 h-4 text-ink" strokeWidth={2.5} />
            </div>
            <span className="font-serif text-xl font-semibold text-cream tracking-tight">
              Cognora
            </span>
          </Link>
        </div>

        <h1 className="font-serif text-2xl font-semibold text-cream">
          Create an account
        </h1>
        <p className="mt-2 text-sm text-cream-dim">
          Start your exam preparation journey
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-5">
          <div className="space-y-2">
            <Label htmlFor="full_name" className="text-cream-dim text-xs">
              Full Name
            </Label>
            <Input
              id="full_name"
              placeholder="John Doe"
              {...register("full_name")}
              className="bg-ink-light border-ink-lighter text-cream placeholder:text-cream-dim/40 focus-visible:ring-amber/40 focus-visible:border-amber/60 h-11"
            />
            {errors.full_name && (
              <p className="text-xs text-coral">{errors.full_name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-cream-dim text-xs">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              {...register("email")}
              className="bg-ink-light border-ink-lighter text-cream placeholder:text-cream-dim/40 focus-visible:ring-amber/40 focus-visible:border-amber/60 h-11"
            />
            {errors.email && (
              <p className="text-xs text-coral">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-cream-dim text-xs">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="At least 8 characters"
              {...register("password")}
              className="bg-ink-light border-ink-lighter text-cream placeholder:text-cream-dim/40 focus-visible:ring-amber/40 focus-visible:border-amber/60 h-11"
            />
            {errors.password && (
              <p className="text-xs text-coral">{errors.password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-cream-dim text-xs">
              Confirm Password
            </Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="Repeat your password"
              {...register("confirmPassword")}
              className="bg-ink-light border-ink-lighter text-cream placeholder:text-cream-dim/40 focus-visible:ring-amber/40 focus-visible:border-amber/60 h-11"
            />
            {errors.confirmPassword && (
              <p className="text-xs text-coral">
                {errors.confirmPassword.message}
              </p>
            )}
          </div>

          <motion.button
            type="submit"
            disabled={loading}
            className="w-full bg-amber text-ink font-medium h-11 rounded-sm text-sm hover:bg-amber-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            whileTap={{ scale: 0.98 }}
          >
            {loading ? "Creating account..." : "Create account"}
          </motion.button>
        </form>

        <p className="mt-8 text-center text-sm text-cream-dim">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-amber hover:text-amber-hover transition-colors"
          >
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
