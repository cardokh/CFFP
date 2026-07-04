# AI Engine

The AI Engine contains reusable pipelines that transform project knowledge into generated software artifacts.

The engine is based on context engineering rather than free-form prompting. The AI model is not the center of the architecture; the context pipeline is.

## Lifecycle

```text
01_context_engineering
        ↓
02_planning
        ↓
03_generation
        ├── db
        ├── backend
        ├── frontend
        ├── testing
        └── deployment
        ↓
04_validation
        ↓
05_apply
        ↓
06_verification
```

## Important Distinction

The lifecycle stages are not the same thing as database/backend/frontend generation.

Database, backend, frontend, testing, and deployment are generation targets inside `03_generation/`.

The overall lifecycle runs once for a project, module, feature, or story generation run. Within the generation stage, specialized generators may run sequentially or independently depending on the plan.

## Pipeline Principles

- Every pipeline has one clear responsibility.
- Every pipeline owns its outputs.
- Every pipeline has an explicit context contract.
- Every pipeline consumes the smallest sufficient context.
- Pipeline outputs are engineering artifacts, not temporary logs.
- Generated artifacts are untrusted until validated and approved.
- Human-authored and approved generated documents remain the source of truth.
- Downstream stages consume validated context packages rather than arbitrary repository files.

## Current Implementation Status

This iteration introduces the first executable pipeline: `01_context_engineering`.

The executable MVP reads the approved Pipeline Management module SRS and ATS, validates the module input contract, extracts the DOCX content, and creates a deterministic context package for downstream planning and generation.

The immediate priority remains to harden `01_context_engineering` because all downstream stages depend on its output.
