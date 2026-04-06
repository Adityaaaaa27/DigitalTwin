"""
config.py — Application-wide configuration.
Environment variables can override these defaults (cloud-ready).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///digitaltwin.db")

# ── Bayesian model ────────────────────────────────────────────────────────────
TREND_WINDOW: int = int(os.getenv("TREND_WINDOW", "5"))
FUTURE_STEPS: int = int(os.getenv("FUTURE_STEPS", "3"))
ALERT_CONSECUTIVE_INCREASE: int = int(os.getenv("ALERT_CONSECUTIVE_INCREASE", "3"))

# ── Discretisation thresholds ─────────────────────────────────────────────────
LOW_THRESHOLD: float = float(os.getenv("LOW_THRESHOLD", "3.5"))
HIGH_THRESHOLD: float = float(os.getenv("HIGH_THRESHOLD", "6.5"))

# ── Gemini AI ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
