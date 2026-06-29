import Link from "next/link"
import { Sparkles, Brain, GraduationCap, BarChart3 } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-gray-100">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#2563EB]">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-semibold text-[#0F172A]">Cognora</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm font-medium text-gray-600 hover:text-gray-900"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="rounded-lg bg-[#2563EB] px-4 py-2 text-sm font-medium text-white hover:bg-[#1d4ed8]"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="mx-auto max-w-7xl px-6 pt-24 pb-16">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-5xl font-bold tracking-tight text-[#0F172A] sm:text-6xl">
              Ace Your Exams with{" "}
              <span className="text-[#2563EB]">AI-Powered</span> Learning
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Prepare for WAEC, NECO, GCE, JAMB, and Post-UTME with personalized
              AI tutoring, practice quizzes, and mock exams.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Link
                href="/signup"
                className="rounded-lg bg-[#2563EB] px-8 py-3 text-base font-medium text-white hover:bg-[#1d4ed8] shadow-sm"
              >
                Start Learning Free
              </Link>
              <Link
                href="/login"
                className="rounded-lg border border-gray-200 bg-white px-8 py-3 text-base font-medium text-gray-900 hover:bg-gray-50"
              >
                Sign In
              </Link>
            </div>
          </div>
        </section>

        <section className="border-t border-gray-100 bg-[#F8FAFC] py-20">
          <div className="mx-auto max-w-7xl px-6">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold text-[#0F172A]">
                Everything you need to succeed
              </h2>
            </div>
            <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <div className="rounded-xl border border-gray-100 bg-white p-8 shadow-sm">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#2563EB]/10">
                  <Brain className="h-6 w-6 text-[#2563EB]" />
                </div>
                <h3 className="mt-6 text-lg font-semibold text-[#0F172A]">AI Tutor</h3>
                <p className="mt-2 text-sm text-gray-600">
                  Ask questions, get explanations, and learn at your own pace with
                  our intelligent AI tutor.
                </p>
              </div>
              <div className="rounded-xl border border-gray-100 bg-white p-8 shadow-sm">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#14B8A6]/10">
                  <GraduationCap className="h-6 w-6 text-[#14B8A6]" />
                </div>
                <h3 className="mt-6 text-lg font-semibold text-[#0F172A]">Mock Exams</h3>
                <p className="mt-2 text-sm text-gray-600">
                  Practice with real exam-style questions for WAEC, NECO, JAMB,
                  and GCE with timed simulations.
                </p>
              </div>
              <div className="rounded-xl border border-gray-100 bg-white p-8 shadow-sm">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#F59E0B]/10">
                  <BarChart3 className="h-6 w-6 text-[#F59E0B]" />
                </div>
                <h3 className="mt-6 text-lg font-semibold text-[#0F172A]">Analytics</h3>
                <p className="mt-2 text-sm text-gray-600">
                  Track your progress, identify weak areas, and improve your
                  performance with detailed insights.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
