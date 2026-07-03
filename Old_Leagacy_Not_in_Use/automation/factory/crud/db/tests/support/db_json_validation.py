"""Reusable JSON metadata assertions for DB pipeline tests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def assert_object(value: Any, label: str) -> dict[str, Any]:
    assert isinstance(value, dict), f"{label} must be a JSON object."
    return value


def assert_string(value: Any, label: str) -> str:
    assert isinstance(value, str) and value, f"{label} must be a non-empty string."
    return value


def assert_name(value: Any, label: str) -> str:
    name = assert_string(value, label)
    assert NAME_PATTERN.match(name), f"{label} must be lowercase snake_case and start with a letter: {name}"
    return name


def assert_unique_strings(values: Any, label: str) -> list[str]:
    assert isinstance(values, list), f"{label} must be a list."
    assert all(isinstance(value, str) and value for value in values), f"Every {label} entry must be a non-empty string."
    assert len(values) == len(set(values)), f"{label} must not contain duplicates."
    return values


def assert_schema_contract(schema: Any, entity_name: str) -> dict[str, Any]:
    schema_object = assert_object(schema, f"schema.json for {entity_name}")
    columns = schema_object.get("columns")
    assert isinstance(columns, list) and columns, f"{entity_name} schema must contain a non-empty columns list."

    column_names: list[str] = []
    for column in columns:
        column_object = assert_object(column, f"column in {entity_name}")
        column_name = assert_name(column_object.get("name"), f"column name in {entity_name}")
        assert_string(column_object.get("type"), f"type for {entity_name}.{column_name}")
        assert column_name not in column_names, f"Duplicate column in {entity_name}: {column_name}"
        column_names.append(column_name)

        for optional_bool_key in ["nullable", "primaryKey", "unique"]:
            if optional_bool_key in column_object:
                assert isinstance(column_object[optional_bool_key], bool), (
                    f"{entity_name}.{column_name}.{optional_bool_key} must be boolean when provided."
                )

    constraints = schema_object.get("constraints", [])
    assert isinstance(constraints, list), f"{entity_name} constraints must be a list when provided."
    for constraint in constraints:
        constraint_object = assert_object(constraint, f"constraint in {entity_name}")
        assert_string(constraint_object.get("type"), f"constraint type in {entity_name}")
        if "columns" in constraint_object:
            assert isinstance(constraint_object["columns"], list), f"constraint columns in {entity_name} must be a list."
            for column_name in constraint_object["columns"]:
                assert column_name in column_names, f"{entity_name} constraint references unknown column: {column_name}"
        if constraint_object.get("type") == "foreignKey":
            references = assert_object(constraint_object.get("references"), f"foreign key references in {entity_name}")
            assert_name(references.get("table"), f"foreign key reference table in {entity_name}")
            assert isinstance(references.get("columns"), list) and references["columns"], (
                f"foreign key references.columns in {entity_name} must be a non-empty list."
            )

    indexes = schema_object.get("indexes", [])
    assert isinstance(indexes, list), f"{entity_name} indexes must be a list when provided."
    return schema_object


def assert_seed_contract(seed: Any, entity_name: str, schema: dict[str, Any]) -> dict[str, Any]:
    seed_object = assert_object(seed, f"seed_data.json for {entity_name}")
    assert seed_object.get("table") == entity_name, f"seed_data.json table must match entity name {entity_name}."
    rows = seed_object.get("rows")
    assert isinstance(rows, list), f"{entity_name} seed rows must be a list."

    column_names = {column["name"] for column in schema["columns"]}
    conflict_column = seed_object.get("conflictColumn", "")
    if rows:
        assert_string(conflict_column, f"conflictColumn for {entity_name}")
    if conflict_column:
        assert conflict_column in column_names, f"{entity_name} seed conflictColumn does not exist in schema: {conflict_column}"

    for row in rows:
        row_object = assert_object(row, f"seed row in {entity_name}")
        unknown_columns = sorted(set(row_object.keys()) - column_names)
        assert not unknown_columns, f"{entity_name} seed row contains unknown columns: {unknown_columns}"

    return seed_object
