"""
app/services/auth_service.py — Simple database-based authentication.

Uses bcrypt for password hashing. No JWT — the frontend stores user info
in localStorage and sends user_id with each request.
"""
from __future__ import annotations

import bcrypt

from app.database.db import create_user, get_user_by_email, get_user_by_id


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def signup_user(name: str, email: str, password: str) -> dict:
    """
    Register a new user. Returns user dict on success.
    Raises ValueError if email already exists.
    """
    existing = get_user_by_email(email)
    if existing:
        raise ValueError("An account with this email already exists.")

    pw_hash = hash_password(password)
    user_id = create_user(name=name, email=email, password_hash=pw_hash)

    return {
        "id": user_id,
        "name": name,
        "email": email,
    }


def login_user(email: str, password: str) -> dict:
    """
    Authenticate a user by email and password.
    Returns user dict on success. Raises ValueError on failure.
    """
    user = get_user_by_email(email)
    if not user:
        raise ValueError("Invalid email or password.")

    if not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password.")

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
    }


def get_current_user(user_id: int) -> dict | None:
    """Fetch user profile by ID."""
    user = get_user_by_id(user_id)
    if not user:
        return None
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
    }
