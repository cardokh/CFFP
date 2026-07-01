# Project Planning / Epic Tracker

## Purpose

Convert requirements and solution design into Agile execution artifacts: epics, user stories, implementation tasks, dependencies, test suites, test cases, and sprint-ready plans.

## Position in the lifecycle

This epic is part of the ordered end-to-end software delivery pipeline. The numeric folder prefix defines the canonical execution order.

## Responsibilities

- Consume the validated output contract from the previous epic.
- Produce a complete and validated output contract for the next epic.
- Record assumptions, decisions, validation results, and reports.
- Stop the pipeline if critical required information is missing.

## Inputs

Inputs live under `inputs/` when implementation begins. For now, this folder is architectural only.

## Outputs

Primary output contract: **Project Plan Package**.

Outputs live under `outputs/` when implementation begins. The output must be complete enough for the next epic to execute without asking additional questions.

## User Stories

User stories will be documented under `user_stories/`.

## Implementation Tasks

Implementation tasks will be documented under `implementation_tasks/`.

## Test Suites

Test suites will be documented under `test_suites/`.

## Test Cases

Test cases will be documented under `test_cases/`.

## Validation

Validation rules and validation outcomes will be documented under `validation/`.

The validation gate must pass before the next numbered epic may begin.

## Reports

Epic-specific reports will be documented under `reports/`.

## Dependencies

This epic depends on the validated output from the previous numbered epic, except Epic 1, which depends on user/client/project input.

## Example folder structure

```text
03_project_planning/
  inputs/
  outputs/
  user_stories/
  implementation_tasks/
  test_suites/
  test_cases/
  validation/
  reports/
  README.md
```

## Future implementation notes

This is where the Epic Tracker concept naturally belongs as a planning capability.

This iteration is architectural only. No business logic, generation logic, migration logic, or executable pipeline code is introduced here.
