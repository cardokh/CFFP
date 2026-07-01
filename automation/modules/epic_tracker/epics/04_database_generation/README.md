# 04 Database Generation

## Purpose

`04_database_generation` is the generic database generation stage.

It is the future replacement/evolution target for the existing `automation/factory/crud/db/` module, but the existing DB module remains untouched.

The purpose of this folder is to hold reusable database-generation tasks. It does not own application-specific requirements, metadata, generated SQL, reports, or validation results.

## Core principle

Application-specific data belongs under `applications/<application_name>/`.

Generic database-generation logic belongs here.

```text
applications/pipeline_management_system/
  requirements/
  metadata/
  database/
  reports/

epics/04_database_generation/
  metadata/tasks/
  implementations/postgres/tasks/
```

The database generation stage reads application-specific input from the active application folder, performs generic tasks, and writes application-specific output back to the active application folder.

## Current task structure

```text
04_database_generation/
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

## Metadata tasks

### `generate_table_metadata`

Reads database requirements for the active application and generates table metadata for that application.

### `remove_metadata_tables`

Removes generated table metadata for the active application when regeneration or cleanup is required.

### `validate_metadata`

Validates the generated table metadata before implementation-specific database tasks are allowed to run.

## PostgreSQL implementation tasks

### `build_database`

Builds PostgreSQL database artifacts from validated application metadata.

### `insert_database`

Generates or executes PostgreSQL insert/seed-data artifacts for the active application.

### `validate_database`

Validates the generated PostgreSQL database artifacts before the pipeline continues.

## Relationship to the existing DB module

The existing module remains the practical reference:

```text
automation/factory/crud/db/
```

This folder should evolve toward the same practical style: focused tasks, implementation-specific folders, support code, tests, and clear validation.

## Scope of this iteration

This iteration only introduces the database-generation task structure.

No business logic is added.
No existing DB files are modified.
No code is copied from the existing DB module yet.
