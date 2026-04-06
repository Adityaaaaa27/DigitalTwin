"""
app/routes/auth.py — Signup and Login endpoints.

Simple database-based authentication. No JWT — returns user info directly
which the frontend stores in localStorage for session management.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.services.auth_service import signup_user, login_user, get_current_user
from app.services.seed_service import seed_user_history

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Request / Response schemas ────────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Please provide a valid email address.")
        return v


class LoginRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="Password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class AuthResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str = "Success"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=AuthResponse)
async def signup(req: SignupRequest) -> AuthResponse:
    """
    Create a new user account and seed 5 months of demo history data.
    Returns the user profile on success.
    """
    try:
        user = signup_user(name=req.name, email=req.email, password=req.password)

        # Seed historical data for demo purposes
        try:
            count = seed_user_history(user["id"])
            print(f"[Auth] Seeded {count} historical records for user {user['id']}")
        except Exception as e:
            print(f"[Auth] Warning: Failed to seed data: {e}")

        return AuthResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            message="Account created successfully!",
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Signup failed: {exc}") from exc


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest) -> AuthResponse:
    """
    Authenticate with email and password.
    Returns the user profile on success.
    """
    try:
        user = login_user(email=req.email, password=req.password)
        return AuthResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            message="Login successful!",
        )

    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Login failed: {exc}") from exc


@router.get("/me/{user_id}", response_model=AuthResponse)
async def me(user_id: int) -> AuthResponse:
    """Get current user profile by id."""
    user = get_current_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return AuthResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
    )
