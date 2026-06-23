# CCore Vertical Slice Blueprint v1.0

## Purpose

This blueprint defines the golden implementation standard for CCore vertical slices. The current reference slice is `ccore_tasks`.

Future slices, including `ccore_metrics`, must follow this structure before the Automation Factory is allowed to generate similar slices automatically.

## Layering Rule

```text
API route
→ API request contract/parser
→ mapper
→ service
→ repository protocol
→ concrete repository
→ database connection provider protocol
→ database manager/driver
```

No layer may skip the contract immediately below it.

## Naming Rule

```text
PostgreSQL tables/columns: snake_case
Python domain/internal: snake_case
JSON/API: camelCase
JavaScript: camelCase
HTML/CSS: kebab-case
Routes/URLs: kebab-case
```

## Public API Contract Rule

External JSON must expose only canonical camelCase fields.

For `ccore_tasks`, the task response contract is:

```json
{
  "taskId": "...",
  "taskName": "...",
  "status": "...",
  "statusLabel": "...",
  "createdAt": "...",
  "updatedAt": "..."
}
```

Legacy/transitional aliases such as `id`, `name`, `created_at`, and `updated_at` are not allowed in golden CCore slices.

## Error Contract Rule

API errors must use a structured error object.

```json
{
  "success": false,
  "error": {
    "code": "CCORE_TASK_VALIDATION_ERROR",
    "message": "Task name is required."
  }
}
```

Frontend API helpers must support this shape and must not require page controllers to parse transport-level errors manually.

## Request Contract Rule

Routes must not manually extract payload fields. They may only:

1. Read JSON body.
2. Delegate payload parsing/validation to a request contract/parser.
3. Delegate request-to-domain conversion to a mapper.
4. Delegate use-case execution to a service.
5. Return mapped response DTOs.

## Validation Rule

Validation is split into two stages:

1. API-boundary validation: JSON shape, supported fields, required public fields.
2. Domain/use-case validation: domain object validity, ID validity, reference/lookup value validity.

## Repository Rule

Services depend on repository protocols.

Concrete repositories depend on database connection/provider protocols, not concrete database managers.

## Reference Data Rule

Lookup values such as status/category/type must be represented through reference tables or reference providers. They must not be hardcoded in frontend option lists or service logic.

## Persistence Metadata Rule

CRUD tables must include standard metadata columns unless a slice documents why they are not applicable.

```text
created_at
updated_at
```

The public API exposes these as:

```text
createdAt
updatedAt
```

Update operations must refresh `updated_at`.

## CCore List View UI Rule

List pages are for browsing, searching, sorting, paginating, and selecting records.

Standard list-page pattern:

```text
Header
→ sortable table
→ message area when needed
→ toolbar with navigation, search, pagination, count, create, refresh
```

Rules:

- The table is the primary content.
- Supported columns are sortable.
- Search and pagination live in the toolbar/footer area.
- Rows are clickable and open the details page.
- No per-row Actions column is used for standard CRUD list pages.

## CCore Details View UI Rule

Details pages are for inspecting and maintaining one record.

Standard details-page pattern:

```text
Header
→ details form/panel
→ message area
→ toolbar with Back, mode indicator, Delete, Create/Update
```

Rules:

- Success/error/info messages appear above the toolbar.
- Details fields should use compact two-column rows where practical.
- Create/update/delete actions belong on the details page, not the list table.
- If a user submits an unchanged edit form, the UI reports that no changes were made instead of sending an unnecessary update.

## Frontend Constants Rule

Page controllers may define page-specific constants for labels, status messages, and confirmation prompts.

Repeated UI strings must not be duplicated across controller logic. They should be centralized at the top of the page controller or moved to shared frontend configuration when reused by multiple pages.

## Automation Factory Rule

A generated vertical slice must include:

1. Domain objects.
2. API request contracts/parsers.
3. Response mapper.
4. Validator.
5. Repository protocol.
6. Concrete repository.
7. Service.
8. Routes.
9. Frontend API usage with canonical JSON fields.
10. Focused contract/mapper/service/route tests.
11. Frontend JavaScript syntax validation.
12. Inspection metadata/reporting hooks.

## Reference Implementation

`backend/src/ccore/tasks` and `frontend/static/desktop/protected/ccore/tasks.html` / `task-details.html` are the golden reference candidates for CCore Blueprint v1.0 after strict API contracts, structured errors, request parsing, validation split, repository protocols, metadata columns, list/details UI rules, and focused tests are applied.
