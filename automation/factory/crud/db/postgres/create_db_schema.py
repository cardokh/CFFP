"""Creates PostgreSQL database objects from per-entity metadata files."""

import sys
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2 import sql


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
from scripts.shared.config_resolution import ConfigurationResolver
from scripts.shared.script_console_utils import print_passed
from scripts.shared.script_json_utils import read_json_file
from scripts.shared.script_path_utils import get_path


class PostgreSQLCreateDbSchemaScript(BaseScript):
    """Provisions PostgreSQL and creates only tables listed in postgres/metadata/entities.json."""

    CONNECTION_KEYS = ["host", "port", "databaseName", "username", "password"]

    def __init__(self):
        super().__init__(__file__)
        self.database_config = self._load_database_config()
        self.entities_config = self._load_entities_config()
        self.execution = self._get_execution_config()
        self.entity_metadata_root = self._resolve_project_path("entityMetadataRoot")
        self.config_resolver = ConfigurationResolver(default_source_name="database.json")
        self.admin_connection_config = self._resolve_connection_config("adminConnection", "admin")
        self.application_connection_config = self._resolve_connection_config("applicationConnection", "application")
        self.dropped_database = False
        self.created_database = False
        self.created_role = False
        self.updated_role_password = False
        self.granted_privileges = []
        self.dropped_tables = []
        self.dropped_unlisted_tables = []
        self.created_tables = []
        self.skipped_existing_tables = []
        self.verified_database = False
        self.verified_tables = []

    def run(self) -> None:
        self._configure_backend_import_path()
        self._validate_database_type()
        self._execute_database_provisioning()
        self._execute_schema_creation()
        self._verify_database_state()
        report = self._build_report()
        self.write_json_report(report)
        print_passed(
            f"PostgreSQL schema created and verified. Database: "
            f"{self.application_connection_config['databaseName']}. Tables: {len(self.created_tables)}"
        )

    def _load_database_config(self) -> dict:
        return read_json_file(self._resolve_project_path("databaseConfigPath"))

    def _load_entities_config(self) -> dict:
        return read_json_file(self._resolve_project_path("entitiesConfigPath"))

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _get_execution_config(self) -> dict:
        execution = self.config.get("execution", {})
        if not isinstance(execution, dict):
            raise ValueError("create_db_schema.json execution must be an object when provided.")
        return execution

    def _configure_backend_import_path(self) -> None:
        backend_path_key = self.database_config.get("backendPathKey")
        if not isinstance(backend_path_key, str) or not backend_path_key:
            raise ValueError("database.json must contain 'backendPathKey'.")
        backend_path = get_path(backend_path_key)
        if str(backend_path) not in sys.path:
            sys.path.append(str(backend_path))

    def _validate_database_type(self) -> None:
        if self.database_config.get("databaseType") != "postgres":
            raise ValueError("create_db_schema.py requires databaseType 'postgres'.")

    def _resolve_connection_config(self, config_key: str, environment_group_key: str) -> dict:
        environment_variables = self.database_config.get("environmentVariables", {})
        return self.config_resolver.resolve_group(
            group_name=environment_group_key,
            configured_values=self.database_config.get(config_key),
            environment_variables=environment_variables.get(environment_group_key, {}),
            keys=self.CONNECTION_KEYS,
            casts={"port": int},
            sensitive_keys={"password"},
        )

    def _execute_database_provisioning(self) -> None:
        if self.execution.get("recreateDatabase") is True:
            self._drop_application_database_if_exists()

        bootstrap_config = self.database_config.get("bootstrap", {})
        if not isinstance(bootstrap_config, dict):
            raise ValueError("database.json bootstrap must be an object when provided.")
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
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            if cursor.fetchone() is None:
                return
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()",
                (database_name,),
            )
            cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name)))
            self.dropped_database = True
        finally:
            conn.close()

    def _create_or_update_application_role(self) -> None:
        conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        conn.autocommit = True
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (self.application_connection_config["username"],))
            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(sql.Identifier(self.application_connection_config["username"])),
                    (self.application_connection_config["password"],),
                )
                self.created_role = True
            else:
                cursor.execute(
                    sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD %s").format(sql.Identifier(self.application_connection_config["username"])),
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
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.application_connection_config["databaseName"],))
            if cursor.fetchone() is None:
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
                    sql.Identifier(database_name), sql.Identifier(application_user)
                )
            )
            self.granted_privileges.append("database")
        finally:
            admin_conn.close()
        target_conn = self._get_admin_connection(database_name)
        target_conn.autocommit = True
        try:
            cursor = target_conn.cursor()
            cursor.execute(sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {}").format(sql.Identifier(application_user)))
            cursor.execute(sql.SQL("ALTER SCHEMA public OWNER TO {}").format(sql.Identifier(application_user)))
            self.granted_privileges.append("schema_public")
        finally:
            target_conn.close()

    def _execute_schema_creation(self) -> None:
        conn = self._get_application_connection()
        try:
            cursor = conn.cursor()
            entity_names = self._get_entity_names()
            if self.execution.get("dropUnlistedTables", False) is True:
                self._drop_unlisted_tables(cursor, entity_names)
            if self.execution.get("recreateExistingTables", True) is True:
                for entity_name in reversed(entity_names):
                    cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(entity_name)))
                    self.dropped_tables.append(entity_name)
            for entity_name in entity_names:
                if self.execution.get("recreateExistingTables", True) is not True and self._table_exists(cursor, entity_name):
                    self.skipped_existing_tables.append(entity_name)
                    continue
                table_definition = self._get_table_definition(entity_name)
                cursor.execute(self._build_generate_table_metadata_sql(entity_name, table_definition, entity_names))
                self.created_tables.append(entity_name)
            conn.commit()
        finally:
            conn.close()

    def _table_exists(self, cursor: Any, table_name: str) -> bool:
        cursor.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s",
            (table_name,),
        )
        return cursor.fetchone() is not None

    def _drop_unlisted_tables(self, cursor: Any, selected_entity_names: list[str]) -> None:
        selected = set(selected_entity_names)
        for table_name in self._get_existing_public_tables(cursor):
            if table_name in selected:
                continue
            cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table_name)))
            self.dropped_unlisted_tables.append(table_name)

    def _get_existing_public_tables(self, cursor: Any) -> list[str]:
        cursor.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name DESC
            """
        )
        return [row[0] for row in cursor.fetchall()]

    def _verify_database_state(self) -> None:
        self._verify_application_database_exists()
        self._verify_application_tables_exist()

    def _verify_application_database_exists(self) -> None:
        conn = self._get_admin_connection(self.admin_connection_config["databaseName"])
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.application_connection_config["databaseName"],))
            self.verified_database = cursor.fetchone() is not None
        finally:
            conn.close()
        if not self.verified_database:
            raise RuntimeError(f"Application database was not found: {self.application_connection_config['databaseName']}")

    def _verify_application_tables_exist(self) -> None:
        expected_tables = self._get_entity_names()
        if not expected_tables:
            self.verified_tables = []
            return
        conn = self._get_application_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name = ANY(%s)
                ORDER BY table_name
                """,
                (expected_tables,),
            )
            self.verified_tables = [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
        missing = sorted(set(expected_tables) - set(self.verified_tables))
        if missing:
            raise RuntimeError("Missing application tables: " + ", ".join(missing))

    def _get_entity_names(self) -> list[str]:
        entities = self.entities_config.get("entities")
        if not isinstance(entities, list):
            raise ValueError("entities.json must contain 'entities' list.")
        for entity in entities:
            if not isinstance(entity, str) or not entity:
                raise ValueError("Every entity entry must be a non-empty string.")
        if len(entities) != len(set(entities)):
            raise ValueError("entities.json must not contain duplicate entity names.")
        return entities

    def _get_table_definition(self, entity_name: str) -> dict:
        schema_path = self.entity_metadata_root / entity_name / "schema.json"
        if not schema_path.exists():
            raise ValueError(f"Missing schema metadata for entity '{entity_name}': {schema_path}")
        table_definition = read_json_file(schema_path)
        if not isinstance(table_definition, dict):
            raise ValueError(f"Schema metadata for '{entity_name}' must be an object.")
        return table_definition

    def _build_generate_table_metadata_sql(self, entity_name: str, table_definition: dict, selected_entity_names: list[str]) -> Any:
        definitions = [self._build_column_sql(column) for column in self._get_columns(table_definition)]
        definitions.extend(
            self._build_table_constraint_sql(constraint)
            for constraint in self._get_selected_table_constraints(entity_name, table_definition, selected_entity_names)
        )
        return sql.SQL("CREATE TABLE {} ({});").format(sql.Identifier(entity_name), sql.SQL(", ").join(definitions))

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

    def _get_selected_table_constraints(self, entity_name: str, table_definition: dict, selected_entity_names: list[str]) -> list[dict]:
        selected = set(selected_entity_names)
        constraints = []
        for constraint in self._get_table_constraints(table_definition):
            if constraint.get("type") != "foreignKey":
                constraints.append(constraint)
                continue

            references = constraint.get("references")
            if not isinstance(references, dict):
                raise ValueError("Foreign key constraint must contain 'references' object.")

            reference_table = self._get_required_string(
                references,
                "table",
                "Foreign key references must contain 'table'.",
            )

            if reference_table not in selected:
                raise ValueError(
                    f"Selected entity '{entity_name}' has a foreign key to unselected entity "
                    f"'{reference_table}'. Add '{reference_table}' to postgres/metadata/entities.json "
                    "before running schema creation."
                )

            constraints.append(constraint)

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
        if column.get("default") is not None:
            parts.extend([sql.SQL("DEFAULT"), sql.SQL(str(column.get("default")))])
        return sql.SQL(" ").join(parts)

    def _build_table_constraint_sql(self, constraint: dict) -> Any:
        constraint_type = self._get_required_string(constraint, "type", "Constraint definition must contain 'type'.")
        if constraint_type == "foreignKey":
            return self._build_foreign_key_sql(constraint)
        if constraint_type == "primaryKey":
            return self._build_primary_key_sql(constraint)
        raise ValueError(f"Unsupported constraint type: {constraint_type}")

    def _build_primary_key_sql(self, constraint: dict) -> Any:
        columns = self._get_required_string_list(constraint, "columns", "Primary key constraint must contain non-empty 'columns'.")
        return sql.SQL("PRIMARY KEY ({})").format(sql.SQL(", ").join(sql.Identifier(column) for column in columns))

    def _build_foreign_key_sql(self, constraint: dict) -> Any:
        columns = self._get_required_string_list(constraint, "columns", "Foreign key constraint must contain non-empty 'columns'.")
        references = constraint.get("references")
        if not isinstance(references, dict):
            raise ValueError("Foreign key constraint must contain 'references' object.")
        reference_table = self._get_required_string(references, "table", "Foreign key references must contain 'table'.")
        reference_columns = self._get_required_string_list(references, "columns", "Foreign key references must contain non-empty 'columns'.")
        parts = [
            sql.SQL("FOREIGN KEY ({})").format(sql.SQL(", ").join(sql.Identifier(column) for column in columns)),
            sql.SQL("REFERENCES {} ({})").format(sql.Identifier(reference_table), sql.SQL(", ").join(sql.Identifier(column) for column in reference_columns)),
        ]
        if isinstance(constraint.get("onDelete"), str) and constraint.get("onDelete"):
            parts.append(sql.SQL(f"ON DELETE {constraint['onDelete']}"))
        return sql.SQL(" ").join(parts)

    def _get_admin_connection(self, database_name: str) -> Any:
        return psycopg2.connect(
            host=self.admin_connection_config["host"], port=self.admin_connection_config["port"], dbname=database_name,
            user=self.admin_connection_config["username"], password=self.admin_connection_config["password"]
        )

    def _get_application_connection(self) -> Any:
        return psycopg2.connect(
            host=self.application_connection_config["host"], port=self.application_connection_config["port"], dbname=self.application_connection_config["databaseName"],
            user=self.application_connection_config["username"], password=self.application_connection_config["password"]
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
            "mode": self.config.get("mode", "create_db_schema"),
            "configurationResolution": self.config_resolver.to_report(),
            "execution": self.execution,
            "summary": {
                "status": "PASSED",
                "adminDatabaseName": self.admin_connection_config["databaseName"],
                "applicationDatabaseName": self.application_connection_config["databaseName"],
                "droppedDatabase": self.dropped_database,
                "createdDatabase": self.created_database,
                "createdRole": self.created_role,
                "updatedRolePassword": self.updated_role_password,
                "grantedPrivileges": self.granted_privileges,
                "droppedTableCount": len(self.dropped_tables),
                "droppedUnlistedTableCount": len(self.dropped_unlisted_tables),
                "createdTableCount": len(self.created_tables),
                "skippedExistingTableCount": len(self.skipped_existing_tables),
                "verifiedTableCount": len(self.verified_tables),
            },
            "tables": {
                "selected": self._get_entity_names(),
                "dropped": self.dropped_tables,
                "droppedUnlisted": self.dropped_unlisted_tables,
                "created": self.created_tables,
                "skippedExisting": self.skipped_existing_tables,
                "verified": self.verified_tables,
            },
        }


if __name__ == "__main__":
    PostgreSQLCreateDbSchemaScript().run()
