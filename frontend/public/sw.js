const CACHE_VERSION = "cognora-v2"
const STATIC_CACHE = `${CACHE_VERSION}-static`
const API_CACHE = `${CACHE_VERSION}-api`
const PAGE_CACHE = `${CACHE_VERSION}-pages`

const CACHE_TTL = {
  api_default: 5 * 60 * 1000,     // 5 minutes — most API data
  api_heavy: 30 * 60 * 1000,      // 30 minutes — AI-generated content
  page: 30 * 60 * 1000,           // 30 minutes — page shells
  static: 7 * 24 * 60 * 60 * 1000, // 7 days — static assets
}

const HEAVY_API_PATHS = ["/api/ai/", "/api/textbook/", "/api/flashcards/generate"]

const STATIC_ASSETS = [
  "/",
  "/dashboard",
  "/subjects",
  "/ai-tutor",
  "/quizzes",
  "/flashcards",
  "/study-planner",
  "/analytics",
  "/past-questions",
  "/study-groups",
]

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
  )
  self.skipWaiting()
})

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => !k.startsWith(CACHE_VERSION))
          .map((k) => caches.delete(k))
      )
    )
  )
  self.clients.claim()
})

function stampCacheDate(response, ttl) {
  const cloned = response.clone()
  const headers = new Headers(cloned.headers)
  headers.set("sw-cache-date", String(Date.now()))
  headers.set("sw-cache-ttl", String(ttl))
  return new Response(cloned.body, {
    status: cloned.status,
    statusText: cloned.statusText,
    headers,
  })
}

function isExpired(response) {
  const dateHeader = response.headers.get("sw-cache-date")
  const ttlHeader = response.headers.get("sw-cache-ttl")
  if (!dateHeader) return true
  const cachedAt = parseInt(dateHeader, 10)
  const ttl = ttlHeader ? parseInt(ttlHeader, 10) : CACHE_TTL.api_default
  return Date.now() - cachedAt > ttl
}

function getCacheTTL(pathname) {
  if (HEAVY_API_PATHS.some((p) => pathname.startsWith(p))) {
    return CACHE_TTL.api_heavy
  }
  return CACHE_TTL.api_default
}

function isCacheableAPI(response, pathname) {
  if (!response.ok) return false
  if (pathname.includes("/auth/")) return false
  if (pathname.includes("/submit")) return false
  if (pathname.includes("/start")) return false
  if (pathname.includes("/payments/")) return false
  return true
}

self.addEventListener("fetch", (event) => {
  const { request } = event
  if (request.method !== "GET") return

  const url = new URL(request.url)

  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      (async () => {
        try {
          const response = await fetch(request)
          if (isCacheableAPI(response, url.pathname)) {
            const ttl = getCacheTTL(url.pathname)
            const stamped = stampCacheDate(response, ttl)
            const cache = await caches.open(API_CACHE)
            cache.put(request, stamped)

            setTimeout(() => {
              cache.delete(request)
            }, ttl)
          }
          return response
        } catch {
          const cache = await caches.open(API_CACHE)
          const cached = await cache.match(request)
          if (cached && !isExpired(cached)) {
            return cached
          }
          return new Response(JSON.stringify({ error: "Offline" }), {
            status: 503,
            headers: { "Content-Type": "application/json" },
          })
        }
      })()
    )
    return
  }

  event.respondWith(
    (async () => {
      const cache = await caches.open(PAGE_CACHE)
      const cached = await cache.match(request)

      const fetched = fetch(request).then((response) => {
        if (response.ok) {
          const stamped = stampCacheDate(response, CACHE_TTL.page)
          cache.put(request, stamped)
        }
        return response
      }).catch(() => cached)

      if (cached) {
        const cachedAt = parseInt(cached.headers.get("sw-cache-date") || "0", 10)
        const ttl = parseInt(cached.headers.get("sw-cache-ttl") || String(CACHE_TTL.page), 10)
        if (Date.now() - cachedAt > ttl) {
          return fetched
        }
        fetched.catch(() => {})
        return cached
      }

      return fetched
    })()
  )
})
