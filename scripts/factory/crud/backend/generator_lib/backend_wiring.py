'''Application wiring patcher for generated pipeline backend CRUD.'''
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PatchResult:
    path: str
    status: str


def _append_once(content: str, block: str) -> tuple[str, bool]:
    normalized = block.strip()
    if normalized in content:
        return content, False
    return content.rstrip() + "\n\n" + normalized + "\n", True


def _insert_before(content: str, marker: str, block: str) -> tuple[str, bool]:
    normalized = block.strip()
    if normalized in content:
        return content, False
    if marker not in content:
        return _append_once(content, block)
    return content.replace(marker, normalized + "\n\n" + marker, 1), True


def _replace_once(content: str, old: str, new: str) -> tuple[str, bool]:
    if new in content:
        return content, False
    if old not in content:
        return content, False
    return content.replace(old, new, 1), True


def _patch_file(repo_root: Path, relative_path: str, patcher) -> PatchResult:
    path = repo_root / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Cannot patch missing file: {relative_path}")
    original = path.read_text(encoding="utf-8")
    patched, changed = patcher(original)
    if changed:
        path.write_text(patched, encoding="utf-8", newline="\n")
        return PatchResult(relative_path, "patched")
    return PatchResult(relative_path, "unchanged")


def patch_api_paths(repo_root: Path) -> PatchResult:
    block = '''
API_PATH_CCORE_PIPELINES = "/api/ccore/pipelines"
API_PATH_CCORE_PIPELINES_PREFIX = "/api/ccore/pipelines/"
API_PATH_CCORE_PIPELINE_STATUSES = "/api/ccore/pipeline-statuses"
'''
    return _patch_file(repo_root, "backend/src/api/api_paths.py", lambda content: _append_once(content, block))


def patch_service_factory(repo_root: Path) -> PatchResult:
    import_block = '''
from backend.src.ccore.pipelines.pipeline_repository import (
    CCorePipelineRepository,
    CCorePipelineStatusRepository,
)
from backend.src.ccore.pipelines.pipeline_service import (
    CCorePipelineService,
    CCorePipelineStatusService,
)
from backend.src.ccore.pipelines.pipeline_validator import CCorePipelineValidator
'''
    function_block = '''
def build_ccore_pipeline_repositories():
    postgres_database_manager = build_postgres_database_manager()

    return (
        CCorePipelineRepository(postgres_database_manager),
        CCorePipelineStatusRepository(postgres_database_manager),
    )


def build_ccore_pipeline_service():
    pipeline_repository, status_repository = build_ccore_pipeline_repositories()
    pipeline_validator = CCorePipelineValidator(status_repository=status_repository)

    return CCorePipelineService(
        pipeline_repository=pipeline_repository,
        pipeline_validator=pipeline_validator,
    )


def build_ccore_pipeline_status_service():
    _, status_repository = build_ccore_pipeline_repositories()

    return CCorePipelineStatusService(
        status_repository=status_repository,
    )
'''

    def patch(content: str) -> tuple[str, bool]:
        changed = False
        content, did_change = _insert_before(content, "from backend.src.ccore.tasks.task_repository import", import_block)
        changed = changed or did_change
        content, did_change = _insert_before(content, "def build_ai_speech_provider_mapper():", function_block)
        changed = changed or did_change
        return content, changed

    return _patch_file(repo_root, "backend/src/ccore/application/service_factory.py", patch)


def patch_service_container(repo_root: Path) -> PatchResult:
    def patch(content: str) -> tuple[str, bool]:
        changed = False
        old_import = "    build_ccore_metric_type_service,\n"
        new_import = "    build_ccore_metric_type_service,\n    build_ccore_pipeline_service,\n    build_ccore_pipeline_status_service,\n"
        content, did_change = _replace_once(content, old_import, new_import)
        changed = changed or did_change

        old_services = "        ccore_metric_type_service=build_ccore_metric_type_service(),\n"
        new_services = "        ccore_metric_type_service=build_ccore_metric_type_service(),\n        ccore_pipeline_service=build_ccore_pipeline_service(),\n        ccore_pipeline_status_service=build_ccore_pipeline_status_service(),\n"
        content, did_change = _replace_once(content, old_services, new_services)
        changed = changed or did_change
        return content, changed

    return _patch_file(repo_root, "backend/src/ccore/application/service_container.py", patch)


