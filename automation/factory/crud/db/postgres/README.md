# Database Automation Task

**Status:** FROZEN

## Purpose

The Database Automation task is responsible for generating, validating, and provisioning the PostgreSQL database from approved metadata.

This task is the first stage of the CRUD Automation Pipeline and serves as the foundation for all subsequent CRUD generation tasks.

---

## Components

### Metadata Generation

* `add_database_schema_entity.py`

  * Updates the PostgreSQL schema metadata.

* `add_database_seed_entity.py`

  * Updates the PostgreSQL seed metadata.

### Validation

* `validate_database_entity_definitions.py`

  * Verifies that all database entity definitions are valid before database provisioning.
  * Acts as the acceptance gate for the Database Automation task.

### PostgreSQL Provisioning

* `postgres_create_schema.py`

  * Creates or updates the PostgreSQL schema from the approved metadata.

* `postgres_seed_data.py`

  * Inserts and verifies the seed data.

---

## Execution

Run the following commands from the repository root in the specified order:

```bash
python automation/factory/crud/db/postgres/add_database_entity/add_database_schema_entity.py

python automation/factory/crud/db/postgres/add_database_entity/add_database_seed_entity.py

python automation/factory/crud/db/postgres/add_database_entity/validate_database_entity_definitions.py

python automation/factory/crud/db/postgres/postgres_create_schema.py

python automation/factory/crud/db/postgres/postgres_seed_data.py
```

---

## Expected Result

Successful execution should produce the following results:

* Database schema metadata updated successfully.
* Database seed metadata updated successfully.
* Database entity definitions validated successfully.
* Validation reports **8 checks passed**.
* PostgreSQL schema created successfully.
* PostgreSQL contains **16 managed tables**.
* PostgreSQL contains **49 seed rows**.

---

## Acceptance Test

The Database Automation task is considered complete when the following workflow succeeds:

1. Delete the five pipeline tables from PostgreSQL.
2. Execute all scripts in the order specified above.
3. Verify that:

   * The five pipeline tables are recreated.
   * `validate_database_entity_definitions.py` reports **8 checks passed**.
   * `postgres_create_schema.py` reports **16 managed tables**.
   * `postgres_seed_data.py` reports **49 seed rows**.
   * No errors occur during execution.

---

## Notes

* Always execute the validation step before provisioning the PostgreSQL database.
* The validation script is the acceptance gate for the Database Automation task.
* Once accepted, this task should remain **frozen** unless a genuine defect is identified.
