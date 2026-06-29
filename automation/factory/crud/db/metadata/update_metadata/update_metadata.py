"""Generates generic database metadata from the current PostgreSQL metadata source."""

import json
import shutil
import sys
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


class UpdateMetadataScript(BaseScript):
    """Builds the database-neutral metadata model used by future database generators."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.source_metadata_root = self._resolve_project_path("sourceMetadataRoot")
        self.target_metadata_root = self._resolve_project_path("targetMetadataRoot")
        self.module_rules = self.config.get("moduleRules", {})

    def run(self) -> None:
        entities = self._read_entities()
        self._prepare_target_metadata()
        module_tables: dict[str, list[str]] = {"ccore/automation": [], "ccore/organization": []}

        for entity_name in entities:
            module_name = self._resolve_module_name(entity_name)
            module_tables.setdefault(module_name, []).append(entity_name)
            table_metadata = self._build_table_metadata(entity_name)
            seed_metadata = self._build_seed_metadata(entity_name)

            table_root = self.target_metadata_root / "modules" / module_name / "tables" / entity_name
            write_json_file(table_root / "schema.json", table_metadata)
            write_json_file(table_root / "data.json", seed_metadata)

        self._write_database_metadata(module_tables)
        self._write_module_metadata(module_tables)

        report = {
            "scriptName": self.script_name,
            "summary": {
                "status": "PASSED",
                "entityCount": len(entities),
                "targetMetadataRoot": self.to_project_relative_path(self.target_metadata_root),
            },
        }
        self.write_json_report(report)
        print_passed(f"update_metadata: generated generic metadata for {len(entities)} tables")

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _read_entities(self) -> list[str]:
        entities_file = self.source_metadata_root / "entities.json"
        entities = read_json_file(entities_file).get("entities")
        if not isinstance(entities, list):
            raise ValueError("Source entities.json must contain an entities list.")
        return entities

    def _prepare_target_metadata(self) -> None:
        modules_root = self.target_metadata_root / "modules"
        if modules_root.exists():
            shutil.rmtree(modules_root)
        for module_name in ["ccore/automation", "ccore/organization"]:
            (modules_root / module_name / "tables").mkdir(parents=True, exist_ok=True)

    def _resolve_module_name(self, entity_name: str) -> str:
        return "ccore/automation"

    def _build_table_metadata(self, entity_name: str) -> dict[str, Any]:
        schema = read_json_file(self.source_metadata_root / "entities" / entity_name / "schema.json")
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
            "name": entity_name,
            "columns": columns,
            "primaryKey": primary_key,
            "foreignKeys": foreign_keys,
        }
        if constraints:
            metadata["constraints"] = constraints
        return metadata

    def _build_seed_metadata(self, entity_name: str) -> dict[str, Any]:
        seed = read_json_file(self.source_metadata_root / "entities" / entity_name / "seed_data.json")
        return {
            "table": entity_name,
            "rows": seed.get("rows", []),
        }

    def _write_database_metadata(self, module_tables: dict[str, list[str]]) -> None:
        database_metadata = {
            "name": self.config.get("databaseName", "ccore_automation"),
            "description": "Generic database metadata source for CFFP Automation Factory database generation.",
            "metadataVersion": self.config.get("metadataVersion", "1.0"),
            "modules": [module for module, tables in module_tables.items() if tables or module == "ccore/organization"],
            "capabilities": [
                "database",
                "tables",
                "columns",
                "primaryKeys",
                "foreignKeys",
                "defaults",
                "seedData",
            ],
        }
        write_json_file(self.target_metadata_root / "database.json", database_metadata)

    def _write_module_metadata(self, module_tables: dict[str, list[str]]) -> None:
        for module_name in ["ccore/automation", "ccore/organization"]:
            module_root = self.target_metadata_root / "modules" / module_name
            module_root.mkdir(parents=True, exist_ok=True)
            write_json_file(module_root / "tables.json", {"tables": module_tables.get(module_name, [])})

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
    UpdateMetadataScript().run()
