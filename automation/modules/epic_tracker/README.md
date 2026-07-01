# Epic Tracker Module

This module is the architectural foundation for an end-to-end AI-assisted software delivery lifecycle.

The current name remains `epic_tracker` at folder level, but the architectural responsibility is broader than simple Agile tracking. The module models a complete pipeline that starts with requirements and constraints and ends with deployment-ready software artifacts.

## Lifecycle

```text
01 Requirements & Constraints Analysis
        ↓
02 Solution Design
        ↓
03 Project Planning / Epic Tracker
        ↓
04 Database Generation
        ↓
05 Backend Generation
        ↓
06 Frontend Generation
        ↓
07 Testing
        ↓
08 Deployment
```

## Architectural principle

Every epic produces a validated package that becomes the input to the next epic.

The output of each epic must be complete enough for the next epic to execute without asking additional questions. If critical information is missing, the pipeline stops at the validation gate.

## Epic 1 as the foundation gate

`01_requirements_constraints_analysis` is the main human/client clarification stage.

It must capture everything downstream epics need, including business goals, functional requirements, non-functional requirements, technical constraints, mandatory technologies, forbidden technologies, deployment constraints, repositories, acceptance criteria, assumptions, and open questions.

After Epic 1, the system should rely primarily on structured metadata, validated contracts, reports, and automation.

## Relationship to the existing Factory

The existing `automation/factory/` implementation remains unchanged.

This module does not migrate, refactor, or rewrite the current factory code in this iteration. Existing factory components may later become reference implementations or execution capabilities for the corresponding lifecycle epics.

For example, the existing database pipeline may later inform `04_database_generation`.

## Applications

Applications live under `applications/`.

The first planned application is the Pipeline Management System. It is not implemented in this iteration.

## Documentation

Module-level documentation lives under `docs/`.

Contracts are currently documentation-only and live under `docs/contracts/`. They may become executable schemas or models in a future implementation iteration.

## Reports and validation

Module-level reporting and validation concepts live under `reports/` and `validation/`.

Epic-specific reports and validation material live inside each numbered epic.

## Scope of this iteration

This iteration is architectural only.

It introduces the ordered eight-epic lifecycle and updates documentation accordingly. It does not add business logic, code generation, migrations, runtime orchestration, or changes to the existing factory/database implementation.
