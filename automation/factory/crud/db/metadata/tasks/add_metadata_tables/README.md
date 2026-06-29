# Add Metadata Tables

This task adds new table definitions to the generic database metadata model.

The feature is intentionally divided into two independent stages:

1. **Generate Table Batch**
   - Produces `input/generated_tables.json`.
   - Long term, this stage will read project requirements and decide which metadata tables are required.
   - For now, it runs in manual placeholder mode and does not generate anything.
   - The expected placeholder message is: `Generation step skipped (manual mode).`

2. **Import Table Batch**
   - Reads `input/generated_tables.json`.
   - Validates the batch.
   - Rejects duplicate tables.
   - Validates foreign-key references.
   - Updates `metadata/modules/.../tables.json`.
   - Creates `schema.json` and `data.json` for every imported table.

The main script is only an orchestrator:

```text
generate_generated_tables()
        ↓
import_generated_tables()
```

The long-term goal is to replace Stage 1 with AI-assisted generation without changing Stage 2. Stage 2 must remain deterministic and must not perform AI generation.

## Current placeholder batch

The current `generated_tables.json` contains an empty batch:

```json
{
    "tables": []
}
```

Running the task should therefore pass without changing metadata:

```text
Generating table batch...
Generation step skipped (manual mode).
Importing generated table batch...
0 tables found.
Nothing to import.
PASSED
```
