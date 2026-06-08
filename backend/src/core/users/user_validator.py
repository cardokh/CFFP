"""
User validator.

Responsibilities:
- Validate user domain objects before service operations.
- Keep validation rules out of routes and services.
- Centralize account, login, registration, and admin CRUD validation.

Architecture:
Mapper -> UserValidator -> UserService -> UserRepository
"""


class UserValidator:
    def validate_user_id(self, user) -> None:
        if user.user_id <= 0:
            raise ValueError("Invalid user ID")

    def validate_login_user(self, user) -> None:
        if not user.email or not user.email.strip():
            raise ValueError("Email is required")

        if not user.password_hash:
            raise ValueError("Password is required")

    def validate_register_user(self, user) -> None:
        if not user.display_name or not user.display_name.strip():
            raise ValueError("Display name is required")

        if not user.email or not user.email.strip():
            raise ValueError("Email is required")

        if "@" not in user.email:
            raise ValueError("Please enter a valid email address.")

        if not user.password_hash:
            raise ValueError("Password is required")

        if len(user.password_hash) < 8:
            raise ValueError("Password must be at least 8 characters.")

    def validate_create_user(self, user) -> None:
        self.validate_register_user(user)

    def validate_update_user(self, user) -> None:
        self.validate_user_id(user)

        if not user.display_name or not user.display_name.strip():
            raise ValueError("Display name is required")

        if not user.email or not user.email.strip():
            raise ValueError("Email is required")

        if "@" not in user.email:
            raise ValueError("Please enter a valid email address.")

    def raise_duplicate_email(self) -> None:
        raise ValueError("A user with this email already exists.")
