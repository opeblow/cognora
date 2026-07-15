"use client"

import { useState, useEffect, useCallback } from "react"
import { motion, AnimatePresence } from "motion/react"

const EXAMPLE_NOTES = [
  {
    subject: "Physics",
    lines: [
      "Newton's Second Law: F = ma",
      "Force equals mass times acceleration",
      "The net force on an object determines",
      "how its velocity changes over time.",
    ],
  },
  {
    subject: "Biology",
    lines: [
      "Mitochondria are the powerhouse",
      "of the cell. They convert glucose",
      "into ATP through cellular respiration,",
      "fueling nearly every biological process.",
    ],
  },
  {
    subject: "Economics",
    lines: [
      "Supply and demand determine price.",
      "When demand exceeds supply, prices rise.",
      "When supply exceeds demand, prices fall.",
      "Equilibrium is where they meet.",
    ],
  },
  {
    subject: "Literature",
    lines: [
      "A metaphor compares two unlike things",
      "without using like or as. The world",
      "is a stage — we are merely players,",
      "each performing our brief part.",
    ],
  },
]

const LINE_DURATION = 1400
const LINE_GAP = 300
const PAUSE_AFTER = 1800
const PAGE_TURN = 800

export default function NotebookAnimation() {
  const [noteIndex, setNoteIndex] = useState(0)
  const [currentLine, setCurrentLine] = useState(0)
  const [phase, setPhase] = useState<"writing" | "pause" | "turning">("writing")
  const [pencilX, setPencilX] = useState(0)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 640)
    check()
    window.addEventListener("resize", check)
    return () => window.removeEventListener("resize", check)
  }, [])

  const note = EXAMPLE_NOTES[noteIndex]
  const totalLines = note.lines.length
  const notebookWidth = isMobile ? 260 : 340

  const advance = useCallback(() => {
    if (phase === "writing") {
      if (currentLine < totalLines - 1) {
        setCurrentLine((c) => c + 1)
      } else {
        setPhase("pause")
      }
    } else if (phase === "pause") {
      setPhase("turning")
    } else if (phase === "turning") {
      setNoteIndex((i) => (i + 1) % EXAMPLE_NOTES.length)
      setCurrentLine(0)
      setPhase("writing")
    }
  }, [phase, currentLine, totalLines])

  useEffect(() => {
    const prefersReduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches
    if (prefersReduced) return

    let timeout: ReturnType<typeof setTimeout>
    if (phase === "writing") {
      timeout = setTimeout(advance, LINE_DURATION + LINE_GAP)
    } else if (phase === "pause") {
      timeout = setTimeout(advance, PAUSE_AFTER)
    } else {
      timeout = setTimeout(advance, PAGE_TURN)
    }
    return () => clearTimeout(timeout)
  }, [phase, currentLine, advance])

  useEffect(() => {
    if (phase !== "writing") {
      setPencilX(0)
      return
    }
    setPencilX(0)
    const start = Date.now()
    let raf: number
    const animate = () => {
      const elapsed = Date.now() - start
      const progress = Math.min(elapsed / LINE_DURATION, 1)
      setPencilX(progress * (notebookWidth - 40))
      if (progress < 1) {
        raf = requestAnimationFrame(animate)
      }
    }
    raf = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(raf)
  }, [phase, currentLine, notebookWidth])

  return (
    <div className="relative w-full flex justify-center" aria-hidden="true">
      <AnimatePresence mode="wait">
        <motion.div
          key={noteIndex}
          initial={phase === "turning" ? { rotateY: -90, opacity: 0 } : { opacity: 1 }}
          animate={{ rotateY: 0, opacity: 1 }}
          exit={{ rotateY: -90, opacity: 0 }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
          className="relative"
          style={{ perspective: "800px" }}
        >
          {/* Notebook */}
          <div
            className="relative bg-paper rounded-sm shadow-2xl overflow-hidden"
            style={{ width: notebookWidth, height: isMobile ? 220 : 280 }}
          >
            {/* Spine line */}
            <div className="absolute left-8 top-0 bottom-0 w-px bg-amber/30" />

            {/* Ruled lines */}
            {Array.from({ length: 12 }).map((_, i) => (
              <div
                key={i}
                className="absolute left-0 right-0 h-px bg-moss/15"
                style={{ top: 36 + i * (isMobile ? 16 : 20) }}
              />
            ))}

            {/* Red margin line */}
            <div className="absolute left-12 top-0 bottom-0 w-px bg-coral/20" />

            {/* Subject label */}
            <div
              className="absolute top-3 right-4 font-hand text-moss/60"
              style={{ fontSize: isMobile ? 13 : 15 }}
            >
              {note.subject}
            </div>

            {/* Written lines */}
            <div className="absolute top-5 left-14 right-4">
              {note.lines.map((line, i) => (
                <div
                  key={`${noteIndex}-${i}`}
                  className="relative overflow-hidden"
                  style={{
                    height: isMobile ? 16 : 20,
                    marginBottom: isMobile ? 4 : 4,
                    opacity: i <= currentLine ? 1 : 0,
                    transition: "opacity 0.2s",
                  }}
                >
                  <span
                    className="font-hand text-ink block whitespace-nowrap"
                    style={{
                      fontSize: isMobile ? 14 : 16,
                      lineHeight: `${isMobile ? 16 : 20}px`,
                    }}
                  >
                    {line}
                  </span>
                  {/* Writing reveal mask */}
                  {i === currentLine && phase === "writing" && (
                    <motion.div
                      className="absolute inset-0 bg-paper"
                      initial={{ width: "100%" }}
                      animate={{ width: "0%" }}
                      transition={{
                        duration: LINE_DURATION / 1000,
                        ease: "linear",
                      }}
                      style={{ left: "auto", right: 0 }}
                    />
                  )}
                </div>
              ))}
            </div>

            {/* Pencil */}
            {phase === "writing" && (
              <motion.div
                className="absolute z-10"
                style={{
                  top: 26 + currentLine * (isMobile ? 20 : 24),
                  left: 44 + pencilX,
                }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
              >
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  style={{ transform: "rotate(-45deg)" }}
                >
                  <rect x="6" y="2" width="4" height="16" rx="1" fill="#C9932E" />
                  <rect x="7" y="2" width="2" height="16" rx="0.5" fill="#B8841F" />
                  <polygon points="6,18 10,18 8,22" fill="#2A3D33" />
                  <rect x="6" y="2" width="4" height="2" rx="0.5" fill="#4B6152" />
                </svg>
              </motion.div>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
