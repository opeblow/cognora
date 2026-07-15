"use client"

import Link from "next/link"
import { motion } from "motion/react"
import {
  BookOpen,
  Brain,
  BarChart3,
  PenLine,
  Zap,
  Target,
  CheckCircle2,
  ArrowRight,
  Star,
} from "lucide-react"
import NotebookAnimation from "@/components/landing/notebook-animation"

const SUBJECTS = [
  "Mathematics",
  "English Language",
  "Physics",
  "Chemistry",
  "Biology",
  "Economics",
  "Government",
  "Literature",
  "Further Mathematics",
  "Agricultural Science",
  "Computer Science",
  "Christian Religious Knowledge",
]

const FEATURES = [
  {
    icon: Brain,
    title: "AI Tutor",
    description:
      "Ask any question and get instant, curriculum-aligned explanations that adapt to your understanding level.",
  },
  {
    icon: PenLine,
    title: "Mock Exams",
    description:
      "Practice with realistic WAEC, JAMB, and NECO-style questions. Timed, scored, and reviewed instantly.",
  },
  {
    icon: BarChart3,
    title: "Progress Tracking",
    description:
      "See exactly where you're strong and where you need work. Every quiz, every exam, every topic tracked.",
  },
  {
    icon: Target,
    title: "Study Plans",
    description:
      "Personalized study schedules that prioritize your weak areas and count down to your exam date.",
  },
  {
    icon: Zap,
    title: "Instant Feedback",
    description:
      "Get detailed explanations for every answer — right or wrong — so you actually learn, not just memorize.",
  },
  {
    icon: BookOpen,
    title: "Complete Syllabus",
    description:
      "Every subject, every topic, every subtopic. Fully covered for WAEC, NECO, GCE, JAMB and Post-UTME.",
  },
]

