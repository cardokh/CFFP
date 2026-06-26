import re
from typing import Any

PLACEHOLDER_PATTERN = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


def get_value_by_path(source: Any, path: str) -> Any:
    current = source

    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Response path not found: {path}")
            current = current[part]
            continue

        if isinstance(current, list):
            index = int(part)
            current = current[index]
            continue

        raise KeyError(f"Response path cannot be resolved: {path}")

    return current


def replace_placeholders(value: Any, runtime_values: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {
            key: replace_placeholders(item, runtime_values)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            replace_placeholders(item, runtime_values)
            for item in value
        ]

    if isinstance(value, str):
        placeholders = PLACEHOLDER_PATTERN.findall(value)

        if len(placeholders) == 1 and value == f"{{{{{placeholders[0]}}}}}":
            return runtime_values.get(placeholders[0], value)

        result = value

        for key in placeholders:
            if key in runtime_values:
                result = result.replace(
                    f"{{{{{key}}}}}",
                    str(runtime_values[key]),
                )

        return result

    return value


def capture_response_values(
    response_body: Any,
    capture_config: dict[str, str] | None,
    runtime_values: dict[str, Any],
) -> dict[str, Any]:
    captured_values: dict[str, Any] = {}

    if not capture_config:
        return captured_values

    for key, path in capture_config.items():
        captured_value = get_value_by_path(
            response_body,
            path,
        )

        runtime_values[key] = captured_value
        captured_values[key] = captured_value

    return captured_values
