"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/store/auth"
import { useState, useEffect } from "react"
import {
  LayoutDashboard,
  BookOpen,
  GraduationCap,
  Brain,
  FileQuestion,
  BarChart3,
  Sparkles,
  CreditCard,
  Settings,
  LogOut,
  RotateCcw,
  Users,
  Video,
  Mic,
  Menu,
  X,
  ClipboardList,
} from "lucide-react"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/subjects", label: "Subjects", icon: BookOpen },
  { href: "/ai-tutor", label: "AI Tutor", icon: Brain },
  { href: "/quizzes", label: "Quizzes", icon: FileQuestion },
  { href: "/exams", label: "Mock Exams", icon: GraduationCap },
  { href: "/past-questions", label: "Past Questions", icon: ClipboardList },
  { href: "/flashcards", label: "Flashcards", icon: RotateCcw },
  { href: "/study-planner", label: "Study Planner", icon: Sparkles },
  { href: "/study-groups", label: "Study Groups", icon: Users },
  { href: "/live", label: "Live Teaching", icon: Video },
  { href: "/record", label: "Audio Recording", icon: Mic },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/credits", label: "Credits", icon: CreditCard },
  { href: "/settings", label: "Settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const { logout } = useAuthStore()
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    setMobileOpen(false)
  }, [pathname])

  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = ""
    }
    return () => { document.body.style.overflow = "" }
  }, [mobileOpen])

  return (
    <>
      <button
        onClick={() => setMobileOpen(true)}
        className="fixed left-4 top-4 z-50 flex h-10 w-10 items-center justify-center rounded-lg bg-white shadow-md border border-gray-100 lg:hidden"
      >
        <Menu className="h-5 w-5 text-[#0F172A]" />
      </button>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed left-0 top-0 z-50 flex h-screen w-64 flex-col border-r border-gray-100 bg-white transition-transform duration-200",
          "lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-gray-100 px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#2563EB]">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-semibold text-[#0F172A]">Cognora</span>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-gray-100 lg:hidden"
          >
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-4">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname.startsWith(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-[#2563EB]/10 text-[#2563EB]"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="truncate">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="border-t border-gray-100 p-4">
          <button
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50 hover:text-red-600"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </button>
        </div>
      </aside>
    </>
  )
}
