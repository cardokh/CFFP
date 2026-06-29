"""Validation helpers for generated metadata table batches."""

from typing import Any


def validate_generated_tables_batch(batch: dict[str, Any], existing_tables: list[str]) -> None:
    """Validate the current supported generated-tables batch structure."""

    tables = batch["tables"]
    table_names: list[str] = []

    for table in tables:
        if not isinstance(table, dict):
            raise ValueError("Each generated table must be a JSON object.")
        name = table.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Each generated table must contain a non-empty 'name'.")
        table_names.append(name)

    duplicates_in_batch = sorted({name for name in table_names if table_names.count(name) > 1})
    if duplicates_in_batch:
        raise ValueError(f"Duplicate tables in generated batch: {duplicates_in_batch}")

    existing_table_set = set(existing_tables)
    duplicates_existing = sorted(name for name in table_names if name in existing_table_set)
    if duplicates_existing:
        raise ValueError(f"Generated tables already exist in metadata: {duplicates_existing}")

    _validate_foreign_keys(tables, set(existing_tables) | set(table_names))


def _validate_foreign_keys(tables: list[dict[str, Any]], known_tables: set[str]) -> None:
    for table in tables:
        schema = table.get("schema", {})
        if schema is None:
            schema = {}
        if not isinstance(schema, dict):
            raise ValueError(f"Table '{table['name']}' field 'schema' must be an object.")

        foreign_keys = schema.get("foreignKeys", [])
        if foreign_keys is None:
            foreign_keys = []
        if not isinstance(foreign_keys, list):
            raise ValueError(f"Table '{table['name']}' field 'schema.foreignKeys' must be a list.")

        for foreign_key in foreign_keys:
            if not isinstance(foreign_key, dict):
                raise ValueError(f"Table '{table['name']}' contains an invalid foreign key object.")
            references = foreign_key.get("references", {})
            if not isinstance(references, dict):
                raise ValueError(f"Table '{table['name']}' contains an invalid foreign key reference.")
            referenced_table = references.get("table")
            if referenced_table not in known_tables:
                raise ValueError(
                    f"Table '{table['name']}' references unknown table '{referenced_table}'."
                )
