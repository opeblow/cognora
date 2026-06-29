"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Sparkles, Calendar } from "lucide-react"
import Link from "next/link"

export default function StudyPlannerPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-4xl">
          <h1 className="text-2xl font-bold text-[#0F172A]">Study Planner</h1>
          <p className="mt-1 text-sm text-gray-600">
            Plan and manage your study schedule
          </p>

          <div className="mt-8">
            <Card>
              <CardContent className="p-12 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[#2563EB]/10">
                  <Sparkles className="h-8 w-8 text-[#2563EB]" />
                </div>
                <h2 className="mt-6 text-xl font-semibold text-[#0F172A]">
                  AI-Powered Study Plans Coming Soon
                </h2>
                <p className="mt-2 text-sm text-gray-600 max-w-md mx-auto">
                  Our AI will generate personalized study plans based on your subjects,
                  target exams, and available time. Get daily and weekly schedules
                  optimized for your learning goals.
                </p>
                <div className="mt-8 flex items-center justify-center gap-4">
                  <Link href="/subjects">
                    <Button variant="outline">
                      Browse Subjects
                    </Button>
                  </Link>
                  <Link href="/dashboard">
                    <Button>
                      Go to Dashboard
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
