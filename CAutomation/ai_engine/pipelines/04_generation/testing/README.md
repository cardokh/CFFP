# 03 Generation / Testing

Testing generation produces unit, integration, endpoint, GUI, and regression tests where required.

## Consumes

- validated Context Package
- implementation plan
- approved outputs from earlier generation targets when required

## Produces

- generated artifacts owned by this target
- artifact manifest
- generation report
- provenance metadata

## Boundary

This generator must only produce artifacts for its own target area.

It must not apply files to the live repository. Application is owned by `06_apply`.
