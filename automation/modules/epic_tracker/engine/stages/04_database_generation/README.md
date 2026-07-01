# Database Generation Stage

Database Generation is a generic reusable pipeline stage inspired by the existing `automation/factory/crud/db/` module.

It does not own application-specific metadata or generated database files. It reads from and writes to the active application folder.

## Generic task structure

```text
metadata/
  tasks/
    generate_table_metadata/
    remove_metadata_tables/
    validate_metadata/

implementations/
  postgres/
    tasks/
      build_database/
      insert_database/
      validate_database/
```

## Application data

For Pipeline Management System, stage-specific artifacts live under:

```text
applications/pipeline_management_system/stages/04_database_generation/
```

## Current rule

The existing `automation/factory/crud/db/` module remains unchanged. This stage is the new architectural target and will be evolved incrementally.
