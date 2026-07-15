"""Test quiz detail generation - the critical path."""
import httpx, time, sys

BASE = "http://localhost:8000/api"
T = sys.argv[1]
H = {"Authorization": f"Bearer {T}"}

r = httpx.get(f"{BASE}/quizzes", headers=H, timeout=10)
d = r.json()
quizzes = d.get("quizzes") or d.get("data") or []
if not quizzes:
    print("No quizzes found - nothing to test")
    sys.exit(0)

qid = quizzes[0].get("id", "")
print(f"Testing quiz: {qid[:8]}...")

start = time.time()
r2 = httpx.get(f"{BASE}/quizzes/{qid}", headers=H, timeout=120)
elapsed = round(time.time() - start)
print(f"Response time: {elapsed}s")
print(f"Status: {r2.status_code}")

if r2.status_code == 200:
    data = r2.json()
    qs = data.get("questions", [])
    print(f"Questions generated: {len(qs)}")
    for i, q in enumerate(qs[:3]):
        print(f"  Q{i+1}: {q.get('text','')[:70]}")
        opts = q.get("options", [])
        print(f"        Options: {opts}")
else:
    print(f"Error: {r2.text[:500]}")
