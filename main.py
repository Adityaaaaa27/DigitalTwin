"""
main.py — FastAPI application entry point.

Run locally:
    uvicorn main:app --reload
"""
import sys
import os

# ── Make sure the project root is on sys.path so absolute imports work ─────
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.schema import init_db
from app.routes.predict  import router as predict_router
from app.routes.history  import router as history_router
from app.routes.future   import router as future_router
from app.routes.auth     import router as auth_router
from app.routes.ai       import router as ai_router

# ── App factory ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Mental Health Digital Twin API",
    description=(
        "Explainable mental-health risk scoring powered by a Bayesian Network. "
        "Tracks individual risk over time (digital twin), explains factor contributions, "
        "predicts future risk trends, and provides personalised AI recommendations."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow all origins for local dev; restrict in production) ─────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB initialisation on startup ───────────────────────────────────────────────
@app.on_event("startup")
async def startup_event() -> None:
    """Create/migrate SQLite tables on startup."""
    init_db()


# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(history_router)
app.include_router(future_router)
app.include_router(ai_router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "healthy", "service": "mental-health-digital-twin"}


@app.get("/", tags=["Root"])
async def root() -> dict:
    return {
        "message": "Mental Health Digital Twin API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /auth/signup": "Create new account",
            "POST /auth/login": "Login",
            "POST /predict": "Run mental health risk prediction",
            "GET  /history/{user_id}": "Get user's mental health history",
            "GET  /future/{user_id}": "Predict future risk trends",
            "POST /ai/tips": "Get AI-generated dashboard tips",
            "POST /ai/recommendations": "Get AI-generated recommendations",
        }
    }
