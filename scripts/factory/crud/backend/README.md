# Backend CRUD Automation — CCore Pipelines

This task generates the backend CRUD slice for `ccore_pipelines`.

## What this automation creates

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

It also patches the application wiring files so the new API routes are reachable:

- `backend/src/api/api_paths.py`
- `backend/src/api/route_registry.py`
- `backend/src/ccore/application/service_factory.py`
- `backend/src/ccore/application/service_container.py`

## Run

From the repository root:

```bash
python scripts/factory/crud/backend/generate_backend.py
```

## Validate

From the repository root:

```bash
python scripts/factory/crud/backend/validation/validate_generate_backend.py
```

The validator runs generation in a temporary copied repository, verifies expected generated files, verifies patch targets, and compiles the generated Python files.

## Scope

This task is intentionally limited to Backend CRUD Automation for CCore pipelines. It does not modify the database task, frontend, orchestration, Gemini provider integration, or navigation.
