# Cognora - AI-Powered Learning Platform

Prepare for WAEC, NECO, GCE, JAMB, and Post-UTME examinations with AI-powered tutoring, practice quizzes, and mock exams.

## Tech Stack

### Frontend
- Next.js 15, React 19, TypeScript
- Tailwind CSS, shadcn/ui
- Motion, TanStack Query, Zustand
- React Hook Form, Zod

### Backend
- FastAPI, PostgreSQL, SQLAlchemy
- Redis, Celery
- JWT Authentication
- Pydantic, Alembic

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL
- Redis

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy .env and configure
cp .env.example .env

# Run migrations
alembic upgrade head

# Seed database
python -m app.utils.seed

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker-compose up -d
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Features

- **AI Tutor**: Ask questions, get explanations, generate quizzes
- **Practice Quizzes**: Subject-specific multiple choice questions
- **Mock Exams**: WAEC, NECO, GCE, JAMB simulations with timers
- **Study Planner**: AI-generated study schedules
- **Analytics**: Track performance, identify weak areas
- **Credit System**: 50 free weekly credits

## Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests (Playwright)
cd frontend && npx playwright test
```

## License

MIT
