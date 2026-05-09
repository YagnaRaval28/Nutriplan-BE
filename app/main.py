from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.db.session import engine, Base
from app.routers import auth, users, foods, food_logs, diet_plans, ai_recipes, reports, messages, subscriptions, admin

# Create all tables on startup (Alembic handles migrations in prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriPlan AI API",
    description="Recipe & Diet Planner Platform — Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://nutriplan.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request timing middleware ──────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response

# ── Global exception handler ──────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
    )

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router,          prefix="/api/v1/auth",          tags=["Auth"])
app.include_router(users.router,         prefix="/api/v1/users",         tags=["Users"])
app.include_router(foods.router,         prefix="/api/v1/foods",         tags=["Foods"])
app.include_router(food_logs.router,     prefix="/api/v1/food-logs",     tags=["Food Logs"])
app.include_router(diet_plans.router,    prefix="/api/v1/diet-plans",    tags=["Diet Plans"])
app.include_router(ai_recipes.router,    prefix="/api/v1/ai",            tags=["AI Recipes"])
app.include_router(reports.router,       prefix="/api/v1/reports",       tags=["Reports"])
app.include_router(messages.router,      prefix="/api/v1/messages",      tags=["Messages"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
app.include_router(admin.router,         prefix="/api/v1/admin",         tags=["Admin"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "NutriPlan AI", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
