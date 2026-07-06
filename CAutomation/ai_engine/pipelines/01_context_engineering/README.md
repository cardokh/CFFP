# Pipeline 01 - Context Engineering

Pipeline 01 converts the approved Pipeline Management module contracts into a deterministic context package for downstream automation pipelines.

This pipeline is intentionally decomposed into small, testable task units.

```text
Pipeline 01 - Context Engineering
├── Task 01 - Load Configuration
├── Task 02 - Normalize Input Documents
├── Task 03 - Extract Contracts
├── Task 04 - Build Context Package
├── Task 05 - Validate Context Package
└── Task 06 - Write Execution Report
```

## Quick Start Commands

Run all commands from the repository root.

### Pipeline 01 - Context Engineering

Execute Pipeline 01 - Context Engineering:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/run_pipeline.py
```

Execute Pipeline 01 - Context Engineering tests:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/run_pipeline_tests.py
```

### Task 01 - Load Configuration

Execute Task 01 - Load Configuration:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/load_configuration/run_task.py
```

Execute Task 01 - Load Configuration tests:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/load_configuration/run_task_tests.py
```

### Task 02 - Normalize Input Documents

Execute Task 02 - Normalize Input Documents:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/normalize_input_documents/run_task.py
```

Execute Task 02 - Normalize Input Documents tests:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/normalize_input_documents/run_task_tests.py
```

### Task 03 - Extract Contracts

Execute Task 03 - Extract Contracts:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/extract_contracts/run_task.py
```

Execute Task 03 - Extract Contracts tests:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/extract_contracts/run_task_tests.py
```

### Task 04 - Build Context Package

Execute Task 04 - Build Context Package:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/build_context_package/run_task.py
```

Execute Task 04 - Build Context Package tests:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/build_context_package/run_task_tests.py
```

### Task 05 - Validate Context Package

Execute Task 05 - Validate Context Package:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/validate_context_package/run_task.py
```

Execute Task 05 - Validate Context Package tests:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/validate_context_package/run_task_tests.py
```

### Task 06 - Write Execution Report

Execute Task 06 - Write Execution Report:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/write_execution_report/run_task.py
```

Execute Task 06 - Write Execution Report tests:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/write_execution_report/run_task_tests.py
```

## Run the pipeline

Run from the repository root:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/run_pipeline.py
```

## Run an individual task

Each task is independently executable from the repository root. For example:

```bash
python CAutomation/ai_engine/pipelines/01_context_engineering/tasks/normalize_input_documents/run_task.py
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
CAutomation/projects/pipeline_management/output/context_packages/pipeline_management_pipeline_management_context_package/
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

Task 02 - Normalize Input Documents is the hard minimum viable input quality gate. It validates the manually authored source documents, verifies supported source formats, extracts machine-readable content, writes the canonical `normalized_input/` workspace, and stops downstream processing if the minimum trusted input contract is not met. After Task 02 succeeds, downstream tasks must consume `normalized_input/` instead of raw `input/` source files.

For the Pipeline Management reference project, Task 02 now normalizes the required project-level client contract, project-level engineering contract, module SRS, and module ATS into one canonical workspace. PDF is the primary execution and test path for this phase. DOCX and Markdown normalizers remain available as existing support, but current Task 02 engineering effort is PDF-first.

Task 02 delegates source-format parsing to document normalizers. Current normalizer implementations cover DOCX, PDF, and Markdown, while the downstream pipeline continues to consume only the generated `normalized_input/` Markdown and metadata.

Task 05 - Validate Context Package remains separate. Task 02 validates and normalizes source documents; Task 05 validates the compiled context package.

