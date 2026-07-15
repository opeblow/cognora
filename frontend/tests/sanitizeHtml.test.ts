import { describe, it, expect, vi, afterEach } from "vitest"

vi.stubGlobal("window", {})

const { sanitizeHtml } = await import("@/lib/sanitizeHtml")

afterEach(() => {
  vi.restoreAllMocks()
})

describe("sanitizeHtml", () => {
  it("allows safe HTML tags", () => {
    const html = '<p>Hello <strong>world</strong></p>'
    expect(sanitizeHtml(html)).toContain("<p>")
    expect(sanitizeHtml(html)).toContain("<strong>")
  })

  it("strips script tags", () => {
    const html = '<p>Safe</p><script>alert("xss")</script>'
    const result = sanitizeHtml(html)
    expect(result).not.toContain("<script>")
    expect(result).toContain("Safe")
  })

  it("strips onclick event handlers", () => {
    const html = '<p onclick="alert(1)">Click me</p>'
    const result = sanitizeHtml(html)
    expect(result).not.toContain("onclick")
  })

  it("allows href on anchor tags with safe protocols", () => {
    const html = '<a href="https://example.com">Link</a>'
    const result = sanitizeHtml(html)
    expect(result).toContain("href")
    expect(result).toContain("https://example.com")
  })

  it("strips javascript: hrefs", () => {
    const html = '<a href="javascript:alert(1)">Link</a>'
    const result = sanitizeHtml(html)
    expect(result).not.toContain("javascript:")
  })

  it("strips data: hrefs", () => {
    const html = '<a href="data:text/html,<script>alert(1)</script>">Link</a>'
    const result = sanitizeHtml(html)
    expect(result).not.toContain("data:")
  })

  it("allows mailto: hrefs", () => {
    const html = '<a href="mailto:test@example.com">Email</a>'
    const result = sanitizeHtml(html)
    expect(result).toContain("mailto:")
  })

  it("allows list elements", () => {
    const html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
    const result = sanitizeHtml(html)
    expect(result).toContain("<ul>")
    expect(result).toContain("<li>")
  })

  it("allows heading elements", () => {
    const html = "<h1>Title</h1><h2>Subtitle</h2>"
    const result = sanitizeHtml(html)
    expect(result).toContain("<h1>")
    expect(result).toContain("<h2>")
  })

  it("allows code and pre elements", () => {
    const html = "<pre><code>const x = 1;</code></pre>"
    const result = sanitizeHtml(html)
    expect(result).toContain("<pre>")
    expect(result).toContain("<code>")
  })

  it("strips div and span tags but keeps content", () => {
    const html = '<div class="evil"><span style="color:red">Text</span></div>'
    const result = sanitizeHtml(html)
    expect(result).not.toContain("<div>")
    expect(result).not.toContain("<span>")
    expect(result).toContain("Text")
  })

  it("strips unknown attributes", () => {
    const html = '<p style="background:url(evil)" data-x="y">Content</p>'
    const result = sanitizeHtml(html)
    expect(result).not.toContain("style")
    expect(result).not.toContain("data-x")
  })

  it("returns empty string on server (no window)", () => {
    const originalWindow = globalThis.window
    // @ts-expect-error testing SSR
    delete globalThis.window
    expect(sanitizeHtml("<p>test</p>")).toBe("")
    globalThis.window = originalWindow
  })
})
