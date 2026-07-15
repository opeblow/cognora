import { describe, it, expect } from "vitest"
import {
  cn,
  formatDate,
  formatTime,
  getInitials,
  getCreditCost,
  getDifficultyColor,
  getScoreColor,
} from "@/lib/utils"

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("px-4", "py-2")).toBe("px-4 py-2")
  })

  it("handles empty inputs", () => {
    expect(cn()).toBe("")
  })
})

describe("formatDate", () => {
  it("formats a date string", () => {
    const result = formatDate("2026-07-03T12:00:00Z")
    expect(result).toContain("Jul")
    expect(result).toContain("2026")
  })
})

describe("formatTime", () => {
  it("formats seconds into m:ss", () => {
    expect(formatTime(125)).toBe("2:05")
  })

  it("handles zero", () => {
    expect(formatTime(0)).toBe("0:00")
  })

  it("pads seconds", () => {
    expect(formatTime(67)).toBe("1:07")
  })
})

describe("getInitials", () => {
  it("returns initials from full name", () => {
    expect(getInitials("John Doe")).toBe("JD")
  })

  it("handles single name", () => {
    expect(getInitials("Alice")).toBe("A")
  })

  it("limits to two characters", () => {
    expect(getInitials("John Michael Doe")).toBe("JM")
  })

  it("handles empty string", () => {
    expect(getInitials("")).toBe("")
  })
})

describe("getCreditCost", () => {
  it("returns cost for known actions", () => {
    expect(getCreditCost("ai_ask")).toBe(1)
    expect(getCreditCost("generate_quiz")).toBe(2)
    expect(getCreditCost("mock_exam")).toBe(10)
  })

  it("returns 0 for unknown actions", () => {
    expect(getCreditCost("unknown")).toBe(0)
  })
})

describe("getDifficultyColor", () => {
  it("returns green for easy", () => {
    expect(getDifficultyColor("easy")).toContain("green")
  })

  it("returns yellow for medium", () => {
    expect(getDifficultyColor("medium")).toContain("yellow")
  })

  it("returns red for hard", () => {
    expect(getDifficultyColor("hard")).toContain("red")
  })

  it("returns gray for unknown", () => {
    expect(getDifficultyColor("unknown")).toContain("gray")
  })

  it("handles case insensitivity", () => {
    expect(getDifficultyColor("EASY")).toContain("green")
  })
})

describe("getScoreColor", () => {
  it("returns green for >= 70", () => {
    expect(getScoreColor(70)).toBe("text-green-600")
    expect(getScoreColor(100)).toBe("text-green-600")
  })

  it("returns yellow for >= 50", () => {
    expect(getScoreColor(50)).toBe("text-yellow-600")
    expect(getScoreColor(69)).toBe("text-yellow-600")
  })

  it("returns red for < 50", () => {
    expect(getScoreColor(0)).toBe("text-red-600")
    expect(getScoreColor(49)).toBe("text-red-600")
  })
})
