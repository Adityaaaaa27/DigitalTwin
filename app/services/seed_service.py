"""
app/services/seed_service.py — Generate realistic demo data on signup.

Creates 5 months of historical mental health observations (4-5 per month)
using the actual Bayesian model for computed outputs. Data has realistic
gradual trends with some noise to simulate a real user's journey.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from app.database.db import insert_record
from app.services.prediction_service import run_prediction


def seed_user_history(user_id: int) -> int:
    """
    Generate ~22 historical records spanning the last 5 months for a user.
    Returns the number of records created.

    The simulated journey:
      Month 1-2: Higher stress, lower sleep (rough period)
      Month 3:   Gradual improvement
      Month 4-5: Mostly balanced with occasional dips
    """
    now = datetime.now(tz=timezone.utc)
    records_created = 0
    uid = str(user_id)

    # Define monthly profiles: (sleep, stress, social, workload, screen_time, exercise)
    # Each value is a base [0-10] with random jitter added
    monthly_profiles = [
        # Month 1 (5 months ago): Rough — low sleep, high stress
        {"sleep": 4.0, "stress": 7.5, "social": 3.5, "workload": 8.0, "screen_time": 8.0, "exercise": 2.0, "entries": 4},
        # Month 2 (4 months ago): Still struggling
        {"sleep": 4.5, "stress": 7.0, "social": 4.0, "workload": 7.5, "screen_time": 7.5, "exercise": 2.5, "entries": 5},
        # Month 3 (3 months ago): Starting to improve
        {"sleep": 5.5, "stress": 5.5, "social": 5.0, "workload": 6.0, "screen_time": 6.0, "exercise": 4.0, "entries": 4},
        # Month 4 (2 months ago): Good progress
        {"sleep": 6.5, "stress": 4.5, "social": 6.5, "workload": 5.5, "screen_time": 5.0, "exercise": 5.5, "entries": 5},
        # Month 5 (1 month ago): Mostly stable with minor fluctuations
        {"sleep": 7.0, "stress": 3.5, "social": 7.0, "workload": 5.0, "screen_time": 4.5, "exercise": 6.0, "entries": 4},
    ]

    for month_idx, profile in enumerate(monthly_profiles):
        # Calculate base date for this month
        months_ago = 5 - month_idx
        base_date = now - timedelta(days=months_ago * 30)
        entries = profile["entries"]

        for entry_idx in range(entries):
            # Spread entries across the month
            day_offset = int((30 / entries) * entry_idx) + random.randint(0, 3)
            entry_date = base_date + timedelta(days=day_offset)

            # Add realistic jitter to each metric (±1.0)
            jitter = lambda base: max(0.0, min(10.0, base + random.uniform(-1.0, 1.0)))

            sleep = round(jitter(profile["sleep"]), 1)
            stress = round(jitter(profile["stress"]), 1)
            social = round(jitter(profile["social"]), 1)
            workload = round(jitter(profile["workload"]), 1)
            screen_time = round(jitter(profile["screen_time"]), 1)
            exercise = round(jitter(profile["exercise"]), 1)

            # Run through the actual Bayesian model for realistic outputs
            result = run_prediction(
                sleep=sleep,
                stress=stress,
                social=social,
                workload=workload,
                screen_time=screen_time,
                exercise=exercise,
            )

            insert_record(
                user_id=uid,
                sleep=sleep,
                stress=stress,
                social=social,
                workload=workload,
                screen_time=screen_time,
                exercise=exercise,
                risk_score=result["risk_score"],
                anxiety_probability=result["anxiety_probability"],
                depression_probability=result["depression_probability"],
                date_override=entry_date.isoformat(),
            )
            records_created += 1

    return records_created
