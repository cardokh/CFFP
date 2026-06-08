import json
import os
from functools import lru_cache

from src.core.shared.app_config_utils import (
    get_config_file_path,
)

from src.core.shared.app_path_utils import (
    get_path,
)

DATABASE_PATH = get_path("database")


@lru_cache(maxsize=1)
def load_app_config():

    config_path = get_config_file_path(__file__)

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_environment_file():
    env_path = get_path("environmentFilePath")

    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split(
                "=",
                1,
            )

            os.environ.setdefault(
                key.strip(),
                value.strip(),
            )


def get_app_setting(key: str):
    config = load_app_config()

    if key not in config:
        raise KeyError(f"Application config key not found: {key}")

    return config[key]


def get_environment_variable(name: str):
    load_environment_file()

    return os.environ.get(name)
