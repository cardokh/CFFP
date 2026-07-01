# Pipeline Stages

This folder contains the generic reusable stages of the Epic Tracker automation pipeline.

A stage is a processing module. It reads application-specific input from `applications/<application_name>/stages/<stage_name>/`, performs its task, and writes application-specific output back to that application folder.

Stages should contain reusable logic, configuration, support utilities, tests, and task definitions. They should not contain application-specific requirements, metadata, generated files, or reports.

## Ordered stages

```text
01_requirements_constraints_analysis
02_solution_design
03_project_planning
04_database_generation
05_backend_generation
06_frontend_generation
07_testing
08_deployment
```

The numbering defines the intended execution order.
