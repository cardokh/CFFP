# Architecture

Epic Tracker is organized around a separation between application state and reusable pipeline stages.

```text
epic_tracker/
  applications/
    pipeline_management_system/
      stages/
        04_database_generation/
          requirements/
          metadata/
          output/
          validation/
          reports/

  stages/
    04_database_generation/
      metadata/
        tasks/
      implementations/
        postgres/
          tasks/
```

The application folder owns data. The stage folder owns reusable processing logic.
