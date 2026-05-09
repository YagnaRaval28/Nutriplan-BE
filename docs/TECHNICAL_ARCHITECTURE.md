# Technical Architecture
# NutriPlan AI — System Design & Architecture

**Version:** 1.1
**Date:** 2026-05-09
**Note:** Stack uses 100% free and open-source tools. Web-first — mobile app is a future phase.

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS (Web Only)                      │
│         Next.js Web App (User + Dietician + Doctor portals)     │
│                  + Admin Dashboard (Next.js)                    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                        │
│             Rate Limiting · SSL · Routing                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                       │
│                                                                 │
│   ┌───────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│   │ Auth      │  │ Users    │  │ Food     │  │ Diet Plans  │  │
│   │ Router    │  │ Router   │  │ Router   │  │ Router      │  │
│   └───────────┘  └──────────┘  └──────────┘  └─────────────┘  │
│                                                                 │
│   ┌───────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│   │ AI        │  │ Reports  │  │ Messages │  │ Payments    │  │
│   │ Router    │  │ Router   │  │ Router   │  │ Router      │  │
│   └───────────┘  └──────────┘  └──────────┘  └─────────────┘  │
└─────────┬─────────────┬──────────────┬────────────────┬────────┘
          │             │              │                │
          ▼             ▼              ▼                ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐   ┌──────────────┐
   │PostgreSQL│  │  Redis   │  │ChromaDB  │   │  LangGraph   │
   │(Primary  │  │ (Cache & │  │(Vector   │   │  AI Agent    │
   │   DB)    │  │ Sessions)│  │ Search)  │   │  Service     │
   └──────────┘  └──────────┘  └──────────┘   └──────┬───────┘
                                                      │
                                              ┌───────▼──────┐
                                              │  Groq API    │
                                              │  (Free LLM)  │
                                              └──────────────┘

External Free Services:
  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
  │  Cloudinary  │  │  Resend.com  │  │  Open Food Facts API │
  │ (Image store │  │ (Free email  │  │  (Free food database)│
  │  free tier)  │  │  100/day)    │  │                      │
  └──────────────┘  └──────────────┘  └──────────────────────┘
