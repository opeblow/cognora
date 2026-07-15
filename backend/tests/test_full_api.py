"""Full API smoke test - pass your token as argument."""
import httpx, sys

BASE = "http://localhost:8000/api"

if len(sys.argv) < 2:
    print("Usage: python test_full_api.py YOUR_TOKEN")
    print("Get your token from localStorage -> token in browser devtools")
    sys.exit(1)

token = sys.argv[1]
headers = {"Authorization": f"Bearer {token}"}

def log(label, status, data, max_len=150):
    status_str = "PASS" if 200 <= status < 400 else "FAIL"
    print(f"[{status_str}] {label} -> {status}")
    text = str(data)
    print(f"  {text[:max_len]}")
    return status < 400

tests = [
    ("Dashboard", lambda: httpx.get(f"{BASE}/dashboard", headers=headers, timeout=10)),
    ("Subjects", lambda: httpx.get(f"{BASE}/subjects", headers=headers, timeout=10)),
    ("Quizzes list", lambda: httpx.get(f"{BASE}/quizzes", headers=headers, timeout=10)),
    ("Exams list", lambda: httpx.get(f"{BASE}/exams", headers=headers, timeout=10)),
    ("Study plans", lambda: httpx.get(f"{BASE}/study-plans", headers=headers, timeout=10)),
    ("Analytics", lambda: httpx.get(f"{BASE}/analytics", headers=headers, timeout=10)),
    ("Credits", lambda: httpx.get(f"{BASE}/credits", headers=headers, timeout=10)),
    ("Flashcards", lambda: httpx.get(f"{BASE}/flashcards", headers=headers, timeout=10)),
    ("Lobbies list", lambda: httpx.get(f"{BASE}/lobbies", headers=headers, timeout=10)),
    ("Study planner calendar", lambda: httpx.get(f"{BASE}/study-plans/calendar", headers=headers, timeout=10)),
    ("Payment packs", lambda: httpx.get(f"{BASE}/payments/packs", headers=headers, timeout=10)),
    ("AI Tutor chat", lambda: httpx.post(f"{BASE}/ai/chat", headers=headers, json={"message": "What is algebra?"}, timeout=30)),
]

for label, fn in tests:
    try:
        r = fn()
        log(label, r.status_code, r.text)
    except Exception as e:
        print(f"[ERROR] {label} -> exception: {e}")

# Special test: quiz detail (generates questions - the critical one)
print("\n--- Testing quiz detail generation (the slow one) ---")
try:
    r = httpx.get(f"{BASE}/quizzes", headers=headers, timeout=10)
    data = r.json()
    quizzes = data.get("quizzes") or data.get("data") or []
    if quizzes:
        qid = quizzes[0].get("id") or ""
        if qid:
            r2 = httpx.get(f"{BASE}/quizzes/{qid}", headers=headers, timeout=60)
            log("Quiz detail (10 questions)", r2.status_code, r2.text[:300])
            if r2.status_code == 200:
                questions = r2.json().get("questions", [])
                print(f"  Question count: {len(questions)}")
                if questions:
                    q = questions[0]
                    print(f"  Sample Q: {q.get('text','')[:60]}")
                    print(f"  Options: {q.get('options',[])}")
except Exception as e:
    print(f"[ERROR] Quiz detail: {e}")

print("\n=== ALL TESTS DONE ===")
