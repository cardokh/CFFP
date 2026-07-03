# 01 Context Engineering

Context Engineering is the first real platform pipeline.

It replaces the earlier idea of a narrow `requirements` pipeline.

The human team provides project knowledge under `projects/<project>/input/`. This pipeline validates, organizes, compresses, orders, and packages that knowledge into AI-ready context packages for downstream stages.

## Responsibility

This pipeline prepares context. It does not generate application code.

## Input

Typical input sources include:

- client vision
- problem statement
- goals and success criteria
- users and personas
- workflows
- acceptance criteria
- engineering constraints
- architecture principles
- technology constraints
- ADRs
- module definitions
- security constraints
- testing expectations

## Output

The primary output is a validated context package.

Example:

```text
context-package/
├── manifest.json
├── global-context.md
├── project-context.md
├── module-context.md
├── architecture-context.md
├── constraints-context.md
├── generation-context.md
└── provenance.json
```

## Non-Goals

This pipeline must not:

- generate source code
- invent missing requirements
- silently resolve conflicts
- read arbitrary repository files
- depend on conversation history
- bypass validation

## Core Concepts

- **Selection**: include only relevant artifacts.
- **Compression**: distill large inputs into reusable context.
- **Ordering**: place foundational rules before task-specific instructions.
- **Isolation**: produce scoped context for downstream stages.
- **Provenance**: record which inputs produced each context package.
