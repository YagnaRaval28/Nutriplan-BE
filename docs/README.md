# NutriPlan AI — Documentation Index

**Platform:** Recipe & Diet Planner with AI  
**Version:** 1.0  
**Last Updated:** 2026-05-07

---

## Documents

| Document | Description |
|----------|-------------|
| [PRD.md](PRD.md) | Full Product Requirements Document — vision, roles, features, phases, success metrics |
| [API_SPEC.md](API_SPEC.md) | Complete REST API specification — all endpoints with request/response examples |
| [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) | PostgreSQL schema, Redis usage, ChromaDB collections |
| [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) | System design, tech stack, folder structure, deployment, security |
| [PAYMENT_SUBSCRIPTION.md](PAYMENT_SUBSCRIPTION.md) | Stripe integration, subscription plans, payment flow, revenue projections |

---

## Quick Summary

- **Backend:** FastAPI + LangGraph + PostgreSQL + Redis
- **AI:** Groq API (Llama 3 — free tier) via LangGraph agents
- **Payments:** Stripe (designed, activate later when ready to monetize)
- **Frontend:** Next.js + Tailwind CSS (web-first)
- **Mobile:** Flutter — Phase 3 only
- **Roles:** User, Dietician, Doctor, Super Admin
- **Phases:** MVP Web (months 1–3) → Core Web (months 3–5) → Growth + Mobile (months 5–8)

## Free Stack Summary

| Layer | Tool | Cost |
|-------|------|------|
| Backend hosting | Render.com | Free |
| Frontend hosting | Vercel | Free |
| Database | Supabase (PostgreSQL) | Free |
| Cache | Upstash (Redis) | Free |
| LLM / AI | Groq API | Free tier |
| Food data | Open Food Facts API | Free |
| Email | Resend.com | Free (100/day) |
| Images | Cloudinary | Free tier |
| AI framework | LangGraph | Open source |

---

## Next Step

Start building **Phase 1 MVP** — FastAPI backend with auth, food logging, and AI recipe generation using the free stack.
