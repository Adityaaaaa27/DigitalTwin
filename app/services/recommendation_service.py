"""
app/services/recommendation_service.py — Alert generation and recommendations.

Alert rules
-----------
* UPWARD_TREND : Risk has increased on every one of the last N consecutive records.
* STRESS_SLEEP  : Stress increasing while Sleep is decreasing over last 3 records.

Recommendation rules
--------------------
Evaluated using deterministic rule-based logic.
"""
from __future__ import annotations

from config import ALERT_CONSECUTIVE_INCREASE


# ── Alert thresholds ──────────────────────────────────────────────────────────

_STRESS_SLEEP_WINDOW = 3   # look-back window for stress/sleep divergence


# ── Internal helpers ──────────────────────────────────────────────────────────

def _is_strictly_increasing(values: list[float]) -> bool:
    """Return True if every element is greater than the previous one."""
    return all(b > a for a, b in zip(values, values[1:]))


# ── Public API ────────────────────────────────────────────────────────────────

def generate_alerts(
    recent_risk_scores: list[float],
    recent_stress: list[float] | None = None,
    recent_sleep: list[float] | None = None,
) -> list[str]:
    """
    Evaluate alert rules against recent history.

    Parameters
    ----------
    recent_risk_scores : risk scores in chronological order (oldest first).
    recent_stress      : raw stress values in same order (optional).
    recent_sleep       : raw sleep values in same order (optional).

    Returns
    -------
    List of human-readable alert strings (empty list = no alerts).
    """
    alerts: list[str] = []
    n = ALERT_CONSECUTIVE_INCREASE

    # Rule 1: Upward risk trend
    if len(recent_risk_scores) >= n:
        tail = recent_risk_scores[-n:]
        if _is_strictly_increasing(tail):
            alerts.append(
                f"⚠️ Risk has increased consecutively for the last {n} sessions. "
                "Please consult a mental-health professional."
            )

    # Rule 2: Stress up & Sleep down
    if recent_stress and recent_sleep and len(recent_stress) >= _STRESS_SLEEP_WINDOW:
        stress_tail = recent_stress[-_STRESS_SLEEP_WINDOW:]
        sleep_tail  = recent_sleep[-_STRESS_SLEEP_WINDOW:]
        if _is_strictly_increasing(stress_tail) and _is_strictly_increasing(
            [-s for s in sleep_tail]   # decreasing sleep == increasing negatives
        ):
            alerts.append(
                "⚠️ Stress is rising while Sleep is declining — a high-risk combination. "
                "Prioritise rest and relaxation techniques."
            )

    return alerts


async def generate_recommendations(
    sleep: float,
    stress: float,
    social: float,
    workload: float,
    screen_time: float,
    exercise: float,
) -> list[str]:
    """
    Generate actionable recommendations using local rules.
    """
    # ── Rule-based recommendations ────────────────────────────────────────────
    recs: list[str] = []

    if sleep < 4:
        recs.append(
            "🛌 Your sleep score is low. Aim for 7–9 hours of quality sleep. "
            "Try a consistent bedtime, avoid screens before bed, and limit caffeine after noon."
        )

    if stress > 6:
        recs.append(
            "🧘 High stress detected. Practice mindfulness, deep breathing, or progressive muscle "
            "relaxation for 10–15 minutes daily to lower your stress response."
        )

    if social < 4:
        recs.append(
            "👥 Low social engagement can worsen mood. Try to schedule at least one meaningful "
            "interaction per day — a call, coffee, or group activity."
        )

    if workload > 7:
        recs.append(
            "📋 Your workload appears very high. Consider timeboxing tasks, delegating, "
            "and taking short breaks (Pomodoro technique) to prevent burnout."
        )

    if exercise < 3:
        recs.append(
            "🏃 Low exercise levels are associated with higher depression risk. "
            "Even 20–30 minutes of walking daily can significantly improve mood."
        )

    if screen_time > 7:
        recs.append(
            "📵 Excessive screen time can disrupt sleep and increase anxiety. "
            "Apply the 20-20-20 rule: every 20 minutes, look 20 feet away for 20 seconds."
        )

    if not recs:
        recs.append("✅ Your inputs look balanced. Keep up the healthy habits!")

    return recs
