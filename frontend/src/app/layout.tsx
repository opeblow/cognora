import type { Metadata } from "next"
import { Inter, Fraunces, Caveat } from "next/font/google"
import "./globals.css"
import { Providers } from "@/lib/providers"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
})

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
})

const caveat = Caveat({
  subsets: ["latin"],
  variable: "--font-hand",
  display: "swap",
})

export const metadata: Metadata = {
  title: "Cognora — Learn Smarter, Not Harder",
  description:
    "AI-powered exam prep for WAEC, NECO, GCE, JAMB & Post-UTME. Personalized tutoring, practice quizzes, and mock exams that adapt to you.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${fraunces.variable} ${caveat.variable} font-sans`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
