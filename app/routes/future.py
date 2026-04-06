"""
app/routes/future.py — GET /future/{user_id} endpoint.

Uses historical risk scores to project the next N future values via
linear regression (see trend_service).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.database.db            import fetch_history
from app.services.trend_service import predict_future_risk
from config                     import FUTURE_STEPS

router = APIRouter()


@router.get("/future/{user_id}", tags=["Future"])
async def get_future(user_id: str):
    """
    Predict the next risk trajectory for a user based on their history.

    Returns
    -------
    {
        user_id:          str,
        history_points:   int,    # how many historical records were used
        future_risk:      list[float],  # next FUTURE_STEPS predicted values
        trend_direction:  str,          # "improving" | "worsening" | "stable"
    }
    """
    if not user_id.strip():
        raise HTTPException(status_code=422, detail="user_id must not be empty.")

    try:
        records      = fetch_history(user_id.strip(), limit=50)
        raw_scores   = [r["risk_score"] for r in records]
        future_risk  = predict_future_risk(raw_scores, steps=FUTURE_STEPS)

        # Determine overall direction from the first to last future prediction.
        if len(future_risk) >= 2:
            delta = future_risk[-1] - future_risk[0]
            if delta > 0.02:
                direction = "worsening"
            elif delta < -0.02:
                direction = "improving"
            else:
                direction = "stable"
        else:
            direction = "stable"

        return {
            "user_id":         user_id,
            "history_points":  len(raw_scores),
            "future_risk":     future_risk,
            "trend_direction": direction,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}") from exc
