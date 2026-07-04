# Pipeline 01 Tasks

The Context Engineering pipeline is composed from reusable task definitions:

1. `load_configuration` - validates pipeline-level configuration.
2. `validate_inputs` - validates required project/module inputs and records non-blocking warnings.
3. `extract_contracts` - extracts SRS and ATS DOCX contracts into deterministic Markdown state files.
4. `build_context_package` - builds the generated context package.
5. `validate_context_package` - validates the generated package artifacts.
6. `write_execution_report` - aggregates task state into the final execution report.

Each task definition:

- extends the shared `BaseScript` infrastructure,
- has its own `config/` folder,
- writes its own report to its local `output/` folder,
- writes shared pipeline state to `01_context_engineering/output/current_run/`,
- can be executed independently for focused debugging.


The pipeline config creates task instances from these definitions. A task instance is the configured use of a reusable task inside Pipeline 01, including sequence, state file, blocking behaviour, and optional instance configuration.
