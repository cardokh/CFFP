# Generate Table Metadata

This task generates generic database table metadata from explicit Architecture Specification documents.

The task has two stages:

1. **Generate Table Batches**
   - Reads the Architecture Specification documents listed in `config/generate_table_metadata.json`.
   - Writes generated table batches under `input/generated/...`.
   - Generates only the metadata explicitly described by each specification.

2. **Import Table Batches**
   - Reads the generated table batch files.
   - Validates the batch structure.
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

## Input Structure

Current input structure:

```text
input/
├── specifications/
│   └── ccore/
│       └── automation/
│           └── architecture_specification_pipelines.json
└── generated/
    └── ccore/
        └── automation/
            └── generated_tables_pipelines.json
```

The task config contains the list of architecture specifications to process:

```json
{
    "architectureSpecifications": [
        {
            "name": "pipelines",
            "path": "../../../docs/specifications/ccore/automation/architecture_specification_pipelines.json",
            "generatedTablesPath": "input/generated/ccore/automation/generated_tables_pipelines.json"
        }
    ]
}
```

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
python automation/factory/crud/db/metadata/tasks/generate_table_metadata/generate_table_metadata.py
```

Expected result:

```text
Generating table metadata batches...
Generated 4 table(s) from ../../../docs/specifications/ccore/automation/architecture_specification_pipelines.json.
Importing generated table metadata batches...
4 tables found in input/generated/ccore/automation/generated_tables_pipelines.json.
Imported 4 tables.
PASSED generate_table_metadata
```
