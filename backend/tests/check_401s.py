"""Check why some endpoints return 401 despite valid token."""
import httpx, sys

BASE = "http://localhost:8000/api"
T = sys.argv[1]
H = {"Authorization": f"Bearer {T}"}

endpoints = [
    "/study-planner",
    "/study-planner/today",
    "/study-planner/calendar",
    "/credits/balance",
    "/settings",
    "/analytics/dashboard",
    "/analytics/overview",
    "/analytics/accuracy-trends",
    "/flashcards",
    "/flashcards/generate",
    "/live",
    "/live/rooms",
    "/issues",
    "/content/syllabus/WAEC/Mathematics",
    "/files",
]

for ep in endpoints:
    method = "POST" if "generate" in ep or ep == "/issues" or ep == "/live/rooms" else "GET"
    try:
        if method == "GET":
            r = httpx.get(f"{BASE}{ep}", headers=H, timeout=10)
        else:
            r = httpx.post(f"{BASE}{ep}", headers=H, json={}, timeout=10)
        s = "PASS" if r.status_code < 400 else f"FAIL ({r.status_code})"
        det = str(r.text)[:150].replace("\n"," ")
        print(f"  [{s}] {method} {ep} -> {r.status_code}: {det}")
    except Exception as e:
        print(f"  [ERR] {method} {ep} -> {e}")
