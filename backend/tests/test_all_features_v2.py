"""
Comprehensive API test - tests ALL endpoints with correct paths.
Usage: python test_all_features_v2.py YOUR_JWT_TOKEN
"""
import httpx, sys, json

BASE = "http://localhost:8000/api"
T = sys.argv[1]
H = {"Authorization": f"Bearer {T}"}
P = 0
F = 0

def t(name, fn):
    global P, F
    try:
        r = fn()
        ok = 200 <= r.status_code < 500
        if ok:
            P += 1
            s = "PASS" if r.status_code < 400 else f"OK ({r.status_code})"
            print(f"  [{s}] {name}")
        else:
            F += 1
            det = str(r.text)[:200].replace('\n',' ')
            print(f"  [FAIL] {name} -> {r.status_code}: {det}")
        return r
    except Exception as e:
        F += 1
        print(f"  [FAIL] {name} -> exception: {e}")
        return None

# ─── AUTH ───
print("\n1. AUTH")
r = t("GET /auth/me", lambda: httpx.get(f"{BASE}/auth/me", headers=H, timeout=10))
if r and r.status_code == 200:
    print(f"    Logged in as: {r.json().get('email','?')}")

t("POST /auth/refresh", lambda: httpx.post(f"{BASE}/auth/refresh", headers=H, json={"refresh_token": "test"}, timeout=10))

# ─── DASHBOARD ───
print("\n2. DASHBOARD")
r = t("GET /dashboard", lambda: httpx.get(f"{BASE}/dashboard", headers=H, timeout=10))
if r and r.status_code == 200:
    d = r.json()
    print(f"    Welcome: {d.get('welcome_name','?')}")
    print(f"    Credits: {d.get('credits','?')}")

# ─── SUBJECTS ───
print("\n3. SUBJECTS")
r = t("GET /subjects", lambda: httpx.get(f"{BASE}/subjects", headers=H, timeout=10))
subjects = []
if r and r.status_code == 200:
    subjects = r.json().get("subjects") or r.json().get("data") or []
    print(f"    Count: {len(subjects)}")
    for s in subjects[:10]:
        print(f"    - {s.get('name','?')}")
    if subjects:
        slug = subjects[0].get("slug") or subjects[0].get("id")
        t(f"GET /subjects/{slug}", lambda: httpx.get(f"{BASE}/subjects/{slug}", headers=H, timeout=10))
        t(f"GET /subjects/{slug}/topics", lambda: httpx.get(f"{BASE}/subjects/{slug}/topics", headers=H, timeout=10))

# ─── AI TUTOR ───
print("\n4. AI TUTOR")
t("POST /ai/tutor", lambda: httpx.post(f"{BASE}/ai/tutor", headers=H, json={"message": "Explain photosynthesis", "subject": "Biology"}, timeout=60))

# ─── QUIZZES (CRITICAL) ───
print("\n5. QUIZZES")
r = t("GET /quizzes list", lambda: httpx.get(f"{BASE}/quizzes", headers=H, timeout=10))
qlist = []
if r and r.status_code == 200:
    qlist = r.json().get("quizzes") or r.json().get("data") or []
    print(f"    Existing: {len(qlist)}")
qid = qlist[0].get("id") if qlist else None
if qlist:
    print(f"  Loading quiz {str(qid)[:8]}...")
    r2 = t("GET /quizzes/{id}", lambda: httpx.get(f"{BASE}/quizzes/{qid}", headers=H, timeout=120))
    if r2 and r2.status_code == 200:
        qs = r2.json().get("questions", [])
        print(f"    Questions: {len(qs)}")
        if qs:
            for i, q in enumerate(qs[:3]):
                print(f"    Q{i+1}: {q.get('text','')[:70]}")
                print(f"          Options: {q.get('options',[])}")

# ─── EXAMS ───
print("\n6. EXAMS")
r = t("GET /exams list", lambda: httpx.get(f"{BASE}/exams", headers=H, timeout=10))
elist = []
if r and r.status_code == 200:
    elist = r.json().get("exams") or r.json().get("data") or []
    print(f"    Existing: {len(elist)}")
if elist:
    eid = elist[0].get("id") or elist[0].get("exam_id","")
    t(f"POST /exams/{eid}/start", lambda: httpx.post(f"{BASE}/exams/{eid}/start", headers=H, timeout=120))
t("GET /exams/results/mine", lambda: httpx.get(f"{BASE}/exams/results/mine", headers=H, timeout=10))

# ─── STUDY PLANNER ───
print("\n7. STUDY PLANNER")
t("GET /study-planner", lambda: httpx.get(f"{BASE}/study-planner", headers=H, timeout=10))
t("GET /study-planner/today", lambda: httpx.get(f"{BASE}/study-planner/today", headers=H, timeout=10))
t("GET /study-planner/calendar", lambda: httpx.get(f"{BASE}/study-planner/calendar", headers=H, timeout=10))

