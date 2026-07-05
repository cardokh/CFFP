"""
Shared configuration resolution utilities.

The resolver keeps configuration resolution explicit by recording whether each value
came from the static configuration file or from an environment variable override.
Sensitive values are masked in reports and logs.
"""

import os
from dataclasses import dataclass
from typing import Any


SECRET_KEY_PARTS = (
    "password",
    "secret",
    "token",
    "key",
)


@dataclass(frozen=True)
class ResolvedConfigValue:
    """A resolved configuration value with source metadata."""

    key: str
    value: Any
    source: str
    environment_variable: str | None = None
    sensitive: bool = False

    def to_report_entry(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": self.masked_value,
            "source": self.source,
            "environmentVariable": self.environment_variable,
            "sensitive": self.sensitive,
        }

    @property
    def masked_value(self) -> Any:
        if not self.sensitive:
            return self.value

        if self.value in (None, ""):
            return ""

        return "********"


class ConfigurationResolver:
    """
    Resolves values from static configuration with optional environment overrides.
    """

    def __init__(self, default_source_name: str = "configuration"):
        self.default_source_name = default_source_name
        self._resolved_values: dict[str, ResolvedConfigValue] = {}

    def resolve_value(
        self,
        *,
        key: str,
        configured_values: dict[str, Any],
        environment_variables: dict[str, Any] | None = None,
        required: bool = True,
        default: Any = None,
        cast_type: type | None = None,
        sensitive: bool | None = None,
    ) -> Any:
        if not isinstance(configured_values, dict):
            raise ValueError("configured_values must be a dictionary.")

        if environment_variables is None:
            environment_variables = {}

        if not isinstance(environment_variables, dict):
            raise ValueError("environment_variables must be a dictionary when provided.")

        source = self.default_source_name
        environment_variable_name = environment_variables.get(key)
        value = None

        if isinstance(environment_variable_name, str) and environment_variable_name:
            environment_value = os.environ.get(environment_variable_name)

            if environment_value not in (None, ""):
                value = environment_value
                source = "environment"

        if value in (None, ""):
            configured_value = configured_values.get(key, default)

            if configured_value not in (None, ""):
                value = configured_value
                source = self.default_source_name

        if value in (None, "") and required:
            raise ValueError(f"Configuration value '{key}' is not configured.")

        if cast_type is not None and value not in (None, ""):
            try:
                value = cast_type(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Configuration value '{key}' could not be converted to {cast_type.__name__}.") from exc

        resolved_value = ResolvedConfigValue(
            key=key,
            value=value,
            source=source,
            environment_variable=environment_variable_name if isinstance(environment_variable_name, str) else None,
            sensitive=self._is_sensitive(key, sensitive),
        )
        self._resolved_values[key] = resolved_value
        return value

    def resolve_group(
        self,
        *,
        group_name: str,
        configured_values: dict[str, Any],
        environment_variables: dict[str, Any] | None,
        keys: list[str],
        required: bool = True,
        casts: dict[str, type] | None = None,
        sensitive_keys: set[str] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(configured_values, dict):
            raise ValueError(f"Configuration group '{group_name}' must be an object.")

        if environment_variables is None:
            environment_variables = {}

        if not isinstance(environment_variables, dict):
            raise ValueError(f"Environment variable mapping group '{group_name}' must be an object.")

        if casts is None:
            casts = {}

        if sensitive_keys is None:
            sensitive_keys = set()

        resolved_group = {}

        for key in keys:
            report_key = f"{group_name}.{key}"
            resolved_group[key] = self.resolve_value(
                key=key,
                configured_values=configured_values,
                environment_variables=environment_variables,
                required=required,
                cast_type=casts.get(key),
                sensitive=(key in sensitive_keys),
            )
            value_metadata = self._resolved_values.pop(key)
            self._resolved_values[report_key] = ResolvedConfigValue(
                key=report_key,
                value=value_metadata.value,
                source=value_metadata.source,
                environment_variable=value_metadata.environment_variable,
                sensitive=value_metadata.sensitive,
            )

        return resolved_group

    def to_report(self) -> dict[str, Any]:
        return {
            key: resolved_value.to_report_entry()
            for key, resolved_value in self._resolved_values.items()
        }

    def to_log_lines(self, title: str = "Configuration Resolution") -> list[str]:
        lines = [title]

        for key in sorted(self._resolved_values):
            resolved_value = self._resolved_values[key]
            environment_note = ""

            if resolved_value.environment_variable:
                environment_note = f" via {resolved_value.environment_variable}"

            lines.append(
                f"  {key}: {resolved_value.masked_value} ({resolved_value.source}{environment_note})"
            )

        return lines

    def _is_sensitive(self, key: str, sensitive: bool | None) -> bool:
        if sensitive is not None:
            return sensitive

        lowered_key = key.lower()
        return any(part in lowered_key for part in SECRET_KEY_PARTS)
