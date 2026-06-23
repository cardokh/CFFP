# CFFP Automation Factory — Generation Contract

## Purpose

This document defines how an AI generator is allowed to generate CCore CRUD modules.

The CRUD module specification defines **what** must be generated.

This Generation Contract defines **how** generation must behave.

The purpose is to prevent guessing, hardcoding, architectural drift, unsafe repository modification, and undocumented assumptions.

## Scope

This contract applies to the Automation Factory task:

```text
Generate CRUD Module
```

The first execution target is:

```text
Organization
```

The same contract must apply when the task is later reused for Users, Modules, Roles, Permissions, Memberships, or any other CCore entity.

## Non-Negotiable Rules

### 1. No Guessing

The generator must not invent missing information.

If a required value is missing from the specification, technology decisions, artifact mapping, golden reference, or repository inspection summary, generation must stop and report the missing information.

The generator must not infer critical implementation details from probability, convention, preference, or common practice.

Examples of forbidden guessing:

- choosing a database type not explicitly declared
- choosing a CSS framework not explicitly declared
- inventing a backend folder structure
- inventing API naming conventions
- inventing validation behavior
- inventing route registration files
- inventing navigation locations
- inventing seed data
- inventing authentication or authorization behavior

### 2. Repository Inspection Is Mandatory

Before generating artifacts, the pipeline must inspect the current repository.

The generator must use inspected files as the factual source for current architecture, naming, structure, import style, route registration, frontend style, and CRUD behavior.

The golden reference for the first CRUD generation task is:

```text
ccore_tasks
```

The generator must treat the Task CRUD implementation as the implementation blueprint unless the specification explicitly overrides a behavior.

### 3. Specification Is the Source of Truth

The entity specification is the source of truth for the target module.

For the first execution, the source specification is:

```text
docs/Automation Factory/specifications/ccore_organizations_spec.yaml
```

The reusable template is:

```text
docs/Automation Factory/specifications/template_crud_spec.yaml
```

The generator must not generate entity behavior that is not present in the specification.

### 4. Technology Decisions Are Binding

The generator must obey:

```text
docs/Automation Factory/architecture/technology-decisions.md
```

If the specification and technology decisions conflict, generation must stop and report the conflict.

The generator must not introduce new frameworks, libraries, runtime dependencies, frontend frameworks, database drivers, or architectural layers unless explicitly approved.

### 5. Artifact Mapping Is Binding

The generator must obey:

```text
docs/Automation Factory/specifications/artifact-mapping-specification.yaml
```

The generator must not decide file destinations by itself.

Every generated artifact must map to a declared artifact type and destination rule.

If a required artifact has no mapping rule, generation must stop.

### 6. Whole-File Generation Only

Generated application artifacts must be whole files.

The generator must not produce partial snippets, line patches, diff fragments, or instructions requiring manual copy/paste.

If an existing file must be changed, the generator must stage a complete replacement version of that file.

### 7. Stage Before Apply

The generator must never write directly into the active application source tree as its first output.

Generated artifacts must first be written to a staging directory.

The pipeline may apply staged files only after validation succeeds.

If validation fails, no application source file may be modified.

### 8. AI Output Is Untrusted

AI-generated artifacts must be treated as untrusted until validated.

Validation must run before apply.

A successful AI response is not enough.

The execution report must clearly show:

- generated files
- skipped files
- validation status
- apply status
- failed checks
- unresolved assumptions

### 9. No Entity-Specific Logic Inside Generic Factory Code

The generic Automation Factory implementation must not contain entity-specific rules such as:

```text
if entity == "organization"
```

Entity-specific behavior belongs in the entity specification and generated artifacts, not in the generic generator engine.

### 10. No Hardcoded Absolute Paths

The generator must not generate absolute machine-specific paths.

All paths must be repository-relative or configuration-driven.

Forbidden examples:

```text
C:\Users\...
/home/...
/Users/...
```

### 11. No Hidden Manual Steps

The output must not require undocumented manual work.

If a manual approval or external action is required, it must appear explicitly in the execution report.

The goal is one Automation Factory execution from the user's perspective.

### 12. Fail Closed

If the generator is uncertain, it must fail closed.

Failing with a useful missing-information report is preferred over generating incorrect code.

## Required Input Documents

The generation pipeline must assemble AI context from these controlled inputs:

```text
docs/Automation Factory/architecture/technology-decisions.md
docs/Automation Factory/specifications/generation-contract.md
docs/Automation Factory/specifications/artifact-mapping-specification.yaml
docs/Automation Factory/specifications/template_crud_spec.yaml
docs/Automation Factory/specifications/ccore_organizations_spec.yaml
docs/Automation Factory/specifications/ai-artifact-manifest-contract.md
docs/Automation Factory/specifications/crud-generation-validation-rules.md
docs/Automation Factory/workflow/generate-crud-module-pipeline.md
```

The pipeline must also include a repository inspection summary and golden reference file contents collected at execution time.

## Required Golden Reference Inputs

For the first CRUD generation task, the pipeline must inspect and include the relevant Task CRUD implementation files.

The exact list must come from the pipeline specification and repository inspection.

The generator must not rely on memory of the Task implementation.

## Output Requirements

The generator must return a structured artifact manifest.

The artifact manifest must conform to:

```text
docs/Automation Factory/specifications/ai-artifact-manifest-contract.md
```

Each generated artifact entry must include:

- artifact id
- artifact type
- target path
- generation status
- full file content or staged file reference
- dependencies
- validation requirements
- whether the file is new or a replacement

## Conflict Handling

If the generator detects a conflict between documents, it must stop and report:

- conflicting documents
- conflicting values
- why the conflict blocks generation
- what decision is needed from the user

## Missing Information Handling

If information is missing, the generator must not continue.

The report must include a `missing_information` section containing:

- missing field
- source document where it should be defined
- why it is needed
- suggested decision options, only when options are directly supported by the inspected repository

## Apply Rules

Generated artifacts may be applied only when all required validation gates pass.

If any validation gate fails, the pipeline must keep files in staging and mark the execution as failed or blocked.

## Definition of Acceptable Generation

A generation result is acceptable only if:

1. It uses declared technology decisions.
2. It follows the inspected golden reference.
3. It satisfies the entity specification.
4. It produces complete artifacts.
5. It passes validation.
6. It applies safely.
7. It records a complete execution report.

## Definition of Failure

The generation attempt must be considered failed if:

- unresolved required values remain
- the AI invents architecture
- generated files are partial
- generated paths are not mapped
- validation fails
- apply fails
- execution report is missing or incomplete

Failure is acceptable if it is explicit, traceable, and useful.

Silent guessing is not acceptable.
