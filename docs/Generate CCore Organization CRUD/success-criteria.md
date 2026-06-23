# Success Criteria — Generate CCore Organization CRUD

## Purpose

This document defines when the first real Automation Factory CRUD generation experiment is considered successful.

## User-Level Success

The experiment succeeds when one Automation Factory task execution can generate a working Organization CRUD vertical slice using the approved specification and current CCore architecture.

The user should not manually create database files, backend files, frontend files, route registrations, or navigation changes.

## Required Successful Outcome

A successful execution must produce:

- staged artifacts,
- validation report,
- applied whole-file artifacts,
- execution report,
- Organization CRUD capability integrated into CCore.

## Database Success Criteria

The generated artifacts must include the configured database/schema/seed outputs required by the current repository baseline.

Validation must confirm:

- generated database artifacts match the approved Organization specification,
- existing database configuration is preserved where required,
- Organization-related objects are added without deleting unrelated existing definitions,
- seed data is explicit and comes from the specification,
- unsupported schema features are not silently invented.

## Backend Success Criteria

The generated backend must follow the CCore Task golden reference.

Validation must confirm:

- required Organization backend files exist,
- Python files compile,
- imports resolve within the current project structure where validation can check this,
- routes use the existing route registration style,
- service depends on repository protocol,
- repository uses the approved database/provider pattern,
- request parsing uses explicit contract/parser classes,
- no Pydantic/async/SQLAlchemy code is introduced unless explicitly approved,
- API response fields match the approved response contract.

## Frontend Success Criteria

The generated frontend must follow the existing CCore Task list/details pattern.

Validation must confirm:

- Organization list page exists,
- Organization details/create/edit behavior exists according to the specification,
- JavaScript uses vanilla JS and existing API conventions,
- CSS follows existing shared CSS conventions,
- no new frontend framework is introduced,
- lookup handling follows the approved specification,
- navigation changes are applied only if explicitly mapped.

## Automation Factory Success Criteria

The Automation Factory execution must:

- load the approved document set,
- inspect the repository before AI invocation,
- invoke AI using a controlled prompt assembled from the approved documents,
- receive a structured artifact manifest,
- reject patches/snippets/manual instructions,
- stage artifacts before applying,
- validate staged artifacts,
- apply only after validation succeeds,
- write a complete execution report.

## Failure Is Acceptable If Controlled

The experiment is still valuable if generation fails for a clear, reported reason.

Acceptable controlled failures include:

- missing required specification value,
- repository inspection conflict,
- AI returned invalid manifest,
- validation failed,
- artifact path not mapped,
- generated code did not compile.

Unacceptable failures include:

- silent guessing,
- direct unvalidated repository modification,
- partial patches,
- hidden hardcoded paths,
- invented frameworks,
- missing execution report.

## Definition of Done

The task is done only when one of these is true:

1. The Organization CRUD module is generated, validated, applied, and reported successfully.
2. The pipeline stops safely with a complete failure report explaining exactly what is missing or invalid.
