# Output Contract

The Context Engineering pipeline produces validated context packages for downstream stages.

## Primary Output

```text
context-package/
```

The package must be deterministic, traceable, and reviewable.

## Required Output Qualities

The output must be:

- scoped
- ordered
- validated
- traceable
- reusable
- independent of conversation history
- suitable for AI planning and generation

## Consumers

The primary consumers are:

- `02_planning`
- `03_generation/db`
- `03_generation/backend`
- `03_generation/frontend`
- `03_generation/testing`
- `03_generation/deployment`
- `04_validation`

## Output Rule

Downstream pipelines should consume the Context Package and approved outputs from previous stages.

They should not go back to the original project input documents unless the pipeline contract explicitly allows it.
