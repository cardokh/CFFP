# Epic Tracker

## Purpose

The Epic Tracker is a reusable CFFP automation module for managing work using standard Agile terminology. It defines how epics, user stories, implementation tasks, test suites, and test cases are documented, validated, reported, and connected to factory implementations.

This module is intentionally implementation-agnostic. It does not generate code, execute pipelines, migrate the existing `automation/factory/crud/db/` module, or introduce business logic.

## Relationship to the Existing Factory

The existing Factory remains unchanged. The Epic Tracker is now placed under `automation/modules/` to make it clear that it is a reusable automation module, not a factory implementation.

```text
automation/
├── factory/
│   └── crud/
│       └── db/
└── modules/
    └── epic_tracker/
```

The Epic Tracker may describe or reference existing implementations, such as the Database Generation Epic, but it does not move, rename, or modify them.

## Epic Interaction Model

The intended long-term architecture is a pipeline of Agile capabilities:

```text
Requirements Analysis
        ↓
Epic Planning
        ↓
User Story Management
        ↓
Implementation Task Management
        ↓
Test Planning
        ↓
Validation and Reporting
        ↓
Factory Execution Integration
```

Each step produces structured artifacts that can become inputs to later steps. The same blueprint should be reusable for database, backend, frontend, testing, documentation, deployment, and future application-specific pipelines.

## Folder Structure

```text
automation/modules/epic_tracker/
├── README.md
├── applications/
│   └── pipeline_management_system/
├── docs/
│   ├── README.md
│   ├── architecture/
│   ├── contracts/
│   └── terminology/
├── epics/
│   ├── requirements_analysis/
│   ├── epic_planning/
│   ├── user_story_management/
│   ├── implementation_task_management/
│   ├── test_planning/
│   ├── validation_and_reporting/
│   ├── factory_execution_integration/
│   └── database_generation/
├── reports/
└── validation/
```

## Contracts

Contracts are currently documentation-only and live under `docs/contracts/`.

They should stay there until they become executable artifacts such as JSON schemas, Python models, or validation rules. If that happens, a future iteration may promote them to a top-level `contracts/` folder.

## Applications

Applications are real or planned systems that use the Epic Tracker architecture. The first application is the Pipeline Management System.

Application-specific epics, outputs, validation reports, and generated artifacts should live inside the relevant application folder once implementation begins.

## Validation and Reports

The top-level `validation/` and `reports/` folders define module-wide conventions for the Epic Tracker.

Application-specific validation output and reports may later be added under each application, for example:

```text
applications/
└── pipeline_management_system/
    ├── epics/
    ├── user_stories/
    ├── implementation_tasks/
    ├── test_suites/
    └── reports/
```

## Current Iteration Boundary

This iteration only reorganizes the architectural folder structure.

Allowed in this iteration:

- Move `epic_tracker` under `automation/modules/`.
- Move documentation-only contracts under `docs/contracts/`.
- Rename `reference_applications/` to `applications/`.
- Keep module-level `validation/` and `reports/`.
- Update README documentation to match the new structure.

Not allowed in this iteration:

- Business logic
- Code generation
- Runtime orchestration
- Database migration
- Changes to `automation/factory/crud/db/`
- Refactoring existing Factory modules
