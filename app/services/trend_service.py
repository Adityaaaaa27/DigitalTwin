"""
app/services/trend_service.py — Moving-average + linear-regression trend prediction.

Responsibilities
----------------
* Compute a smoothed risk trend from historical scores.
* Project the next N risk scores using simple linear regression.
* Supports the /future/{user_id} endpoint.
"""
from __future__ import annotations

import numpy as np
from config import TREND_WINDOW, FUTURE_STEPS


def moving_average(scores: list[float], window: int | None = None) -> list[float]:
    """
    Return a list of simple moving averages with the given window size.
    The first (window-1) values use expanding windows so we never return
    fewer elements than the input.
    """
    w = window or TREND_WINDOW
    result: list[float] = []
    for i, _ in enumerate(scores):
        start = max(0, i - w + 1)
        chunk = scores[start : i + 1]
        result.append(round(float(np.mean(chunk)), 4))
    return result


def predict_future_risk(scores: list[float], steps: int | None = None) -> list[float]:
    """
    Extrapolate future risk values from historical scores.

    Strategy
    --------
    * If ≥ 2 data points: ordinary least-squares linear regression on the
      last TREND_WINDOW points.
    * If only 1 data point: return that value repeated.
    * If no data: return [0.5] * steps as a neutral default.

    Returns
    -------
    List of *steps* predicted risk scores, each clamped to [0, 1].
    """
    n_steps = steps or FUTURE_STEPS

    if not scores:
        return [round(0.5, 4)] * n_steps

    if len(scores) == 1:
        return [round(float(scores[0]), 4)] * n_steps

    # Use the last TREND_WINDOW scores for recency.
    window_scores = scores[-TREND_WINDOW:]
    x = np.arange(len(window_scores), dtype=float)
    y = np.array(window_scores, dtype=float)

    # Fit line: y = slope * x + intercept
    coeffs     = np.polyfit(x, y, deg=1)
    slope      = coeffs[0]
    intercept  = coeffs[1]

    # Predict the next `n_steps` time-steps.
    base = len(window_scores)
    future: list[float] = []
    for i in range(n_steps):
        predicted = slope * (base + i) + intercept
        # Clamp to valid risk range [0, 1].
        predicted = float(np.clip(predicted, 0.0, 1.0))
        future.append(round(predicted, 4))

    return future
