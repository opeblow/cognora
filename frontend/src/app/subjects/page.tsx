"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { subjectService } from "@/services/subjects"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen } from "lucide-react"
import Link from "next/link"
import { SUBJECT_CATEGORIES } from "@/constants"

const categoryIcons: Record<string, string> = {
  Science: "#2563EB",
  Commercial: "#14B8A6",
  Arts: "#F59E0B",
}

export default function SubjectsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data, isLoading } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => subjectService.getAll(),
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000,
  })

  if (!isAuthenticated) return null

  const subjectsByCategory = SUBJECT_CATEGORIES.map((cat) => ({
    ...cat,
    subjects: data?.subjects?.filter((s) => s.category === cat.value) || [],
  }))

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-6xl">
          <h1 className="text-2xl font-bold text-[#0F172A]">Subjects</h1>
          <p className="mt-1 text-sm text-gray-600">
            Choose a subject to start learning
          </p>

          {isLoading && (
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-12 w-12 rounded-lg bg-gray-100" />
                  <div className="mt-4 h-5 w-32 rounded bg-gray-100" />
                  <div className="mt-2 h-4 w-48 rounded bg-gray-100" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!isLoading && (
        <div className="mt-8 space-y-10">
            {subjectsByCategory.map((category) => (
              <div key={category.value}>
                <h2 className="text-lg font-semibold text-[#0F172A]">
                  {category.label}
                </h2>
                <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {category.subjects.map((subject) => (
                    <Link key={subject.id} href={`/subjects/${subject.slug}`}>
                      <Card className="cursor-pointer transition-shadow hover:shadow-md">
                        <CardContent className="p-6">
                          <div
                            className="flex h-12 w-12 items-center justify-center rounded-lg"
                            style={{
                              backgroundColor: `${subject.color || categoryIcons[category.value]}15`,
                            }}
                          >
                            <BookOpen
                              className="h-6 w-6"
                              style={{ color: subject.color || categoryIcons[category.value] }}
                            />
                          </div>
                          <h3 className="mt-4 font-semibold text-[#0F172A]">
                            {subject.name}
                          </h3>
                          {subject.description && (
                            <p className="mt-1 text-xs text-gray-500">
                              {subject.description}
                            </p>
                          )}
                          <Badge className="mt-3" variant="secondary">
                            {subject.category}
                          </Badge>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
        </div>
      </main>
    </div>
  )
}