```

---

## 2. Free Technology Stack

### Backend
| Layer | Technology | Cost | Purpose |
|-------|-----------|------|---------|
| API Framework | FastAPI (Python 3.11+) | Free | High performance REST API |
| AI Orchestration | LangGraph | Free (open source) | Multi-step AI agent workflows |
| LLM | Groq API (llama3-70b) | Free tier (generous) | Recipe generation, meal planning |
| Task Queue | FastAPI BackgroundTasks | Free (built-in) | Background jobs — no Celery needed |
| WebSockets | FastAPI WebSocket | Free (built-in) | Real-time messaging |

> **Why Groq instead of Claude/OpenAI?**
> Groq offers a free tier with fast inference on Llama 3 70B — very capable for recipe generation. When you have budget you can swap to Claude with one line change.

### Databases
| Database | Technology | Cost | Purpose |
|----------|-----------|------|---------|
| Primary DB | PostgreSQL 15 (local / Supabase free) | Free | All relational data |
| Cache | Redis (local / Upstash free tier) | Free | Sessions, rate limits |
| Vector DB | ChromaDB (local) | Free | Semantic food/recipe search |

### Frontend
| Platform | Technology | Cost | Purpose |
|----------|-----------|------|---------|
| Web App | Next.js 14 + TypeScript | Free | User, Dietician, Doctor portals |
| Styling | Tailwind CSS + shadcn/ui | Free | Component library |
| Admin Panel | Same Next.js app (separate route) | Free | Super Admin dashboard |
| Charts | Recharts | Free | Calorie/macro graphs |
| Mobile | Flutter | Free — Phase 3 only | iOS + Android (future) |

### Infrastructure (All Free)
| Component | Technology | Free Plan Details |
|-----------|-----------|------------------|
| Backend Hosting | Render.com | Free tier: 1 web service, sleeps after 15min inactivity |
| Frontend Hosting | Vercel | Free tier: unlimited personal projects |
| Database | Supabase | Free tier: 500MB PostgreSQL, no sleep |
| Redis Cache | Upstash | Free tier: 10,000 commands/day |
| Image Storage | Cloudinary | Free tier: 25GB storage, 25GB bandwidth/month |
| Reverse Proxy | Nginx (local dev) | Free |
| SSL | Let's Encrypt (via Render/Vercel) | Free |

### External Free Services
| Service | Provider | Free Limit | Purpose |
|---------|----------|-----------|---------|
| Email | Resend.com | 100 emails/day free | Transactional emails |
| LLM / AI | Groq API | Free tier (generous RPM) | Recipe generation |
| Food Data | Open Food Facts API | Completely free | Food nutrition database |
| Auth (optional) | Supabase Auth | Free (built-in with Supabase) | Can replace custom JWT |

> **Payment Note:** Stripe integration is designed and documented but will be activated later when you are ready to monetize. For now the platform runs fully free for development and testing.

---

## 3. Local Development Setup (Zero Cost)

Everything runs locally on your machine:

```
Your Laptop
├── FastAPI server         → localhost:8000
├── Next.js frontend       → localhost:3000
├── PostgreSQL (Docker)    → localhost:5432
├── Redis (Docker)         → localhost:6379
└── ChromaDB (Docker)      → localhost:8001
```

You only need Docker Desktop (free) and Python 3.11+ installed.

---

## 4. Project Folder Structure

```
nutriplan-api/                   ← Backend (FastAPI)
│
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings from .env file
│   │
│   ├── routers/                 # API route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── foods.py
│   │   ├── food_logs.py
│   │   ├── diet_plans.py
│   │   ├── ai_recipes.py
│   │   ├── reports.py
│   │   ├── messages.py
│   │   ├── subscriptions.py
│   │   └── admin.py
│   │
│   ├── models/                  # SQLAlchemy DB models
│   │   ├── user.py
│   │   ├── food.py
│   │   ├── diet_plan.py
│   │   ├── report.py
│   │   ├── message.py
│   │   └── payment.py
│   │
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── food.py
│   │   ├── diet_plan.py
│   │   └── payment.py
│   │
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── food_service.py
│   │   ├── diet_plan_service.py
│   │   ├── report_service.py
│   │   ├── payment_service.py
│   │   └── notification_service.py
│   │
│   ├── ai/                      # LangGraph AI agents
│   │   ├── graph.py             # LangGraph workflow definition
│   │   ├── nodes/
│   │   │   ├── profile_analyzer.py
│   │   │   ├── diet_checker.py
│   │   │   ├── recipe_generator.py
│   │   │   └── nutrition_calculator.py
│   │   └── tools/
│   │       ├── food_db_tool.py
│   │       └── nutrition_tool.py
│   │
│   ├── db/
│   │   ├── session.py           # DB session (SQLAlchemy)
│   │   └── migrations/          # Alembic migration files
│   │
│   ├── cache/
│   │   └── redis_client.py      # Redis connection helpers
│   │
│   ├── middleware/
│   │   ├── auth_middleware.py   # JWT token validation
│   │   └── rate_limit.py        # Rate limiting via Redis
│   │
│   └── utils/
│       ├── security.py          # Password hashing, JWT
│       ├── email.py             # Resend email helpers
│       └── cloudinary.py        # Image upload helpers
│
├── tests/
│   ├── test_auth.py
│   ├── test_food_logs.py
│   ├── test_diet_plans.py
│   └── test_ai_recipes.py
│
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example

nutriplan-web/                   ← Frontend (Next.js)
│
├── app/
│   ├── (auth)/                  # Login, Register pages
│   ├── (user)/                  # User portal pages
│   ├── (dietician)/             # Dietician portal pages
│   ├── (doctor)/                # Doctor portal pages
│   └── (admin)/                 # Admin dashboard pages
│
├── components/
│   ├── ui/                      # shadcn/ui base components
│   ├── charts/                  # Recharts wrappers
│   ├── food-log/                # Food logging components
│   └── diet-plan/               # Diet plan components
│
├── lib/
│   ├── api.ts                   # API client (axios/fetch)
│   └── auth.ts                  # Auth helpers
│
└── public/
```

---

## 5. LangGraph AI Agent Architecture

```
User Request (preferences, goals, allergies)
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│              LangGraph Recipe Agent                        │
│                                                            │
│  START                                                     │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────────────────────┐                          │
│  │ Node 1: profile_analyzer   │  Reads user health        │
│  │ - age, weight, goals        │  profile + allergies     │
│  │ - allergies, conditions     │  from PostgreSQL         │
│  └────────────┬────────────────┘                          │
│               ▼                                            │
│  ┌─────────────────────────────┐                          │
│  │ Node 2: diet_checker        │  Checks active diet      │
│  │ - active plan lookup        │  plan constraints        │
│  └────────────┬────────────────┘                          │
│               ▼                                            │
│  ┌─────────────────────────────┐                          │
│  │ Node 3: recipe_generator    │  Calls Groq LLM          │
│  │ - Groq API call (Llama 3)   │  with structured prompt  │
│  └────────────┬────────────────┘                          │
│               ▼                                            │
│  ┌─────────────────────────────┐                          │
│  │ Node 4: nutrition_calc      │  Looks up each           │
│  │ - lookup each ingredient    │  ingredient in food DB   │
│  │ - compute total macros      │  and sums macros         │
│  └────────────┬────────────────┘                          │
│               ▼                                            │
│  ┌─────────────────────────────┐                          │
│  │ Node 5: validator           │  Checks calorie goal     │
│  │ - calorie target check      │  and allergy safety      │
│  │ - allergy safety check      │                          │
│  └────────────┬────────────────┘                          │
│               │                                            │
│    [Pass] ───►│◄─── [Fail → loop back to Node 3]          │
│               ▼                                            │
│           FINISH — return recipe + full nutrition          │
└────────────────────────────────────────────────────────────┘
```

---

## 6. Authentication Flow

```
Client                       FastAPI                      PostgreSQL
  │                             │                              │
  │── POST /auth/login ────────►│                              │
  │                             │── Query user by email ──────►│
  │                             │◄─ Return user row ───────────│
  │                             │                              │
  │                             │  Verify bcrypt password hash │
  │                             │  Generate JWT access_token   │
  │                             │  Generate refresh_token      │
  │                             │── Store refresh_token hash ─►│
  │◄─ Return tokens ───────────│                              │
  │                             │                              │
  │── API calls with token ────►│                              │
  │   Authorization: Bearer     │  Decode JWT → get user_id   │
  │   <access_token>            │  Check role permissions      │
  │◄─ API response ────────────│                              │
