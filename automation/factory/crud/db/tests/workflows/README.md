# DB Metadata Workflow Tests

This folder contains the workflow-level regression suite for the DB metadata lifecycle.

The suite intentionally executes the real task scripts:

- `generate_table_metadata`
- `remove_metadata_tables`
- `validate_metadata`
- `db_pipeline`

It does not mock the metadata tasks and does not modify production code. During execution, the runner temporarily rewrites task config files and metadata folders, then restores the original repository state before exiting.

## Run

From the repository root:

```bash
python automation/factory/crud/db/tests/workflows/run_metadata_workflows.py
```

A JSON workflow report is written to:

```text
automation/factory/crud/db/tests/workflows/output/
```

## Covered workflows

1. Empty metadata → generate → validate → DB pipeline.
2. Generate → remove selected tables → validate → verify removal.
3. Generate → remove all → generate again → validate → DB pipeline.
4. Repeated generate/remove cycles followed by DB pipeline.
5. Negative cases:
   - removing a missing table
   - duplicate removal table names
   - empty removal list
   - empty architecture specification list
   - malformed architecture specification document

The runner stops immediately on the first unexpected failure.
