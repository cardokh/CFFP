# CRUD Module Specification Readiness Checklist

## Purpose

This checklist is the gate before the Automation Factory may execute the `Generate CRUD Module` task.

The goal is to prevent guessing. If any required answer is missing, the pipeline must stop before AI generation.

## Required Source Files

The pipeline must receive these files as input:

- `docs/Automation Factory/architecture/technology-decisions.md`
- `docs/Automation Factory/architecture/ccore-vertical-slice-blueprint-v1.0.md`
- `docs/Automation Factory/workflow/cffp-working-agreement-v1.1.md`
- `docs/Automation Factory/workflow/generate-crud-module-pipeline.md`
- `docs/Automation Factory/specifications/crud-generation-validation-rules.md`
- `docs/Automation Factory/specifications/template_crud_spec.yaml`
- one concrete entity specification, for example `ccore_organizations_spec.yaml`
- the golden reference files listed in the concrete entity specification

## Hard Stop Rules

The pipeline must stop before AI generation if any input file contains unresolved markers:

- `REQUIRED_USER_DECISION`
- `USER_DECISION_REQUIRED`
- `REQUIRED_IF`
- `UNKNOWN`
- `TODO`
- blank mandatory values
- null mandatory values

## Technology Decision Gate

The concrete specification must explicitly declare:

- database provider
- database driver/access layer
- schema generation strategy
- seed-data strategy
- backend language
- backend routing style
- domain object style
- API request contract style
- service/repository layering style
- frontend rendering style
- frontend JavaScript style
- frontend CSS/style system
- AI provider
- AI model
- orchestration provider
- execution mode

The pipeline must not infer technology choices from package names, memories, or previous conversations.

## Golden Reference Gate

The concrete specification must list exact golden-reference files for:

- backend domain object
- backend constants
- backend messages
- backend contracts/request parser
- backend mapper
- backend validator
- backend repository protocol
- backend concrete repository
- backend service
- backend routes
- route registration
- service factory/container registration
- frontend list HTML
- frontend details HTML
- frontend list JavaScript
- frontend details JavaScript
- frontend CSS

If any golden-reference file is missing in the repository, the pipeline must stop.

## Entity Specification Gate

The concrete entity specification must explicitly declare:

- entity name
- plural name
- variable name
- plural variable name
- slug
- display name
- ownership boundary
- business purpose
- lookup/reference entities
- parent/child relationships
- many-to-many relationships
- all database tables
- all fields/columns
- all public API fields
- all Python fields
- all frontend field names
- all validation rules
- all seed data

The pipeline must not invent additional fields.

## Database Gate

For every table, the specification must declare:

- table name
- primary key column
- primary key type
- primary key strategy
- column names
- SQL types
- nullability
- defaults
- primary key constraints
- foreign key constraints
- unique constraints
- indexes
- seed data
- conflict column for seed upsert

The pipeline must not generate database artifacts from convention alone.

## Backend Gate

The concrete specification must declare exact generated file paths for:

- domain object
- constants
- messages
- contracts/request parser
- mapper
- validator
- repository protocol
- concrete repository
- service
- routes
- `__init__.py`

The concrete specification must declare exact class names for:

- domain object
- lookup domain object
- request parser
- create request
- update request
- mapper
- validator
- repository protocol
- lookup repository protocol
- concrete repository
- service
- lookup service

## API Gate

The concrete specification must declare:

- route prefix
- lookup route prefix, if any
- collection response field
- single-item response field
- lookup response collection field, if any
- create payload fields
- update payload fields
- public response fields
- error codes
- path constants to add
- route registry file to update
- service factory file to update
- service container file to update

## Frontend Gate

The concrete specification must declare:

- list page path
- details page path
- list controller path
- details controller path
- CSS paths
- API endpoint constants/usage
- table columns
- form fields
- lookup dropdown sources
- toolbar behavior
- row-click behavior
- navigation/menu decision
- exact menu file if a menu entry must be added

## AI Context Gate

The AI prompt must include:

- the concrete entity specification
- technology decisions
- CCore vertical slice blueprint
- working agreement
- validation rules
- golden reference backend files
- golden reference frontend files
- relevant route registry and service container files
- relevant database config files

The AI prompt must explicitly instruct the model to output a structured artifact manifest with full file contents only.

## Validation Gate

Generated artifacts must be staged first.

Before applying files, the pipeline must validate:

- specification completeness
- artifact manifest schema
- required files exist in staged output
- generated Python compiles
- generated JavaScript parses
- generated SQL/config is syntactically valid according to the existing schema configuration pattern
- route registration changes are present
- service factory/container changes are present
- backend layering follows the golden reference
- frontend pages follow list/details pattern
- no forbidden unresolved markers remain
- no hardcoded absolute paths exist
- no entity-specific branching is added to generic factory code

## Apply Gate

The pipeline may apply staged files only when validation succeeds.

If validation fails:

- no repository files are modified
- the execution report explains the failure
- staged artifacts remain available for inspection

## Execution Report Gate

The report must include:

- specification summary
- source files used
- golden reference files used
- AI model used
- prompt summary
- generated artifact manifest
- staged files
- validation results
- applied files
- skipped files
- failure reason, if any
