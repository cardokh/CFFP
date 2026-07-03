"""Dependency ordering helpers for PostgreSQL metadata consumers."""

from typing import Any


def sort_schemas_by_dependency(schemas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return schemas sorted so referenced tables appear before dependants."""
    schemas_by_name = {str(schema["name"]): schema for schema in schemas}
    dependencies: dict[str, set[str]] = {name: set() for name in schemas_by_name}

    for schema in schemas:
        table_name = str(schema["name"])
        for foreign_key in schema.get("foreignKeys", []):
            referenced_table = foreign_key.get("references", {}).get("table")
            if referenced_table in schemas_by_name and referenced_table != table_name:
                dependencies[table_name].add(str(referenced_table))

    ordered_names: list[str] = []
    temporary_marks: set[str] = set()
    permanent_marks: set[str] = set()

    def visit(table_name: str) -> None:
        if table_name in permanent_marks:
            return
        if table_name in temporary_marks:
            cycle = " -> ".join([*temporary_marks, table_name])
            raise ValueError(f"Foreign-key dependency cycle detected: {cycle}")

        temporary_marks.add(table_name)
        for dependency_name in sorted(dependencies[table_name]):
            visit(dependency_name)
        temporary_marks.remove(table_name)
        permanent_marks.add(table_name)
        ordered_names.append(table_name)

    for table_name in sorted(schemas_by_name):
        visit(table_name)

    return [schemas_by_name[name] for name in ordered_names]
