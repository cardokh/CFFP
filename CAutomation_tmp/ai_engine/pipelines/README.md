# Pipelines

Pipelines are isolated stages in the AI-assisted software development lifecycle.

Each pipeline converts a defined set of inputs into a defined set of outputs. A pipeline must not read arbitrary repository content or depend on conversation history.

## Lifecycle Sequence

```text
00_shared
01_context_engineering
02_planning
03_generation
04_validation
05_apply
06_verification
```

## Generation Targets

`03_generation/` contains specialized generation targets:

```text
03_generation/
├── db/
├── backend/
├── frontend/
├── testing/
└── deployment/
```

These are not separate lifecycle phases. They are specialized generators that consume the validated context package and the implementation plan.

## Shared Rule

Every stage must declare:

- consumed inputs
- produced outputs
- forbidden inputs
- validation rules
- provenance requirements

This keeps the platform deterministic, auditable, and reusable across projects.
