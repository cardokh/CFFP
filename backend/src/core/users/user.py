"""
Users domain models.

Responsibilities:
- Represent internal user-related domain data.
- Keep database/domain naming in snake_case.
- Avoid HTTP, API response, and frontend concerns.

Architecture:
Repository -> Domain Model -> Mapper -> Contracts/DTOs
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    user_id: int
    display_name: str
    email: str
    password_hash: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: str | None = None


@dataclass(frozen=True)
class UserLesson:
    user_id: int
    lesson_id: int
    title: str
    category_name: str | None
    lesson_type_name: str | None
    is_active: bool
    assigned_at: str | None = None
