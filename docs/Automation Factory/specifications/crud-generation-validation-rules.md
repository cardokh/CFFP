# CRUD Generation Validation Rules

## Purpose

These rules define what must be checked before AI-generated CRUD artifacts are applied to the repository.

The Automation Factory must stage output, validate it, and only apply it if validation succeeds.

## Specification Completeness Rules

Fail if any of the following remain in the selected specification:

- `REQUIRED`
- `REQUIRED_USER_DECISION`
- `UNKNOWN`
- `TODO`
- empty mandatory strings
- unresolved conditional values such as `REQUIRED_IF_addMenuEntry_TRUE`

## Technology Decision Rules

Fail if generated artifacts use unapproved technologies.

For the current inspected baseline, generated Organization CRUD must not introduce these unless an explicit migration decision exists:

- Pydantic v2.
- Async database sessions.
- SQLAlchemy.
- Tailwind.
- New frontend framework.
- New database provider.

## Whole-File Rule

Fail if AI output contains:

- patch fragments,
- diff hunks,
- instructions instead of file content,
- incomplete files,
- manual copy/paste steps.

Every generated or modified file must be represented as a whole-file replacement.

## Backend Rules

Generated backend must follow the CCore vertical slice blueprint.

Required files for a normal CRUD slice:

- domain object file,
- constants file,
- messages file,
- request contracts/parser file,
- mapper file,
- validator file,
- repository protocol file,
- concrete repository file,
- service file,
- routes file,
- `__init__.py`.

Required architecture:

```text
routes -> request contracts/parser -> mapper -> service -> repository protocol -> concrete repository -> database provider protocol
```

Fail if:

- routes manually parse business fields instead of using request parser contracts,
- service directly depends on concrete repository,
- repository directly creates database manager instead of receiving provider,
- structured error contract is not used,
- API response fields are not canonical camelCase,
- Python compilation fails.

## Frontend Rules

Generated frontend must follow the CCore Tasks list/details pattern.

Required behavior:

- list page has sortable table,
- list page has search/pagination/refresh toolbar,
- list rows are clickable,
- details page owns create/update/delete,
- no per-row Actions column on the list page,
- API fields use canonical camelCase,
- page uses existing shared CSS conventions.

Fail if:

- hardcoded lookup lists are used when lookup reference API is specified,
- JavaScript syntax validation fails,
- page references unknown API fields,
- page creates a different UI pattern without approval.

## Database Rules

Generated database artifacts must match the specification exactly.

Fail if:

- table names differ from specification,
- column names differ from specification,
- primary key strategy differs from specification,
- foreign keys are missing or incorrect,
- unique constraints are missing or incorrect,
- seed data differs from specification,
- generated SQL/config cannot be parsed by the existing schema/seed tooling.

## Registration Rules

Fail if generated backend routes are not registered in the appropriate route registry.

Fail if generated services/repositories are not registered in service factory/container where required by the current CCore pattern.

Fail if frontend navigation is requested but not added.

## Hardcoding Rules

Fail if generated files include:

- absolute machine paths,
- undeclared repository paths,
- entity-specific logic inside generic Automation Factory code,
- magic strings that should be constants,
- lookup values duplicated in frontend instead of coming from API/reference data.

## Report Rules

Every execution must produce a report.

The report must include:

- pass/fail outcome,
- selected task/provider/implementer/target/configuration,
- specification file used,
- AI provider/model used,
- generated artifact list,
- validation result list,
- applied file list,
- skipped file list,
- failure reason.
