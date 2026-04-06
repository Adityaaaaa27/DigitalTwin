"""
app/models/bayesian_model.py — Core Bayesian Network with precomputed lookup table.

Graph topology
--------------
Observed (leaf) nodes:
    Sleep, Stress, Workload, Social, ScreenTime, Exercise

Intermediate nodes:
    Anxiety    ← Sleep, Stress, Social, ScreenTime
    Depression ← Sleep, Workload, Exercise, Social

Output node:
    Risk ← Anxiety, Depression

All CPTs are hand-crafted with domain-plausible probabilities.
Each variable has three states: 0=Low, 1=Medium, 2=High.

Performance
-----------
Instead of running pgmpy VariableElimination on every request (which is very slow),
we precompute all 3^6=729 possible inference results at module load time and store
them in a dictionary.  All subsequent requests are instant O(1) dict lookups.
"""
from __future__ import annotations

import itertools
import numpy as np
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork

# ── State constants ───────────────────────────────────────────────────────────
LOW, MEDIUM, HIGH = 0, 1, 2
STATES = [LOW, MEDIUM, HIGH]

# Evidence variable names in a fixed canonical order for lookup key
EVIDENCE_NODES = ["Sleep", "Stress", "Social", "Workload", "ScreenTime", "Exercise"]


# ────────────────────────────────────────────────────────────────────────────
# Helper – build a CPD whose columns sum to 1 from a raw value list.
# ────────────────────────────────────────────────────────────────────────────

def _normalize_cpd(values: list[list[float]]) -> np.ndarray:
    """Column-normalize a CPT so each column sums to exactly 1.0."""
    arr = np.array(values, dtype=float)
    col_sums = arr.sum(axis=0, keepdims=True)
    return (arr / col_sums).tolist()


# ── Network edges ─────────────────────────────────────────────────────────────
EDGES = [
    ("Sleep",       "Anxiety"),
    ("Stress",      "Anxiety"),
    ("Social",      "Anxiety"),
    ("ScreenTime",  "Anxiety"),
    ("Sleep",       "Depression"),
    ("Workload",    "Depression"),
    ("Exercise",    "Depression"),
    ("Social",      "Depression"),
    ("Anxiety",     "Risk"),
    ("Depression",  "Risk"),
]


# ── CPDs for root (prior) nodes ───────────────────────────────────────────────

def _root_cpd(name: str, probs: list[float]) -> TabularCPD:
    """Create a marginal CPD for a root node with 3 states."""
    return TabularCPD(variable=name, variable_card=3, values=[[p] for p in probs])


# ── Anxiety CPD (parents: Sleep, Stress, Social, ScreenTime) ─────────────────

def _build_anxiety_cpd() -> TabularCPD:
    columns: list[list[float]] = []
    for sleep in STATES:
        for stress in STATES:
            for social in STATES:
                for screen in STATES:
                    score = (
                        (2 - sleep)   * 2   +
                        stress        * 2   +
                        (2 - social)  * 1   +
                        screen        * 1
                    )
                    p_low  = max(0.05, 1.0 - score / 12)
                    p_high = max(0.05, score / 12)
                    p_med  = max(0.05, 1.0 - p_low - p_high + 0.05)
                    columns.append([p_low, p_med, p_high])

    normalised = _normalize_cpd(list(zip(*columns)))
    return TabularCPD(
        variable="Anxiety",
        variable_card=3,
        values=normalised,
        evidence=["Sleep", "Stress", "Social", "ScreenTime"],
        evidence_card=[3, 3, 3, 3],
    )


# ── Depression CPD (parents: Sleep, Workload, Exercise, Social) ───────────────

def _build_depression_cpd() -> TabularCPD:
    columns: list[list[float]] = []
    for sleep in STATES:
        for workload in STATES:
            for exercise in STATES:
                for social in STATES:
                    score = (
                        (2 - sleep)     * 2 +
                        workload        * 2 +
                        (2 - exercise)  * 1 +
                        (2 - social)    * 1
                    )
                    p_low  = max(0.05, 1.0 - score / 12)
                    p_high = max(0.05, score / 12)
                    p_med  = max(0.05, 1.0 - p_low - p_high + 0.05)
                    columns.append([p_low, p_med, p_high])

    normalised = _normalize_cpd(list(zip(*columns)))
    return TabularCPD(
        variable="Depression",
        variable_card=3,
        values=normalised,
        evidence=["Sleep", "Workload", "Exercise", "Social"],
        evidence_card=[3, 3, 3, 3],
    )


# ── Risk CPD (parents: Anxiety, Depression) ───────────────────────────────────

