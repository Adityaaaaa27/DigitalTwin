"""
app/routes/ai.py — AI-powered recommendation endpoints.

Uses Gemini API for personalized mental health tips and recommendations.
Falls back to rule-based generation if Gemini is unavailable.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_service import generate_dashboard_tips, generate_insights_recommendations

router = APIRouter(prefix="/ai", tags=["AI Recommendations"])


# ── Request schema ────────────────────────────────────────────────────────────

class AIRequest(BaseModel):
    """Input data for AI-powered recommendations."""
    sleep: float = Field(..., ge=0, le=10)
    stress: float = Field(..., ge=0, le=10)
    social: float = Field(..., ge=0, le=10)
    workload: float = Field(..., ge=0, le=10)
    screen_time: float = Field(..., ge=0, le=10)
    exercise: float = Field(..., ge=0, le=10)
    anxiety_probability: float = Field(..., ge=0, le=1)
    depression_probability: float = Field(..., ge=0, le=1)
    risk_score: float = Field(..., ge=0, le=1)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/tips")
async def get_tips(req: AIRequest):
    """
    Generate short, actionable dashboard tips based on user metrics.
    Returns a list of 3 tip strings.
    """
    try:
        tips = await generate_dashboard_tips(
            sleep=req.sleep,
            stress=req.stress,
            social=req.social,
            workload=req.workload,
            screen_time=req.screen_time,
            exercise=req.exercise,
            anxiety_probability=req.anxiety_probability,
            depression_probability=req.depression_probability,
            risk_score=req.risk_score,
        )
        return {"tips": tips}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI tips generation failed: {exc}") from exc


@router.post("/recommendations")
async def get_recommendations(req: AIRequest):
    """
    Generate detailed insights-page recommendations based on user metrics.
    Returns a dict with summary, insight, and actions.
    """
    try:
        result = await generate_insights_recommendations(
            sleep=req.sleep,
            stress=req.stress,
            social=req.social,
            workload=req.workload,
            screen_time=req.screen_time,
            exercise=req.exercise,
            anxiety_probability=req.anxiety_probability,
            depression_probability=req.depression_probability,
            risk_score=req.risk_score,
        )
        return result

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {exc}") from exc
