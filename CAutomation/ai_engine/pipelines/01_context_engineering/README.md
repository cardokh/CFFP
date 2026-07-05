# Pipeline 01 - Context Engineering

Pipeline 01 converts the approved Pipeline Management module contracts into a deterministic context package for downstream automation pipelines.

This pipeline is intentionally decomposed into small, testable task units.

```text
Pipeline 01 - Context Engineering
├── Task 01 - Load Configuration
├── Task 02 - Validate Inputs
├── Task 03 - Extract Contracts
├── Task 04 - Build Context Package
├── Task 05 - Validate Context Package
└── Task 06 - Write Execution Report
```

## Run the pipeline

Run from the repository root:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/context_engineering_pipeline.py
```

## Run an individual task

Each task is independently executable from the repository root. For example:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/validate_inputs/validate_inputs.py
```

Individual tasks are intended for focused validation and debugging. In normal use, run the pipeline orchestrator.

## Configuration

The pipeline-level configuration is stored in:

```text
CAutomation/ai_engine/pipelines/01_context_engineering/config/context_engineering_pipeline.json
```

The reusable task definition registry is stored separately in:

```text
CAutomation/ai_engine/pipelines/01_context_engineering/config/task_definitions.json
```

Each task has its own small task config under its task folder. The task config points to the pipeline config and declares the task identity/version.

Task folders are reusable task definitions. The pipeline configuration now contains only the pipeline-specific task instances and a reference to the task registry. The registry defines reusable implementations; the pipeline instances define ordering, state files, blocking behaviour, and per-run configuration.

## Output

The context package is written to the configured project output folder:

```text
CAutomation/projects/cffp/output/context_packages/cffp_pipeline_management_context_package/
```

Pipeline runtime state and task reports are written to the latest-run folder:

```text
CAutomation/ai_engine/pipelines/01_context_engineering/output/current_run/
```

After each run, the latest-run folder is archived to execution history:

```text
CAutomation/ai_engine/pipelines/01_context_engineering/output/executions/<execution_id>/
```

The pipeline also writes timestamped reports to the orchestrator and task output folders, following the shared scripting infrastructure.

## Scope

This pipeline is scoped to the CAutomation first deliverable. The Pipeline Management module is the reference module used to validate the automation package.

## Validation Gate

Task 02 - Validate Inputs is a hard perimeter gate. It validates the manually authored module specification documents before extraction or context compilation starts. Invalid, incomplete, ambiguous, inconsistent, or template-nonconformant inputs stop downstream processing. The pipeline still runs the reporting path so the final execution report contains machine-readable gap details instead of failing with an unhandled crash.

Task 05 - Validate Context Package remains separate. Task 02 validates raw human-authored documents; Task 05 validates the compiled context package.

