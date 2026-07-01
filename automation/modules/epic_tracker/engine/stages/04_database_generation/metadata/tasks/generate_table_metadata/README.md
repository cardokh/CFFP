# Generate Table Metadata

This task generates generic database table metadata from Architecture Specification documents for the configured application stage.

The task has two stages:

1. **Generate Table Batches**
   - Reads the Architecture Specification documents listed in `config/generate_table_metadata.json`.
   - Resolves application artifacts from the configured `applicationStageRoot`.
   - Writes generated table batches under the application stage `generated/` folder.
   - Generates only the metadata explicitly described by each specification.

2. **Import Table Batches**
   - Reads the generated table batch files.
   - Validates the batch structure.
   - Rejects duplicate tables.
   - Validates foreign-key references.
   - Updates the application stage `metadata/modules/.../tables.json`.
   - Creates `schema.json` and `data.json` for every imported table.

The main script remains only an orchestrator:

```text
generate_generated_tables()
        ↓
import_generated_tables()
```

## Application Stage Input Structure

```text
applications/pipeline_management_system/stages/04_database_generation/
├── specifications/
│   └── architecture_specification_pipelines.json
├── generated/
│   └── generated_tables_pipelines.json
└── metadata/
```

The task config points to the application stage once, and all artifact paths are relative to that stage:

```json
{
    "applicationStageRoot": "applications/pipeline_management_system/stages/04_database_generation",
    "architectureSpecifications": [
        {
            "name": "pipelines",
            "path": "specifications/architecture_specification_pipelines.json",
            "generatedTablesPath": "generated/generated_tables_pipelines.json"
        }
    ],
    "targetMetadataRoot": "metadata"
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
python automation/modules/epic_tracker/engine/stages/04_database_generation/metadata/tasks/generate_table_metadata/generate_table_metadata.py
```

Expected result:

```text
Generating table metadata batches...
Generated 4 table(s) from specifications/architecture_specification_pipelines.json.
Importing generated table metadata batches...
4 tables found in generated/generated_tables_pipelines.json.
Imported 4 tables.
PASSED generate_table_metadata
```
