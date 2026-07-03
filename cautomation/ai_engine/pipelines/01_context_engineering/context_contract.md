# Context Engineering Pipeline Context Contract

## Purpose

This document defines how the Context Engineering Pipeline treats context.

Context is not a raw dump of project files. Context is a curated, validated, traceable package of information prepared for a specific downstream purpose.

## Context Model

A context package should contain:

```text
context_package/
├── context_manifest.json
├── context_summary.md
├── source_index.md
├── selected_inputs/
├── normalized_context/
├── decisions.md
├── open_questions.md
├── constraints.md
└── validation_report.json
```

This structure is conceptual for the current iteration. Exact file names may evolve when implementation begins.

## Required Context Properties

A valid context package must be:

- **Scoped** — it contains only information relevant to the downstream pipeline.
- **Traceable** — every included fact or decision can be traced to a source document or approved generated artifact.
- **Ordered** — foundational rules and constraints are clearly separated from task-specific context.
- **Auditable** — a human can inspect what context was selected and why.
- **Reusable** — a later pipeline or future run can consume the package without relying on conversation history.
- **Minimal** — unnecessary files and unrelated project material are excluded.

## Context Scope

Every context package must declare its scope.

Examples:

```text
scope: project_overview
scope: module:epic_tracker
scope: pipeline:02_db
scope: pipeline:03_backend
scope: feature:project_creation
```

The scope determines which inputs are selected and which are excluded.

## Selection Rules

The pipeline should select:

- project metadata,
- relevant client input,
- relevant engineering constraints,
- relevant module input,
- approved upstream outputs required by the requested scope.

The pipeline should exclude:

- unrelated modules,
- outdated draft material,
- implementation-specific documents not needed by the requested scope,
- generated code unless explicitly approved as an input source,
- logs that are not approved engineering artifacts.

## Ordering Rules

The generated context should present information in this order:

1. Platform-level rules and principles.
2. Project-level vision and constraints.
3. Module-level requirements and domain knowledge.
4. Downstream pipeline-specific requirements.
5. Open questions, conflicts, and risks.

This ordering keeps stable constraints visible before task-specific details.

## Provenance Rules

Every meaningful statement in the context package should be traceable to one of:

- a human-authored input document,
- an approved generated artifact,
- a pipeline validation result,
- or an explicit project configuration value.

The pipeline must not invent product requirements, architectural decisions, business rules, or technology choices.

## Open Questions

If the pipeline detects missing or ambiguous information, it must record the issue in `open_questions.md` or the equivalent structured output.

Open questions should block downstream generation when the missing information is required for correctness.
