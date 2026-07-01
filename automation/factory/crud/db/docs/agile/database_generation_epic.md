# Database Generation Epic

## Epic Statement

As the CFFP Automation Factory, we need a deterministic database generation capability so that database metadata, database structures, and seed data can be generated, validated, recreated, and regression tested from approved source specifications.

## Scope

This epic represents the current `db` module under:

```text
automation/factory/crud/db/
```

The physical folder remains named `db` to keep imports, configuration paths, scripts, and tests stable. Conceptually, this module is the implementation of the **Database Generation Epic**.

## Current User Story Focus

The current user story is intentionally small and limited to the pipeline foundation tables only.

```text
Generate pipeline foundation metadata from an approved architecture specification.
```

The current source specification defines exactly four database tables:

```text
pipeline_statuses
pipeline_execution_modes
pipeline_trigger_types
pipelines
```

## Divide-and-Conquer Rule

This epic must evolve incrementally. Each user story should be small enough to validate independently and should not expand the module scope unnecessarily.

A user story may introduce or validate a specific capability, for example:

```text
- generate metadata for a small table group
- remove selected metadata tables
- validate metadata consistency
- run the DB task group
- build PostgreSQL tables from validated metadata
- insert deterministic seed data
```

## Architectural Boundary

Higher-level CFFP pipelines will eventually be created and executed from the web UI. Those pipelines may contain DB tasks, validation tasks, or other factory tasks.

The DB module itself should therefore expose deterministic tasks and task runners, not become a UI-specific or monolithic pipeline implementation.
