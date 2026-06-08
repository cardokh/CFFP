"""
User API routes.

Responsibilities:
- Handle user/account route actions.
- Keep HTTP/request handling out of UserService.
- Convert request JSON into user domain objects through mapper.
- Delegate business logic to UserService.
- Convert returned domain objects into API responses.

Architecture:
HTTP -> Routes -> Mapper -> UserService -> Repository
"""

from src.api.route_utils import (
    extract_path_id,
    read_json_body,
    send_json,
)
from src.core.users.user_mapper import (
    login_request_to_user,
    register_request_to_user,
    update_user_request_to_user,
    user_id_to_user,
    user_to_response,
    users_to_response,
)
from src.core.users.user_messages import (
    ACCOUNT_CREATED_SUCCESSFULLY,
    INVALID_JSON_BODY,
    PASSWORDS_DO_NOT_MATCH,
    REGISTRATION_FAILED,
    USER_DELETED_SUCCESSFULLY,
    USER_NOT_FOUND,
    USER_UPDATED_SUCCESSFULLY,
)


def handle_login(handler, user_service) -> None:
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_JSON_BODY,
            },
        )
        return

    try:
        user = login_request_to_user(request_data)
        logged_in_user = user_service.login(user)

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if logged_in_user is None:
        send_json(
            handler,
            401,
            {
                "success": False,
                "error": USER_NOT_FOUND,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "user": user_to_response(logged_in_user),
        },
    )


def handle_register(handler, user_service) -> None:
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_JSON_BODY,
            },
        )
        return

    try:
        password = request_data.get("password", "")
        confirm_password = request_data.get("confirmPassword", "")

        if password != confirm_password:
            send_json(
                handler,
                400,
                {
                    "success": False,
                    "error": PASSWORDS_DO_NOT_MATCH,
                },
            )
            return

        user = register_request_to_user(request_data)
        created_user = user_service.register_user(user)

        send_json(
            handler,
            201,
            {
                "success": True,
                "message": ACCOUNT_CREATED_SUCCESSFULLY,
                "user": user_to_response(created_user),
            },
        )

    except ValueError as error:
        send_json(
            handler,
            409,
            {
                "success": False,
                "error": str(error),
            },
        )

    except Exception as error:
        print("Registration error:", error)

        send_json(
            handler,
            500,
            {
                "success": False,
                "error": REGISTRATION_FAILED,
            },
        )


def handle_forgot_password(handler, user_service) -> None:
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_JSON_BODY,
            },
        )
        return

    email = request_data.get("email", "").strip()

    if not email:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": "Email is required",
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": (
                "If an account exists for this email address, "
                "a password reset link will be sent."
            ),
        },
    )


def handle_get_users(handler, user_service) -> None:
    users = user_service.get_all_users()

    send_json(
        handler,
        200,
        {
            "success": True,
            "users": users_to_response(users),
        },
    )


def handle_get_user_by_id(handler, user_service, path: str) -> None:
    try:
        user_id = extract_path_id(path)
        user = user_id_to_user(user_id)
        found_user = user_service.get_user_by_id(user)

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if found_user is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": USER_NOT_FOUND,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "user": user_to_response(found_user),
        },
    )


def handle_update_user(handler, user_service, path: str) -> None:
    try:
        user_id = extract_path_id(path)

    except ValueError:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": USER_NOT_FOUND,
            },
        )
        return

    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_JSON_BODY,
            },
        )
        return

    try:
        user = update_user_request_to_user(
            user_id=user_id,
            request_data=request_data,
        )

        updated_user = user_service.update_user(user)

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if updated_user is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": USER_NOT_FOUND,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": USER_UPDATED_SUCCESSFULLY,
            "user": user_to_response(updated_user),
        },
    )


def handle_delete_user(handler, user_service, path: str) -> None:
    try:
        user_id = extract_path_id(path)
        user = user_id_to_user(user_id)
        was_deleted = user_service.delete_user(user)

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if not was_deleted:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": USER_NOT_FOUND,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": USER_DELETED_SUCCESSFULLY,
        },
    )
