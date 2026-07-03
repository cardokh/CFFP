# Context Engineering Pipeline Output Contract

## Purpose

This document defines the outputs produced by the Context Engineering Pipeline.

The pipeline output is an AI-ready context package. It is not application code.

## Required Outputs

Each pipeline run should produce a run-specific output directory containing:

```text
context_manifest.json
context_summary.md
source_index.md
selected_inputs/
normalized_context/
decisions.md
constraints.md
open_questions.md
validation_report.json
```

Exact storage location will be defined during implementation. The location must be outside the live application source tree until an apply or approval step exists.

## Output Descriptions

### context_manifest.json

Structured metadata for the context package.

Should include:

- project id,
- pipeline id,
- run id,
- requested scope,
- selected source files,
- excluded source files,
- output files,
- validation status,
- created timestamp.

### context_summary.md

Human-readable summary of the selected context.

Should include:

- project purpose,
- selected scope,
- key requirements,
- key constraints,
- downstream pipeline readiness.

### source_index.md

Human-readable index of source documents used to build the context package.

Should include:

- source path,
- source category,
- reason for inclusion,
- relevant sections if applicable.

### selected_inputs/

A copied or referenced set of selected input documents used for this context package.

The pipeline must preserve source traceability.

### normalized_context/

Normalized versions of selected inputs prepared for downstream AI consumption.

Normalization may include:

- consistent headings,
- removal of irrelevant boilerplate,
- grouping related requirements,
- extracting constraints,
- resolving terminology.

Normalization must not change meaning.

### decisions.md

A concise list of architectural, product, workflow, or technology decisions found in the selected inputs.

### constraints.md

A concise list of constraints that downstream generation must obey.

### open_questions.md

A list of missing, conflicting, or ambiguous information.

### validation_report.json

Machine-readable validation result for the context package.

## Output Failure Conditions

The pipeline must fail if it cannot produce:

- a manifest,
- a source index,
- a context summary,
- a validation report,
- or traceability from selected context back to approved inputs.

## Approval Status

A context package is not automatically approved.

Downstream pipelines may only consume context packages that have passed validation. Later iterations may introduce explicit human approval before downstream AI generation.
