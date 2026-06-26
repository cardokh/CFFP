"""
Updates PostgreSQL entity and schema metadata from split CRUD schema configuration.

This script does not connect to PostgreSQL and does not create database tables.
It updates metadata consumed by the existing PostgreSQL schema script.
"""

from pathlib import Path

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file


class AddDatabaseSchemaEntityScript(BaseScript):
    """Adds configured database schema entities to existing PostgreSQL metadata files."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_metadata_paths()
        self.options = self._get_options()
        self.allowed_entities = self._get_allowed_entities()
        self.entities = self._get_entities()
        self.updated_entities = []
        self.updated_schema_tables = []

    def run(self) -> None:
        entities_config = self._read_metadata_file("entitiesConfigPath")
        schema_config = self._read_metadata_file("schemaConfigPath")

        self._validate_metadata_files(
            entities_config=entities_config,
            schema_config=schema_config,
        )

        for entity in self.entities:
            entity_name = self._get_required_string(
                entity,
                "name",
                "Every schema entity must contain 'name'.",
            )
            self._validate_entity_is_listed(entity_name)
            entity_schema = self._get_required_object(
                entity,
                "schema",
                f"Schema entity '{entity_name}' must contain 'schema'.",
            )

            self._upsert_entity_name(
                entities_config=entities_config,
                entity_name=entity_name,
            )
            self._upsert_schema_table(
                schema_config=schema_config,
                entity_name=entity_name,
                entity_schema=entity_schema,
            )

        self._write_metadata_file("entitiesConfigPath", entities_config)
        self._write_metadata_file("schemaConfigPath", schema_config)

        report = self._build_report()
        self.write_json_report(report)
        self._print_success(report)

    def _get_metadata_paths(self) -> dict:
        metadata_paths = self.config.get("metadataPaths")

        if not isinstance(metadata_paths, dict):
            raise ValueError("Config must contain 'metadataPaths' object.")

        required_keys = [
            "databaseEntitiesPath",
            "entitiesConfigPath",
            "schemaConfigPath",
        ]

        for key in required_keys:
            value = metadata_paths.get(key)

            if not isinstance(value, str) or not value:
                raise ValueError(f"metadataPaths must contain non-empty '{key}'.")

        return metadata_paths

    def _get_options(self) -> dict:
        options = self.config.get("options", {})

        if not isinstance(options, dict):
            raise ValueError("Config 'options' must be an object when provided.")

        return options

    def _get_allowed_entities(self) -> list[str]:
        database_entities = self._read_metadata_file("databaseEntitiesPath")
        entities = database_entities.get("entities")

        if not isinstance(entities, list) or not entities:
            raise ValueError("database_entities.json must contain non-empty 'entities' list.")

        for entity_name in entities:
            if not isinstance(entity_name, str) or not entity_name:
                raise ValueError("Every database_entities.json entry must be a non-empty string.")

        if len(entities) != len(set(entities)):
            raise ValueError("database_entities.json must not contain duplicate entity names.")

        return entities

    def _get_entities(self) -> list[dict]:
        entities = self.config.get("entities")

        if not isinstance(entities, list) or not entities:
            raise ValueError("Config must contain non-empty 'entities' list.")

        for entity in entities:
            if not isinstance(entity, dict):
                raise ValueError("Every schema entity definition must be an object.")

        return entities

    def _read_metadata_file(self, metadata_path_key: str) -> dict:
        return read_json_file(self._resolve_project_path(self.metadata_paths[metadata_path_key]))

    def _write_metadata_file(self, metadata_path_key: str, data: dict) -> None:
        write_json_file(
            self._resolve_project_path(self.metadata_paths[metadata_path_key]),
            data,
        )

    def _resolve_project_path(self, configured_path: str) -> Path:
        return self.project_root / configured_path

    def _validate_metadata_files(
        self,
        entities_config: dict,
        schema_config: dict,
    ) -> None:
        if not isinstance(entities_config.get("entities"), list):
            raise ValueError("entities.json must contain 'entities' list.")

        if not isinstance(schema_config.get("tables"), dict):
            raise ValueError("postgres_create_schema.json must contain 'tables' object.")

    def _validate_entity_is_listed(self, entity_name: str) -> None:
        if entity_name not in self.allowed_entities:
            raise ValueError(
                f"Schema entity '{entity_name}' is not listed in database_entities.json."
            )

    def _upsert_entity_name(
        self,
        entities_config: dict,
        entity_name: str,
    ) -> None:
        entity_names = entities_config["entities"]

        if entity_name not in entity_names:
            entity_names.append(entity_name)

        self.updated_entities.append(entity_name)

    def _upsert_schema_table(
        self,
        schema_config: dict,
        entity_name: str,
        entity_schema: dict,
    ) -> None:
        self._validate_schema_definition(entity_name, entity_schema)

        table_exists = entity_name in schema_config["tables"]
        replace_existing = self.options.get("replaceExistingTableDefinitions", True)

        if table_exists and replace_existing is not True:
            raise ValueError(
                f"Schema table '{entity_name}' already exists and replaceExistingTableDefinitions is false."
            )

        schema_config["tables"][entity_name] = entity_schema
        self.updated_schema_tables.append(entity_name)

    def _validate_schema_definition(
        self,
        entity_name: str,
        schema_definition: dict,
    ) -> None:
        columns = schema_definition.get("columns")

        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema for '{entity_name}' must contain non-empty 'columns' list.")

        column_names = []

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

            column_names.append(column_name)

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

    def _get_required_object(
        self,
        source: dict,
        key: str,
        error_message: str,
    ) -> dict:
        value = source.get(key)

        if not isinstance(value, dict):
            raise ValueError(error_message)

        return value

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

    def _build_report(self) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "update_postgres_schema_metadata"),
            "summary": {
                "status": "PASSED",
                "listedEntityCount": len(self.allowed_entities),
                "updatedEntityCount": len(self.updated_entities),
                "updatedSchemaTableCount": len(self.updated_schema_tables),
                "updatedEntities": self.updated_entities,
                "updatedSchemaTables": self.updated_schema_tables,
            },
            "metadataPaths": self.metadata_paths,
        }

    def _print_success(self, report: dict) -> None:
        summary = report["summary"]
        print_passed(
            "add_database_schema_entity: "
            f"{summary['updatedEntityCount']} entities, "
            f"{summary['updatedSchemaTableCount']} schema tables updated"
        )


def main() -> None:
    script = AddDatabaseSchemaEntityScript()

    try:
        script.run()
    except Exception as exc:
        print_failed(f"add_database_schema_entity failed: {exc}")
        raise


if __name__ == "__main__":
    main()
