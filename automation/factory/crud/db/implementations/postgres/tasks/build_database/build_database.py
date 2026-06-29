"""Builds PostgreSQL database SQL from the generic database metadata model."""

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


class BuildDatabaseScript(BaseScript):
    """Builds a PostgreSQL database artifact without touching the live database."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.metadata_root = self._resolve_project_path("metadataRoot")
        self.implementation_root = self._resolve_project_path("implementationRoot")
        self.schemas: list[dict[str, Any]] = []

    def run(self) -> None:
        started = time.perf_counter()
        implementation_metadata = read_json_file(self.implementation_root / "database.json")
        self.schemas = self._load_schemas()
        sql = self._render_database_sql(implementation_metadata)

        output_file = self.output_directory / self.config.get("outputFileName", "database.sql")
        output_file.write_text(sql, encoding="utf-8")
        self.write_json_report({
            "scriptName": self.script_name,
            "summary": {
                "status": "PASSED",
                "metadataRoot": self.to_project_relative_path(self.metadata_root),
                "implementationRoot": self.to_project_relative_path(self.implementation_root),
                "outputFile": self.to_project_relative_path(output_file),
                "tableCount": len(self.schemas),
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            },
        })
        print_passed(f"build_database: generated {self.to_project_relative_path(output_file)}")

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _load_schemas(self) -> list[dict[str, Any]]:
        schemas: list[dict[str, Any]] = []
        for module_root_value in self.config.get("moduleRoots", []):
            module_root = self.metadata_root / "modules" / str(module_root_value)
            tables_json = read_json_file(module_root / "tables.json")
            for table_name in tables_json.get("tables", []):
                schema = read_json_file(module_root / "tables" / str(table_name) / "schema.json")
                schemas.append(schema)
        return schemas

    def _render_database_sql(self, implementation_metadata: dict[str, Any]) -> str:
        application_connection = implementation_metadata.get("applicationConnection", {})
        database_name = application_connection.get("databaseName", "")
        username = application_connection.get("username", "")

        lines: list[str] = [
            "-- Generated from automation/factory/crud/db/metadata.",
            "-- Parallel implementation artifact. Existing postgres/ pipeline is unchanged.",
            "",
            "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
            "",
        ]
        if username:
            lines.extend([
                f"-- Application role: {username}",
            ])
        if database_name:
            lines.extend([
                f"-- Application database: {database_name}",
                "",
            ])

        for schema in self.schemas:
            lines.extend(self._render_create_table(schema))
            lines.append("")

        if implementation_metadata.get("enableForeignKeys", True):
            for schema in self.schemas:
                fk_lines = self._render_foreign_keys(schema)
                if fk_lines:
                    lines.extend(fk_lines)
                    lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _render_create_table(self, schema: dict[str, Any]) -> list[str]:
        table_name = schema["name"]
        definitions: list[str] = []
        for column in schema.get("columns", []):
            definitions.append("    " + self._render_column(column))
        primary_key = schema.get("primaryKey", [])
        if primary_key:
            columns = ", ".join(self._identifier(column_name) for column_name in primary_key)
            definitions.append(f"    CONSTRAINT {self._identifier(table_name + '_pk')} PRIMARY KEY ({columns})")

        lines = [f"CREATE TABLE IF NOT EXISTS {self._identifier(table_name)} ("]
        lines.append(",\n".join(definitions))
        lines.append(");")
        return lines

    def _render_column(self, column: dict[str, Any]) -> str:
        pieces = [self._identifier(column["name"]), self._map_type(column["type"])]
        if column.get("nullable") is False:
            pieces.append("NOT NULL")
        if "default" in column:
            pieces.append("DEFAULT " + self._map_default(column["default"]))
        return " ".join(pieces)

    def _render_foreign_keys(self, schema: dict[str, Any]) -> list[str]:
        table_name = schema["name"]
        lines: list[str] = []
        for index, foreign_key in enumerate(schema.get("foreignKeys", []), start=1):
            columns = ", ".join(self._identifier(column_name) for column_name in foreign_key.get("columns", []))
            references = foreign_key.get("references", {})
            referenced_table = references.get("table")
            referenced_columns = ", ".join(self._identifier(column_name) for column_name in references.get("columns", []))
            constraint_name = foreign_key.get("name", f"{table_name}_fk_{index}")
            statement = (
                f"ALTER TABLE {self._identifier(table_name)} "
                f"ADD CONSTRAINT {self._identifier(constraint_name)} "
                f"FOREIGN KEY ({columns}) REFERENCES {self._identifier(referenced_table)} ({referenced_columns})"
            )
            on_delete = foreign_key.get("onDelete")
            if isinstance(on_delete, str) and on_delete:
                statement += " ON DELETE " + on_delete.upper()
            lines.append(statement + ";")
        return lines

    def _map_type(self, generic_type: str) -> str:
        mappings = self.config.get("typeMappings", {})
        if generic_type not in mappings:
            raise ValueError(f"No PostgreSQL type mapping configured for generic type '{generic_type}'.")
        return mappings[generic_type]

    def _map_default(self, default: Any) -> str:
        if isinstance(default, dict):
            default_type = default.get("type")
            if default_type is None:
                return "'" + __import__("json").dumps(default).replace("'", "''") + "'::jsonb"
            mappings = self.config.get("defaultMappings", {})
            if default_type not in mappings:
                raise ValueError(f"No PostgreSQL default mapping configured for default type '{default_type}'.")
            return mappings[default_type]
        if isinstance(default, bool):
            return "true" if default else "false"
        if isinstance(default, (int, float)):
            return str(default)
        return "'" + str(default).replace("'", "''") + "'"

    def _identifier(self, value: str) -> str:
        return '"' + str(value).replace('"', '""') + '"'


if __name__ == "__main__":
    BuildDatabaseScript().run()