const STEPS = [
  {
    number: "01",
    title: "Tell us your subjects",
    description:
      "Pick the subjects you're writing. We'll build everything around your actual exam combination.",
  },
  {
    number: "02",
    title: "Learn with the AI tutor",
    description:
      "Ask questions, get explanations, read expanded notes. The tutor knows the syllabus and adapts to you.",
  },
  {
    number: "03",
    title: "Practice and test yourself",
    description:
      "Quizzes after every topic. Full mock exams under timed conditions. Real scoring, real feedback.",
  },
  {
    number: "04",
    title: "Track and improve",
    description:
      "See your progress across every subject. Know exactly what to focus on before exam day.",
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-ink">
      {/* ─── Nav ─── */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-ink/90 backdrop-blur-sm border-b border-ink-lighter/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-amber flex items-center justify-center rounded-sm">
              <BookOpen className="w-4 h-4 text-ink" strokeWidth={2.5} />
            </div>
            <span className="font-serif text-xl font-semibold text-cream tracking-tight">
              Cognora
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link
              href="/login"
              className="text-sm text-cream-dim hover:text-cream transition-colors"
            >
              Log in
            </Link>
            <Link
              href="/signup"
              className="text-sm font-medium bg-amber text-ink px-5 py-2 rounded-sm hover:bg-amber-hover transition-colors"
            >
              Get started
            </Link>
          </div>

          {/* Mobile auth */}
          <div className="flex md:hidden items-center gap-3">
            <Link
              href="/login"
              className="text-sm text-cream-dim"
            >
              Log in
            </Link>
            <Link
              href="/signup"
              className="text-sm font-medium bg-amber text-ink px-4 py-1.5 rounded-sm"
            >
              Sign up
            </Link>
          </div>
        </div>
      </nav>

      {/* ─── Hero ─── */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <motion.h1
              className="font-serif text-4xl sm:text-5xl lg:text-6xl font-semibold text-cream leading-[1.1] tracking-tight text-balance"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
            >
              Learn smarter,
              <br />
              <span className="text-amber">not harder.</span>
            </motion.h1>

            <motion.p
              className="mt-6 text-lg text-cream-dim leading-relaxed max-w-md"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.6,
                ease: [0.25, 0.1, 0.25, 1],
                delay: 0.1,
              }}
            >
              AI-powered exam prep for WAEC, NECO, GCE, JAMB &amp; Post-UTME.
              Personalized tutoring, practice quizzes, and mock exams that adapt
              to how you learn.
            </motion.p>

            <motion.div
              className="mt-10 flex flex-wrap gap-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.6,
                ease: [0.25, 0.1, 0.25, 1],
                delay: 0.2,
              }}
            >
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 bg-amber text-ink font-medium px-7 py-3 rounded-sm hover:bg-amber-hover transition-colors text-sm"
              >
                Get started free
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 border border-ink-lighter text-cream px-7 py-3 rounded-sm hover:border-cream-dim transition-colors text-sm"
              >
                Log in
              </Link>
            </motion.div>
          </div>

          {/* Notebook animation */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.8,
              ease: [0.25, 0.1, 0.25, 1],
              delay: 0.3,
            }}
          >
            <NotebookAnimation />
          </motion.div>
        </div>
      </section>

      {/* ─── Subject Marquee ─── */}
      <section className="py-12 border-y border-ink-lighter/40 overflow-hidden">
        <div className="flex w-fit" style={{ animation: "marquee-scroll 30s linear infinite" }}>
          {[...SUBJECTS, ...SUBJECTS].map((subject, i) => (
            <span
              key={`${subject}-${i}`}
              className="px-6 py-2 text-sm text-cream-dim/70 whitespace-nowrap font-hand text-base"
            >
              {subject}
            </span>
          ))}
        </div>
        <div
          className="flex w-fit mt-3"
          style={{
            animation: "marquee-scroll-reverse 35s linear infinite",
          }}
        >
          {[...SUBJECTS.slice().reverse(), ...SUBJECTS.slice().reverse()].map(
            (subject, i) => (
              <span
                key={`rev-${subject}-${i}`}
                className="px-6 py-2 text-sm text-cream-dim/50 whitespace-nowrap font-hand text-base"
              >
                {subject}
              </span>
            )
          )}
        </div>
      </section>

      {/* ─── Features ─── */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="max-w-lg mb-16">
            <span className="text-amber text-sm font-medium tracking-wide uppercase">
              What you get
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-semibold text-cream mt-3 tracking-tight">
              Everything you need to pass.
            </h2>
            <p className="text-cream-dim mt-4 leading-relaxed">
              No fluff. No filler. Every feature is built around one thing:
              helping you score higher on exam day.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature, i) => (
              <motion.div
                key={feature.title}
                className="p-6 bg-ink-light border border-ink-lighter/50 rounded-sm"
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{
                  duration: 0.5,
                  ease: [0.25, 0.1, 0.25, 1],
                  delay: i * 0.08,
                }}
              >
                <feature.icon className="w-5 h-5 text-amber mb-4" strokeWidth={1.5} />
                <h3 className="font-serif text-lg font-medium text-cream">
                  {feature.title}
                </h3>
                <p className="text-sm text-cream-dim mt-2 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How It Works ─── */}
      <section className="py-24 px-6 bg-ink-light/30">
        <div className="max-w-6xl mx-auto">
          <div className="max-w-lg mb-16">
            <span className="text-amber text-sm font-medium tracking-wide uppercase">
              How it works
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-semibold text-cream mt-3 tracking-tight">
              Four steps to exam success.
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {STEPS.map((step, i) => (
              <motion.div
                key={step.number}
                className="relative"
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{
                  duration: 0.5,
                  ease: [0.25, 0.1, 0.25, 1],
                  delay: i * 0.1,
                }}
              >
                <span className="font-serif text-5xl font-bold text-ink-lighter/80">
                  {step.number}
                </span>
                <h3 className="font-serif text-lg font-medium text-cream mt-3">
                  {step.title}
                </h3>
                <p className="text-sm text-cream-dim mt-2 leading-relaxed">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Testimonial ─── */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="flex justify-center gap-1 mb-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <Star
                key={i}
                className="w-4 h-4 fill-amber text-amber"
              />
            ))}
          </div>
          <blockquote className="font-serif text-xl sm:text-2xl text-cream leading-relaxed text-balance">
            &ldquo;I went from scoring 45% in my practice tests to 78% in my
            actual JAMB exam. The AI tutor explained things in a way my teachers
            never could.&rdquo;
          </blockquote>
          <div className="mt-8">
            <p className="text-cream font-medium text-sm">Adaeze O.</p>
            <p className="text-cream-dim text-sm mt-0.5">
              JAMB 2025 — Scored 298/400
            </p>
          </div>
        </div>
      </section>

      {/* ─── Final CTA ─── */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="font-serif text-3xl sm:text-4xl font-semibold text-cream tracking-tight">
            Ready to start?
          </h2>
          <p className="text-cream-dim mt-4 leading-relaxed">
            Join thousands of students already using Cognora to prepare smarter.
            Free to start — no credit card needed.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 bg-amber text-ink font-medium px-8 py-3 rounded-sm hover:bg-amber-hover transition-colors text-sm"
            >
              Get started free
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="py-12 px-6 border-t border-ink-lighter/40">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-amber flex items-center justify-center rounded-sm">
              <BookOpen className="w-3.5 h-3.5 text-ink" strokeWidth={2.5} />
            </div>
            <span className="font-serif text-lg font-semibold text-cream tracking-tight">
              Cognora
            </span>
          </div>

          <div className="flex items-center gap-6 text-sm text-cream-dim">
            <Link href="/login" className="hover:text-cream transition-colors">
              Log in
            </Link>
            <Link href="/signup" className="hover:text-cream transition-colors">
              Sign up
            </Link>
          </div>

          <p className="text-xs text-cream-dim/50">
            &copy; {new Date().getFullYear()} Cognora. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}
