def replace_payload_placeholders(
    value,
    runtime_values: dict,
):
    if isinstance(value, dict):
        return {
            key: replace_payload_placeholders(
                item,
                runtime_values,
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            replace_payload_placeholders(
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
                replacement,
            )

        return result

    return value


def build_endpoint_payload(
    endpoint: dict,
    runtime_values: dict,
) -> dict:
    return replace_payload_placeholders(
        endpoint.get(
            "payload",
            {},
        ),
        runtime_values,
    )
