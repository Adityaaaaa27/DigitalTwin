"""
app/database/db.py — Data-access layer using SQLAlchemy.

Provides CRUD operations for both users and user_data tables.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import insert, select, desc, text

from app.database.schema import engine, user_data_table, users_table


# ══════════════════════════════════════════════════════════════════════════════
# User operations
# ══════════════════════════════════════════════════════════════════════════════

def create_user(name: str, email: str, password_hash: str) -> int:
    """Create a new user and return their id."""
    now = datetime.now(tz=timezone.utc).isoformat()
    stmt = insert(users_table).values(
        name=name,
        email=email,
        password_hash=password_hash,
        created_at=now,
    )
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.lastrowid  # type: ignore[return-value]


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    """Fetch a user by email. Returns None if not found."""
    stmt = select(users_table).where(users_table.c.email == email)
    with engine.connect() as conn:
        row = conn.execute(stmt).fetchone()
    return dict(row._mapping) if row else None


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    """Fetch a user by id. Returns None if not found."""
    stmt = select(users_table).where(users_table.c.id == user_id)
    with engine.connect() as conn:
        row = conn.execute(stmt).fetchone()
    return dict(row._mapping) if row else None


# ══════════════════════════════════════════════════════════════════════════════
# User data (mental health observations)
# ══════════════════════════════════════════════════════════════════════════════

def insert_record(
    user_id: str,
    sleep: float,
    stress: float,
    social: float,
    workload: float,
    screen_time: float,
    exercise: float,
    risk_score: float,
    anxiety_probability: float = 0.0,
    depression_probability: float = 0.0,
    date_override: str | None = None,
) -> int:
    """
    Persist one observation for a user. Returns the new row id.
    The timestamp is always recorded in UTC so reports are timezone-agnostic.
    If date_override is provided, use that instead of current time (for seeding).
    """
    now = date_override or datetime.now(tz=timezone.utc).isoformat()
    stmt = insert(user_data_table).values(
        user_id=user_id,
        date=now,
        sleep=sleep,
        stress=stress,
        social=social,
        workload=workload,
        screen_time=screen_time,
        exercise=exercise,
        risk_score=risk_score,
        anxiety_probability=anxiety_probability,
        depression_probability=depression_probability,
    )
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.lastrowid  # type: ignore[return-value]


def fetch_history(user_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """
    Return up to *limit* records for a user, ordered oldest → newest.
    Each element is a dict that mirrors the user_data columns.
    """
    stmt = (
        select(user_data_table)
        .where(user_data_table.c.user_id == user_id)
        .order_by(user_data_table.c.date.asc())
        .limit(limit)
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt).fetchall()
    return [dict(row._mapping) for row in rows]


def fetch_recent_risk_scores(user_id: str, n: int) -> list[float]:
    """
    Return the *n* most recent risk scores for a user (oldest first).
    Used by trend and alert services.
    """
    stmt = (
        select(user_data_table.c.risk_score)
        .where(user_data_table.c.user_id == user_id)
        .order_by(desc(user_data_table.c.date))
        .limit(n)
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt).fetchall()
    return [float(row[0]) for row in reversed(rows)]
