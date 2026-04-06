"""
app/database/schema.py — Table definitions and initialisation using SQLAlchemy.

Tables:
  - users:     Authentication & user profile
  - user_data: Historical mental health observations linked to users
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, MetaData, Table, Index, Text
)
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# ── Users table ───────────────────────────────────────────────────────────────
users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', Text, nullable=False),
    Column('email', Text, nullable=False, unique=True),
    Column('password_hash', Text, nullable=False),
    Column('created_at', Text, nullable=False),
)

# ── User data table (mental health observations) ─────────────────────────────
user_data_table = Table(
    'user_data', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', String(50), nullable=False),
    Column('date', String(50), nullable=False),
    Column('sleep', Float, nullable=False),
    Column('stress', Float, nullable=False),
    Column('social', Float, nullable=False),
    Column('workload', Float, nullable=False),
    Column('screen_time', Float, nullable=False),
    Column('exercise', Float, nullable=False),
    Column('risk_score', Float, nullable=False),
    Column('anxiety_probability', Float, nullable=True),
    Column('depression_probability', Float, nullable=True),
)

Index('idx_user_data_user_id', user_data_table.c.user_id, user_data_table.c.date)
Index('idx_users_email', users_table.c.email, unique=True)


def init_db() -> None:
    """Create tables and indexes if they do not already exist."""
    metadata.create_all(engine)

    # Add new columns to existing tables if they don't exist (migration)
    with engine.connect() as conn:
        try:
            conn.execute(
                __import__('sqlalchemy', fromlist=['text']).text(
                    "ALTER TABLE user_data ADD COLUMN anxiety_probability FLOAT"
                )
            )
            conn.commit()
        except Exception:
            pass  # Column already exists

        try:
            conn.execute(
                __import__('sqlalchemy', fromlist=['text']).text(
                    "ALTER TABLE user_data ADD COLUMN depression_probability FLOAT"
                )
            )
            conn.commit()
        except Exception:
            pass  # Column already exists
