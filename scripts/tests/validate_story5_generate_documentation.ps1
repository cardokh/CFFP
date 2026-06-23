$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[story5] $Message"
}

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $ProjectRoot
$BackendRoot = Join-Path $ProjectRoot "backend"
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$BackendRoot;$env:PYTHONPATH"
} else {
    $env:PYTHONPATH = $BackendRoot
}

Write-Step "Compiling changed CCore Python files"
python -m compileall -q `
    backend/src/ccore/tasks/task_execution_constants.py `
    backend/src/ccore/tasks/task_execution_runner.py `
    backend/tests/test_ccore_automation_factory_seed_data.py `
    backend/tests/test_ccore_task_execution_framework_contract.py

Write-Step "Running Story 5 contract tests"
python -m pytest `
    backend/tests/test_ccore_automation_factory_seed_data.py `
    backend/tests/test_ccore_task_execution_framework_contract.py `
    -q

Write-Step "Executing Generate Documentation runner directly"
$PythonScript = @'
from pathlib import Path
from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_execution_constants import CCORE_TASK_EXECUTION_STATUS_SUCCEEDED
from backend.src.ccore.tasks.task_execution_runner import CCoreTaskRunnerRegistry, GENERATE_DOCUMENTATION_TASK_NAME

project_root = Path.cwd()
task = CCoreTask(
    task_id="44444444-4444-4444-4444-444444444444",
    task_name=GENERATE_DOCUMENTATION_TASK_NAME,
    status_code="PENDING",
)
runner = CCoreTaskRunnerRegistry(project_root=project_root).get_runner_for_task(task)
if runner is None:
    raise SystemExit("Generate Documentation runner was not registered.")

result = runner.execute(task)
if result["status_code"] != CCORE_TASK_EXECUTION_STATUS_SUCCEEDED:
    raise SystemExit(f"Generate Documentation failed: {result}")

documentation_path = project_root / "docs" / "automation_factory" / "automation_factory_capabilities.md"
if not documentation_path.is_file():
    raise SystemExit("Expected generated documentation file was not created.")

text = documentation_path.read_text(encoding="utf-8")
required_fragments = [
    "# Automation Factory Capabilities",
    "Generate Documentation",
    "CCore -> Prefect -> Task Runner -> Structured Report -> Execution History",
]
missing = [fragment for fragment in required_fragments if fragment not in text]
if missing:
    raise SystemExit(f"Generated documentation is missing expected content: {missing}")

print("Generate Documentation runner validated successfully.")
'@
$PythonScript | python -

Write-Step "Story 5 validation completed successfully"
