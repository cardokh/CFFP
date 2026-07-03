# 05 Apply

Apply moves validated artifacts into the target repository or target workspace.

## Consumes

- validation-approved artifacts
- artifact manifest
- apply plan

## Produces

```text
apply-output/
├── apply-report.json
├── changed-files.md
└── provenance.json
```

## Responsibility

Apply is responsible for controlled file operations only.

It must:

- respect approved paths
- avoid uncontrolled overwrite
- report every changed file
- support dry-run mode where practical
- preserve provenance

## Non-Goals

Apply does not decide whether generated content is correct. That is handled by validation and verification.
