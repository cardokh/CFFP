# Database CRUD Automation Task

This task is the database stage of the CRUD automation flow.

Run from repository root:

```bash
python automation/factory/crud/db/db_task.py
```

The task delegates to the selected database engine from `config/db_task.json`.
For PostgreSQL, metadata lives under `postgres/metadata`.

`postgres/metadata/entities.json` is the selector. Only entities listed there are loaded by the schema and seed scripts.
