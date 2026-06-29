"""Adds generic metadata table definitions from the current PostgreSQL metadata source."""

import json
import sys
import time
from pathlib import Path
from typing import Any


def _configure_project_import_path() -> None:
    project_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "shared").is_dir()
        ),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file


class AddMetadataTablesScript(BaseScript):
    """Adds table metadata to the generic database-neutral metadata model."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.source_metadata_root = self._resolve_project_path("sourceMetadataRoot")
        self.target_metadata_root = self._resolve_project_path("targetMetadataRoot")
        self.target_module = self.config.get("targetModule", "ccore/automation")

    def run(self) -> None:
        started = time.perf_counter()
        requested_tables = self._read_requested_tables()
        added_tables: list[str] = []

        for table_name in requested_tables:
            table_root = self.target_metadata_root / "modules" / self.target_module / "tables" / table_name
            table_root.mkdir(parents=True, exist_ok=True)
            write_json_file(table_root / "schema.json", self._build_table_schema(table_name))
            write_json_file(table_root / "data.json", self._build_table_data(table_name))
            added_tables.append(table_name)

        self._write_table_registry(added_tables)
        self._write_database_metadata()

        self.write_json_report(
            {
                "scriptName": self.script_name,
                "summary": {
                    "status": "PASSED",
                    "tableCount": len(added_tables),
                    "targetModule": self.target_module,
                    "elapsedSeconds": round(time.perf_counter() - started, 3),
                },
                "tables": added_tables,
            }
        )
        print_passed(f"add_metadata_tables: added {len(added_tables)} metadata tables")

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _read_requested_tables(self) -> list[str]:
        requested_tables = self.config.get("tables", [])
        if requested_tables == ["*"]:
            entities = read_json_file(self.source_metadata_root / "entities.json").get("entities", [])
            return list(entities)
        if not isinstance(requested_tables, list):
            raise ValueError("Config value 'tables' must be a list.")
        return [str(table_name) for table_name in requested_tables]

    def _build_table_schema(self, table_name: str) -> dict[str, Any]:
        schema = read_json_file(self.source_metadata_root / "entities" / table_name / "schema.json")
        columns = []
        primary_key = []
        foreign_keys = []
        constraints = []

        for source_column in schema.get("columns", []):
            column = {
                "name": source_column["name"],
                "type": self._to_generic_type(source_column["type"]),
                "nullable": bool(source_column.get("nullable", not source_column.get("primaryKey", False))),
            }
            if source_column.get("primaryKey") is True:
                column["nullable"] = False
                primary_key.append(source_column["name"])
            if "default" in source_column:
                column["default"] = self._to_generic_default(source_column["default"])
            if source_column.get("unique") is True:
                column["unique"] = True
            columns.append(column)

        for source_constraint in schema.get("constraints", []):
            constraint_type = source_constraint.get("type")
            if constraint_type == "primaryKey":
                primary_key = source_constraint.get("columns", primary_key)
            elif constraint_type == "foreignKey":
                foreign_key = {
                    "columns": source_constraint.get("columns", []),
                    "references": {
                        "table": source_constraint.get("references", {}).get("table"),
                        "columns": source_constraint.get("references", {}).get("columns", []),
                    },
                }
                if source_constraint.get("onDelete"):
                    foreign_key["onDelete"] = source_constraint["onDelete"].lower()
                if source_constraint.get("onUpdate"):
                    foreign_key["onUpdate"] = source_constraint["onUpdate"].lower()
                foreign_keys.append(foreign_key)
            else:
                constraints.append(source_constraint)

        metadata = {
            "name": table_name,
            "columns": columns,
            "primaryKey": primary_key,
            "foreignKeys": foreign_keys,
        }
        if constraints:
            metadata["constraints"] = constraints
        return metadata

    def _build_table_data(self, table_name: str) -> dict[str, Any]:
        seed = read_json_file(self.source_metadata_root / "entities" / table_name / "seed_data.json")
        return {"table": table_name, "rows": seed.get("rows", [])}

    def _write_table_registry(self, added_tables: list[str]) -> None:
        module_root = self.target_metadata_root / "modules" / self.target_module
        module_root.mkdir(parents=True, exist_ok=True)
        registry_path = module_root / "tables.json"
        existing_tables = []
        if registry_path.exists():
            existing_tables = read_json_file(registry_path).get("tables", [])
        merged_tables = sorted(set(existing_tables) | set(added_tables))
        write_json_file(registry_path, {"tables": merged_tables})

    def _write_database_metadata(self) -> None:
        database_metadata = {
            "name": self.config.get("databaseName", "CFFP"),
            "version": self.config.get("metadataVersion", "1.0"),
            "description": "Generic database metadata source for CFFP database generation.",
            "currentImplementation": self.config.get("currentImplementation", "postgres"),
        }
        write_json_file(self.target_metadata_root / "database.json", database_metadata)

        implementation_config_path = self.config.get("implementationConfigSource")
        if implementation_config_path:
            source_path = self.project_root / implementation_config_path
            implementation_name = database_metadata["currentImplementation"]
            write_json_file(
                self.target_metadata_root / "implementations" / implementation_name / "database.json",
                read_json_file(source_path),
            )

    def _to_generic_type(self, source_type: str) -> str:
        normalized = source_type.upper()
        if normalized == "UUID":
            return "uuid"
        if normalized.startswith("VARCHAR"):
            return "string"
        if normalized == "TEXT":
            return "text"
        if normalized in {"INTEGER", "INT", "BIGINT", "SMALLINT"}:
            return "integer"
        if normalized == "BOOLEAN":
            return "boolean"
        if normalized in {"JSON", "JSONB"}:
            return "json"
        if normalized.startswith("TIMESTAMP"):
            return "timestamp"
        if normalized.startswith("DATE"):
            return "date"
        if normalized.startswith("NUMERIC") or normalized.startswith("DECIMAL"):
            return "decimal"
        return normalized.lower()

    def _to_generic_default(self, source_default: Any) -> Any:
        if source_default is None:
            return None
        value = str(source_default)
        normalized = value.upper()
        if normalized == "CURRENT_TIMESTAMP":
            return {"type": "currentTimestamp"}
        if normalized == "GEN_RANDOM_UUID()":
            return {"type": "generatedUuid"}
        if value == "'{}'::jsonb" or value == "{}":
            return {}
        if value == "true":
            return True
        if value == "false":
            return False
        return value


if __name__ == "__main__":
    AddMetadataTablesScript().run()
