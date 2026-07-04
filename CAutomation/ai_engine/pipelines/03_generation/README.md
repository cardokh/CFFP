# 03 Generation

Generation produces implementation artifacts from the validated Context Package and the approved implementation plan.

Generation is split into specialized targets.

```text
03_generation/
├── db/
├── backend/
├── frontend/
├── testing/
└── deployment/
```

## Important Rule

Database, backend, frontend, testing, and deployment are generation targets, not lifecycle phases.

The lifecycle is:

```text
Context Engineering → Planning → Generation → Validation → Apply → Verification
```

## Shared Generation Inputs

All generators consume:

- Context Package
- implementation plan
- prior approved generation outputs when required

## Shared Generation Outputs

Each generator should produce:

- generated artifacts
- artifact manifest
- generation report
- provenance metadata
- validation hints

## Non-Goals

Generators must not:

- read arbitrary repository files
- apply changes directly
- skip validation
- modify outputs from other generators without an explicit plan
