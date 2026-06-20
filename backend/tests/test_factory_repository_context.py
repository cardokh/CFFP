"""
Automation Factory repository context provider tests.

Responsibilities:
- Verify deterministic, configuration-driven repository context collection.
- Verify default exclusions for generated/cache/dependency/VCS content.
- Verify prompt and report representations for future Factory execution flows.
"""

from src.core.factory.repository_context import (
    RepositoryContextProvider,
    build_repository_context_config,
)


def test_collect_context_returns_matching_repository_files(tmp_path) -> None:
    project_root = tmp_path
    source_file = project_root / "backend" / "src" / "core" / "factory" / "run_factory.py"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("print('factory')\n", encoding="utf-8")

    ignored_file = project_root / "frontend" / "static" / "index.html"
    ignored_file.parent.mkdir(parents=True)
    ignored_file.write_text("<html></html>\n", encoding="utf-8")

    config = build_repository_context_config(
        {
            "enabled": True,
            "include_patterns": ["backend/src/core/factory/*.py"],
            "max_files": 10,
            "max_file_characters": 1000,
        }
    )

    context_package = RepositoryContextProvider(project_root).collect_context(config)

    assert context_package.enabled is True
    assert len(context_package.files) == 1
    assert context_package.files[0].path == "backend/src/core/factory/run_factory.py"
    assert "factory" in context_package.files[0].content


def test_collect_context_excludes_default_generated_and_cache_paths(tmp_path) -> None:
    project_root = tmp_path
    generated_report = project_root / "backend" / "src" / "core" / "factory" / "reports" / "report.json"
    generated_report.parent.mkdir(parents=True)
    generated_report.write_text("{}", encoding="utf-8")

    cache_file = project_root / "backend" / "src" / "core" / "factory" / "__pycache__" / "x.pyc"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_bytes(b"cache")

    included_file = project_root / "backend" / "src" / "core" / "factory" / "models.py"
    included_file.parent.mkdir(parents=True, exist_ok=True)
    included_file.write_text("class Model: pass\n", encoding="utf-8")

    config = build_repository_context_config(
        {
            "enabled": True,
            "include_patterns": ["backend/src/core/factory/**"],
            "max_files": 10,
            "max_file_characters": 1000,
        }
    )

    context_package = RepositoryContextProvider(project_root).collect_context(config)

    included_paths = [context_file.path for context_file in context_package.files]

    assert included_paths == ["backend/src/core/factory/models.py"]
    assert "backend/src/core/factory/reports/report.json" in context_package.skipped_files
    assert "backend/src/core/factory/__pycache__/x.pyc" in context_package.skipped_files


def test_collect_context_truncates_large_files(tmp_path) -> None:
    source_file = tmp_path / "backend" / "src" / "core" / "factory" / "large.py"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("abcdef", encoding="utf-8")

    config = build_repository_context_config(
        {
            "enabled": True,
            "include_patterns": ["backend/src/core/factory/*.py"],
            "max_files": 10,
            "max_file_characters": 3,
        }
    )

    context_package = RepositoryContextProvider(tmp_path).collect_context(config)

    assert context_package.files[0].content == "abc"
    assert context_package.files[0].truncated is True


def test_context_package_exposes_prompt_text_and_report_snapshot(tmp_path) -> None:
    source_file = tmp_path / "backend" / "src" / "core" / "factory" / "models.py"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("class FactoryConfig: pass\n", encoding="utf-8")

    config = build_repository_context_config(
        {
            "enabled": True,
            "include_patterns": ["backend/src/core/factory/*.py"],
            "max_files": 10,
            "max_file_characters": 1000,
        }
    )

    context_package = RepositoryContextProvider(tmp_path).collect_context(config)

    prompt_text = context_package.to_prompt_text()
    report_snapshot = context_package.to_report_snapshot()

    assert "Repository Context" in prompt_text
    assert "--- FILE: backend/src/core/factory/models.py ---" in prompt_text
    assert "class FactoryConfig" in prompt_text
    assert report_snapshot["enabled"] is True
    assert report_snapshot["file_count"] == 1
    assert report_snapshot["files"][0]["path"] == "backend/src/core/factory/models.py"
