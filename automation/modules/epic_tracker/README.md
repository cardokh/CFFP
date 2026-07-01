# Epic Tracker

Epic Tracker is the automation module that moves an application through a structured software generation lifecycle.

This module separates application-specific data from reusable automation logic.

## Root structure

```text
epic_tracker/
  applications/
  engine/
    stages/
  docs/
  README.md
```

## Applications

`applications/` contains the projects being processed by Epic Tracker.

Each application owns its own inputs, metadata, outputs, validation results, and reports.

Example:

```text
applications/
  pipeline_management_system/
    stages/
      01_requirements_constraints_analysis/
      02_solution_design/
      03_project_planning/
      04_database_generation/
      05_backend_generation/
      06_frontend_generation/
      07_testing/
      08_deployment/
```

## Engine

`engine/stages/` contains the reusable automation logic.

The engine reads from an application stage, executes the matching generic stage logic, and writes results back to the application stage.

Example:

```text
engine/
  stages/
    01_requirements_constraints_analysis/
    02_solution_design/
    03_project_planning/
    04_database_generation/
    05_backend_generation/
    06_frontend_generation/
    07_testing/
    08_deployment/
```

## Current architectural rule

The application folder contains data.

The engine folder contains reusable behaviour.

Module-level `reports/` and `validation/` folders are intentionally not used for now. Reports and validation results belong to the application stage that produced them.
