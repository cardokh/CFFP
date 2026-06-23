# Golden Reference — CCore Task CRUD

## Purpose

The Organization CRUD generator must follow an existing, working CCore CRUD implementation instead of inventing architecture.

The golden reference for this task is the CCore Task module.

## Backend Golden Reference

The backend reference module is:

```text
backend/src/ccore/tasks
```

Reference files:

```text
backend/src/ccore/tasks/__init__.py
backend/src/ccore/tasks/task.py
backend/src/ccore/tasks/task_constants.py
backend/src/ccore/tasks/task_contracts.py
backend/src/ccore/tasks/task_mapper.py
backend/src/ccore/tasks/task_messages.py
backend/src/ccore/tasks/task_repository.py
backend/src/ccore/tasks/task_repository_contract.py
backend/src/ccore/tasks/task_routes.py
backend/src/ccore/tasks/task_service.py
backend/src/ccore/tasks/task_validator.py
```

Task execution files are useful as runtime examples but are not the primary CRUD reference unless the Organization spec explicitly requires execution behavior:

```text
backend/src/ccore/tasks/task_execution.py
backend/src/ccore/tasks/task_execution_constants.py
backend/src/ccore/tasks/task_execution_mapper.py
backend/src/ccore/tasks/task_execution_repository.py
backend/src/ccore/tasks/task_execution_repository_contract.py
backend/src/ccore/tasks/task_execution_runner.py
```

## Frontend Golden Reference

The frontend reference pages are:

```text
frontend/static/desktop/protected/ccore/tasks.html
frontend/static/desktop/protected/ccore/task-details.html
frontend/static/desktop/protected/ccore/js/tasks.js
frontend/static/desktop/protected/ccore/js/task-details.js
frontend/static/desktop/protected/ccore/css/tasks.css
frontend/static/desktop/protected/ccore/css/task-details.css
```

## Patterns To Replicate

The generated Organization module must replicate these patterns from the Task module:

- vertical slice folder structure,
- dataclass-style domain object,
- constants file,
- messages file,
- explicit request contracts/parser classes,
- mapper layer,
- validator layer,
- repository protocol,
- concrete repository,
- service layer,
- route handler layer,
- custom route registry style,
- canonical API response format,
- frontend list/details page pattern,
- vanilla JavaScript controller pattern,
- existing shared CSS conventions.

## Patterns Not To Invent

The generator must not introduce:

- Pydantic schemas,
- async database sessions,
- SQLAlchemy,
- Tailwind,
- React/Vue/Angular,
- a different route registration style,
- a different API response style,
- a different frontend layout pattern.

## Repository Inspection Requirement

This document is not a replacement for repository inspection.

Before generation, the pipeline must read the actual golden reference files from the current repository and summarize the current patterns.

If this document conflicts with inspected repository facts, the pipeline must stop and report the conflict.

## Golden Reference Protection

Generated Organization artifacts must not modify files under:

```text
backend/src/ccore/tasks
frontend/static/desktop/protected/ccore/tasks.html
frontend/static/desktop/protected/ccore/task-details.html
frontend/static/desktop/protected/ccore/js/tasks.js
frontend/static/desktop/protected/ccore/js/task-details.js
frontend/static/desktop/protected/ccore/css/tasks.css
frontend/static/desktop/protected/ccore/css/task-details.css
```

Those files are reference inputs only.
