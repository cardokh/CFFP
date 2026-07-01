# Database Generation Epic - User Stories

## US-DB-001 - Generate Pipeline Foundation Metadata

### User Story

As the Automation Factory,
I want to read an approved architecture specification for pipeline foundation tables,
so that deterministic table metadata can be generated for the database-only pipeline foundation scope.

### Current Scope

This story covers exactly these four tables:

```text
pipeline_statuses
pipeline_execution_modes
pipeline_trigger_types
pipelines
```

### Source Specification

```text
docs/specifications/ccore/automation/architecture_specification_pipelines.json
```

### Main Production Task

```text
metadata/tasks/generate_table_metadata/generate_table_metadata.py
```

### Related Tasks

```text
metadata/tasks/validate_metadata/validate_metadata.py
metadata/tasks/remove_metadata_tables/remove_metadata_tables.py
run_db_tasks.py
```

### Acceptance Criteria

- The source architecture specification is stored as a DB module documentation/specification artifact.
- The generate-table-metadata task reads the approved specification from the `docs/specifications` folder.
- Generated metadata remains deterministic for the four-table scope.
- The story does not introduce unrelated database tables or broader CRUD generation behavior.

## Future User Stories

Future stories should remain small and independently testable. Examples:

```text
US-DB-002 - Remove selected metadata tables
US-DB-003 - Validate metadata repository consistency
US-DB-004 - Run the DB task group from generated metadata
US-DB-005 - Build PostgreSQL tables from metadata
US-DB-006 - Insert deterministic seed data
US-DB-007 - Add task-level validation tasks for DB generation behavior
```
