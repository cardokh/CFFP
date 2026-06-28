"""Contract tests for the DB task orchestrator configuration."""

from __future__ import annotations

import py_compile

from automation.factory.crud.db.tests.support.db_json_validation import read_json
from automation.factory.crud.db.tests.support.db_test_paths import get_db_root, get_project_root, to_project_relative

EXPECTED_COMPONENTS = [
    "generate_table_metadata",
    "promote_db_metadata",
    "create_db_schema",
    "seed_db_data",
    "build_db_context",
]


def test_db_pipeline_json_declares_expected_task_order_and_scripts() -> None:
    project_root = get_project_root()
    db_root = get_db_root()
    config = read_json(db_root / "config" / "db_pipeline.json")

    assert config["scriptName"] == "db_pipeline"
    assert config["mode"] == "database_crud_pipeline"
    assert config["databaseEngine"] == "postgres"
    assert isinstance(config.get("execution"), dict)

    components = config.get("components")
    assert isinstance(components, list)
    assert [component.get("name") for component in components] == EXPECTED_COMPONENTS

    for component in components:
        name = component["name"]
        assert isinstance(component.get("enabled"), bool), f"{name}.enabled must be explicit boolean."
        script_path_value = component.get("scriptPath")
        assert isinstance(script_path_value, str) and script_path_value
        assert script_path_value == f"automation/factory/crud/db/postgres/{name}/{name}.py"
        script_path = project_root / script_path_value
        assert script_path.is_file(), f"Configured script path does not exist: {script_path_value}"
        assert script_path.parent.name == name
        assert script_path.stem == name


def test_db_pipeline_does_not_configure_child_pipelines() -> None:
    db_root = get_db_root()
    config = read_json(db_root / "config" / "db_pipeline.json")

    for component in config["components"]:
        script_path = component["scriptPath"]
        assert not script_path.endswith("pipeline.py"), f"DB task orchestrator must not execute child pipelines: {script_path}"
        assert "/backend/" not in script_path and "/frontend/" not in script_path


def test_db_python_files_compile() -> None:
    db_root = get_db_root()
    python_files = sorted(path for path in db_root.rglob("*.py") if "__pycache__" not in path.parts)
    assert python_files, "Expected DB pipeline Python files to compile."
    for python_file in python_files:
        py_compile.compile(str(python_file), doraise=True)


def test_pipeline_report_output_folder_is_db_local() -> None:
    db_root = get_db_root()
    report_paths = sorted((db_root / "output").glob("db_pipeline_*.json"))
    for report_path in report_paths:
        report = read_json(report_path)
        assert report.get("scriptName") == "db_pipeline"
        for component in report.get("components", []):
            component_script_path = component.get("scriptPath", "")
            assert component_script_path.startswith("automation/factory/crud/db/postgres/"), component_script_path
        assert to_project_relative(report_path).startswith("automation/factory/crud/db/output/")
