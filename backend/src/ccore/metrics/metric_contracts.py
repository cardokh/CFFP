"""
CCore metric API request contracts.

Responsibilities:
- Represent metric create/update request data at the API boundary.
- Validate public JSON/API payload shape before domain mapping.
- Keep route handlers independent from request field extraction details.

Naming rule:
- JSON/API fields are camelCase.
- Python contract attributes are snake_case.
"""

from dataclasses import dataclass
from typing import Any

from backend.src.ccore.metrics.metric_constants import (
    CCORE_METRIC_API_FIELD_METRIC_KEY,
    CCORE_METRIC_API_FIELD_METRIC_NAME,
    CCORE_METRIC_API_FIELD_METRIC_TYPE,
)
from backend.src.ccore.metrics.metric_messages import (
    CCORE_METRIC_KEY_REQUIRED_MESSAGE,
    CCORE_METRIC_NAME_REQUIRED_MESSAGE,
    CCORE_METRIC_PAYLOAD_OBJECT_REQUIRED_MESSAGE,
    CCORE_METRIC_TYPE_REQUIRED_MESSAGE,
    CCORE_METRIC_UNKNOWN_FIELD_MESSAGE,
)

_CREATE_METRIC_FIELDS = {
    CCORE_METRIC_API_FIELD_METRIC_NAME,
    CCORE_METRIC_API_FIELD_METRIC_KEY,
    CCORE_METRIC_API_FIELD_METRIC_TYPE,
}

_UPDATE_METRIC_FIELDS = {
    CCORE_METRIC_API_FIELD_METRIC_NAME,
    CCORE_METRIC_API_FIELD_METRIC_KEY,
    CCORE_METRIC_API_FIELD_METRIC_TYPE,
}


@dataclass(frozen=True)
class CreateCCoreMetricRequest:
    metric_name: str
    metric_key: str
    metric_type_code: str | None = None


@dataclass(frozen=True)
class UpdateCCoreMetricRequest:
    metric_id: str
    metric_name: str
    metric_key: str
    metric_type_code: str


class CCoreMetricRequestParser:
    def parse_create_request(self, payload: dict[str, Any]) -> CreateCCoreMetricRequest:
        self._validate_payload_object(payload)
        self._validate_known_fields(payload, _CREATE_METRIC_FIELDS)

        metric_name = self._require_text(payload, CCORE_METRIC_API_FIELD_METRIC_NAME, CCORE_METRIC_NAME_REQUIRED_MESSAGE)
        metric_key = self._require_text(payload, CCORE_METRIC_API_FIELD_METRIC_KEY, CCORE_METRIC_KEY_REQUIRED_MESSAGE)
        metric_type_code = self._optional_text(payload, CCORE_METRIC_API_FIELD_METRIC_TYPE)

        return CreateCCoreMetricRequest(
            metric_name=metric_name,
            metric_key=metric_key,
            metric_type_code=metric_type_code,
        )

    def parse_update_request(self, metric_id: str, payload: dict[str, Any]) -> UpdateCCoreMetricRequest:
        self._validate_payload_object(payload)
        self._validate_known_fields(payload, _UPDATE_METRIC_FIELDS)

        metric_name = self._require_text(payload, CCORE_METRIC_API_FIELD_METRIC_NAME, CCORE_METRIC_NAME_REQUIRED_MESSAGE)
        metric_key = self._require_text(payload, CCORE_METRIC_API_FIELD_METRIC_KEY, CCORE_METRIC_KEY_REQUIRED_MESSAGE)
        metric_type_code = self._require_text(payload, CCORE_METRIC_API_FIELD_METRIC_TYPE, CCORE_METRIC_TYPE_REQUIRED_MESSAGE)

        return UpdateCCoreMetricRequest(
            metric_id=metric_id,
            metric_name=metric_name,
            metric_key=metric_key,
            metric_type_code=metric_type_code,
        )

    def _validate_payload_object(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ValueError(CCORE_METRIC_PAYLOAD_OBJECT_REQUIRED_MESSAGE)

    def _validate_known_fields(
        self,
        payload: dict[str, Any],
        supported_fields: set[str],
    ) -> None:
        unknown_fields = sorted(set(payload.keys()) - supported_fields)

        if unknown_fields:
            raise ValueError(
                f"{CCORE_METRIC_UNKNOWN_FIELD_MESSAGE}: {', '.join(unknown_fields)}"
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
