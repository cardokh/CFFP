def replace_placeholders(
    value,
    runtime_values: dict,
):
    if isinstance(value, dict):
        return {
            key: replace_placeholders(
                item,
                runtime_values,
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            replace_placeholders(
                item,
                runtime_values,
            )
            for item in value
        ]

    if isinstance(value, str):
        result = value

        for key, replacement in runtime_values.items():
            result = result.replace(
                f"{{{{{key}}}}}",
                str(replacement),
            )

        return result

    return value


def build_endpoint_path(
    endpoint: dict,
    runtime_values: dict,
) -> str:
    return replace_placeholders(
        endpoint["path"],
        runtime_values,
    )


def build_endpoint_payload(
    endpoint: dict,
    runtime_values: dict,
) -> dict:
    return replace_placeholders(
        endpoint.get(
            "payload",
            {},
        ),
        runtime_values,
    )
