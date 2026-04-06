"""
app/services/prediction_service.py — Input normalisation + inference orchestration.

Responsibilities
----------------
1. Validate and discretise raw [0–10] inputs into Low/Medium/High states.
2. Delegate to the Bayesian model for probabilistic inference.
3. Return a structured result dict consumed by the /predict route.
"""
from __future__ import annotations

from config import LOW_THRESHOLD, HIGH_THRESHOLD
from app.models.bayesian_model import model, LOW, MEDIUM, HIGH


# ── Discretisation ────────────────────────────────────────────────────────────

def discretise(value: float) -> int:
    """
    Map a raw [0, 10] value to a 3-state integer.
    Low=0  if value ≤ LOW_THRESHOLD
    High=2 if value ≥ HIGH_THRESHOLD
    Medium=1 otherwise
    """
    if value <= LOW_THRESHOLD:
        return LOW
    if value >= HIGH_THRESHOLD:
        return HIGH
    return MEDIUM


def build_evidence(
    sleep: float,
    stress: float,
    social: float,
    workload: float,
    screen_time: float,
    exercise: float,
) -> dict[str, int]:
    """
    Convert raw float inputs to a pgmpy evidence dict.

    Note: For 'protective' factors (sleep, social, exercise) the raw
    discretisation applies directly — a High value is genuinely positive.
    The Bayesian CPTs already encode the direction of each factor's effect.
    """
    return {
        "Sleep":      discretise(sleep),
        "Stress":     discretise(stress),
        "Social":     discretise(social),
        "Workload":   discretise(workload),
        "ScreenTime": discretise(screen_time),
        "Exercise":   discretise(exercise),
    }


# ── Main prediction function ──────────────────────────────────────────────────

def run_prediction(
    sleep: float,
    stress: float,
    social: float,
    workload: float,
    screen_time: float,
    exercise: float,
) -> dict:
    """
    Run the full inference pipeline.

    Returns
    -------
    {
        risk_score:             float,
        anxiety_probability:    float,
        depression_probability: float,
        evidence:               dict[str, int],   # discretised inputs
    }
    """
    evidence = build_evidence(sleep, stress, social, workload, screen_time, exercise)
    result   = model.predict(evidence)
    result["evidence"] = evidence
    return result
