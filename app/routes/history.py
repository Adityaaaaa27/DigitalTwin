"""
app/routes/history.py — GET /history/{user_id} endpoint.

Returns all stored records for a user along with a smoothed risk trend.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.database.db         import fetch_history
from app.services.trend_service import moving_average

router = APIRouter()


@router.get("/history/{user_id}", tags=["History"])
async def get_history(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=500, description="Maximum number of records to return"),
):
    """
    Retrieve the stored mental-health history for a user.

    Returns
    -------
    {
        user_id:     str,
        record_count: int,
        records:     list of observation dicts,
        risk_trend:  list of smoothed risk scores (same length as records),
    }
    """
    if not user_id.strip():
        raise HTTPException(status_code=422, detail="user_id must not be empty.")

    try:
        records    = fetch_history(user_id.strip(), limit=limit)
        raw_scores = [r["risk_score"] for r in records]
        trend      = moving_average(raw_scores) if raw_scores else []

        return {
            "user_id":      user_id,
            "record_count": len(records),
            "records":      records,
            "risk_trend":   trend,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}") from exc
