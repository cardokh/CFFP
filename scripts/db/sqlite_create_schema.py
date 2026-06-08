"""
Creates a completely fresh SQLite database schema for the LLA application.

IMPORTANT:
This script DELETES the existing database file before creating a new one.

Run this script before running sqlite_seed_data.py:

    python scripts/db/sqlite_create_schema.py
    python scripts/db/sqlite_seed_data.py
"""

import sys
from pathlib import Path
from typing import Any

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_json_utils import (
    read_json_file,
    write_json_file,
)
from scripts.shared.script_path_utils import (
    get_path,
)


class SQLiteCreateSchemaScript(BaseScript):
    """
    Creates the SQLite schema from structured database, entity, and schema configs.
    """

    def __init__(self):
        super().__init__(__file__)
        self.database_config = self._load_database_config()
        self.entities_config = self._load_entities_config()
        self.database_path = self._resolve_database_path()
        self.deleted_existing_database = False
        self.created_tables = []

    def run(self) -> None:
        self._configure_backend_import_path()
        self._execute_schema_creation()

        report = self._build_report()
        self._write_report(report)
        self._print_success(report)

    def _load_database_config(self) -> dict:
        database_config_path = self._resolve_config_path("databaseConfigPath")

        return read_json_file(database_config_path)

    def _load_entities_config(self) -> dict:
        entities_config_path = self._resolve_config_path("entitiesConfigPath")

        return read_json_file(entities_config_path)

    def _resolve_config_path(
        self,
        config_key: str,
    ) -> Path:
        config_path = self.config.get(config_key)

        if not isinstance(config_path, str) or not config_path:
            raise ValueError(f"Config must contain '{config_key}'.")

        return self.project_root / config_path

    def _configure_backend_import_path(self) -> None:
        backend_path_key = self.database_config.get("backendPathKey")

        if not isinstance(backend_path_key, str) or not backend_path_key:
            raise ValueError("database.json must contain 'backendPathKey'.")

        backend_path = get_path(backend_path_key)

        if str(backend_path) not in sys.path:
            sys.path.append(str(backend_path))

    def _resolve_database_path(self) -> Path:
        database_path_key = self.database_config.get("databasePathKey")

        if not isinstance(database_path_key, str) or not database_path_key:
            raise ValueError("database.json must contain 'databasePathKey'.")

        return get_path(database_path_key)

    def _execute_schema_creation(self) -> None:
        if self.database_config.get("databaseType") != "sqlite":
            raise ValueError("sqlite_create_schema.py requires databaseType 'sqlite'.")

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._delete_existing_database()

        from src.core.infrastructure.database import DatabaseManager

        db = DatabaseManager(str(self.database_path))
        conn = db.get_connection()

        try:
            if self.database_config.get("enableForeignKeys") is True:
                conn.execute("PRAGMA foreign_keys = ON")

            cursor = conn.cursor()

            for entity_name in self._get_entity_names():
                table_definition = self._get_table_definition(entity_name)
                create_table_sql = self._build_create_table_sql(
                    entity_name,
                    table_definition,
                )

                cursor.execute(create_table_sql)
                self.created_tables.append(entity_name)

            conn.commit()

        finally:
            conn.close()

    def _delete_existing_database(self) -> None:
        if self.database_path.exists():
            self.database_path.unlink()
            self.deleted_existing_database = True

    def _get_entity_names(self) -> list[str]:
        entities = self.entities_config.get("entities")

        if not isinstance(entities, list) or not entities:
            raise ValueError("entities.json must contain non-empty 'entities'.")

        for entity in entities:
            if not isinstance(entity, str) or not entity:
                raise ValueError("Every entity entry must be a non-empty string.")

        return entities

    def _get_table_definition(
        self,
        entity_name: str,
    ) -> dict:
        tables = self.config.get("tables")

        if not isinstance(tables, dict):
            raise ValueError("sqlite_create_schema.json must contain 'tables' object.")

        table_definition = tables.get(entity_name)

        if not isinstance(table_definition, dict):
            raise ValueError(f"Missing table definition for entity '{entity_name}'.")

        return table_definition

    def _build_create_table_sql(
        self,
        entity_name: str,
        table_definition: dict,
    ) -> str:
        columns = self._get_columns(table_definition)
        table_constraints = self._get_table_constraints(table_definition)

        definitions = []

        for column in columns:
            definitions.append(
                self._build_column_sql(column),
            )

        for constraint in table_constraints:
            definitions.append(
                self._build_table_constraint_sql(constraint),
            )

        joined_definitions = ",\n    ".join(definitions)

        return f"CREATE TABLE {entity_name} (\n    {joined_definitions}\n)"

    def _get_columns(
        self,
        table_definition: dict,
    ) -> list[dict]:
        columns = table_definition.get("columns")

        if not isinstance(columns, list) or not columns:
            raise ValueError("Every table definition must contain non-empty 'columns'.")

        return columns

    def _get_table_constraints(
        self,
        table_definition: dict,
    ) -> list[dict]:
        constraints = table_definition.get("constraints", [])

        if not isinstance(constraints, list):
            raise ValueError("'constraints' must be a list when provided.")

        return constraints

    def _build_column_sql(
        self,
        column: dict,
    ) -> str:
        column_name = self._get_required_string(
            column,
            "name",
            "Column definition must contain 'name'.",
        )

        data_type = self._get_required_string(
            column,
            "type",
            "Column definition must contain 'type'.",
        )

        parts = [
            column_name,
            data_type,
        ]

        if column.get("primaryKey") is True:
            parts.append("PRIMARY KEY")

        if column.get("autoIncrement") is True:
            parts.append("AUTOINCREMENT")

        if column.get("nullable") is False:
            parts.append("NOT NULL")

        if column.get("unique") is True:
            parts.append("UNIQUE")

        default_value = column.get("default")

        if default_value is not None:
            parts.append(f"DEFAULT {default_value}")

        return " ".join(parts)

    def _build_table_constraint_sql(
        self,
        constraint: dict,
    ) -> str:
        constraint_type = self._get_required_string(
            constraint,
            "type",
            "Constraint definition must contain 'type'.",
        )

        if constraint_type == "primaryKey":
            return self._build_primary_key_sql(constraint)

        if constraint_type == "foreignKey":
            return self._build_foreign_key_sql(constraint)

        raise ValueError(f"Unsupported table constraint type '{constraint_type}'.")

    def _build_primary_key_sql(
        self,
        constraint: dict,
    ) -> str:
        columns = self._get_required_string_list(
            constraint,
            "columns",
            "Primary key constraint must contain 'columns'.",
        )

        return f"PRIMARY KEY ({', '.join(columns)})"

    def _build_foreign_key_sql(
        self,
        constraint: dict,
    ) -> str:
        columns = self._get_required_string_list(
            constraint,
            "columns",
            "Foreign key constraint must contain 'columns'.",
        )

        references = constraint.get("references")

        if not isinstance(references, dict):
            raise ValueError("Foreign key constraint must contain 'references'.")

        referenced_table = self._get_required_string(
            references,
            "table",
            "Foreign key references must contain 'table'.",
        )

        referenced_columns = self._get_required_string_list(
            references,
            "columns",
            "Foreign key references must contain 'columns'.",
        )

        sql = (
            f"FOREIGN KEY ({', '.join(columns)}) "
            f"REFERENCES {referenced_table}({', '.join(referenced_columns)})"
        )

        on_delete = constraint.get("onDelete")

        if isinstance(on_delete, str) and on_delete:
            sql = f"{sql} ON DELETE {on_delete}"

        return sql

    def _get_required_string(
        self,
        source: dict,
        key: str,
        error_message: str,
    ) -> str:
        value = source.get(key)

        if not isinstance(value, str) or not value:
            raise ValueError(error_message)

        return value

    def _get_required_string_list(
        self,
        source: dict,
        key: str,
        error_message: str,
    ) -> list[str]:
        value = source.get(key)

        if not isinstance(value, list) or not value:
            raise ValueError(error_message)

        for item in value:
            if not isinstance(item, str) or not item:
                raise ValueError(error_message)

        return value

    def _build_report(self) -> dict[str, Any]:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "create_schema",
            ),
            "summary": {
                "status": "PASSED",
                "databasePath": self.to_project_relative_path(self.database_path),
                "deletedExistingDatabase": self.deleted_existing_database,
                "createdTableCount": len(self.created_tables),
            },
            "createdTables": self.created_tables,
        }

    def _write_report(
        self,
        report: dict,
    ) -> None:
        output_file_path = (
            self.output_directory / f"{self.script_name}_report_{self.timestamp}.json"
        )

        write_json_file(
            output_file_path,
            report,
        )

    def _print_success(
        self,
        report: dict,
    ) -> None:
        created_table_count = report["summary"]["createdTableCount"]

        print_passed(
            (
                f"{self.script_name}: fresh SQLite schema created "
                f"with {created_table_count} table(s)"
            )
        )


def main() -> None:
    try:
        SQLiteCreateSchemaScript().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
