# Generate CCore Organization CRUD

## Purpose

This folder contains the complete, task-specific document set for the first real CFFP Automation Factory generation experiment:

```text
Generate CRUD Module -> Organization
```

The goal is to prove that the Automation Factory can generate one complete CCore vertical slice from a controlled specification, using AI only inside a staged, validated, no-guessing pipeline.

This folder is intentionally separate from `docs/Automation Factory`.

- `docs/Automation Factory` describes the reusable platform and long-term automation architecture.
- `docs/Generate CCore Organization CRUD` describes one concrete generation task.

## Scope

This task is responsible for generating the Organization CRUD module, including the configured database artifacts, backend vertical slice, frontend pages/controllers/styles, registrations, validation output, and execution report.

The task must not perform direct free-form repository edits.

The required flow is:

```text
specification -> repository inspection -> AI generation -> artifact manifest -> staging -> validation -> apply -> execution report
```

## Required Reading Order

Any human reviewer or AI assistant must read the documents in this order:

1. `README.md`
2. `workflow/generate-crud-module-document-set.md`
3. `architecture/technology-decisions.md`
4. `architecture/ccore-vertical-slice-blueprint-v1.0.md`
5. `specifications/generation-contract.md`
6. `specifications/template_crud_spec.yaml`
7. `specifications/ccore_organizations_spec.yaml`
8. `specifications/artifact-mapping-specification.yaml`
9. `specifications/ai-artifact-manifest-contract.md`
10. `specifications/crud-generation-validation-rules.md`
11. `specifications/crud-module-specification-readiness-checklist.md`
12. `workflow/generate-crud-module-pipeline.md`
13. `workflow/generation-prompt-template.md`
14. `success-criteria.md`
15. `golden-reference.md`

## Non-Negotiable Rules

- Do not guess.
- Do not invent missing architecture.
- Do not introduce new frameworks.
- Do not switch database technology.
- Do not generate patch fragments.
- Do not generate manual copy/paste instructions as implementation.
- Do not apply generated code before validation passes.
- Do not create files outside the artifact mapping specification.
- Do not modify the golden reference module.
- Stop and report missing information if any required decision is absent.

## Authoritative Documents

The authoritative input for the generated Organization module is:

```text
specifications/ccore_organizations_spec.yaml
```

The reusable schema for future CRUD module specifications is:

```text
specifications/template_crud_spec.yaml
```

The rules that control how AI may generate artifacts are:

```text
specifications/generation-contract.md
specifications/ai-artifact-manifest-contract.md
specifications/artifact-mapping-specification.yaml
specifications/crud-generation-validation-rules.md
```

## Expected AI Output

The AI must return a structured artifact manifest only.

It must not return informal instructions, code snippets, or patch fragments.

The artifact manifest must contain full file contents for each generated or replaced file.

## Current Execution Status

Before execution, check:

```yaml
approval.approvedForExecution
```

inside:

```text
specifications/ccore_organizations_spec.yaml
```

If this value is false, the pipeline must stop before invoking AI generation.
