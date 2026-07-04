# 06 Verification

Verification confirms that applied artifacts work in the target project.

## Consumes

- applied repository/workspace
- validation report
- apply report
- verification plan

## Produces

```text
verification-output/
├── verification-report.json
├── test-results/
└── provenance.json
```

## Responsibility

Verification may include:

- build checks
- compile checks
- unit tests
- integration tests
- endpoint tests
- GUI workflow tests
- smoke tests
- regression checks

## Rule

A generation run is not complete merely because files were applied.

It is complete only when the intended behavior has been verified and human approval has been obtained where required.