```

---

## 7. Docker Setup (Local Development)

```yaml
# docker-compose.yml
version: '3.9'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/nutriplan
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: nutriplan
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"

volumes:
  postgres_data:
```

---

## 8. Environment Variables (.env)

```env
# App
APP_ENV=development
SECRET_KEY=any_long_random_string_here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database (local Docker)
DATABASE_URL=postgresql://user:pass@localhost:5432/nutriplan

# Cache (local Docker)
REDIS_URL=redis://localhost:6379

# AI — Groq (free)
GROQ_API_KEY=gsk_...

# Food Database (free, no key needed)
OPEN_FOOD_FACTS_BASE_URL=https://world.openfoodfacts.org

# Email — Resend (free 100/day)
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@yourdomain.com

# Image Upload — Cloudinary (free tier)
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Stripe (add later when ready to monetize)
# STRIPE_SECRET_KEY=sk_live_...
# STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## 9. Free Deployment Architecture

```
Internet
    │
    ▼
Vercel (Frontend - Next.js)          ← Free, auto-deploys from GitHub
    │
    │ API calls
    ▼
Render.com (FastAPI Backend)         ← Free tier web service
    │
    ├──► Supabase (PostgreSQL)       ← Free 500MB database
    │
    ├──► Upstash (Redis)             ← Free 10k commands/day
    │
    └──► ChromaDB (on Render)        ← Runs as a separate free service
```

> **Render.com Free Tier Limitation:** The free web service "sleeps" after 15 minutes of inactivity and takes ~30 seconds to wake up on the next request. This is fine for development and early testing. When you get users, upgrade to Render's $7/month plan.

---

## 10. Security Measures

| Area | Implementation |
|------|---------------|
| Authentication | JWT (HS256), bcrypt password hashing |
| Authorization | Role-based access control (RBAC) per route |
| HTTPS | Auto-provided by Vercel and Render free tier |
| Rate Limiting | Via Redis counter per user per endpoint |
| Input Validation | Pydantic schemas on all request bodies |
| SQL Injection | SQLAlchemy ORM — no raw SQL |
| Secrets | .env file locally, environment vars on Render/Vercel |
| Medical Data | Standard PostgreSQL encryption at rest (Supabase) |
| Payment Data | Stripe handles all card data — never touches our server |
| Audit Logs | All admin actions logged with user_id + timestamp |

---

## 11. Free Resources Reference

| Resource | URL | What You Get Free |
|----------|-----|------------------|
| Groq API | console.groq.com | Fast LLM inference, generous free tier |
| Supabase | supabase.com | 500MB PostgreSQL + Auth |
| Upstash | upstash.com | Redis, 10k commands/day |
| Render | render.com | 1 free web service |
| Vercel | vercel.com | Unlimited frontend deploys |
| Cloudinary | cloudinary.com | 25GB storage free |
| Resend | resend.com | 100 emails/day free |
| Open Food Facts | world.openfoodfacts.org | Completely free food API |
| ChromaDB | github.com/chroma-core/chroma | Open source, self-hosted |
| LangGraph | github.com/langchain-ai/langgraph | Open source |

---

*Last Updated: 2026-05-09*
