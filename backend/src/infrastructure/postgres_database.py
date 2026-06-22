"""
PostgreSQL database infrastructure manager.

Responsibilities:
- Resolve PostgreSQL application connection settings from repository metadata.
- Allow environment variables to override JSON configuration values.
- Create PostgreSQL database connections for CCore services.
- Keep low-level PostgreSQL connection handling out of services and repositories.
"""

import json
import os
from pathlib import Path
from typing import Any

import psycopg2


DEFAULT_POSTGRES_DATABASE_CONFIG_PATH = "scripts/db/postgres/config/database.json"
PROJECT_ROOT_MARKERS = (
    "ccore.py",
    "requirements.txt",
)


class PostgresDatabaseManager:
    def __init__(
        self,
        database_config_path: str = DEFAULT_POSTGRES_DATABASE_CONFIG_PATH,
    ):
        self.database_config_path = database_config_path
        self.project_root = self._find_project_root()
        self.connection_config = self._resolve_application_connection_config()

    def get_connection(self):
        return psycopg2.connect(
            host=self.connection_config["host"],
            port=int(self.connection_config["port"]),
            dbname=self.connection_config["databaseName"],
            user=self.connection_config["username"],
            password=self.connection_config["password"],
        )

    def _find_project_root(self) -> Path:
        current_path = Path(__file__).resolve()

        for parent_path in current_path.parents:
            if all((parent_path / marker).exists() for marker in PROJECT_ROOT_MARKERS):
                return parent_path

        return Path.cwd()

    def _load_database_config(self) -> dict[str, Any]:
        config_path = self.project_root / self.database_config_path

        with config_path.open("r", encoding="utf-8") as config_file:
            return json.load(config_file)

    def _resolve_application_connection_config(self) -> dict[str, Any]:
        database_config = self._load_database_config()
        application_config = database_config.get("applicationConnection", {})
        environment_config = database_config.get("environmentVariables", {}).get(
            "application",
            {},
        )

        resolved_config = {}

        for key, fallback_value in application_config.items():
            environment_variable = environment_config.get(key)
            environment_value = os.environ.get(environment_variable) if environment_variable else None

            resolved_config[key] = environment_value if environment_value else fallback_value

        return resolved_config
