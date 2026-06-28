"""Validates staged table metadata listed in new_tables.json."""

import re
import sys
from pathlib import Path


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
from scripts.shared.script_json_utils import read_json_file


_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class ValidateGenerateTableMetadataScript(BaseScript):
    """Validates staged metadata and added entity registration for new tables."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_metadata_paths()
        self.checks: list[str] = []
        self.table_names: list[str] = []

    def run(self) -> None:
        table_entries = self._read_new_table_entries()
        added_entities = self._validate_added_entities_file()

        for table_entry in table_entries:
            table_name = self._get_table_name(table_entry)
            if table_name in self.table_names:
                raise ValueError(f"Duplicate table '{table_name}' found in new_tables.json.")
            self.table_names.append(table_name)
            self._validate_added_entities_registration(table_name, added_entities)
            schema = self._validate_generated_schema(table_name, table_entry)
            self._validate_generated_seed(table_name, table_entry, schema)

        report = self._build_report(added_entities)
        self.write_json_report(report)
        print_passed(f"validate_generate_table_metadata: {len(self.checks)} checks passed")

    def _get_metadata_paths(self) -> dict:
        metadata_paths = self.config.get("metadataPaths")
        if not isinstance(metadata_paths, dict):
            raise ValueError("Config must contain metadataPaths object.")
        for key in ["newTablesPath", "addedEntitiesPath", "addedEntityMetadataRoot"]:
            if not isinstance(metadata_paths.get(key), str) or not metadata_paths.get(key):
                raise ValueError(f"metadataPaths must contain non-empty '{key}'.")
        return metadata_paths

    def _read_json_config(self, path_key: str) -> dict:
        value = read_json_file(self.project_root / self.metadata_paths[path_key])
        if not isinstance(value, dict):
            raise ValueError(f"{path_key} must point to a JSON object.")
        return value

    def _read_new_table_entries(self) -> list[str | dict]:
        config = self._read_json_config("newTablesPath")
        tables = config.get("tables", [])
        if not isinstance(tables, list):
            raise ValueError("new_tables.json must contain a tables list.")
        if not all(isinstance(table, (str, dict)) for table in tables):
            raise ValueError("Every new_tables.json table entry must be a table name string or a table definition object.")
        self.checks.append("new_tables.json contains a valid tables list")
        return tables

    def _get_table_name(self, table_entry: str | dict) -> str:
        if isinstance(table_entry, str):
            table_name = table_entry
        else:
            table_name = table_entry.get("table")
        if not isinstance(table_name, str) or not _NAME_PATTERN.match(table_name):
            raise ValueError("Each new_tables.json table must use lowercase snake_case and start with a letter.")
        return table_name

    def _validate_added_entities_file(self) -> list[str]:
        added_entities_config = self._read_json_config("addedEntitiesPath")
        entities = added_entities_config.get("entities")
        if not isinstance(entities, list):
            raise ValueError("added_entities.json must contain entities list.")
        if not all(isinstance(entity, str) and entity for entity in entities):
            raise ValueError("Every added_entities.json entry must be a non-empty string.")
        if len(entities) != len(set(entities)):
            raise ValueError("added_entities.json must not contain duplicate entity names.")
        self.checks.append("added_entities.json contains a valid unique entities list")
        return entities

    def _validate_added_entities_registration(self, table_name: str, added_entities: list[str]) -> None:
        if table_name not in added_entities:
            raise ValueError(f"Generated table '{table_name}' is not registered in added_entities.json.")
        self.checks.append(f"{table_name} is registered in added_entities.json")

    def _validate_generated_schema(self, table_name: str, table_entry: str | dict) -> dict:
        schema_path = self._get_entity_folder(table_name) / "schema.json"
        if not schema_path.exists():
            raise ValueError(f"Missing generated schema metadata: {schema_path}")
        schema = read_json_file(schema_path)
        if not isinstance(schema, dict):
            raise ValueError(f"Generated schema.json for '{table_name}' must contain an object.")
        if isinstance(table_entry, dict):
            if schema.get("columns") != table_entry.get("columns"):
                raise ValueError(f"Generated schema.json columns do not match new_tables.json for '{table_name}'.")
            if schema.get("constraints", []) != table_entry.get("constraints", []):
                raise ValueError(f"Generated schema.json constraints do not match new_tables.json for '{table_name}'.")
        self._validate_schema_shape(table_name, schema)
        self.checks.append(f"generated schema.json is valid for {table_name}")
        return schema

    def _validate_schema_shape(self, table_name: str, schema: dict) -> None:
        columns = schema.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema for '{table_name}' must contain non-empty columns list.")
        column_names = []
        for column in columns:
            if not isinstance(column, dict):
                raise ValueError(f"Every column for '{table_name}' must be an object.")
            column_name = column.get("name")
            if not isinstance(column_name, str) or not _NAME_PATTERN.match(column_name):
                raise ValueError(f"Column name '{column_name}' must use lowercase snake_case and start with a letter.")
            if not isinstance(column.get("type"), str) or not column.get("type"):
                raise ValueError(f"Column '{column_name}' must contain non-empty type.")
            if column_name in column_names:
                raise ValueError(f"Duplicate column '{column_name}' found for '{table_name}'.")
            column_names.append(column_name)
        constraints = schema.get("constraints", [])
        if not isinstance(constraints, list):
            raise ValueError(f"Schema constraints for '{table_name}' must be a list when provided.")

    def _validate_generated_seed(self, table_name: str, table_entry: str | dict, schema: dict) -> None:
        seed_path = self._get_entity_folder(table_name) / "seed_data.json"
        if not seed_path.exists():
            raise ValueError(f"Missing generated seed metadata: {seed_path}")
        seed = read_json_file(seed_path)
        if not isinstance(seed, dict):
            raise ValueError(f"Generated seed_data.json for '{table_name}' must contain an object.")
        if isinstance(table_entry, dict):
            expected_seed = table_entry.get("seedData", {})
            if seed.get("rows") != expected_seed.get("rows", []):
                raise ValueError(f"Generated seed_data.json rows do not match new_tables.json for '{table_name}'.")
            if seed.get("conflictColumn", "") != expected_seed.get("conflictColumn", ""):
                raise ValueError(f"Generated seed_data.json conflictColumn does not match new_tables.json for '{table_name}'.")
        if seed.get("table") != table_name:
            raise ValueError(f"Generated seed_data.json table must match table '{table_name}'.")
        self._validate_seed_shape(table_name, seed, schema)
        self.checks.append(f"generated seed_data.json is valid for {table_name}")

    def _validate_seed_shape(self, table_name: str, seed: dict, schema: dict) -> None:
        rows = seed.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"Seed metadata for '{table_name}' must contain rows list.")
        conflict_column = seed.get("conflictColumn", "")
        if rows and (not isinstance(conflict_column, str) or not conflict_column):
            raise ValueError(f"Seed metadata for '{table_name}' must contain conflictColumn when rows are present.")
        column_names = {column["name"] for column in schema["columns"]}
        if conflict_column and conflict_column not in column_names:
            raise ValueError(f"Seed conflictColumn '{conflict_column}' does not match a schema column.")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every seed row for '{table_name}' must be an object.")
            unknown_columns = sorted(set(row.keys()) - column_names)
            if unknown_columns:
                raise ValueError(f"Seed row contains unknown columns: {', '.join(unknown_columns)}")

    def _get_entity_folder(self, table_name: str) -> Path:
        return self.project_root / self.metadata_paths["addedEntityMetadataRoot"] / table_name

    def _build_report(self, added_entities: list[str]) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "validate_generated_postgres_table_metadata"),
            "summary": {
                "status": "PASSED",
                "tableCount": len(self.table_names),
                "addedEntityCount": len(added_entities),
                "checkCount": len(self.checks),
            },
            "tables": self.table_names,
            "checks": self.checks,
        }


if __name__ == "__main__":
    ValidateGenerateTableMetadataScript().run()
