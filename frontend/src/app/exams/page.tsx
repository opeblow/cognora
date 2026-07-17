"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { examService } from "@/services/exams"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { GraduationCap, Clock } from "lucide-react"
import Link from "next/link"

export default function ExamsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data } = useQuery({
    queryKey: ["exams"],
    queryFn: () => examService.getAll(),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-4xl">
          <h1 className="text-2xl font-bold text-[#0F172A]">Mock Exams</h1>
          <p className="mt-1 text-sm text-gray-600">
            Simulate real WAEC, NECO, GCE, and JAMB exams
          </p>

          <div className="mt-6 space-y-3">
            {data?.exams?.map((exam) => (
              <Link key={exam.id} href={`/exams/${exam.id}`}>
                <Card className="cursor-pointer transition-shadow hover:shadow-md">
                  <CardContent className="flex items-center justify-between p-5">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#F59E0B]/10">
                        <GraduationCap className="h-6 w-6 text-[#F59E0B]" />
                      </div>
                        <div>
                        <h3 className="font-semibold text-[#0F172A]">{exam.title}</h3>
                        <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                          <Badge variant="accent">{exam.exam_type}</Badge>
                          {exam.year && <span>{exam.year}</span>}
                          {exam.total_questions && (
                            <span>{exam.total_questions} questions</span>
                          )}
                          {exam.time_limit_minutes && (
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {exam.time_limit_minutes} min
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      Start Exam
                    </Button>
                  </CardContent>
                </Card>
              </Link>
            ))}
            {(!data?.exams || data.exams.length === 0) && (
              <Card>
                <CardContent className="p-8 text-center">
                  <p className="text-gray-500">No exams available yet.</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
