# Pipelines

Pipelines are isolated stages in the AI-assisted software development lifecycle.

Each pipeline converts a defined set of inputs into a defined set of outputs. A pipeline must not read arbitrary repository content or depend on conversation history.

## Lifecycle Sequence

```text
00_shared
01_context_engineering
02_planning
03_project_management_publishing
04_generation
05_validation
06_apply
07_verification
```

## Generation Targets

`04_generation/` contains specialized generation targets:

```text
04_generation/
├── db/
├── backend/
├── frontend/
├── testing/
└── deployment/
```

These are not separate lifecycle phases. They are specialized generators that consume the validated context package and the frozen implementation plan.

## Shared Rule

Every stage must declare:

- consumed inputs
- produced outputs
- forbidden inputs
- validation rules
- provenance requirements

Every completed task must also pass against all available reference modules. For the current project this means at least:

- Pipeline Management
- User & Client Management

This keeps the platform deterministic, auditable, and reusable across projects and modules.
