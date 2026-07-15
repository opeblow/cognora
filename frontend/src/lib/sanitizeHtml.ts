const ALLOWED_TAGS = new Set(["p", "br", "strong", "em", "b", "i", "u", "h1", "h2", "h3", "h4", "ul", "ol", "li", "blockquote", "pre", "code", "table", "thead", "tbody", "tr", "th", "td", "hr", "a"])
const ALLOWED_ATTRS = new Set(["href", "title"])

/** Sanitizes generated lesson HTML before it reaches dangerouslySetInnerHTML. */
export function sanitizeHtml(html: string): string {
  if (typeof window === "undefined") return ""
  const parsed = new DOMParser().parseFromString(html, "text/html")
  for (const element of Array.from(parsed.body.querySelectorAll("*"))) {
    if (!ALLOWED_TAGS.has(element.tagName.toLowerCase())) {
      element.replaceWith(...Array.from(element.childNodes))
      continue
    }
    for (const attribute of Array.from(element.attributes)) {
      const name = attribute.name.toLowerCase()
      const value = attribute.value.trim()
      const safeHref = name === "href" && /^(https?:|mailto:|#|\/)/i.test(value)
      if (!ALLOWED_ATTRS.has(name) || (name === "href" && !safeHref)) element.removeAttribute(attribute.name)
    }
  }
  return parsed.body.innerHTML
}
