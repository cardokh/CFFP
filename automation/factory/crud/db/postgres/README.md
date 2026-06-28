# PostgreSQL Database Automation

## Purpose

The PostgreSQL database automation component validates database metadata, provisions the PostgreSQL schema, seeds data, and exports DB-only handoff context for downstream automation tasks.

This component is database-focused only. Backend and frontend naming decisions belong to their own blueprints.

## Main task entry point

Run the full DB task from the repository root:

```bash
python automation/factory/crud/db/db_task.py
```

## Components

### Add metadata task

* `add/add_task.py`
  * Reads `add/metadata/added_entities.json` as the selector for metadata to add.
  * Reads per-table source metadata from `add/metadata/entities/<table>/schema.json` and `add/metadata/entities/<table>/seed_data.json`.
  * Writes approved metadata into `metadata/entities/<table>/`.
  * Updates `metadata/entities.json`.
  * Runs validation and writes an add-task report.
  * Remains a manual metadata-preparation task, not a normal provisioning component.

### Validation

* `add/validator/validate_database_entity_definitions.py`
  * Verifies selected table metadata before provisioning.
  * Fails early if a selected table has a foreign key to an unselected table.

### DB handoff context

* `context/build_db_context.py`
  * Writes `output/master_context.json`.
  * Writes `output/tables/<table_name>.json` for each selected table.
  * Exports database facts only.

### PostgreSQL provisioning

* `create_schema.py`
  * Creates or updates the PostgreSQL schema from selected metadata.
* `seed_data.py`
  * Inserts and verifies seed data for selected metadata.

## Table selection

`metadata/entities.json` is the table selector. Only listed tables are validated, exported, created, and seeded.

## Recreation behavior

* `recreateDatabase: true` drops/recreates the application database and then creates only selected tables.
* `dropUnlistedTables: true` keeps the application database but removes public tables not listed in `metadata/entities.json`.
* `recreateExistingTables: true` drops/recreates selected tables.
* `recreateExistingTables: false` skips selected tables that already exist.

## Acceptance rule

The component passes when the configured task completes without errors and all component reports show `PASSED`. Expected table counts and seed row counts are derived from metadata, not hard-coded in this README.
