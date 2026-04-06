"""
app/services/explanation_service.py — Explainable AI via feature perturbation.

Methodology (sensitivity analysis / one-at-a-time perturbation)
----------------------------------------------------------------
For each input feature:
  1. Compute the baseline risk score with the actual evidence.
  2. Set that feature to its "worst" possible state (the state that, by
     domain knowledge, maximally worsens mental health).
  3. The absolute change in risk score is the feature's contribution.
  4. Normalise contributions to [0, 1] so they are comparable.

The "worst" state direction is:
    Sleep, Social, Exercise → LOW  (protective factor: having less is worse)
    Stress, Workload, ScreenTime → HIGH (risk factor: more is worse)

This gives a direct, human-readable answer to "which factor hurt you most?"
"""
from __future__ import annotations

from app.models.bayesian_model import model, LOW, HIGH


# Direction: the state that represents the "worst" value for each factor.
WORST_STATE: dict[str, int] = {
    "Sleep":      LOW,
    "Stress":     HIGH,
    "Social":     LOW,
    "Workload":   HIGH,
    "ScreenTime": HIGH,
    "Exercise":   LOW,
}


def compute_explanations(evidence: dict[str, int]) -> dict[str, float]:
    """
    Return a dict mapping each feature name to its normalised risk contribution.

    Parameters
    ----------
    evidence : discretised evidence dict (as returned by prediction_service)

    Returns
    -------
    {
        "stress":      0.45,
        "sleep":       0.30,
        "screen_time": 0.18,
        ...
    }
    Keys are lower-cased, underscore-separated for JSON friendliness.
    """
    baseline_risk = model.query_risk(evidence)

    contributions: dict[str, float] = {}

    for node, worst_state in WORST_STATE.items():
        # Already at worst state → perturbation would show no change.
        if evidence.get(node) == worst_state:
            # Feature is already maxing out its negative impact.
            # Assign a base contribution equal to the baseline risk.
            delta = baseline_risk
        else:
            # Perturb: set this feature to worst state, keep others.
            perturbed_evidence = {**evidence, node: worst_state}
            perturbed_risk = model.query_risk(perturbed_evidence)
            delta = abs(perturbed_risk - baseline_risk)

        # Map CamelCase node names → snake_case JSON keys.
        key = _node_to_key(node)
        contributions[key] = round(delta, 4)

    # Normalise so all contributions sum to 1 (0 if all deltas are zero).
    total = sum(contributions.values())
    if total > 0:
        contributions = {k: round(v / total, 4) for k, v in contributions.items()}

    # Sort descending for readability.
    contributions = dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True))
    return contributions


def _node_to_key(node: str) -> str:
    """CamelCase → snake_case for JSON output."""
    mapping = {
        "Sleep":      "sleep",
        "Stress":     "stress",
        "Social":     "social",
        "Workload":   "workload",
        "ScreenTime": "screen_time",
        "Exercise":   "exercise",
    }
    return mapping.get(node, node.lower())
