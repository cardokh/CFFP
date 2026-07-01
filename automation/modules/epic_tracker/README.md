# Epic Tracker Module

Epic Tracker is the experimental automation module for managing an application through a reusable software-generation pipeline.

This module separates two concerns:

- `applications/` contains application-specific input, metadata, outputs, validation results, and reports.
- `stages/` contains generic reusable pipeline stages and tasks.

The stage folders are not Agile epics. Agile epics, user stories, and implementation tasks are application artifacts produced by the Project Planning stage.

## Pipeline stages

1. Requirements & Constraints Analysis
2. Solution Design
3. Project Planning
4. Database Generation
5. Backend Generation
6. Frontend Generation
7. Testing
8. Deployment

Each application mirrors these stages so generated artifacts remain application-specific while the stage logic remains reusable.

## Current iteration

This iteration renames the generic processing area from `epics/` to `stages/` and creates a mirrored stage structure under the first application, `pipeline_management_system`.

No business logic is implemented in this iteration.
