# Context Engineering Pipeline Input Contract

## Purpose

This document defines the inputs that the Context Engineering Pipeline may consume.

The pipeline must only use explicit, approved project inputs and approved upstream pipeline outputs. It must not depend on conversation history or implicit assumptions.

## Allowed Inputs

For a project with id `<projectId>`, the pipeline may read:

```text
cautomation/projects/<projectId>/README.md
cautomation/projects/<projectId>/project.json
cautomation/projects/<projectId>/input/client/**
cautomation/projects/<projectId>/input/engineering/**
cautomation/projects/<projectId>/input/modules/**
```

Later iterations may allow approved outputs from earlier pipeline runs, but those outputs must be explicitly declared in the pipeline configuration before use.

## Client Input

`input/client/` may contain documents such as:

- product vision,
- problem statement,
- goals and success criteria,
- users and personas,
- workflows,
- acceptance expectations,
- domain terminology,
- externally supplied requirements.

Client input describes what should be built and why.

## Engineering Input

`input/engineering/` may contain documents such as:

- architecture principles,
- technology constraints,
- security and access-control constraints,
- data and integration constraints,
- deployment expectations,
- definition of done,
- quality and testing expectations.

Engineering input describes how the project must be constrained and validated.

## Module Input

`input/modules/` may contain one folder per module.

Each module may contain documents such as:

- module overview,
- domain model,
- user stories,
- acceptance criteria,
- workflow descriptions,
- module-specific constraints.

Module input describes bounded areas of functionality.

## Forbidden Inputs

The pipeline must not read:

- arbitrary source code,
- arbitrary files from `backend/`, `frontend/`, `generated/`, `runtime/`, or old `docs/`,
- local IDE state,
- previous chat history,
- unapproved temporary files,
- provider-specific memory files,
- or internet content.

Any additional input source must be added to this contract before the pipeline is allowed to consume it.

## Input Failure Conditions

The pipeline must fail if:

- `project.json` is missing,
- the project input directory is missing,
- required project metadata is missing,
- no project input documents exist,
- an input file cannot be read,
- an input file type is unsupported,
- or a required input category is empty when the downstream task requires it.
