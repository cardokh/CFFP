# Context Engineering Pipeline Validation Rules

## Purpose

This document defines the initial validation rules for AI-ready context packages.

Validation happens before downstream AI generation. Invalid context must block generation.

## Minimum Validation Rules

### 1. Project Metadata Exists

The project must have a readable `project.json` file.

Required fields:

- `projectId`
- `name`

### 2. Input Root Exists

The project must have an input root:

```text
cautomation/projects/<projectId>/input/
```

### 3. Required Input Categories Exist

The input root must contain:

```text
client/
engineering/
modules/
```

### 4. At Least One Input Document Exists

The pipeline must fail if no human-authored input documents exist.

Placeholder files such as `.gitkeep` do not count as input documents.

### 5. Unsupported Files Are Reported

Unsupported file types must be reported.

They may be ignored or treated as errors depending on the downstream scope.

### 6. Context Scope Is Declared

Every context package must declare a scope.

The scope must be specific enough to explain why files were selected or excluded.

### 7. Source Traceability Exists

Every selected context item must be traceable to a source path.

Untraceable claims must be rejected or moved to open questions.

### 8. Conflicts Are Reported

The pipeline must report conflicts such as:

- competing technology choices,
- inconsistent module names,
- incompatible security assumptions,
- contradictory acceptance criteria,
- duplicate definitions with different meanings.

Blocking conflicts must prevent downstream generation.

### 9. Missing Required Information Is Reported

The pipeline must report missing information required by the requested downstream scope.

Examples:

- no users or personas for a UX-heavy feature,
- no persistence requirements before database generation,
- no API expectations before backend generation,
- no acceptance criteria before test generation.

### 10. Forbidden Inputs Are Not Used

The pipeline must fail if the context package includes forbidden inputs unless the input contract has first been updated and approved.

### 11. Output Manifest Is Complete

The manifest must list:

- selected files,
- excluded files,
- generated context files,
- validation status,
- validation errors,
- validation warnings.

### 12. Validation Status Is Explicit

The final validation status must be one of:

- `PASSED`
- `PASSED_WITH_WARNINGS`
- `FAILED`

Downstream generation may only proceed from `PASSED` or from explicitly approved `PASSED_WITH_WARNINGS`.

## Human Review Questions

Before a context package is approved for downstream generation, a human reviewer should be able to answer:

- Is the scope correct?
- Are the right documents included?
- Are unnecessary documents excluded?
- Are constraints clearly visible?
- Are open questions acceptable?
- Is the context sufficient for the next pipeline?
