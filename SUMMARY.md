## Goal
Build Cognora into a world-class WAEC/NECO/GCE/JAMB exam preparation platform with comprehensive textbook-like content for every subject.

## Constraints & Preferences
- No quizzes or mock exams shown under the subject detail page — already removed from frontend
- Content must be extremely comprehensive — 72 lessons, 298 topics across all 15 subjects
- Explanations must be kid-friendly, step-by-step from zero to professor level
- Must include real-world analogies for every concept
- For English, based on "Fundamental Formulas in English" by Barrister Oscar Izeyor Iyoha
- PostgreSQL: user=cognora, password=cognora, database=cognora

## Progress
### Done
- Quizzes and mock exams removed from subject detail page (frontend)
- Seed data massively expanded from old 50 lessons / 137 topics → **72 lessons / 298 topics** using actual WAEC/WAEC syllabi for all 15 subjects
- Mathematics: 5 lessons, 38 topics (Number & Numeration, Algebra, Geometry/Trig, Calculus, Stats/Prob)
- English Language: 6 lessons, 31 topics (Lexis/Structure, Grammar, Oral English, Comprehension, Essay Writing, Literature)
- Physics: 5 lessons, 29 topics (Motion, Forces & Energy, Waves/Light/Sound, Electricity/Magnetism, Modern Physics)
- Chemistry: 11 lessons, 31 topics (Atomic Structure, States of Matter, Reactions, Acids/Bases/Salts, Electrochemistry, Rate/Equilibrium, Organic, Energy Changes, Water, Environmental, Radioactivity)
- Biology: 5 lessons, 29 topics (Cell Biology, Genetics/Evolution, Ecology, Physiology, Classification)
- Economics: 5 lessons, 24 topics (Fundamentals, Microeconomics, Macroeconomics, Public Finance/Trade, Development)
- Government: 6 lessons, 23 topics (Concepts, Constitutions, Political Parties, Civil Service, Pre-Colonial/Colonial, Military/Intl)
- Literature in English: 5 lessons, 9 topics (Prose, Poetry, Drama, Appreciation)
- History: 3 lessons, 16 topics (Pre-Colonial, Colonial, Independence/Post-Colonial)
- CRS: 2 lessons, 12 topics (Old Testament, New Testament)
- Civic Education: 3 lessons, 14 topics (Citizenship/Rights, Government/Democracy, Social Issues)
- Commerce: 4 lessons, 12 topics (Intro, Trade, Aids to Trade, Business Units)
- Accounting: 3 lessons, 13 topics (Principles, Financial Statements, Specialized Accounts)
- Agricultural Science: 5 lessons, 16 topics (Intro, Soil, Crop Production, Animal Production, Economics/Extension)
- Further Mathematics: 4 lessons, 11 topics (Advanced Algebra, Calculus, Vectors/Mechanics, Coordinate Geometry/Complex Numbers)
- Database reseeded with all new content verified
- Credit `amount` column changed from String to Integer (fixes SUM() error)
- `User.credits`, `User.weekly_credits_used`, `User.learning_streak` changed from String to Integer
- Email service logs verification URL to console
- Backend lesson/topic API routes created
- Frontend lesson reader page with topic navigation tabs and prev/next
- Auth callback page wrapped in `<Suspense>` to fix build error

### In Progress
- Content is now comprehensive but could be further expanded per user feedback
- Need to add full textbook-depth explanations to each topic (currently ~100-200 words per topic, target is textbook chapter level)

### Blocked
- (none)

## Key Decisions
- Use absolute path for `script_location` in `alembic.ini` to avoid path resolution issues
- Store content as HTML in database for direct frontend rendering
- Use existing Subject → Lesson → Topic model structure (keeps schema compatible)
- Drop and recreate all tables rather than writing individual migrations (dev DB, no real data)
- For English, "Fundamental Formulas in English" by Barrister Oscar is the reference textbook — 31+ topics including phrasal verbs, concord, collocations, conditionals, subjunctive mood
- Seed data still creates quizzes/exams in DB but frontend hides them from subject detail page

## Next Steps
1. Expand each topic's content to full textbook chapter depth (paragraphs of explanation, multiple examples, practice questions with answers)
2. Consider adding search functionality for topics across subjects
3. Add progress tracking for students

## Critical Context
- Backend server runs on http://localhost:8000
- Frontend server runs on http://localhost:3000
- API docs at http://localhost:8000/api/docs
- Current seed data: 15 subjects, 72 lessons, 298 topics
- Database: 15 subjects, 72 lessons, 298 topics, 15 quizzes, 14 exams

## Relevant Files
- `backend/app/utils/seed_data.py`: Complete content payload — 15 subjects, 72 lessons, 298 topics
- `backend/app/utils/seed.py`: Seed script — drops/recreates tables, inserts all content
- `backend/app/routes/api/lessons.py`: Lesson/topic API routes
- `backend/app/models/lesson.py`: Lesson and Topic models (order_index now Integer)
- `backend/app/models/credit.py`: CreditTransaction model (amount now Integer)
- `backend/app/models/user.py`: User model (credits fields now Integer)
- `frontend/src/app/subjects/[slug]/page.tsx`: Subject detail — quizzes/exams removed
- `frontend/src/app/subjects/[slug]/lessons/[lessonSlug]/page.tsx`: Textbook reader page with topic navigation
