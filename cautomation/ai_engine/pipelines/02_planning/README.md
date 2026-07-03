# 02 Planning

Planning converts a validated Context Package into an implementation plan.

This stage does not generate source code.

## Consumes

- Context Package from `01_context_engineering`
- approved outputs from previous planning runs when updating existing work

## Produces

Typical outputs:

```text
planning-output/
├── implementation-plan.md
├── generation-targets.json
├── dependency-plan.md
├── validation-plan.md
└── provenance.json
```

## Responsibility

Planning answers:

- what should be generated
- which generators should run
- in what order
- what each generator should consume
- what validation is required
- what risks or blockers exist

## Non-Goals

This stage must not:

- generate source code
- apply artifacts
- bypass context validation
- silently invent missing business decisions
