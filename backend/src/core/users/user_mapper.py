"""
User mapper.

Responsibilities:
- Convert request dictionaries into User domain objects.
- Convert User domain objects into API response dictionaries.
- Keep DTO/API field naming out of services and repositories.

Architecture:
Routes -> Mapper -> UserService -> Repository
"""

from src.core.users.user import User


def user_id_to_user(user_id: int) -> User:
    return User(
        user_id=user_id,
        display_name="",
        email="",
        password_hash="",
        is_active=True,
        is_verified=True,
        is_admin=False,
        created_at=None,
    )


def login_request_to_user(request_data: dict) -> User:
    return User(
        user_id=0,
        display_name="",
        email=request_data.get("email", "").strip().lower(),
        password_hash=request_data.get("password", ""),
        is_active=True,
        is_verified=True,
        is_admin=False,
        created_at=None,
    )


def register_request_to_user(request_data: dict) -> User:
    return User(
        user_id=0,
        display_name=request_data.get("displayName", "").strip(),
        email=request_data.get("email", "").strip().lower(),
        password_hash=request_data.get("password", ""),
        is_active=True,
        is_verified=True,
        is_admin=False,
        created_at=None,
    )


def update_user_request_to_user(
    user_id: int,
    request_data: dict,
) -> User:
    return User(
        user_id=user_id,
        display_name=request_data.get("displayName", "").strip(),
        email=request_data.get("email", "").strip().lower(),
        password_hash="",
        is_active=bool(request_data.get("isActive", False)),
        is_verified=bool(request_data.get("isVerified", False)),
        is_admin=bool(request_data.get("isAdmin", False)),
        created_at=None,
    )


def user_to_response(user: User) -> dict:
    return {
        "userId": user.user_id,
        "displayName": user.display_name,
        "email": user.email,
        "isActive": user.is_active,
        "isVerified": user.is_verified,
        "isAdmin": user.is_admin,
        "createdAt": user.created_at,
    }


def users_to_response(users: list[User]) -> list[dict]:
    return [user_to_response(user) for user in users]
