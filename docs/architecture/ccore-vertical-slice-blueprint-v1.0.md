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
  "createdAt": "..."
}
```

Legacy/transitional aliases such as `id` and `name` are not allowed in golden CCore slices.

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
10. Focused contract/mapper/service tests.
11. Inspection metadata/reporting hooks.

## Reference Implementation

`backend/src/ccore/tasks` is the golden reference candidate for CCore Blueprint v1.0 after the strict API contract, request parsing, validation split, repository protocol, and tests are applied.
