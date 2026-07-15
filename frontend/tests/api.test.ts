import { describe, it, expect, vi, beforeEach } from "vitest"

const mockFetch = vi.fn()
vi.stubGlobal("fetch", mockFetch)

import { api } from "@/services/api"

beforeEach(() => {
  mockFetch.mockReset()
  localStorage.clear()
})

function jsonResponse(data: unknown, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
  } as Response)
}

function errorResponse(detail: string, status = 400) {
  return Promise.resolve({
    ok: false,
    status,
    json: () => Promise.resolve({ detail }),
  } as Response)
}

describe("api.get", () => {
  it("sends GET request with correct URL", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ ok: true }))
    const result = await api.get("/health")
    expect(mockFetch).toHaveBeenCalledTimes(1)
    const [url, opts] = mockFetch.mock.calls[0]
    expect(url).toBe("http://localhost:8000/api/health")
    expect(opts.method).toBeUndefined()
    expect(result).toEqual({ ok: true })
  })

  it("includes Authorization header when token exists", async () => {
    localStorage.setItem("token", "test-token-abc")
    mockFetch.mockReturnValueOnce(jsonResponse({ data: 1 }))
    await api.get("/me")
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.headers["Authorization"]).toBe("Bearer test-token-abc")
  })

  it("does not include Authorization header when no token", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ data: 1 }))
    await api.get("/me")
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.headers["Authorization"]).toBeUndefined()
  })
})

describe("api.post", () => {
  it("sends POST with JSON body", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ id: 1 }))
    await api.post("/items", { name: "test" })
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.method).toBe("POST")
    expect(opts.body).toBe('{"name":"test"}')
    expect(opts.headers["Content-Type"]).toBe("application/json")
  })

  it("sends POST without body when data is undefined", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ ok: true }))
    await api.post("/action")
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.body).toBeUndefined()
  })
})

describe("api.put and api.patch", () => {
  it("sends PUT with correct method", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ updated: true }))
    await api.put("/items/1", { name: "new" })
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.method).toBe("PUT")
    expect(opts.body).toBe('{"name":"new"}')
  })

  it("sends PATCH with correct method", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ patched: true }))
    await api.patch("/items/1", { name: "patched" })
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.method).toBe("PATCH")
  })
})

describe("api.delete", () => {
  it("sends DELETE request", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ deleted: true }))
    await api.delete("/items/1")
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.method).toBe("DELETE")
  })
})

describe("error handling", () => {
  it("throws ApiError with status and detail on non-ok response", async () => {
    mockFetch.mockReturnValueOnce(errorResponse("Not found", 404))
    await expect(api.get("/missing")).rejects.toThrow("Not found")
  })

  it("uses fallback message when response has no JSON detail", async () => {
    mockFetch.mockReturnValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.reject(new Error("bad json")),
    } as Response)
    await expect(api.get("/crash")).rejects.toThrow("Request failed")
  })
})

describe("401 handling", () => {
  it("does not call refresh for auth endpoints", async () => {
    localStorage.setItem("token", "expired")
    localStorage.setItem("refreshToken", "refresh-abc")
    mockFetch.mockReturnValueOnce(errorResponse("Unauthorized", 401))

    await expect(api.post("/auth/login", { email: "a@b.com", password: "x" })).rejects.toThrow()
    expect(mockFetch).toHaveBeenCalledTimes(1)
  })

  it("skips refresh when no refreshToken in storage", async () => {
    localStorage.setItem("token", "expired")
    mockFetch.mockReturnValueOnce(errorResponse("Unauthorized", 401))

    await expect(api.get("/protected")).rejects.toThrow()
    expect(mockFetch).toHaveBeenCalledTimes(1)
  })
})

describe("request timeout", () => {
  it("passes abort signal to fetch", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ ok: true }))
    await api.get("/endpoint")
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.signal).toBeInstanceOf(AbortSignal)
  })
})
