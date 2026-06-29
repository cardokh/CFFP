"""Generates PostgreSQL seed-data SQL from the generic database metadata model."""

import json
import sys
import time
from pathlib import Path
from typing import Any


def _configure_project_import_path() -> None:
    project_root = next(
        (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_passed
from scripts.shared.script_json_utils import read_json_file


class InsertDataScript(BaseScript):
    """Builds a PostgreSQL data artifact without touching the live database."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.metadata_root = self._resolve_project_path("metadataRoot")
        self.implementation_root = self._resolve_project_path("implementationRoot")
        self.tables: list[dict[str, Any]] = []

    def run(self) -> None:
        started = time.perf_counter()
        self.tables = self._load_tables()
        sql = self._render_data_sql()

        output_file = self.output_directory / self.config.get("outputFileName", "data.sql")
        output_file.write_text(sql, encoding="utf-8")
        row_count = sum(len(table["data"].get("rows", [])) for table in self.tables)
        self.write_json_report({
            "scriptName": self.script_name,
            "summary": {
                "status": "PASSED",
                "metadataRoot": self.to_project_relative_path(self.metadata_root),
                "implementationRoot": self.to_project_relative_path(self.implementation_root),
                "outputFile": self.to_project_relative_path(output_file),
                "tableCount": len(self.tables),
                "rowCount": row_count,
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            },
        })
        print_passed(f"insert_data: generated {self.to_project_relative_path(output_file)}")

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _load_tables(self) -> list[dict[str, Any]]:
        tables: list[dict[str, Any]] = []
        for module_root_value in self.config.get("moduleRoots", []):
            module_root = self.metadata_root / "modules" / str(module_root_value)
            tables_json = read_json_file(module_root / "tables.json")
            for table_name in tables_json.get("tables", []):
                table_root = module_root / "tables" / str(table_name)
                tables.append({
                    "name": str(table_name),
                    "schema": read_json_file(table_root / "schema.json"),
                    "data": read_json_file(table_root / "data.json"),
                })
        return tables

    def _render_data_sql(self) -> str:
        lines: list[str] = [
            "-- Generated from automation/factory/crud/db/metadata.",
            "-- Parallel implementation artifact. Existing postgres/ pipeline is unchanged.",
            "",
        ]
        for table in self.tables:
            table_lines = self._render_table_data(table)
            if table_lines:
                lines.extend(table_lines)
                lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _render_table_data(self, table: dict[str, Any]) -> list[str]:
        table_name = table["name"]
        rows = table["data"].get("rows", [])
        if not rows:
            return [f"-- No seed rows for {table_name}."]

        lines = [f"-- Seed data for {table_name}."]
        primary_key = table["schema"].get("primaryKey", [])
        for row in rows:
            columns = list(row.keys())
            column_sql = ", ".join(self._identifier(column) for column in columns)
            value_sql = ", ".join(self._literal(row[column]) for column in columns)
            statement = f"INSERT INTO {self._identifier(table_name)} ({column_sql}) VALUES ({value_sql})"
            if self.config.get("usePrimaryKeyConflictHandling", True) and primary_key:
                conflict_columns = ", ".join(self._identifier(column) for column in primary_key)
                statement += f" ON CONFLICT ({conflict_columns}) DO NOTHING"
            lines.append(statement + ";")
        return lines

    def _literal(self, value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (dict, list)):
            return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
        return "'" + str(value).replace("'", "''") + "'"

    def _identifier(self, value: str) -> str:
        return '"' + str(value).replace('"', '""') + '"'


if __name__ == "__main__":
    InsertDataScript().run()
