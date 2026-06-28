# PostgreSQL Add Metadata Task

`add_task.py` prepares approved PostgreSQL entity metadata for the main DB task.

Run from the repository root:

```bash
python automation/factory/crud/db/postgres/add/add_task.py
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
metadata/entities/<table>/seed_data.json
```

The task copies selected metadata into:

```text
../metadata/entities/<table>/schema.json
../metadata/entities/<table>/seed_data.json
```

It also updates:

```text
../metadata/entities.json
```

## Boundary

This task handles database metadata only. It must not generate backend repositories, services, routes, DTOs, frontend artifacts, or naming decisions for downstream layers.
