# DB Task Validation Strategy

## Principle

Every production task should eventually have a corresponding validation task that tests it thoroughly and deterministically.

The goal is not only to test workflows, but to test each task in and out before those tasks are composed into larger UI-created pipelines.

## Production Task to Validation Task Mapping

```text
generate_table_metadata     -> test_generate_table_metadata
remove_metadata_tables      -> test_remove_metadata_tables
validate_metadata           -> test_validate_metadata
run_db_tasks                -> test_run_db_tasks
build_database              -> test_build_database
insert_data                 -> test_insert_data
```

## Validation Task Expectations

Each validation task should:

```text
- execute the real production task
- prepare deterministic test input
- verify the produced output
- verify repository consistency after success or failure
- stop immediately on failure
- produce clear logs and reports
- avoid modifying production code
```

## UI Direction

The current command-line execution path is temporary. In the long-term CFFP architecture, the web UI will create and run higher-level pipelines. Those pipelines will compose production tasks and validation tasks as needed.

Therefore, validation logic should remain modular and task-oriented rather than being hidden inside one large end-to-end script.
