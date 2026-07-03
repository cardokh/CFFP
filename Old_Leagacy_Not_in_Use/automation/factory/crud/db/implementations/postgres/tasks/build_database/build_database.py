"""Builds a PostgreSQL database from the generic database metadata model."""

import sys
import time
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2 import sql


def _configure_project_import_path() -> None:
    project_root = next(
        (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    db_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "run_db_tasks.py").is_file()
            and (parent / "metadata").is_dir()
            and (parent / "implementations").is_dir()
        ),
        None,
    )
    if db_root is not None and str(db_root) not in sys.path:
        sys.path.insert(0, str(db_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.config_resolution import ConfigurationResolver
from scripts.shared.script_console_utils import print_passed
from scripts.shared.script_json_utils import read_json_file
from support.db_path_utils import get_db_root, resolve_db_path

from implementations.postgres.support.dependency_resolver import sort_schemas_by_dependency


class BuildDatabaseScript(BaseScript):
    """Builds PostgreSQL database structure and writes the executed SQL artifact."""

    CONNECTION_KEYS = ["host", "port", "databaseName", "username", "password"]

    def __init__(self) -> None:
        super().__init__(__file__)
        self.db_root = get_db_root(__file__)
        self.metadata_root = self._resolve_db_path("metadataRoot")
        self.implementation_root = self._resolve_db_path("implementationRoot")
        self.config_resolver = ConfigurationResolver(default_source_name="database.json")
        self.implementation_metadata = read_json_file(self.implementation_root / "database.json")
        self.admin_connection_config = self._resolve_connection_config("adminConnection", "admin")
        self.application_connection_config = self._resolve_connection_config("applicationConnection", "application")
        self.execution_config = self._resolve_execution_config()
        self.schemas: list[dict[str, Any]] = []
        self.ordered_schemas: list[dict[str, Any]] = []
        self.existing_application_tables: list[str] = []
        self.created_database = False
        self.created_role = False
        self.updated_role_password = False
        self.dropped_tables: list[str] = []
        self.created_tables: list[str] = []
        self.added_foreign_keys: list[str] = []

    def run(self) -> None:
        started = time.perf_counter()
        self._validate_database_type()
        self.schemas = self._load_schemas()
        self.ordered_schemas = sort_schemas_by_dependency(self.schemas)

        if self.config.get("executeSql", True) is True:
            self._execute_database_provisioning()
            self.existing_application_tables = self._load_existing_application_tables()

        sql_text = self._render_database_sql()

        output_file = self.output_directory / self.config.get("outputFileName", "database.sql")
        output_file.write_text(sql_text, encoding="utf-8")

        if self.config.get("executeSql", True) is True:
            self._execute_sql(sql_text)

        self.write_json_report({
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "build_postgres_database_from_generic_metadata"),
            "configurationResolution": self.config_resolver.to_report(),
            "summary": {
                "status": "PASSED",
                "metadataRoot": self.to_project_relative_path(self.metadata_root),
                "implementationRoot": self.to_project_relative_path(self.implementation_root),
                "outputFile": self.to_project_relative_path(output_file),
                "applicationDatabaseName": self.application_connection_config["databaseName"],
                "tableCount": len(self.ordered_schemas),
                "createdDatabase": self.created_database,
                "createdRole": self.created_role,
                "updatedRolePassword": self.updated_role_password,
                "droppedTableCount": len(self.dropped_tables),
                "createdTableCount": len(self.created_tables),
                "addedForeignKeyCount": len(self.added_foreign_keys),
                "executed": self.config.get("executeSql", True) is True,
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            },
            "orderedTables": [schema["name"] for schema in self.ordered_schemas],
            "existingApplicationTables": self.existing_application_tables,
            "effectiveExecution": self.execution_config,
            "droppedTables": self.dropped_tables,
            "createdTables": self.created_tables,
            "addedForeignKeys": self.added_foreign_keys,
        })
        action = "built" if self.config.get("executeSql", True) is True else "generated"
        print_passed(
            f"build_database: {action} {self.application_connection_config['databaseName']} from "
            f"{len(self.ordered_schemas)} table(s); SQL {self.to_project_relative_path(output_file)}"
        )

    def _resolve_db_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return resolve_db_path(self.db_root, configured_path)

    def _resolve_execution_config(self) -> dict[str, Any]:
        execution_config: dict[str, Any] = {}

        run_db_tasks_config_path = self.db_root / "config" / "run_db_tasks.json"
        if run_db_tasks_config_path.is_file():
            run_db_tasks_config = read_json_file(run_db_tasks_config_path)
            run_db_tasks_execution = run_db_tasks_config.get("execution", {})
            if isinstance(run_db_tasks_execution, dict):
                execution_config.update(run_db_tasks_execution)

        local_execution = self.config.get("execution", {})
        if isinstance(local_execution, dict):
            for key, value in local_execution.items():
                if key not in execution_config:
                    execution_config[key] = value

        return {
            "recreateDatabase": execution_config.get("recreateDatabase") is True,
            "recreateExistingTables": execution_config.get("recreateExistingTables", True) is True,
            "dropUnlistedTables": execution_config.get("dropUnlistedTables") is True,
        }

    def _validate_database_type(self) -> None:
        if self.implementation_metadata.get("databaseType") != "postgres":
            raise ValueError("build_database.py requires databaseType 'postgres'.")

    def _resolve_connection_config(self, config_key: str, environment_group_key: str) -> dict[str, Any]:
        environment_variables = self.implementation_metadata.get("environmentVariables", {})
        return self.config_resolver.resolve_group(
            group_name=environment_group_key,
            configured_values=self.implementation_metadata.get(config_key),
            environment_variables=environment_variables.get(environment_group_key, {}),
            keys=self.CONNECTION_KEYS,
            casts={"port": int},
            sensitive_keys={"password"},
        )

    def _load_schemas(self) -> list[dict[str, Any]]:
        schemas: list[dict[str, Any]] = []
        for module_root_value in self.config.get("moduleRoots", []):
            module_root = self.metadata_root / "modules" / str(module_root_value)
            tables_json = read_json_file(module_root / "tables.json")
            for table_name in tables_json.get("tables", []):
                schemas.append(read_json_file(module_root / "tables" / str(table_name) / "schema.json"))
        return schemas

    def _execute_sql(self, sql_text: str) -> None:
        conn = self._get_application_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql_text)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _execute_database_provisioning(self) -> None:
        bootstrap_config = self.implementation_metadata.get("bootstrap", {})
        if not isinstance(bootstrap_config, dict):
            raise ValueError("database.json bootstrap must be an object when provided.")

        if self.execution_config.get("recreateDatabase") is True:
            self._drop_application_database_if_exists()
        if bootstrap_config.get("createApplicationRole", True) is True:
            self._create_or_update_application_role()
        if bootstrap_config.get("createApplicationDatabase", True) is True:
            self._create_application_database_if_missing()
        self._grant_application_privileges()

    def _drop_application_database_if_exists(self) -> None:
        database_name = self.application_connection_config["databaseName"]
        conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        conn.autocommit = True
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
                if cursor.fetchone() is None:
                    return
                cursor.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()",
                    (database_name,),
                )
                cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name)))
                self.created_database = False
        finally:
            conn.close()

    def _create_or_update_application_role(self) -> None:
        conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        conn.autocommit = True
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (self.application_connection_config["username"],))
                if cursor.fetchone() is None:
                    cursor.execute(
                        sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(
                            sql.Identifier(self.application_connection_config["username"])
                        ),
                        (self.application_connection_config["password"],),
                    )
                    self.created_role = True
                else:
                    cursor.execute(
                        sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD %s").format(
                            sql.Identifier(self.application_connection_config["username"])
                        ),
                        (self.application_connection_config["password"],),
                    )
                    self.updated_role_password = True
        finally:
            conn.close()

    def _create_application_database_if_missing(self) -> None:
        database_name = self.application_connection_config["databaseName"]
        conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        conn.autocommit = True
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        sql.SQL("CREATE DATABASE {} OWNER {}").format(
                            sql.Identifier(database_name),
                            sql.Identifier(self.application_connection_config["username"]),
                        )
                    )
                    self.created_database = True
        finally:
            conn.close()

    def _grant_application_privileges(self) -> None:
        database_name = self.application_connection_config["databaseName"]
        application_user = self.application_connection_config["username"]
        conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        conn.autocommit = True
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                        sql.Identifier(database_name), sql.Identifier(application_user)
                    )
                )
        finally:
            conn.close()

        conn = self._get_admin_connection(database_name)
        conn.autocommit = True
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {}").format(sql.Identifier(application_user)))
                cursor.execute(sql.SQL("ALTER SCHEMA public OWNER TO {}").format(sql.Identifier(application_user)))
        finally:
            conn.close()

    def _load_existing_application_tables(self) -> list[str]:
        conn = self._get_application_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """
                )
                return [str(row[0]) for row in cursor.fetchall()]
        finally:
            conn.close()

    def _render_database_sql(self) -> str:
        lines: list[str] = [
            "-- Generated from db/metadata.",
            "-- Parallel PostgreSQL implementation artifact.",
            "",
            "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
            "",
        ]

        desired_table_names = [str(schema["name"]) for schema in self.ordered_schemas]
        desired_table_name_set = set(desired_table_names)
        rendered_drop_table_names: set[str] = set()

        if self.execution_config.get("dropUnlistedTables") is True:
            for table_name in self.existing_application_tables:
                if table_name not in desired_table_name_set:
                    lines.append(f"DROP TABLE IF EXISTS {self._identifier(table_name)} CASCADE;")
                    self.dropped_tables.append(table_name)
                    rendered_drop_table_names.add(table_name)
            if rendered_drop_table_names:
                lines.append("")

        if self.execution_config.get("recreateExistingTables") is True:
            for schema in reversed(self.ordered_schemas):
                table_name = str(schema["name"])
                if table_name not in rendered_drop_table_names:
                    lines.append(f"DROP TABLE IF EXISTS {self._identifier(table_name)} CASCADE;")
                    self.dropped_tables.append(table_name)
                    rendered_drop_table_names.add(table_name)
            lines.append("")

        for schema in self.ordered_schemas:
            lines.extend(self._render_create_table(schema))
            self.created_tables.append(str(schema['name']))
            lines.append("")

        if self.implementation_metadata.get("enableForeignKeys", True):
            for schema in self.ordered_schemas:
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

        return [f"CREATE TABLE {self._identifier(table_name)} (", ",\n".join(definitions), ");"]

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
            self.added_foreign_keys.append(constraint_name)
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

    def _identifier(self, value: str) -> str:
        return '"' + str(value).replace('"', '""') + '"'


if __name__ == "__main__":
    BuildDatabaseScript().run()
