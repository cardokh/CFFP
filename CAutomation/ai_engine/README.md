# AI Engine

The AI Engine contains reusable pipelines that transform project knowledge into generated software artifacts.

The engine is based on context engineering rather than free-form prompting. The AI model is not the center of the architecture; the context pipeline is.

## Lifecycle

```text
01_context_engineering
        ↓
02_planning
        ↓
03_project_management_publishing
        ↓
04_generation
        ├── db
        ├── backend
        ├── frontend
        ├── testing
        └── deployment
        ↓
05_validation
        ↓
06_apply
        ↓
07_verification
```

## Important Distinction

The lifecycle stages are not the same thing as database/backend/frontend generation.

Database, backend, frontend, testing, and deployment are generation targets inside `04_generation/`.

Project Management Publishing is its own lifecycle pipeline. It publishes approved planning artifacts; it does not create planning content and does not generate code.

The overall lifecycle runs once for a project, module, feature, or story generation run. Within the generation stage, specialized generators may run sequentially or independently depending on the frozen plan.

## Pipeline Principles

- Every pipeline has one clear responsibility.
- Every pipeline owns its outputs.
- Every pipeline has an explicit context contract.
- Every pipeline consumes the smallest sufficient context.
- Pipeline outputs are engineering artifacts, not temporary logs.
- Generated artifacts are untrusted until validated and approved.
- Human-authored and approved generated documents remain the source of truth.
- Downstream stages consume validated context packages rather than arbitrary repository files.
- Every completed task must be validated against all available reference modules before it is considered complete.

## Current Implementation Status

This baseline synchronization iteration aligns the repository structure with the frozen seven-pipeline architecture.

The immediate priority remains to validate `01_context_engineering` end-to-end because all downstream stages depend on its output.
