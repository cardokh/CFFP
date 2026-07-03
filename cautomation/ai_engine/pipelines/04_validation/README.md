# 04 Validation

Validation checks generated artifacts before they are applied.

## Consumes

- Context Package
- implementation plan
- generated artifacts
- artifact manifests
- generation reports

## Produces

```text
validation-output/
├── validation-report.json
├── validation-summary.md
└── provenance.json
```

## Responsibility

Validation checks:

- artifact ownership
- manifest completeness
- path safety
- contract compliance
- required files
- forbidden files
- architectural constraints
- obvious security violations
- hard-coded path issues
- test expectations where practical

## Rule

Generated artifacts are untrusted until validation passes.
