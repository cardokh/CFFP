# Database CRUD Automation Task

This task is the database stage of the CRUD automation flow.

Run from repository root:

```bash
python automation/factory/crud/db/db_pipeline.py
```

The task delegates to the selected database engine from `config/db_pipeline.json`.
For PostgreSQL, metadata lives under `metadata/postgres`.

`metadata/postgres/entities.json` is the selector. Only entities listed there are validated, created, seeded, and exported into DB handoff context files.

## Scope boundary

The DB task produces database facts only. It must not decide backend repository names, service names, route names, DTO names, frontend names, or other downstream implementation concepts.

## DB handoff context

The task writes downstream handoff context files to:

* `output/master_context.json`
* `output/tables/<table_name>.json`

The master context summarizes the database engine, database name/schema, selected tables, and table context file locations.

Each table context file contains database facts only: table name, columns, PostgreSQL types, nullability, defaults, primary key, foreign keys, constraints, indexes when present, and seed row count.

## Selection and recreation semantics

* `recreateDatabase: true`
  * Drops and recreates the application database.
  * Creates and seeds only tables listed in `metadata/postgres/entities.json`.
* `recreateDatabase: false` and `dropUnlistedTables: true`
  * Keeps the database.
  * Removes existing public tables that are not listed in `metadata/postgres/entities.json`.
  * Creates and seeds only selected tables.
* `recreateExistingTables: true`
  * Drops and recreates selected tables before creation.
* `recreateExistingTables: false`
  * Skips selected tables that already exist.

## Dependency validation

Selected tables must include their selected foreign key dependencies. If a selected table references an unselected table, validation fails before PostgreSQL schema creation.


## PostgreSQL Add Task

`postgres/promote_db_metadata/promote_db_metadata.py` is the component-level task for preparing database entity metadata. It reads `postgres/promote_db_metadata/metadata/added_entities.json` as a selector list and reads per-table source metadata from `postgres/promote_db_metadata/metadata/entities/<table>/schema.json` and `postgres/promote_db_metadata/metadata/entities/<table>/seed_db_data.json`. It then copies those files into `metadata/postgres/entities/<table>/`, updates `metadata/postgres/entities.json`, runs metadata validation, and writes an add-task report under `postgres/promote_db_metadata/output/`. The add task is run manually when adding metadata and is not enabled as part of every normal `db_pipeline.py` run.

The add task remains database-focused only. It prepares PostgreSQL metadata and does not generate backend repositories, services, routes, DTOs, or frontend concepts.
