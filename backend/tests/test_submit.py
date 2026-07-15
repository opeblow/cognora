"""Test quiz submit flow."""
import httpx, sys

BASE = "http://localhost:8000/api"
T = sys.argv[1]
H = {"Authorization": f"Bearer {T}"}

# Get first quiz
r = httpx.get(f"{BASE}/quizzes", headers=H, timeout=10)
quizzes = r.json().get("quizzes", [])
if not quizzes:
    print("No quizzes")
    sys.exit()
qid = quizzes[0].get("id")
print(f"Quiz: {qid[:8]}")

# Start quiz (generates questions)
r2 = httpx.get(f"{BASE}/quizzes/{qid}", headers=H, timeout=120)
data = r2.json()
session_id = data.get("session_id")
questions = data.get("questions", [])
print(f"Session: {str(session_id)[:8]}")
print(f"Questions: {len(questions)}")

if not session_id or not questions:
    print("No session/questions")
    sys.exit()

# Submit answers
answers = {}
for q in questions:
    answers[q["id"]] = q["options"][0]

r3 = httpx.post(f"{BASE}/quizzes/{qid}/submit", headers=H, json={
    "session_id": session_id,
    "answers": answers,
    "time_taken_seconds": 60
}, timeout=30)

print(f"Submit status: {r3.status_code}")
if r3.status_code == 200:
    res = r3.json()
    print(f"Score: {res['score']}/{res['total']} ({res['percentage']}%)")
    print(f"Passed: {res['passed']}")
    for a in res["answers"][:3]:
        print(f"  Q: {a['question_text'][:40]}...")
        print(f"    You: {a['selected_answer']}")
        print(f"    Correct: {a['correct_answer']}")
        print(f"    Right: {a['is_correct']}")
else:
    print(f"Error: {r3.text[:300]}")