def _build_risk_cpd() -> TabularCPD:
    raw_values = []
    for anxiety in STATES:
        for depression in STATES:
            score = anxiety + depression
            p_low  = max(0.05, 1.0 - score / 4)
            p_high = max(0.05, score / 4)
            p_med  = max(0.05, 1.0 - p_low - p_high + 0.05)
            raw_values.append([p_low, p_med, p_high])

    normalised = _normalize_cpd(list(zip(*raw_values)))
    return TabularCPD(
        variable="Risk",
        variable_card=3,
        values=normalised,
        evidence=["Anxiety", "Depression"],
        evidence_card=[3, 3],
    )


# ────────────────────────────────────────────────────────────────────────────
# Singleton model with precomputed lookup table
# ────────────────────────────────────────────────────────────────────────────

class MentalHealthBayesianModel:
    """
    Wraps the pgmpy BayesianNetwork. Uses a precomputed lookup table for
    all 3^6 = 729 possible evidence combinations so every request is O(1).
    """

    def __init__(self) -> None:
        self._bn = BayesianNetwork(EDGES)

        self._bn.add_cpds(
            _root_cpd("Sleep",      [0.33, 0.34, 0.33]),
            _root_cpd("Stress",     [0.33, 0.34, 0.33]),
            _root_cpd("Workload",   [0.33, 0.34, 0.33]),
            _root_cpd("Social",     [0.33, 0.34, 0.33]),
            _root_cpd("ScreenTime", [0.33, 0.34, 0.33]),
            _root_cpd("Exercise",   [0.33, 0.34, 0.33]),
            _build_anxiety_cpd(),
            _build_depression_cpd(),
            _build_risk_cpd(),
        )

        if not self._bn.check_model():
            raise RuntimeError("Bayesian Network model is invalid — check CPDs.")

        # Build precomputed lookup table for all 3^6 = 729 evidence combinations.
        print("[BayesianModel] Precomputing inference table for all 729 evidence combinations...")
        self._infer = VariableElimination(self._bn)
        self._lookup: dict[tuple, dict[str, float]] = {}
        self._precompute_all()
        print(f"[BayesianModel] Precomputation complete. {len(self._lookup)} states cached.")

    def _precompute_all(self) -> None:
        """
        Enumerate all combinations of (Sleep, Stress, Social, Workload, ScreenTime, Exercise)
        each in {0,1,2} and run inference once per combination.
        Results are stored in self._lookup keyed by a tuple of state values.
        """
        for combo in itertools.product(STATES, repeat=6):
            sleep, stress, social, workload, screen, exercise = combo
            evidence = {
                "Sleep":      sleep,
                "Stress":     stress,
                "Social":     social,
                "Workload":   workload,
                "ScreenTime": screen,
                "Exercise":   exercise,
            }
            anxiety_dist    = self._infer.query(["Anxiety"],    evidence=evidence, show_progress=False)
            depression_dist = self._infer.query(["Depression"], evidence=evidence, show_progress=False)
            risk_dist       = self._infer.query(["Risk"],       evidence=evidence, show_progress=False)

            p_anxiety    = float(anxiety_dist.values[HIGH])
            p_depression = float(depression_dist.values[HIGH])
            risk_values  = risk_dist.values
            risk_score   = float(np.dot(risk_values, [0.0, 0.5, 1.0]))

            self._lookup[combo] = {
                "anxiety_probability":    round(p_anxiety,    4),
                "depression_probability": round(p_depression, 4),
                "risk_score":             round(risk_score,   4),
            }

    def _evidence_to_key(self, evidence: dict[str, int]) -> tuple:
        """Convert an evidence dict to the canonical tuple key."""
        return (
            evidence.get("Sleep",      MEDIUM),
            evidence.get("Stress",     MEDIUM),
            evidence.get("Social",     MEDIUM),
            evidence.get("Workload",   MEDIUM),
            evidence.get("ScreenTime", MEDIUM),
            evidence.get("Exercise",   MEDIUM),
        )

    # ── Public interface ──────────────────────────────────────────────────────

    def predict(self, evidence: dict[str, int]) -> dict[str, float]:
        """
        Instant O(1) lookup from precomputed table.

        Parameters
        ----------
        evidence : mapping of node name → state (0=Low, 1=Medium, 2=High)

        Returns
        -------
        {
            "anxiety_probability":    float,
            "depression_probability": float,
            "risk_score":             float,
        }
        """
        key = self._evidence_to_key(evidence)
        return self._lookup[key]

    def query_risk(self, evidence: dict[str, int]) -> float:
        """Convenience method: return only the scalar risk score."""
        return self.predict(evidence)["risk_score"]


# Module-level singleton — imported by services.
# The precomputation runs once here at import time (server startup).
model = MentalHealthBayesianModel()
