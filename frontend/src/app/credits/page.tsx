"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/auth"
import { creditService } from "@/services/credits"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Zap, CreditCard, Sparkles, BookOpen, GraduationCap, Brain } from "lucide-react"

const creditCosts = [
  { action: "Ask AI Tutor", cost: 1, icon: Brain, color: "#2563EB" },
  { action: "Generate Quiz", cost: 2, icon: BookOpen, color: "#14B8A6" },
  { action: "Take Mock Exam", cost: 10, icon: GraduationCap, color: "#F59E0B" },
]

export default function CreditsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  const { data } = useQuery({
    queryKey: ["credits"],
    queryFn: creditService.getBalance,
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-4xl">
          <h1 className="text-2xl font-bold text-[#0F172A]">Credits</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your learning credits
          </p>

          <div className="mt-6 grid gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Your Balance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#2563EB]/10">
                    <Zap className="h-8 w-8 text-[#2563EB]" />
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-[#0F172A]">
                      {data?.credits ?? 0}
                    </div>
                    <p className="text-sm text-gray-500">
                      {(data?.weekly_credits_total ?? 50) - (data?.weekly_credits_used ?? 0)} weekly credits remaining
                    </p>
                  </div>
                </div>
                <div className="mt-6 rounded-lg bg-[#F8FAFC] p-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Free weekly credits</span>
                    <span className="font-medium text-[#0F172A]">{data?.weekly_credits_total ?? 50}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Used this week</span>
                    <span className="font-medium text-[#0F172A]">{data?.weekly_credits_used ?? 0}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Remaining this week</span>
                    <span className="font-medium text-[#14B8A6]">
                      {(data?.weekly_credits_total ?? 50) - (data?.weekly_credits_used ?? 0)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Credit Usage</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {creditCosts.map((item) => {
                  const Icon = item.icon
                  return (
                    <div key={item.action} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className="flex h-8 w-8 items-center justify-center rounded-lg"
                          style={{ backgroundColor: `${item.color}15` }}
                        >
                          <Icon className="h-4 w-4" style={{ color: item.color }} />
                        </div>
                        <span className="text-sm text-[#0F172A]">{item.action}</span>
                      </div>
                      <Badge variant="secondary">{item.cost} credit{item.cost > 1 ? "s" : ""}</Badge>
                    </div>
                  )
                })}
              </CardContent>
            </Card>
          </div>

          <div className="mt-8">
            <h2 className="text-lg font-semibold text-[#0F172A]">Transaction History</h2>
            {data?.transactions?.length ? (
              <div className="mt-4 space-y-2">
                {data.transactions.map((tx) => (
                  <Card key={tx.id}>
                    <CardContent className="flex items-center justify-between p-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                            tx.transaction_type === "purchase"
                              ? "bg-green-50"
                              : "bg-gray-50"
                          }`}
                        >
                          <CreditCard
                            className={`h-4 w-4 ${
                              tx.transaction_type === "purchase"
                                ? "text-green-600"
                                : "text-gray-600"
                            }`}
                          />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-[#0F172A]">
                            {tx.description || tx.transaction_type}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(tx.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <span
                        className={`text-sm font-medium ${
                          tx.transaction_type === "purchase"
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {tx.transaction_type === "purchase" ? "+" : ""}
                        {tx.amount}
                      </span>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="mt-4">
                <CardContent className="p-8 text-center">
                  <Sparkles className="mx-auto h-8 w-8 text-gray-300" />
                  <p className="mt-2 text-sm text-gray-500">No transactions yet</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
