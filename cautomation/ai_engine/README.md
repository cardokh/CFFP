# AI Engine

The AI Engine contains reusable pipelines that transform project knowledge into generated software artifacts.

The engine is based on context engineering rather than free-form prompting. Each pipeline must explicitly define the context it consumes, the context it produces, the boundaries it must not cross, and the validation rules that apply to its output.

## Conceptual Flow

```text
01 Input Documents
        ↓
02 Context Engineering
        ↓
03 Context Validation
        ↓
04 AI Generation
        ↓
05 Artifact Validation
        ↓
06 Apply
```

## Pipeline Principles

- Every pipeline has one clear responsibility.
- Every pipeline owns its outputs.
- Every pipeline has an explicit context contract.
- Every pipeline should consume the smallest sufficient context.
- Pipeline outputs are engineering artifacts, not temporary logs.
- Generated artifacts are untrusted until validated and approved.
- Human-authored and approved generated documents remain the source of truth.

## Directory Structure

- `pipelines/00_shared/` contains shared tasks and scripts.
- `pipelines/01_context_engineering/` creates and validates AI-ready context.
- Later pipelines will use validated context to generate database, backend, frontend, testing, and deployment artifacts.
