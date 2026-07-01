# Engine

The engine contains the reusable automation logic for Epic Tracker.

It does not store application-specific requirements, metadata, generated artifacts, validation results, or reports.

Those belong under `applications/<application_name>/`.

The engine is organized into numbered stages. Each stage reads from the matching application stage folder, performs generic automation work, and writes results back to the application folder.

```text
epic_tracker/
  applications/
    pipeline_management_system/
      stages/
        04_database_generation/   # application-specific data

  engine/
    stages/
      04_database_generation/     # reusable generic logic
```
