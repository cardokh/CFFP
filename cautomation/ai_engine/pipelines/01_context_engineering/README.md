# 01 Context Engineering

Context Engineering is the first executable pipeline in the CAutomation package.

Its first runnable task is:

```text
01_context_engineering/
└── tasks/
    └── context_engineering/
        ├── context_engineering.py
        ├── config/
        │   └── context_engineering.json
        └── output/
```

## Responsibility

The `context_engineering` task reads the approved Pipeline Management module SRS and ATS and produces a deterministic context package for downstream planning and generation.

It does not generate application code and it does not apply changes to the repository.

## Run

Run from the repository root:

```bash
python cautomation/ai_engine/pipelines/01_context_engineering/tasks/context_engineering/context_engineering.py
```

## Configuration

All project/module/path settings are loaded from:

```text
cautomation/ai_engine/pipelines/01_context_engineering/tasks/context_engineering/config/context_engineering.json
```

The task must not hard-code project IDs, module IDs, input paths, output paths, or file names.

## Outputs

The task writes two kinds of output:

```text
cautomation/projects/cffp/output/context_packages/<context-package-id>/
```

and an execution report under the task output folder:

```text
cautomation/ai_engine/pipelines/01_context_engineering/tasks/context_engineering/output/
```

The execution report follows the repository scripting infrastructure provided by `scripts/shared/base_script.py`.
