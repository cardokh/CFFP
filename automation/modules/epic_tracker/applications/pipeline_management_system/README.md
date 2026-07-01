# Pipeline Management System

Pipeline Management System is the first application used to exercise the Epic Tracker automation pipeline.

Its folder structure mirrors the reusable pipeline stages. The application owns the artifacts; the stages own the generic processing logic.

```text
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

For example, the generic database generation logic lives in:

```text
../../stages/04_database_generation/
```

The Pipeline Management System database-specific requirements, metadata, outputs, validation results, and reports live in:

```text
stages/04_database_generation/
```
