"""
Creates the PostgreSQL application database, application role, and schema from metadata.

Run before postgres_seed_data.py:

    python -m scripts.db.postgres.postgres_create_schema
    python -m scripts.db.postgres.postgres_seed_data
"""

import os
import sys
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2 import sql

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file
from scripts.shared.script_path_utils import get_path


class PostgreSQLCreateSchemaScript(BaseScript):
    """
    Provisions the PostgreSQL application database and creates schema objects from metadata.
    """

    def __init__(self):
        super().__init__(__file__)
        self.database_config = self._load_database_config()
        self.entities_config = self._load_entities_config()
        self.admin_connection_config = self._resolve_connection_config("adminConnection", "admin")
        self.application_connection_config = self._resolve_connection_config("applicationConnection", "application")
        self.created_database = False
        self.created_role = False
        self.updated_role_password = False
        self.granted_privileges = []
        self.dropped_tables = []
        self.created_tables = []

    def run(self) -> None:
        self._configure_backend_import_path()
        self._validate_database_type()
        self._execute_database_provisioning()
        self._execute_schema_creation()

        report = self._build_report()
        self._write_report(report)
        self._print_success(report)

    def _load_database_config(self) -> dict:
        return read_json_file(self._resolve_config_path("databaseConfigPath"))

    def _load_entities_config(self) -> dict:
        return read_json_file(self._resolve_config_path("entitiesConfigPath"))

    def _resolve_config_path(self, config_key: str) -> Path:
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

    def _validate_database_type(self) -> None:
        if self.database_config.get("databaseType") != "postgres":
            raise ValueError("postgres_create_schema.py requires databaseType 'postgres'.")

    def _resolve_connection_config(self, config_key: str, environment_group_key: str) -> dict:
        configured_connection = self.database_config.get(config_key)
        environment_variables = self.database_config.get("environmentVariables", {})
        grouped_environment_variables = environment_variables.get(environment_group_key, {})

        if not isinstance(configured_connection, dict):
            raise ValueError(f"database.json must contain '{config_key}' object.")

        if not isinstance(grouped_environment_variables, dict):
            raise ValueError(
                f"database.json environmentVariables must contain '{environment_group_key}' object."
            )

        return {
            "host": self._resolve_connection_value("host", configured_connection, grouped_environment_variables),
            "port": int(self._resolve_connection_value("port", configured_connection, grouped_environment_variables)),
            "databaseName": self._resolve_connection_value("databaseName", configured_connection, grouped_environment_variables),
            "username": self._resolve_connection_value("username", configured_connection, grouped_environment_variables),
            "password": self._resolve_connection_value("password", configured_connection, grouped_environment_variables),
        }

    def _resolve_connection_value(
        self,
        key: str,
        configured_connection: dict,
        environment_variables: dict,
    ) -> Any:
        environment_variable_name = environment_variables.get(key)

        if isinstance(environment_variable_name, str) and environment_variable_name:
            environment_value = os.environ.get(environment_variable_name)

            if environment_value not in (None, ""):
                return environment_value

        configured_value = configured_connection.get(key)

        if configured_value in (None, ""):
            raise ValueError(f"PostgreSQL connection value '{key}' is not configured.")

        return configured_value

    def _execute_database_provisioning(self) -> None:
        bootstrap_config = self.database_config.get("bootstrap", {})

        if not isinstance(bootstrap_config, dict):
            raise ValueError("database.json bootstrap must be an object when provided.")

        if bootstrap_config.get("createApplicationRole", True) is True:
            self._create_or_update_application_role()

        if bootstrap_config.get("createApplicationDatabase", True) is True:
            self._create_application_database_if_missing()

        self._grant_application_privileges()

    def _create_or_update_application_role(self) -> None:
        conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        conn.autocommit = True

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s",
                (self.application_connection_config["username"],),
            )

            role_exists = cursor.fetchone() is not None

            if not role_exists:
                cursor.execute(
                    sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(
                        sql.Identifier(self.application_connection_config["username"]),
                    ),
                    (self.application_connection_config["password"],),
                )
                self.created_role = True
            else:
                cursor.execute(
                    sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD %s").format(
                        sql.Identifier(self.application_connection_config["username"]),
                    ),
                    (self.application_connection_config["password"],),
                )
                self.updated_role_password = True
        finally:
            conn.close()

    def _create_application_database_if_missing(self) -> None:
        conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        conn.autocommit = True

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.application_connection_config["databaseName"],),
            )

            database_exists = cursor.fetchone() is not None

            if not database_exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(self.application_connection_config["databaseName"]),
                        sql.Identifier(self.application_connection_config["username"]),
                    )
                )
                self.created_database = True
        finally:
            conn.close()

    def _grant_application_privileges(self) -> None:
        database_name = self.application_connection_config["databaseName"]
        application_user = self.application_connection_config["username"]

        admin_conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        admin_conn.autocommit = True

        try:
            cursor = admin_conn.cursor()
            cursor.execute(
                sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                    sql.Identifier(database_name),
                    sql.Identifier(application_user),
                )
            )
            self.granted_privileges.append("database")
        finally:
            admin_conn.close()

        target_conn = self._get_admin_connection(database_name)
        target_conn.autocommit = True

        try:
            cursor = target_conn.cursor()
            cursor.execute(
                sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {}").format(
                    sql.Identifier(application_user),
                )
            )
            cursor.execute(
                sql.SQL("ALTER SCHEMA public OWNER TO {}").format(
                    sql.Identifier(application_user),
                )
            )
            self.granted_privileges.append("schema_public")
        finally:
            target_conn.close()

    def _execute_schema_creation(self) -> None:
        conn = self._get_application_connection()

        try:
            cursor = conn.cursor()

            for entity_name in reversed(self._get_entity_names()):
                cursor.execute(
                    sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                        sql.Identifier(entity_name),
                    )
                )
                self.dropped_tables.append(entity_name)

            for entity_name in self._get_entity_names():
                table_definition = self._get_table_definition(entity_name)
                cursor.execute(self._build_create_table_sql(entity_name, table_definition))
                self.created_tables.append(entity_name)

            conn.commit()
        finally:
            conn.close()

    def _get_entity_names(self) -> list[str]:
        entities = self.entities_config.get("entities")

        if not isinstance(entities, list) or not entities:
            raise ValueError("entities.json must contain non-empty 'entities'.")

        for entity in entities:
            if not isinstance(entity, str) or not entity:
                raise ValueError("Every entity entry must be a non-empty string.")

        return entities

    def _get_table_definition(self, entity_name: str) -> dict:
        tables = self.config.get("tables")

        if not isinstance(tables, dict):
            raise ValueError("postgres_create_schema.json must contain 'tables' object.")

        table_definition = tables.get(entity_name)

        if not isinstance(table_definition, dict):
            raise ValueError(f"Missing table definition for entity '{entity_name}'.")

        return table_definition

    def _build_create_table_sql(self, entity_name: str, table_definition: dict) -> Any:
        definitions = []

        for column in self._get_columns(table_definition):
            definitions.append(self._build_column_sql(column))

        for constraint in self._get_table_constraints(table_definition):
            definitions.append(self._build_table_constraint_sql(constraint))

        return sql.SQL("CREATE TABLE {} ({});").format(
            sql.Identifier(entity_name),
            sql.SQL(", ").join(definitions),
        )

    def _get_columns(self, table_definition: dict) -> list[dict]:
        columns = table_definition.get("columns")

        if not isinstance(columns, list) or not columns:
            raise ValueError("Every table definition must contain non-empty 'columns'.")

        return columns

    def _get_table_constraints(self, table_definition: dict) -> list[dict]:
        constraints = table_definition.get("constraints", [])

        if not isinstance(constraints, list):
            raise ValueError("'constraints' must be a list when provided.")

        return constraints

    def _build_column_sql(self, column: dict) -> Any:
        column_name = self._get_required_string(column, "name", "Column definition must contain 'name'.")
        data_type = self._get_required_string(column, "type", "Column definition must contain 'type'.")

        parts = [sql.Identifier(column_name), sql.SQL(data_type)]

        if column.get("primaryKey") is True:
            parts.append(sql.SQL("PRIMARY KEY"))

        if column.get("nullable") is False:
            parts.append(sql.SQL("NOT NULL"))

        if column.get("unique") is True:
            parts.append(sql.SQL("UNIQUE"))

        default_value = column.get("default")

        if default_value is not None:
            parts.extend([sql.SQL("DEFAULT"), sql.SQL(str(default_value))])

        return sql.SQL(" ").join(parts)

    def _build_table_constraint_sql(self, constraint: dict) -> Any:
        constraint_type = self._get_required_string(
            constraint,
            "type",
            "Constraint definition must contain 'type'.",
        )

        if constraint_type == "foreignKey":
            return self._build_foreign_key_sql(constraint)

        if constraint_type == "primaryKey":
            return self._build_primary_key_sql(constraint)

        raise ValueError(f"Unsupported constraint type: {constraint_type}")

    def _build_primary_key_sql(self, constraint: dict) -> Any:
        columns = self._get_required_string_list(
            constraint,
            "columns",
            "Primary key constraint must contain non-empty 'columns'.",
        )

        return sql.SQL("PRIMARY KEY ({})").format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        )

    def _build_foreign_key_sql(self, constraint: dict) -> Any:
        columns = self._get_required_string_list(
            constraint,
            "columns",
            "Foreign key constraint must contain non-empty 'columns'.",
        )
        references = constraint.get("references")

        if not isinstance(references, dict):
            raise ValueError("Foreign key constraint must contain 'references' object.")

        reference_table = self._get_required_string(
            references,
            "table",
            "Foreign key references must contain 'table'.",
        )
        reference_columns = self._get_required_string_list(
            references,
            "columns",
            "Foreign key references must contain non-empty 'columns'.",
        )

        parts = [
            sql.SQL("FOREIGN KEY ({})").format(
                sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            ),
            sql.SQL("REFERENCES {} ({})").format(
                sql.Identifier(reference_table),
                sql.SQL(", ").join(sql.Identifier(column) for column in reference_columns),
            ),
        ]

        on_delete = constraint.get("onDelete")

        if isinstance(on_delete, str) and on_delete:
            parts.append(sql.SQL(f"ON DELETE {on_delete}"))

        return sql.SQL(" ").join(parts)

    def _get_admin_connection(self, database_name: str) -> Any:
        return psycopg2.connect(
            host=self.admin_connection_config["host"],
            port=self.admin_connection_config["port"],
            dbname=database_name,
            user=self.admin_connection_config["username"],
            password=self.admin_connection_config["password"],
        )

    def _get_application_connection(self) -> Any:
        return psycopg2.connect(
            host=self.application_connection_config["host"],
            port=self.application_connection_config["port"],
            dbname=self.application_connection_config["databaseName"],
            user=self.application_connection_config["username"],
            password=self.application_connection_config["password"],
        )

    def _get_required_string(self, source: dict, key: str, error_message: str) -> str:
        value = source.get(key)

        if not isinstance(value, str) or not value:
            raise ValueError(error_message)

        return value

    def _get_required_string_list(self, source: dict, key: str, error_message: str) -> list[str]:
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
            "mode": self.config.get("mode", "create_schema"),
            "summary": {
                "status": "PASSED",
                "adminDatabaseName": self.admin_connection_config["databaseName"],
                "applicationDatabaseName": self.application_connection_config["databaseName"],
                "host": self.application_connection_config["host"],
                "port": self.application_connection_config["port"],
                "applicationUsername": self.application_connection_config["username"],
                "createdDatabase": self.created_database,
                "createdRole": self.created_role,
                "updatedRolePassword": self.updated_role_password,
                "grantedPrivileges": self.granted_privileges,
                "droppedTableCount": len(self.dropped_tables),
                "createdTableCount": len(self.created_tables),
            },
            "droppedTables": self.dropped_tables,
            "createdTables": self.created_tables,
        }

    def _write_report(self, report: dict) -> None:
        output_file_path = self.output_directory / f"{self.script_name}_report_{self.timestamp}.json"
        write_json_file(output_file_path, report)

    def _print_success(self, report: dict) -> None:
        print_passed(
            "PostgreSQL schema created. "
            f"Database: {report['summary']['applicationDatabaseName']}. "
            f"Tables: {report['summary']['createdTableCount']}"
        )


def main() -> None:
    script = PostgreSQLCreateSchemaScript()

    try:
        script.run()
    except Exception as exc:
        print_failed(f"PostgreSQL schema creation failed: {exc}")
        raise


if __name__ == "__main__":
    main()
