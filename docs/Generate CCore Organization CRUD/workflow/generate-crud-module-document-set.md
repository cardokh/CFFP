# Generate CRUD Module — Required Document Set

## Purpose

This document identifies which files in `docs/Automation Factory` are required for the first real Automation Factory task:

```text
Generate CRUD Module → Organization
```

The goal is to keep the working context focused and avoid feeding unnecessary documents into the AI generation pipeline.

## Required For This Task

These documents should be included in the generation context or used directly by the pipeline.

| Document | Why It Is Required |
| --- | --- |
| `architecture/technology-decisions.md` | Locks the current technology stack and prevents tool/framework guessing. |
| `architecture/ccore-vertical-slice-blueprint-v1.0.md` | Defines the CCore vertical-slice architecture the generated CRUD module must follow. |
| `specifications/generation-contract.md` | Defines how the AI is allowed to generate artifacts and what it must not do. |
| `specifications/artifact-mapping-specification.yaml` | Defines where generated artifacts are allowed to be staged/applied. |
| `specifications/template_crud_spec.yaml` | Reusable master structure for future CRUD specifications. |
| `specifications/ccore_organizations_spec.yaml` | First real entity specification. Source of truth for Organization generation. |
| `specifications/ai-artifact-manifest-contract.md` | Defines the required structured output from the AI generator. |
| `specifications/crud-generation-validation-rules.md` | Defines validation gates before generated artifacts may be applied. |
| `specifications/crud-module-specification-readiness-checklist.md` | Used before execution to confirm the Organization specification is complete. |
| `workflow/generate-crud-module-pipeline.md` | Defines the sequential Prefect pipeline steps for the task. |
| `workflow/cffp-working-agreement-v1.1.md` | Defines project workflow rules such as no guessing, validation-first, and whole artifacts. |

## Required Runtime Inputs Not Stored As Static Docs

These inputs must be collected by the pipeline at execution time.

| Runtime Input | Why It Is Required |
| --- | --- |
| Repository inspection summary | Prevents guessing about current code structure. |
| Golden reference file contents from `ccore_tasks` | Gives the AI exact implementation patterns to replicate. |
| Current generated artifact staging path | Ensures output is staged before apply. |
| Execution metadata | Links generated output to an Automation Factory execution report. |

## Supporting But Not Required In AI Prompt Context

These documents are useful background but should not be part of the main AI generation context unless a specific question requires them.

| Document | Recommendation |
| --- | --- |
| `architecture/architecture-discovery.md` | Keep as historical discovery/reference. Do not feed into the main generation prompt by default. |
| `architecture/security-architecture-summary.md` | Keep as platform background. Use only when generating security-specific modules. |
| `specifications/vision-and-purpose.md` | Keep as project vision. Do not feed into the generation prompt by default. |
| `CFFP Automation Factory.docx` | Keep as high-level project document. Not needed for pipeline execution. |
| `reports/REP-SPEC-READINESS-001.md` | Keep as previous readiness report. Generate a new report for each execution. |
| `reports/REP-ORG-001_validation.json` | Replace or regenerate when validation runs. Empty placeholder should not be used as input. |

## Not Required For The CRUD Generation Task

The ADR files are important platform architecture records, but they are not required to generate the first Organization CRUD module unless the generated module includes authentication, authorization, roles, permissions, sessions, or organization isolation behavior.

| Document | Recommendation |
| --- | --- |
| `adr/ADR-001-authentication-strategy.md` | Keep, but exclude from default CRUD generation prompt. |
| `adr/ADR-002-authorization-strategy.md` | Keep, but exclude from default CRUD generation prompt unless authorization is in scope. |
| `adr/ADR-003-role-model.md` | Keep, but exclude until role/user generation. |
| `adr/ADR-004-permission-model.md` | Keep, but exclude until permission generation. |
| `adr/ADR-005-organization-isolation.md` | Keep, but exclude until organization isolation/security behavior is generated. |
| `adr/ADR-006-session-strategy.md` | Keep, but exclude until session behavior is generated. |

## Recommended Folder Policy

Do not delete architectural documents simply because they are not needed for this specific task.

Instead, keep them in the folder but control what the pipeline loads.

The pipeline should use an explicit document allow-list for each generation task.

For the first Organization CRUD generation task, the allow-list should be the files in the **Required For This Task** section.

## Recommended AI Context Assembly Order

The pipeline should assemble the AI context in this order:

1. Generation Contract
2. Technology Decisions
3. CCore Vertical Slice Blueprint
4. CRUD Template
5. Organization Specification
6. Artifact Mapping Specification
7. Artifact Manifest Contract
8. Validation Rules
9. Pipeline Workflow Summary
10. Repository Inspection Summary
11. Golden Reference File Contents

## Stop Rule

If any required document is missing, empty, internally inconsistent, or contains unresolved required decisions, the pipeline must stop before invoking AI generation.
