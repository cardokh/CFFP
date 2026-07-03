# Context Package

A Context Package is the formal output of the Context Engineering pipeline.

It is the boundary between human-authored project knowledge and downstream AI-assisted planning/generation.

Downstream pipelines consume Context Packages instead of reading arbitrary source documents directly.

## Required Files

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

## manifest.json

Describes the package itself.

Required information:

- package id
- project id
- package type
- creation timestamp
- source input root
- included context files
- validation status
- downstream consumers

## global-context.md

Contains platform-wide principles that apply to all projects unless overridden by approved project input.

Examples:

- AI output is untrusted until validated
- use smallest sufficient context
- preserve provenance
- prefer whole artifacts
- no arbitrary repository reads

## project-context.md

Contains project-specific goals and constraints.

Examples:

- project vision
- product goals
- target users
- success criteria
- scope and out-of-scope

## module-context.md

Contains module-specific information.

Examples:

- module purpose
- core workflows
- domain concepts
- user stories
- acceptance criteria

## architecture-context.md

Contains architectural constraints and decisions.

Examples:

- technology stack
- architectural principles
- ADR summaries
- integration constraints
- security model

## constraints-context.md

Contains hard rules that downstream generators must obey.

Examples:

- forbidden technologies
- required validation gates
- naming conventions
- security constraints
- dependency restrictions

## generation-context.md

Contains AI-facing instructions for downstream planning and generation.

This file should be deterministic and ordered.

Recommended order:

1. Global rules
2. Project rules
3. Architecture rules
4. Module rules
5. Current generation objective
6. Output expectations
7. Validation requirements

## provenance.json

Records how the package was produced.

Required information:

- source files used
- source file checksums where practical
- source file categories
- transformations performed
- excluded files and reasons
- detected warnings
- validation results
- producing pipeline version
