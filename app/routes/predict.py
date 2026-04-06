"""
app/routes/predict.py — POST /predict endpoint.

Orchestrates:
  1. Input validation (Pydantic)
  2. Bayesian inference → risk score, anxiety/depression probabilities
  3. XAI explanation (perturbation)
  4. DB persistence (including anxiety/depression probabilities)
  5. Alerts + recommendations
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.services.prediction_service    import run_prediction
from app.services.explanation_service   import compute_explanations
from app.services.recommendation_service import generate_alerts, generate_recommendations
from app.database.db                    import insert_record, fetch_history

router = APIRouter()


# ── Request / Response schemas ────────────────────────────────────────────────

class PredictRequest(BaseModel):
    """All raw inputs are expected in the range [0, 10]."""
    user_id:     str   = Field(..., description="Unique user identifier")
    sleep:       float = Field(..., ge=0, le=10, description="Sleep quality / duration [0–10]")
    stress:      float = Field(..., ge=0, le=10, description="Perceived stress level [0–10]")
    social:      float = Field(..., ge=0, le=10, description="Social engagement score [0–10]")
    workload:    float = Field(..., ge=0, le=10, description="Workload intensity [0–10]")
    screen_time: float = Field(..., ge=0, le=10, description="Daily screen time (normalised) [0–10]")
    exercise:    float = Field(..., ge=0, le=10, description="Physical exercise score [0–10]")

    @field_validator("user_id")
    @classmethod
    def user_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_id must not be empty.")
        return v.strip()


class PredictResponse(BaseModel):
    user_id:                str
    risk_score:             float
    anxiety_probability:    float
    depression_probability: float
    explanation:            dict[str, float]
    alerts:                 list[str]
    recommendations:        list[str]


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict(req: PredictRequest) -> PredictResponse:
    """
    Run the full mental-health digital-twin pipeline:
    inference → explanation → persistence → alerts → recommendations.
    """
    try:
        # 1. Bayesian inference
        result   = run_prediction(
            sleep=req.sleep,
            stress=req.stress,
            social=req.social,
            workload=req.workload,
            screen_time=req.screen_time,
            exercise=req.exercise,
        )
        evidence = result["evidence"]

        # 2. Explainability
        explanation = compute_explanations(evidence)

        # 3. Persist to database (digital twin) — including model outputs
        insert_record(
            user_id=req.user_id,
            sleep=req.sleep,
            stress=req.stress,
            social=req.social,
            workload=req.workload,
            screen_time=req.screen_time,
            exercise=req.exercise,
            risk_score=result["risk_score"],
            anxiety_probability=result["anxiety_probability"],
            depression_probability=result["depression_probability"],
        )

        # 4. Fetch recent context for alert generation
        history          = fetch_history(req.user_id, limit=10)
        recent_risk      = [r["risk_score"] for r in history]
        recent_stress    = [r["stress"]     for r in history]
        recent_sleep     = [r["sleep"]      for r in history]

        # 5. Alerts
        alerts = generate_alerts(
            recent_risk_scores=recent_risk,
            recent_stress=recent_stress,
            recent_sleep=recent_sleep,
        )

        # 6. Recommendations
        recommendations = await generate_recommendations(
            sleep=req.sleep,
            stress=req.stress,
            social=req.social,
            workload=req.workload,
            screen_time=req.screen_time,
            exercise=req.exercise,
        )

        return PredictResponse(
            user_id=req.user_id,
            risk_score=result["risk_score"],
            anxiety_probability=result["anxiety_probability"],
            depression_probability=result["depression_probability"],
            explanation=explanation,
            alerts=alerts,
            recommendations=recommendations,
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}") from exc
