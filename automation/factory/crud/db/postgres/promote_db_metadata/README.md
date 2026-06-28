# PostgreSQL Add Metadata Task

`promote_db_metadata.py` prepares approved PostgreSQL entity metadata for the main DB task.

Run from the repository root:

```bash
python automation/factory/crud/db/postgres/promote_db_metadata/promote_db_metadata.py
```

## Metadata layout

`metadata/added_entities.json` is the selector:

```json
{
    "entities": [
        "example_table"
    ]
}
```

Each selected entity must have its own source metadata folder:

```text
metadata/entities/<table>/schema.json
metadata/entities/<table>/seed_db_data.json
```

The task copies selected metadata into:

```text
../metadata/entities/<table>/schema.json
../metadata/entities/<table>/seed_db_data.json
```

It also updates:

```text
../metadata/entities.json
```

## Boundary

This task handles database metadata only. It must not generate backend repositories, services, routes, DTOs, frontend artifacts, or naming decisions for downstream layers.
