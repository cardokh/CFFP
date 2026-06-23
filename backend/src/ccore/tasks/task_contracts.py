"""
CCore task API request contracts.

Responsibilities:
- Represent task create/update request data at the API boundary.
- Validate public JSON/API payload shape before domain mapping.
- Keep API parsing independent from repository and service logic.
"""

from dataclasses import dataclass
from typing import Any

from backend.src.ccore.tasks.task_constants import (
    CCORE_TASK_API_FIELD_STATUS_ID,
    CCORE_TASK_API_FIELD_TASK_NAME,
)
from backend.src.ccore.tasks.task_messages import (
    CCORE_TASK_NAME_REQUIRED_MESSAGE,
    CCORE_TASK_PAYLOAD_OBJECT_REQUIRED_MESSAGE,
    CCORE_TASK_STATUS_REQUIRED_MESSAGE,
    CCORE_TASK_UNKNOWN_FIELD_MESSAGE,
)

_CREATE_TASK_FIELDS = {
    CCORE_TASK_API_FIELD_TASK_NAME,
    CCORE_TASK_API_FIELD_STATUS_ID,
}
_UPDATE_TASK_FIELDS = {
    CCORE_TASK_API_FIELD_TASK_NAME,
    CCORE_TASK_API_FIELD_STATUS_ID,
}


@dataclass(frozen=True)
class CreateCCoreTaskRequest:
    task_name: str
    status_id: int | None = None


@dataclass(frozen=True)
class UpdateCCoreTaskRequest:
    task_id: str
    task_name: str
    status_id: int


class CCoreTaskRequestParser:
    def parse_create_request(self, payload: dict[str, Any]) -> CreateCCoreTaskRequest:
        self._validate_payload_object(payload)
        self._validate_known_fields(payload, _CREATE_TASK_FIELDS)

        task_name = self._require_text(
            payload,
            CCORE_TASK_API_FIELD_TASK_NAME,
            CCORE_TASK_NAME_REQUIRED_MESSAGE,
        )
        status_id = self._optional_integer(payload, CCORE_TASK_API_FIELD_STATUS_ID)

        return CreateCCoreTaskRequest(task_name=task_name, status_id=status_id)

    def parse_update_request(
        self,
        task_id: str,
        payload: dict[str, Any],
    ) -> UpdateCCoreTaskRequest:
        self._validate_payload_object(payload)
        self._validate_known_fields(payload, _UPDATE_TASK_FIELDS)

        task_name = self._require_text(
            payload,
            CCORE_TASK_API_FIELD_TASK_NAME,
            CCORE_TASK_NAME_REQUIRED_MESSAGE,
        )
        status_id = self._require_integer(
            payload,
            CCORE_TASK_API_FIELD_STATUS_ID,
            CCORE_TASK_STATUS_REQUIRED_MESSAGE,
        )

        return UpdateCCoreTaskRequest(
            task_id=task_id,
            task_name=task_name,
            status_id=status_id,
        )

    def _validate_payload_object(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ValueError(CCORE_TASK_PAYLOAD_OBJECT_REQUIRED_MESSAGE)

    def _validate_known_fields(
        self,
        payload: dict[str, Any],
        supported_fields: set[str],
    ) -> None:
        unknown_fields = sorted(set(payload.keys()) - supported_fields)

        if unknown_fields:
            raise ValueError(
                f"{CCORE_TASK_UNKNOWN_FIELD_MESSAGE}: {', '.join(unknown_fields)}"
            )

    def _require_text(
        self,
        payload: dict[str, Any],
        field_name: str,
        message: str,
    ) -> str:
        value = self._optional_text(payload, field_name)

        if value is None:
            raise ValueError(message)

        return value

    def _optional_text(self, payload: dict[str, Any], field_name: str) -> str | None:
        value = payload.get(field_name)

        if value is None:
            return None

        text_value = str(value).strip()

        if not text_value:
            return None

        return text_value

    def _require_integer(
        self,
        payload: dict[str, Any],
        field_name: str,
        message: str,
    ) -> int:
        value = self._optional_integer(payload, field_name)

        if value is None:
            raise ValueError(message)

        return value

    def _optional_integer(self, payload: dict[str, Any], field_name: str) -> int | None:
        value = payload.get(field_name)

        if value is None:
            return None

        try:
            integer_value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(CCORE_TASK_STATUS_REQUIRED_MESSAGE) from exc

        if integer_value <= 0:
            raise ValueError(CCORE_TASK_STATUS_REQUIRED_MESSAGE)

        return integer_value
