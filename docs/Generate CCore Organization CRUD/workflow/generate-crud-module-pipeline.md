# Generate CRUD Module Pipeline

## Purpose

This workflow defines the first real Automation Factory task that should automate useful CCore development.

The task is generic:

```text
Generate CRUD Module
```

The first execution target is:

```text
Organization
```

The same task should later be reused for Users, Modules, Roles, Permissions, Memberships, and other CCore entities by changing the specification file only.

## Non-Negotiable Rule

No guessing.

If the specification, repository inspection, technology decision document, or golden reference does not contain enough information, the pipeline must stop and report the missing information.

## User-Level Behavior

From the user's perspective this should be one Automation Factory execution.

The user selects:

```text
Provider: Local Provider
Implementer Type: Prefect AI Flow Implementer Type
Target: Generate CRUD Module
Configuration: Generate Organization CRUD Module Configuration
```

Then the pipeline runs all internal steps sequentially.

## Pipeline Steps

### 1. Read specification

Input:

```text
docs/Generate CCore Organization CRUD/specifications/ccore_organizations_spec.yaml
```

Output:

- Parsed generation specification.
- Missing required values report.

Failure condition:

- Any `REQUIRED`, `REQUIRED_USER_DECISION`, `UNKNOWN`, empty mandatory field, or unresolved conditional value remains.

### 2. Validate specification completeness

The pipeline checks that the specification contains:

- Technology stack.
- Entity naming.
- Database tables, columns, constraints, indexes, and seed data.
- Backend files, classes, contracts, mappers, services, repositories, routes, and registrations.
- Frontend pages, JavaScript controllers, CSS files, API endpoints, and navigation decisions.
- Validation requirements.

Failure condition:

- Any mandatory block is incomplete.

### 3. Inspect repository

The pipeline inspects the current repository before generation.

Required inspection targets:

```text
backend/src/ccore/tasks
backend/src/ccore/application/service_factory.py
backend/src/ccore/application/service_container.py
backend/src/api/api_paths.py
backend/src/api/module_route_registry.py
backend/src/ccore/infrastructure/database.py
frontend/static/desktop/protected/ccore/tasks.html
frontend/static/desktop/protected/ccore/task-details.html
frontend/static/desktop/protected/ccore/js/tasks.js
frontend/static/desktop/protected/ccore/js/task-details.js
frontend/static/desktop/protected/ccore/css/tasks.css
frontend/static/desktop/protected/ccore/css/task-details.css
scripts/db/postgres/config/entities.json
scripts/db/postgres/config/postgres_create_schema.json
scripts/db/postgres/config/postgres_seed_data.json
```

Output:

- Repository inspection summary.
- Confirmed golden-reference patterns.
- Any conflicts between spec and repo.

Failure condition:

- Required reference files are missing.
- The specification contradicts the inspected baseline without an explicit migration decision.

### 4. Collect golden reference files

The pipeline collects complete file contents from the CCore Tasks golden reference.

These files are used as implementation examples, not as vague inspiration.

### 5. Build AI context

The AI context must include:

- Full specification.
- Technology decisions.
- README and task scope.
- CCore vertical slice blueprint.
- Repository inspection summary.
- Golden reference file contents.
- AI artifact manifest contract.
- Success criteria.

The prompt must instruct the AI to generate a complete artifact manifest, not direct edits.

### 6. Generate artifact manifest

The AI must return a structured artifact manifest containing full file contents.

The output must include:

- New backend files.
- Modified backend registration files if required.
- New frontend files.
- Modified navigation files if required.
- Database schema/seed artifacts or config updates.
- Tests/validation helpers if specified.

Failure condition:

- Missing required file.
- Patch fragments instead of whole-file content.
- Undeclared files.
- Unapproved dependencies.

### 7. Write staged artifacts

The artifact writer writes generated output to a staging directory only.

No repository application happens yet.

### 8. Validate staged artifacts

Validation runs against staged artifacts and affected repository context.

Required validation categories:

- Python compile validation.
- JavaScript syntax validation.
- Route registration validation.
- Service/repository layering validation.
- Database config/schema/seed validation.
- Frontend contract validation.
- Architecture rule validation.

Failure condition:

- Any fatal validation rule fails.

### 9. Apply staged artifacts

Only after validation passes may the pipeline apply generated artifacts to the repository.

Application must be whole-file replacement only.

### 10. Write execution report

The final report must include:

- Specification summary.
- Technology decisions used.
- AI provider/model used.
- Generated artifact manifest.
- Validation results.
- Applied files.
- Skipped files.
- Failure reason if failed.

## Success Definition

The first experiment is successful when one Automation Factory execution can generate and apply a working Organization CRUD vertical slice that follows the CCore Task golden reference.

---

## Required Control Documents

Before generation, the pipeline must load the approved document set defined in:

```text
docs/Generate CCore Organization CRUD/workflow/generate-crud-module-document-set.md
```

The following documents are mandatory control documents for the first Organization CRUD generation attempt:

```text
docs/Generate CCore Organization CRUD/specifications/generation-contract.md
docs/Generate CCore Organization CRUD/specifications/artifact-mapping-specification.yaml
```

The Generation Contract controls how AI is allowed to generate artifacts.

The Artifact Mapping Specification controls where generated artifacts may be staged and applied.

If either file is missing or incomplete, the pipeline must stop before invoking AI.
