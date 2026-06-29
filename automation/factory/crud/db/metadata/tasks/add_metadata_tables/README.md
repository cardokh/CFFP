# Add Metadata Tables

This task adds new table definitions to the generic database metadata model.

The feature is divided into two independent stages:

1. **Generate Table Batch**
   - Reads `input/architecture_specification.json`.
   - Produces `input/generated_tables.json`.
   - Converts explicit architectural intent into generic database table metadata.
   - The generator is additive: it generates only the tables described by the specification.

2. **Import Table Batch**
   - Reads `input/generated_tables.json`.
   - Validates the batch.
   - Rejects duplicate tables.
   - Validates foreign-key references.
   - Updates `metadata/modules/.../tables.json`.
   - Creates `schema.json` and `data.json` for every imported table.

The main script remains only an orchestrator:

```text
generate_generated_tables()
        ↓
import_generated_tables()
```

Stage 1 is responsible for translating an Architecture Specification into a generated table batch.
Stage 2 remains deterministic and only imports the generated batch.

## Current Architecture Specification Scope

The first architecture specification contains the agreed pipeline foundation only:

Reference tables:

- `pipeline_statuses`
- `pipeline_execution_modes`
- `pipeline_trigger_types`

Entity tables:

- `pipelines`

Tasks, relationship tables, nested pipelines, pipeline types, and runtime execution tables are intentionally excluded from this iteration.

## Run

From the repository root:

```bash
python automation/factory/crud/db/metadata/tasks/add_metadata_tables/add_metadata_tables.py
```

Expected result:

```text
Generating table batch...
Generated 4 table(s) from architecture specification.
Importing generated table batch...
4 tables found.
Imported 4 tables.
PASSED add_metadata_tables
```
