"""
Users API contracts.

Responsibilities:
- Define request and response DTOs for the Users module.
- Keep API/frontend naming in camelCase.
- Keep DTO structure separate from domain and repository models.

Architecture:
Routes -> Contracts -> Validator/Service -> Mapper -> Repository
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserResponse:
    userId: int
    displayName: str
    email: str
    isActive: bool
    isVerified: bool
    isAdmin: bool
    createdAt: str | None = None


@dataclass(frozen=True)
class UpdateUserRequest:
    displayName: str
    email: str
    isActive: bool
    isVerified: bool
    isAdmin: bool


@dataclass(frozen=True)
class UserLessonResponse:
    userId: int
    lessonId: int
    title: str
    categoryName: str | None
    lessonTypeName: str | None
    isActive: bool
    assignedAt: str | None = None


@dataclass(frozen=True)
class UpdateUserLessonsRequest:
    lessonIds: list[int]
