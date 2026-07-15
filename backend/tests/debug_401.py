"""Debug why routes return 401 with identical header pattern."""
import httpx, sys

BASE = "http://localhost:8000/api"
T = sys.argv[1]

# Test the exact same header
H = {"Authorization": f"Bearer {T}"}

# Working routes
for path in ["/auth/me", "/dashboard", "/subjects", "/quizzes"]:
    r = httpx.get(f"{BASE}{path}", headers=H, timeout=10)
    print(f"GET {path}: {r.status_code} {str(r.text)[:80]}")

# Non-working routes
for path in ["/study-planner", "/credits/balance", "/settings", "/analytics/dashboard"]:
    r = httpx.get(f"{BASE}{path}", headers=H, timeout=10)
    print(f"GET {path}: {r.status_code} {str(r.text)[:80]}")

# Try sending via raw bearer
H2 = {"Authorization": f"Bearer {T}", "Content-Type": "application/json"}
for path in ["/study-planner", "/credits/balance"]:
    r = httpx.get(f"{BASE}{path}", headers=H2, timeout=10)
    print(f"GET {path} (with CT): {r.status_code} {str(r.text)[:80]}")
