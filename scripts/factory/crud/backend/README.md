# Backend CRUD Automation — CCore Pipelines

This task generates and validates the backend CRUD slice for `ccore_pipelines`.

## Scope

This automation is intentionally limited to Backend CRUD Automation for CCore pipelines. It does not redesign the database task, frontend, navigation, orchestration, Gemini provider integration, or AI provider integration.

## Script architecture

The executable scripts follow the shared CFFP scripting blueprint:

- script classes extend `scripts.shared.base_script.BaseScript`
- each script reads from its own `config/` folder
- each script writes reports to its own `output/` folder through `BaseScript.write_json_report`
- repository root resolution comes from the shared scripting infrastructure
- terminal output is intentionally concise

## What generation creates

Running `generate_backend.py` creates:

- `backend/src/ccore/pipelines/__init__.py`
- `backend/src/ccore/pipelines/pipeline.py`
- `backend/src/ccore/pipelines/pipeline_constants.py`
- `backend/src/ccore/pipelines/pipeline_messages.py`
- `backend/src/ccore/pipelines/pipeline_contracts.py`
- `backend/src/ccore/pipelines/pipeline_mapper.py`
- `backend/src/ccore/pipelines/pipeline_validator.py`
- `backend/src/ccore/pipelines/pipeline_repository_contract.py`
- `backend/src/ccore/pipelines/pipeline_repository.py`
- `backend/src/ccore/pipelines/pipeline_service.py`
- `backend/src/ccore/pipelines/pipeline_routes.py`

It also patches application wiring files so the pipeline API routes are reachable:

- `backend/src/api/api_paths.py`
- `backend/src/api/route_registry.py`
- `backend/src/ccore/application/service_factory.py`
- `backend/src/ccore/application/service_container.py`

## Run

From the repository root:

```bash
python scripts/factory/crud/backend/generate_backend.py
```

The script writes its report to:

```text
scripts/factory/crud/backend/output/
```

## Validate

From the repository root:

```bash
python scripts/factory/crud/backend/validation/validate_generate_backend.py
```

The validator runs generation in a temporary copied repository, verifies expected generated files, verifies patch targets, and compiles the generated Python files. The temporary repository is deleted automatically when validation finishes.

The script writes its report to:

```text
scripts/factory/crud/backend/validation/output/
```
