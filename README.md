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
# Development
docker-compose up -d

# Production (multi-backend, PgBouncer, Celery workers)
docker-compose -f docker-compose.prod.yml up -d
```

## Production Architecture

```
                          Cloudflare (CDN, DDoS, WAF)
                                    |
                          nginx (TLS, rate limiting, gzip)
                    /       |        |        \
              backend-1  backend-2  backend-3  backend-4
              (4 workers each = 16 total uvicorn workers)
                    \       |        |        /
                  PgBouncer (primary, 1000 max conns)
                  PgBouncer (replica, 1500 max conns)
                    /                    \
              PostgreSQL primary    PostgreSQL replica
              (WAL streaming)       (read-only, hot standby)
                    
              redis-cache (2GB, allkeys-lru, WebSocket pub/sub)
              redis-broker (1GB, noeviction, Celery task queue)
                    
              worker-1 (cpu queue ×4 concurrency)
              worker-2 (io queue ×2 concurrency)
              worker-3 (io queue ×2 concurrency)
              celery-beat (scheduled tasks)
                    
              Prometheus (metrics, 30d retention)
              Grafana (dashboards, alerting)
              Sentry (error tracking, APM)
```

### Capacity

| Component | Concurrent capacity |
|-----------|-------------------|
| 4 backends × 4 workers = 16 uvicorn workers | ~8,000-16,000 requests |
| PgBouncer primary | 1,000 DB connections |
| PgBouncer replica | 1,500 read connections |
| PostgreSQL (4 CPU, 4GB RAM) | ~2,000 queries/sec |
| Redis cache (2GB, LRU) | ~100,000 ops/sec |
| 3 Celery workers (8 total concurrency) | ~8 concurrent AI/OCR jobs |
| nginx | ~50,000 connections |

### Scaling behavior

- **Backend auto-scaling**: ECS Cloud Auto Scaling — scales 2→20 tasks based on CPU (70%), memory (75%), and requests/target (1000 req/target)
- **Read replica**: Read-heavy routes (analytics, dashboard, quizzes, subjects) route to replica — primary handles writes only
- **Celery separation**: CPU-bound jobs (DB cleanup) on dedicated queue, AI/OCR jobs on separate workers — no cross-blocking
- **Redis split**: Cache uses LRU eviction (ephemeral OK), broker uses noeviction (task queue safe)

Key infrastructure decisions:
- **Cloudflare**: CDN for static assets, DDoS protection, WAF rules, HTTP/3, Brotli compression
- **PgBouncer**: Transaction-mode pooling — 16 backends share 1,000 primary connections efficiently
- **Read replica**: Hot standby with WAL streaming — zero-config failover, automatic read routing
- **Prometheus + Grafana**: Real-time metrics, latency percentiles (p50/p95/p99), error rate dashboards
- **Sentry**: Error tracking with source maps, performance tracing, session replay
- **Auto-scaling**: CPU/memory targets + request count per target — scales on real load, not just resource usage

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Features

- **AI Tutor**: Ask questions, get explanations, generate quizzes
- **Practice Quizzes**: Subject-specific multiple choice questions
- **Mock Exams**: WAEC, NECO, GCE, JAMB simulations with timers
- **Past Questions**: Live-fetched real exam questions via Brave Search + AI parsing — unique per user, reshuffled every retry
- **Study Planner**: AI-generated study schedules with adaptive weighting based on quiz performance
- **Analytics**: Performance score gauge, exam readiness, trend bars, topic mastery, weekly heatmap, weak area recommendations
- **Study Groups**: Create/browse groups, real-time messaging, member management
- **Flashcards**: Spaced repetition, SM-2 scheduling, topic-based decks
- **Live Teaching**: WebSocket-based sessions with mock provider (Agora-ready)
- **Credit System**: 50 free weekly credits, Paystack integration
- **Offline Support**: Service worker with TTL-based caching, stale-while-revalidate
- **Mobile Responsive**: Full mobile-first UI with hamburger sidebar
- **Monitoring**: Prometheus metrics, Grafana dashboards, Sentry error tracking
- **Auto-Scaling**: ECS Fargate 2→20 tasks based on CPU/memory/request count

## Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests (Playwright)
cd frontend && npx playwright test
```

## License

MIT
