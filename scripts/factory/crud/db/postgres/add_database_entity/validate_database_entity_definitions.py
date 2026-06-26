"""
Validates split PostgreSQL database entity definitions and generated metadata.

This script validates configuration and generated JSON metadata only.
It does not connect to PostgreSQL.
"""

from pathlib import Path

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file


class ValidateDatabaseEntityDefinitionsScript(BaseScript):
    """Validates split database entity definitions against generated metadata files."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_metadata_paths()
        self.expected = self._get_expected()
        self.checks = []

    def run(self) -> None:
        database_entities = self._read_metadata_file("databaseEntitiesPath")
        schema_entity_config = self._read_metadata_file("schemaEntityConfigPath")
        seed_entity_config = self._read_metadata_file("seedEntityConfigPath")
        entities_config = self._read_metadata_file("entitiesConfigPath")
        schema_config = self._read_metadata_file("schemaConfigPath")
        seed_config = self._read_metadata_file("seedConfigPath")

        listed_entities = self._validate_database_entities(database_entities)
        schema_definitions = self._validate_schema_entity_config(
            schema_entity_config=schema_entity_config,
            listed_entities=listed_entities,
        )
        seed_groups = self._validate_seed_entity_config(
            seed_entity_config=seed_entity_config,
            listed_entities=listed_entities,
        )

        self._validate_generated_entities(
            entities_config=entities_config,
            listed_entities=listed_entities,
        )
        self._validate_generated_schema(
            schema_config=schema_config,
            schema_definitions=schema_definitions,
        )
        self._validate_generated_seed(
            seed_config=seed_config,
            seed_groups=seed_groups,
        )
        self._validate_generated_schema_integrity(schema_config)
        self._validate_seed_rows_against_schema(
            seed_config=seed_config,
            schema_config=schema_config,
        )
        self._validate_expected_generated_metadata(
            entities_config=entities_config,
            seed_config=seed_config,
        )

        report = self._build_report()
        self.write_json_report(report)
        self._print_success(report)

    def _get_metadata_paths(self) -> dict:
        metadata_paths = self.config.get("metadataPaths")

        if not isinstance(metadata_paths, dict):
            raise ValueError("Config must contain 'metadataPaths' object.")

        required_keys = [
            "databaseEntitiesPath",
            "schemaEntityConfigPath",
            "seedEntityConfigPath",
            "entitiesConfigPath",
            "schemaConfigPath",
            "seedConfigPath",
        ]

        for key in required_keys:
            value = metadata_paths.get(key)

            if not isinstance(value, str) or not value:
                raise ValueError(f"metadataPaths must contain non-empty '{key}'.")

        return metadata_paths

    def _get_expected(self) -> dict:
        expected = self.config.get("expected", {})

        if not isinstance(expected, dict):
            raise ValueError("Config 'expected' must be an object when provided.")

        return expected

    def _read_metadata_file(self, metadata_path_key: str) -> dict:
        return read_json_file(self._resolve_project_path(self.metadata_paths[metadata_path_key]))

    def _resolve_project_path(self, configured_path: str) -> Path:
        return self.project_root / configured_path

    def _validate_database_entities(self, database_entities: dict) -> list[str]:
        entities = database_entities.get("entities")

        if not isinstance(entities, list) or not entities:
            raise ValueError("database_entities.json must contain non-empty 'entities' list.")

        for entity_name in entities:
            if not isinstance(entity_name, str) or not entity_name:
                raise ValueError("Every database_entities.json entry must be a non-empty string.")

        if len(entities) != len(set(entities)):
            raise ValueError("database_entities.json must not contain duplicate entity names.")

        expected_count = self.expected.get("entityCount")
        if expected_count is not None and len(entities) != expected_count:
            raise ValueError(
                f"Expected {expected_count} listed entities but found {len(entities)}."
            )

        self._add_check("database_entities.json contains valid entity list")
        return entities

    def _validate_schema_entity_config(
        self,
        schema_entity_config: dict,
        listed_entities: list[str],
    ) -> dict:
        entities = schema_entity_config.get("entities")

        if not isinstance(entities, list) or not entities:
            raise ValueError("add_database_schema_entity.json must contain non-empty 'entities' list.")

        schema_definitions = {}

        for entity in entities:
            if not isinstance(entity, dict):
                raise ValueError("Every schema entity definition must be an object.")

            entity_name = self._get_required_string(
                entity,
                "name",
                "Every schema entity must contain 'name'.",
            )

            if entity_name not in listed_entities:
                raise ValueError(
                    f"Schema entity '{entity_name}' is not listed in database_entities.json."
                )

            if entity_name in schema_definitions:
                raise ValueError(f"Duplicate schema entity '{entity_name}' found.")

            schema = entity.get("schema")
            if not isinstance(schema, dict):
                raise ValueError(f"Schema entity '{entity_name}' must contain 'schema' object.")

            self._validate_schema_definition(entity_name, schema)
            schema_definitions[entity_name] = schema

        missing_schema_entities = set(listed_entities) - set(schema_definitions)
        if missing_schema_entities:
            raise ValueError(
                "Missing schema definitions for: "
                + ", ".join(sorted(missing_schema_entities))
            )

        self._add_check("add_database_schema_entity.json contains valid schema definitions")
        return schema_definitions

    def _validate_seed_entity_config(
        self,
        seed_entity_config: dict,
        listed_entities: list[str],
    ) -> dict:
        seed_groups = seed_entity_config.get("seedGroups")

        if not isinstance(seed_groups, list):
            raise ValueError("add_database_seed_entity.json must contain 'seedGroups' list.")

        expected_count = self.expected.get("seedGroupCount")
        if expected_count is not None and len(seed_groups) != expected_count:
            raise ValueError(
                f"Expected {expected_count} seed groups but found {len(seed_groups)}."
            )

        seed_by_table = {}

        for seed_group in seed_groups:
            if not isinstance(seed_group, dict):
                raise ValueError("Every seed group must be an object.")

            table_name = self._get_required_string(
                seed_group,
                "table",
                "Every seed group must contain 'table'.",
            )

            if table_name not in listed_entities:
                raise ValueError(
                    f"Seed group '{table_name}' is not listed in database_entities.json."
                )

            if table_name in seed_by_table:
                raise ValueError(f"Duplicate seed group for table '{table_name}' found.")

            self._validate_seed_group(table_name, seed_group)
            seed_by_table[table_name] = seed_group

        self._add_check("add_database_seed_entity.json contains valid seed definitions")
        return seed_by_table

    def _validate_generated_entities(
        self,
        entities_config: dict,
        listed_entities: list[str],
    ) -> None:
        generated_entities = entities_config.get("entities")

        if not isinstance(generated_entities, list):
            raise ValueError("entities.json must contain 'entities' list.")

        for entity_name in generated_entities:
            if not isinstance(entity_name, str) or not entity_name:
                raise ValueError("Every entities.json entry must be a non-empty string.")

        if len(generated_entities) != len(set(generated_entities)):
            raise ValueError("entities.json must not contain duplicate entity names.")

        missing_entities = set(listed_entities) - set(generated_entities)
        if missing_entities:
            raise ValueError(
                "Generated entities.json is missing: "
                + ", ".join(sorted(missing_entities))
            )

        self._add_check("entities.json contains all listed database entities")

    def _validate_generated_schema(
        self,
        schema_config: dict,
        schema_definitions: dict,
    ) -> None:
        generated_tables = schema_config.get("tables")

        if not isinstance(generated_tables, dict):
            raise ValueError("postgres_create_schema.json must contain 'tables' object.")

        for table_name, table_schema in generated_tables.items():
            if not isinstance(table_name, str) or not table_name:
                raise ValueError("Every postgres_create_schema.json table name must be a non-empty string.")

            if not isinstance(table_schema, dict):
                raise ValueError(f"Generated schema for '{table_name}' must be an object.")

        for entity_name, schema_definition in schema_definitions.items():
            generated_schema = generated_tables.get(entity_name)

            if generated_schema is None:
                raise ValueError(
                    f"postgres_create_schema.json is missing table '{entity_name}'."
                )

            if generated_schema != schema_definition:
                raise ValueError(
                    f"Generated schema for '{entity_name}' does not match add_database_schema_entity.json."
                )

        self._add_check("postgres_create_schema.json matches schema definitions")

    def _validate_generated_seed(
        self,
        seed_config: dict,
        seed_groups: dict,
    ) -> None:
        generated_seed_groups = seed_config.get("seedGroups")

        if not isinstance(generated_seed_groups, list):
            raise ValueError("postgres_seed_data.json must contain 'seedGroups' list.")

        generated_seed_by_table = {}
        for seed_group in generated_seed_groups:
            if not isinstance(seed_group, dict):
                raise ValueError("Every postgres_seed_data.json seed group must be an object.")

            table_name = self._get_required_string(
                seed_group,
                "table",
                "Every postgres_seed_data.json seed group must contain 'table'.",
            )

            if table_name in generated_seed_by_table:
                raise ValueError(f"Duplicate generated seed group for table '{table_name}' found.")

            generated_seed_by_table[table_name] = seed_group

        for table_name, seed_group in seed_groups.items():
            generated_seed_group = generated_seed_by_table.get(table_name)

            if generated_seed_group is None:
                raise ValueError(
                    f"postgres_seed_data.json is missing seed group '{table_name}'."
                )

            if generated_seed_group != seed_group:
                raise ValueError(
                    f"Generated seed group for '{table_name}' does not match add_database_seed_entity.json."
                )

        self._add_check("postgres_seed_data.json matches seed definitions")


    def _validate_generated_schema_integrity(self, schema_config: dict) -> None:
        generated_tables = schema_config.get("tables")

        if not isinstance(generated_tables, dict):
            raise ValueError("postgres_create_schema.json must contain 'tables' object.")

        table_columns_by_name = {}
        for table_name, table_schema in generated_tables.items():
            if not isinstance(table_schema, dict):
                raise ValueError(f"Generated schema for '{table_name}' must be an object.")

            self._validate_schema_definition(table_name, table_schema)
            table_columns_by_name[table_name] = set(self._get_column_names(table_name, table_schema))

        for table_name, table_schema in generated_tables.items():
            constraints = table_schema.get("constraints", [])
            for constraint in constraints:
                if constraint.get("type") != "foreignKey":
                    continue

                references = constraint.get("references", {})
                referenced_table = references.get("table")
                referenced_columns = references.get("columns", [])

                if referenced_table not in table_columns_by_name:
                    raise ValueError(
                        f"Foreign key for '{table_name}' references unknown table '{referenced_table}'."
                    )

                for referenced_column in referenced_columns:
                    if referenced_column not in table_columns_by_name[referenced_table]:
                        raise ValueError(
                            f"Foreign key for '{table_name}' references unknown column "
                            f"'{referenced_table}.{referenced_column}'."
                        )

        self._add_check("postgres_create_schema.json has valid table, column, and foreign key integrity")

    def _validate_seed_rows_against_schema(
        self,
        seed_config: dict,
        schema_config: dict,
    ) -> None:
        generated_tables = schema_config.get("tables")
        generated_seed_groups = seed_config.get("seedGroups")

        if not isinstance(generated_tables, dict):
            raise ValueError("postgres_create_schema.json must contain 'tables' object.")

        if not isinstance(generated_seed_groups, list):
            raise ValueError("postgres_seed_data.json must contain 'seedGroups' list.")

        for seed_group in generated_seed_groups:
            if not isinstance(seed_group, dict):
                raise ValueError("Every postgres_seed_data.json seed group must be an object.")

            table_name = self._get_required_string(
                seed_group,
                "table",
                "Every postgres_seed_data.json seed group must contain 'table'.",
            )

            table_schema = generated_tables.get(table_name)
            if not isinstance(table_schema, dict):
                raise ValueError(f"Seed group '{table_name}' does not have a generated schema table.")

            column_names = set(self._get_column_names(table_name, table_schema))
            conflict_column = self._get_required_string(
                seed_group,
                "conflictColumn",
                f"Seed group for '{table_name}' must contain 'conflictColumn'.",
            )

            if conflict_column not in column_names:
                raise ValueError(
                    f"Seed group for '{table_name}' uses unknown conflict column '{conflict_column}'."
                )

            rows = seed_group.get("rows")
            if not isinstance(rows, list):
                raise ValueError(f"Seed group for '{table_name}' must contain 'rows' list.")

            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError(f"Every seed row for '{table_name}' must be an object.")

                unknown_columns = set(row) - column_names
                if unknown_columns:
                    raise ValueError(
                        f"Seed row for '{table_name}' contains unknown columns: "
                        + ", ".join(sorted(unknown_columns))
                    )

        self._add_check("postgres_seed_data.json rows match generated schema columns")

    def _validate_expected_generated_metadata(
        self,
        entities_config: dict,
        seed_config: dict,
    ) -> None:
        generated_entity_count = self.expected.get("generatedEntityCount")
        generated_seed_row_count = self.expected.get("generatedSeedRowCount")

        if generated_entity_count is None and generated_seed_row_count is None:
            return

        if generated_entity_count is not None:
            generated_entities = entities_config.get("entities")
            if not isinstance(generated_entities, list):
                raise ValueError("entities.json must contain 'entities' list.")

            if len(generated_entities) != generated_entity_count:
                raise ValueError(
                    f"Expected {generated_entity_count} generated entities but found "
                    f"{len(generated_entities)}."
                )

        if generated_seed_row_count is not None:
            generated_seed_groups = seed_config.get("seedGroups")
            if not isinstance(generated_seed_groups, list):
                raise ValueError("postgres_seed_data.json must contain 'seedGroups' list.")

            actual_seed_row_count = 0
            for seed_group in generated_seed_groups:
                if not isinstance(seed_group, dict):
                    raise ValueError("Every postgres_seed_data.json seed group must be an object.")

                rows = seed_group.get("rows")
                if not isinstance(rows, list):
                    table_name = seed_group.get("table", "<unknown>")
                    raise ValueError(f"Seed group for '{table_name}' must contain 'rows' list.")

                actual_seed_row_count += len(rows)

            if actual_seed_row_count != generated_seed_row_count:
                raise ValueError(
                    f"Expected {generated_seed_row_count} generated seed rows but found "
                    f"{actual_seed_row_count}."
                )

        self._add_check("generated metadata matches expected acceptance counts")

    def _get_column_names(
        self,
        table_name: str,
        table_schema: dict,
    ) -> list[str]:
        columns = table_schema.get("columns")

        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema for '{table_name}' must contain non-empty 'columns' list.")

        column_names = []
        for column in columns:
            if not isinstance(column, dict):
                raise ValueError(f"Every column for '{table_name}' must be an object.")

            column_names.append(
                self._get_required_string(
                    column,
                    "name",
                    f"Every column for '{table_name}' must contain 'name'.",
                )
            )

        return column_names

    def _validate_schema_definition(
        self,
        entity_name: str,
        schema_definition: dict,
    ) -> None:
        columns = schema_definition.get("columns")

        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema for '{entity_name}' must contain non-empty 'columns' list.")

        column_names = []
        primary_key_count = 0

        for column in columns:
            if not isinstance(column, dict):
                raise ValueError(f"Every column for '{entity_name}' must be an object.")

            column_name = self._get_required_string(
                column,
                "name",
                f"Every column for '{entity_name}' must contain 'name'.",
            )
            self._get_required_string(
                column,
                "type",
                f"Column '{column_name}' for '{entity_name}' must contain 'type'.",
            )

            if column_name in column_names:
                raise ValueError(f"Duplicate column '{column_name}' found for '{entity_name}'.")

            if column.get("primaryKey") is True:
                primary_key_count += 1

            column_names.append(column_name)

        if primary_key_count == 0:
            raise ValueError(f"Schema for '{entity_name}' must define a primary key column.")

        constraints = schema_definition.get("constraints", [])

        if not isinstance(constraints, list):
            raise ValueError(f"Schema constraints for '{entity_name}' must be a list when provided.")

        for constraint in constraints:
            self._validate_constraint(entity_name, column_names, constraint)

    def _validate_constraint(
        self,
        entity_name: str,
        column_names: list[str],
        constraint: dict,
    ) -> None:
        if not isinstance(constraint, dict):
            raise ValueError(f"Every constraint for '{entity_name}' must be an object.")

        constraint_type = self._get_required_string(
            constraint,
            "type",
            f"Every constraint for '{entity_name}' must contain 'type'.",
        )

        if constraint_type not in {"foreignKey", "primaryKey"}:
            raise ValueError(f"Unsupported constraint type '{constraint_type}' for '{entity_name}'.")

        constrained_columns = self._get_required_string_list(
            constraint,
            "columns",
            f"Constraint for '{entity_name}' must contain non-empty 'columns'.",
        )

        for constrained_column in constrained_columns:
            if constrained_column not in column_names:
                raise ValueError(
                    f"Constraint for '{entity_name}' references unknown column '{constrained_column}'."
                )

        if constraint_type == "foreignKey":
            references = constraint.get("references")

            if not isinstance(references, dict):
                raise ValueError(f"Foreign key constraint for '{entity_name}' must contain 'references' object.")

            self._get_required_string(
                references,
                "table",
                f"Foreign key constraint for '{entity_name}' references must contain 'table'.",
            )
            self._get_required_string_list(
                references,
                "columns",
                f"Foreign key constraint for '{entity_name}' references must contain non-empty 'columns'.",
            )

    def _validate_seed_group(
        self,
        table_name: str,
        seed_group: dict,
    ) -> None:
        conflict_column = self._get_required_string(
            seed_group,
            "conflictColumn",
            f"Seed group for '{table_name}' must contain 'conflictColumn'.",
        )

        rows = seed_group.get("rows")

        if not isinstance(rows, list):
            raise ValueError(f"Seed group for '{table_name}' must contain 'rows' list.")

        seen_conflict_values = set()

        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every seed row for '{table_name}' must be an object.")

            if conflict_column not in row:
                raise ValueError(
                    f"Seed row for '{table_name}' is missing conflict column '{conflict_column}'."
                )

            conflict_value = row[conflict_column]
            if conflict_value in seen_conflict_values:
                raise ValueError(
                    f"Duplicate seed value '{conflict_value}' for '{table_name}.{conflict_column}'."
                )

            seen_conflict_values.add(conflict_value)

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
        values = source.get(key)

        if not isinstance(values, list) or not values:
            raise ValueError(error_message)

        for value in values:
            if not isinstance(value, str) or not value:
                raise ValueError(error_message)

        return values

    def _add_check(self, description: str) -> None:
        self.checks.append(
            {
                "status": "PASSED",
                "description": description,
            }
        )

    def _build_report(self) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "validate_postgres_database_entity_definitions"),
            "summary": {
                "status": "PASSED",
                "checkCount": len(self.checks),
            },
            "checks": self.checks,
            "metadataPaths": self.metadata_paths,
        }

    def _print_success(self, report: dict) -> None:
        summary = report["summary"]
        print_passed(
            "validate_database_entity_definitions: "
            f"{summary['checkCount']} checks passed"
        )


def main() -> None:
    script = ValidateDatabaseEntityDefinitionsScript()

    try:
        script.run()
    except Exception as exc:
        print_failed(f"validate_database_entity_definitions failed: {exc}")
        raise


if __name__ == "__main__":
    main()
