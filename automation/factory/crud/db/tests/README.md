# DB Pipeline Tests

These tests harden the DB Pipeline by checking its contracts, structure, and deterministic DB metadata outputs.

They are **pytest contract tests**. They are not PostgreSQL integration tests and they do not require a running PostgreSQL instance.

## What the tests validate

### `contracts/`

Contract tests for DB Pipeline configuration, PostgreSQL task folder structure, and metadata files.

- `test_db_pipeline_config_contract.py`
  - verifies `config/db_pipeline.json`
  - verifies the DB task execution order
  - verifies component names
  - verifies configured script paths exist
  - verifies the DB task orchestrator does not execute backend, frontend, or child pipeline scripts
  - verifies DB Python files compile

- `test_postgres_folder_structure_contract.py`
  - verifies `postgres/` only contains valid DB task folders and shared metadata
  - rejects obsolete folders such as `create_table`, `add`, and `context`
  - verifies each DB task folder has its script and config file

- `test_metadata_contracts.py`
  - validates `generate_table_metadata/metadata/new_tables.json`
  - validates promoted metadata under `promote_db_metadata/metadata/`
  - validates active metadata under `postgres/metadata/`
  - validates required `schema.json` and `seed_data.json` files
  - validates foreign key dependencies are included in selected metadata

### `tasks/`

Task-level contract tests for individual DB Pipeline tasks.

- `test_build_db_context_contract.py`
  - verifies `build_db_context` writes to its own task output folder
  - verifies the existing `master_context.json` matches active DB metadata
  - verifies generated table context files stay database-only

### `support/`

Shared helper code used by the tests. These files are not tests.

- `db_test_paths.py`
  - finds the repository root and DB Pipeline paths

- `db_json_validation.py`
  - shared JSON loading and metadata contract assertions

## How to run

From the repository root:

```bash
python -m pytest automation/factory/crud/db/tests
```

Or use the DB-local runner:

```bash
python automation/factory/crud/db/tests/run_db_tests.py
```

## Expected result

All tests should pass without starting PostgreSQL.

Example:

```text
13 passed
```

## Test type summary

| Test group | Type | Requires PostgreSQL | Purpose |
|---|---|---:|---|
| `contracts/` | Contract tests | No | Validate DB Pipeline configuration, folder boundaries, and metadata contracts |
| `tasks/` | Task-level contract tests | No | Validate deterministic task output contracts |
| `support/` | Helpers | No | Shared path and JSON validation utilities |
