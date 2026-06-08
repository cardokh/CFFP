from scripts.shared.script_path_utils import (
    CONFIG,
    get_path,
)


def test_script_path_utils():
    print()

    for key, value in CONFIG.items():
        if not isinstance(value, str):
            continue

        resolved_path = get_path(key)

        print(f"{key}: {resolved_path}")


if __name__ == "__main__":
    test_script_path_utils()