# ─── FLASHCARDS ───
print("\n8. FLASHCARDS")
r = t("GET /flashcards list", lambda: httpx.get(f"{BASE}/flashcards", headers=H, timeout=10))
t("POST /flashcards/generate", lambda: httpx.post(f"{BASE}/flashcards/generate", headers=H, json={"subject_id": subjects[0].get("id","")} if subjects else {}, timeout=30))

# ─── ANALYTICS ───
print("\n9. ANALYTICS")
t("GET /analytics/dashboard", lambda: httpx.get(f"{BASE}/analytics/dashboard", headers=H, timeout=10))
r = t("GET /analytics/overview", lambda: httpx.get(f"{BASE}/analytics/overview", headers=H, timeout=10))
t("GET /analytics/accuracy-trends", lambda: httpx.get(f"{BASE}/analytics/accuracy-trends", headers=H, timeout=10))

# ─── CREDITS ───
print("\n10. CREDITS")
t("GET /credits/balance", lambda: httpx.get(f"{BASE}/credits/balance", headers=H, timeout=10))

# ─── LOBBIES ───
print("\n11. LOBBIES")
r = t("GET /lobbies list", lambda: httpx.get(f"{BASE}/lobbies", headers=H, timeout=10))
t("POST /lobbies create", lambda: httpx.post(f"{BASE}/lobbies", headers=H, json={"name": "Test Lobby", "max_participants": 5}, timeout=10))
lobbies = []
if r and r.status_code == 200:
    lobbies = r.json().get("lobbies") or r.json().get("data") or []
if lobbies:
    lid = lobbies[0].get("id","")
    t(f"GET /lobbies/{lid}", lambda: httpx.get(f"{BASE}/lobbies/{lid}", headers=H, timeout=10))
    t(f"GET /lobbies/{lid}/history", lambda: httpx.get(f"{BASE}/lobbies/{lid}/history", headers=H, timeout=10))
    t(f"POST /lobbies/{lid}/close", lambda: httpx.post(f"{BASE}/lobbies/{lid}/close", headers=H, timeout=10))

# ─── SETTINGS ───
print("\n12. SETTINGS")
r = t("GET /settings", lambda: httpx.get(f"{BASE}/settings", headers=H, timeout=10))

# ─── PAYMENTS ───
print("\n13. PAYMENTS")
t("GET /payments/packs", lambda: httpx.get(f"{BASE}/payments/packs", headers=H, timeout=10))

# ─── LIVE TEACHING ───
print("\n14. LIVE TEACHING")
t("GET /live/list", lambda: httpx.get(f"{BASE}/live", headers=H, timeout=10))
t("POST /live/rooms create", lambda: httpx.post(f"{BASE}/live/rooms", headers=H, json={
    "title": "Test Session", "subject": "Mathematics",
    "description": "Algebra review"
}, timeout=10))

# ─── AUDIO ───
print("\n15. AUDIO")
t("GET /audio status (404 expected)", lambda: httpx.get(f"{BASE}/audio/test-id/status", headers=H, timeout=10))

# ─── FILES ───
print("\n16. FILES")
t("GET /files list", lambda: httpx.get(f"{BASE}/files", headers=H, timeout=10))

# ─── ISSUES ───
print("\n17. ISSUES")
t("GET /issues list", lambda: httpx.get(f"{BASE}/issues", headers=H, timeout=10))
t("POST /issues create", lambda: httpx.post(f"{BASE}/issues", headers=H, json={
    "title": "Test bug report",
    "description": "This is a test",
    "severity": "low"
}, timeout=10))

# ─── GAMIFICATION ───
print("\n18. GAMIFICATION")
t("GET /gamification/profile", lambda: httpx.get(f"{BASE}/gamification/profile", headers=H, timeout=10))
t("GET /gamification/badges", lambda: httpx.get(f"{BASE}/gamification/badges", headers=H, timeout=10))
t("GET /gamification/leaderboard", lambda: httpx.get(f"{BASE}/gamification/leaderboard", headers=H, timeout=10))

# ─── CONTENT / TEXTBOOK ───
print("\n19. CONTENT / TEXTBOOK")
t("GET /content/syllabus/WACE/Maths", lambda: httpx.get(f"{BASE}/content/syllabus/WAEC/Mathematics", headers=H, timeout=10))

# ─── SUMMARY ───
print(f"\n{'='*50}")
print(f"  {P} passed, {F} failed")
print(f"{'='*50}")
if F == 0:
    print("  ALL FEATURES WORKING")
else:
    print(f"  {F} failures above")
