# Validation Rules

Context Engineering validation protects downstream generation from weak, ambiguous, or inconsistent input.

## Required Validation

The pipeline should validate:

- required folders exist
- required input categories are present
- documents are readable
- obvious duplicate documents are detected
- required module information exists
- references are resolvable where practical
- conflicting decisions are reported
- source files are recorded in provenance
- output files follow the Context Package contract

## Blocking Conditions

The pipeline must fail when:

- project input root is missing
- required project identity is missing
- no client/project intent is available
- no module or generation target is available
- required engineering constraints are absent for a generation run
- output package manifest cannot be produced
- provenance cannot be recorded

## Non-Blocking Warnings

The pipeline may warn when:

- some optional documents are missing
- requirements are vague
- acceptance criteria are incomplete
- personas are missing
- diagrams or external references cannot be resolved
- old documents appear to duplicate newer documents

## Conflict Handling

The pipeline must not silently choose between conflicting instructions.

Conflicts must be reported with:

- conflicting files
- conflicting statements where practical
- affected downstream stages
- recommended human decision