def patch_route_registry(repo_root: Path) -> PatchResult:
    import_block = '''
from src.api.api_paths import (
    API_PATH_CCORE_PIPELINES,
    API_PATH_CCORE_PIPELINES_PREFIX,
    API_PATH_CCORE_PIPELINE_STATUSES,
)
from backend.src.ccore.pipelines.pipeline_routes import (
    handle_create_ccore_pipeline,
    handle_delete_ccore_pipeline,
    handle_get_ccore_pipeline_by_id,
    handle_get_ccore_pipeline_statuses,
    handle_get_ccore_pipelines,
    handle_update_ccore_pipeline,
)
'''

    def patch(content: str) -> tuple[str, bool]:
        changed = False
        content, did_change = _insert_before(content, "def build_core_route_registry(", import_block)
        changed = changed or did_change

        replacements = [
            (
                '''                API_PATH_CCORE_METRIC_TYPES: lambda: handle_get_ccore_metric_types(
                    handler,
                    services.ccore_metric_type_service,
                ),
''',
                '''                API_PATH_CCORE_METRIC_TYPES: lambda: handle_get_ccore_metric_types(
                    handler,
                    services.ccore_metric_type_service,
                ),
                API_PATH_CCORE_PIPELINES: lambda: handle_get_ccore_pipelines(
                    handler,
                    services.ccore_pipeline_service,
                ),
                API_PATH_CCORE_PIPELINE_STATUSES: lambda: handle_get_ccore_pipeline_statuses(
                    handler,
                    services.ccore_pipeline_status_service,
                ),
''',
            ),
            (
                '''                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_get_ccore_metric_by_id(
                    handler,
                    services.ccore_metric_service,
                    path,
                ),
''',
                '''                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_get_ccore_metric_by_id(
                    handler,
                    services.ccore_metric_service,
                    path,
                ),
                API_PATH_CCORE_PIPELINES_PREFIX: lambda path: handle_get_ccore_pipeline_by_id(
                    handler,
                    services.ccore_pipeline_service,
                    path,
                ),
''',
            ),
            (
                '''                API_PATH_CCORE_METRICS: lambda: handle_create_ccore_metric(
                    handler,
                    services.ccore_metric_service,
                ),
''',
                '''                API_PATH_CCORE_METRICS: lambda: handle_create_ccore_metric(
                    handler,
                    services.ccore_metric_service,
                ),
                API_PATH_CCORE_PIPELINES: lambda: handle_create_ccore_pipeline(
                    handler,
                    services.ccore_pipeline_service,
                ),
''',
            ),
            (
                '''                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_update_ccore_metric(
                    handler,
                    services.ccore_metric_service,
                    path,
                ),
''',
                '''                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_update_ccore_metric(
                    handler,
                    services.ccore_metric_service,
                    path,
                ),
                API_PATH_CCORE_PIPELINES_PREFIX: lambda path: handle_update_ccore_pipeline(
                    handler,
                    services.ccore_pipeline_service,
                    path,
                ),
''',
            ),
            (
                '''                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_delete_ccore_metric(
                    handler,
                    services.ccore_metric_service,
                    path,
                ),
''',
                '''                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_delete_ccore_metric(
                    handler,
                    services.ccore_metric_service,
                    path,
                ),
                API_PATH_CCORE_PIPELINES_PREFIX: lambda path: handle_delete_ccore_pipeline(
                    handler,
                    services.ccore_pipeline_service,
                    path,
                ),
''',
            ),
        ]
        for old, new in replacements:
            content, did_change = _replace_once(content, old, new)
            changed = changed or did_change
        return content, changed

    return _patch_file(repo_root, "backend/src/api/route_registry.py", patch)


def patch_application_wiring(repo_root: Path) -> list[PatchResult]:
    return [
        patch_api_paths(repo_root),
        patch_service_factory(repo_root),
        patch_service_container(repo_root),
        patch_route_registry(repo_root),
    ]
