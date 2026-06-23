# Generate CRUD Module — Required Document Set

## Purpose

This document defines the self-contained document set for the concrete generation task:

```text
Generate CRUD Module -> Organization
```

The goal is to keep the context focused and avoid feeding unnecessary historical or platform-level documents into the AI generation pipeline.

## Folder Policy

This folder contains only the documents needed to prepare, run, validate, and review the first Organization CRUD generation experiment.

Long-term Automation Factory platform documents may remain under:

```text
docs/Automation Factory
```

They should not be included in this task-specific AI context unless a required document in this folder explicitly references them.

## Required Static Documents For This Task

These documents should be included in the generation context or used directly by the pipeline.

| Document | Why It Is Required |
| --- | --- |
| `README.md` | Entry point, scope, reading order, and non-negotiable rules. |
| `architecture/technology-decisions.md` | Locks the current technology stack and prevents tool/framework guessing. |
| `architecture/ccore-vertical-slice-blueprint-v1.0.md` | Defines the CCore vertical-slice architecture the generated CRUD module must follow. |
| `golden-reference.md` | Identifies the concrete backend/frontend golden reference files. |
| `specifications/generation-contract.md` | Defines how the AI is allowed to generate artifacts and what it must not do. |
| `specifications/artifact-mapping-specification.yaml` | Defines where generated artifacts are allowed to be staged/applied. |
| `specifications/template_crud_spec.yaml` | Reusable master structure for future CRUD specifications. |
| `specifications/ccore_organizations_spec.yaml` | First real entity specification. Source of truth for Organization generation. |
| `specifications/ai-artifact-manifest-contract.md` | Defines the required structured output from the AI generator. |
| `specifications/crud-generation-validation-rules.md` | Defines validation gates before generated artifacts may be applied. |
| `specifications/crud-module-specification-readiness-checklist.md` | Used before execution to confirm the Organization specification is complete. |
| `workflow/generate-crud-module-pipeline.md` | Defines the sequential Prefect pipeline steps for the task. |
| `workflow/generation-prompt-template.md` | Defines how the final AI prompt is assembled from controlled inputs. |
| `success-criteria.md` | Defines success, controlled failure, and definition of done. |

## Required Runtime Inputs Not Stored As Static Docs

These inputs must be collected by the pipeline at execution time.

| Runtime Input | Why It Is Required |
| --- | --- |
| Repository inspection summary | Prevents guessing about current code structure. |
| Golden reference file contents from `ccore_tasks` | Gives the AI exact implementation patterns to replicate. |
| Current generated artifact staging path | Ensures output is staged before apply. |
| Execution metadata | Links generated output to an Automation Factory execution report. |
| Approved task configuration values | Connects the UI-selected Automation Factory configuration to the generation pipeline. |

## Documents Not Required In This Task Folder

The following are useful project/platform documents, but they are not required inside this concrete task folder unless the task scope changes:

- ADRs for authentication, authorization, roles, permissions, sessions, or organization isolation.
- Historical architecture discovery notes.
- General Automation Factory vision documents.
- Previous reports from earlier experiments.
- Jira exports.
- High-level `.docx` project notes.

If the Organization CRUD module later includes security behavior, authorization, session ownership, or organization isolation, the relevant ADRs should be copied or referenced explicitly at that time.

## Recommended AI Context Assembly Order

The pipeline should assemble the AI context in this order:

1. `README.md`
2. `specifications/generation-contract.md`
3. `architecture/technology-decisions.md`
4. `architecture/ccore-vertical-slice-blueprint-v1.0.md`
5. `golden-reference.md`
6. `specifications/template_crud_spec.yaml`
7. `specifications/ccore_organizations_spec.yaml`
8. `specifications/artifact-mapping-specification.yaml`
9. `specifications/ai-artifact-manifest-contract.md`
10. `specifications/crud-generation-validation-rules.md`
11. `workflow/generate-crud-module-pipeline.md`
12. `workflow/generation-prompt-template.md`
13. `success-criteria.md`
14. Runtime repository inspection summary.
15. Runtime golden reference file contents.

## Stop Rule

If any required static document is missing, empty, internally inconsistent, or contains unresolved required decisions, the pipeline must stop before invoking AI generation.

If runtime repository inspection contradicts the static documents, the pipeline must stop and report the conflict.
