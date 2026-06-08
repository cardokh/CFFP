"""
User application service.

Responsibilities:
- Coordinate user/account use cases.
- Keep API handlers separate from repository/database details.
- Delegate validation to UserValidator.
- Delegate password operations to PasswordService.
- Work with user domain objects only.

Architecture:
API -> Mapper -> UserService -> UserValidator -> UserRepository -> SQLite Database
"""

from dataclasses import replace


class UserService:
    def __init__(
        self,
        user_repository,
        user_validator,
        password_service,
    ):
        self.user_repository = user_repository
        self.user_validator = user_validator
        self.password_service = password_service

    def get_all_users(self):
        return self.user_repository.find_all_users()

    def get_user_by_id(
        self,
        user,
    ):
        self.user_validator.validate_user_id(user)

        return self.user_repository.find_by_id(user.user_id)

    def create_user(
        self,
        user,
    ):
        self.user_validator.validate_create_user(user)

        existing_user = self.user_repository.find_by_email(user.email)

        if existing_user is not None:
            self.user_validator.raise_duplicate_email()

        user_to_create = replace(
            user,
            password_hash=self.password_service.hash_password(user.password_hash),
        )

        return self.user_repository.create_user(user_to_create)

    def register_user(
        self,
        user,
    ):
        self.user_validator.validate_register_user(user)

        existing_user = self.user_repository.find_by_email(user.email)

        if existing_user is not None:
            self.user_validator.raise_duplicate_email()

        user_to_register = replace(
            user,
            user_id=0,
            password_hash=self.password_service.hash_password(user.password_hash),
            is_active=True,
            is_verified=True,
            is_admin=False,
            created_at=None,
        )

        return self.user_repository.create_user(user_to_register)

    def update_user(
        self,
        user,
    ):
        self.user_validator.validate_update_user(user)

        return self.user_repository.update_user_basic_info(
            user_id=user.user_id,
            display_name=user.display_name,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
        )

    def delete_user(
        self,
        user,
    ):
        self.user_validator.validate_user_id(user)

        return self.user_repository.delete_user_by_id(user.user_id)

    def login(
        self,
        user,
    ):
        self.user_validator.validate_login_user(user)

        existing_user = self.user_repository.find_by_email(user.email)

        if existing_user is None:
            return None

        if not existing_user.is_active:
            return None

        if not existing_user.is_verified:
            return None

        password_is_valid = self.password_service.verify_password(
            user.password_hash,
            existing_user.password_hash,
        )

        if not password_is_valid:
            return None

        return existing_user
