<#
Validates CFFP Automation Factory task execution with one command.
Run from the repository root after the backend is running and bootstrap has completed.

Usage:
  powershell -ExecutionPolicy Bypass -File scripts/tests/validate_story2_task_execution.ps1

Optional:
  powershell -ExecutionPolicy Bypass -File scripts/tests/validate_story2_task_execution.ps1 -BaseUrl "http://localhost:8000"
#>

param(
    [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"
$Failures = New-Object System.Collections.Generic.List[string]

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Write-Pass {
    param([string]$Message)
    Write-Host "PASS: $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "FAIL: $Message" -ForegroundColor Red
    $Failures.Add($Message) | Out-Null
}

function Assert-FileExists {
    param([string]$Path)
    if (Test-Path $Path) {
        Write-Pass "Found $Path"
    }
    else {
        Write-Fail "Missing $Path"
    }
}

function Invoke-JsonRequest {
    param(
        [string]$Method,
        [string]$Url
    )

    return Invoke-RestMethod -Method $Method -Uri $Url -ContentType "application/json"
}

function Get-TaskName {
    param($Task)
    if ($null -ne $Task.taskName) { return $Task.taskName }
    if ($null -ne $Task.name) { return $Task.name }
    return $null
}

function Get-TaskId {
    param($Task)
    if ($null -ne $Task.taskId) { return $Task.taskId }
    if ($null -ne $Task.id) { return $Task.id }
    return $null
}

function Get-ExecutionId {
    param($Execution)
    if ($null -ne $Execution.executionId) { return $Execution.executionId }
    if ($null -ne $Execution.id) { return $Execution.id }
    return $null
}

function Invoke-TaskExecutionValidation {
    param(
        [array]$Tasks,
        [string]$TaskName,
        [array]$ExpectedSections
    )

    $selectedTask = $Tasks | Where-Object { (Get-TaskName $_) -eq $TaskName } | Select-Object -First 1
    if ($null -eq $selectedTask) {
        Write-Fail "$TaskName task was not found in CCore task registry"
        return
    }

    $selectedTaskId = Get-TaskId $selectedTask
    if ([string]::IsNullOrWhiteSpace($selectedTaskId)) {
        Write-Fail "$TaskName task did not include a task id"
        return
    }

    Write-Pass "$TaskName task found: $selectedTaskId"

    Write-Step "Executing $TaskName task through CCore"
    $encodedTaskId = [System.Uri]::EscapeDataString($selectedTaskId)
    $executeResponse = Invoke-JsonRequest -Method "POST" -Url "$BaseUrl/api/ccore/tasks/$encodedTaskId/execute"
    if (-not $executeResponse.success) {
        Write-Fail "$TaskName execute endpoint returned success=false"
        return
    }

    if ($null -eq $executeResponse.execution) {
        Write-Fail "$TaskName execute endpoint did not return an execution object"
        return
    }

    $executionId = Get-ExecutionId $executeResponse.execution
    Write-Pass "$TaskName execution completed with status: $($executeResponse.execution.status)"
    Write-Pass "$TaskName execution id: $executionId"

    if ($null -eq $executeResponse.execution.report) {
        Write-Fail "$TaskName execution did not include a report"
    }
    else {
        Write-Pass "$TaskName execution report returned"
        $sectionNames = @($executeResponse.execution.report.sections | ForEach-Object { $_.name })
        foreach ($expectedSection in $ExpectedSections) {
            if ($sectionNames -contains $expectedSection) {
                Write-Pass "$TaskName report contains $expectedSection section"
            }
            else {
                Write-Fail "$TaskName report missing $expectedSection section"
            }
        }
    }

    Write-Step "Checking $TaskName execution history"
    $historyResponse = Invoke-JsonRequest -Method "GET" -Url "$BaseUrl/api/ccore/tasks/$encodedTaskId/executions"
    if (-not $historyResponse.success) {
        Write-Fail "$TaskName execution history endpoint returned success=false"
    }
    elseif ($null -eq $historyResponse.executions -or $historyResponse.executions.Count -lt 1) {
        Write-Fail "$TaskName execution history did not contain any executions"
    }
    else {
        Write-Pass "$TaskName execution history contains $($historyResponse.executions.Count) execution(s)"
    }
}

Write-Host "CFFP Automation Factory validation: CCore executable tasks"
Write-Host "Repository: $(Get-Location)"
Write-Host "Backend URL: $BaseUrl"

Write-Step "Checking Automation Factory files"
Assert-FileExists "backend/src/api/route_registry.py"
Assert-FileExists "backend/src/ccore/application/service_factory.py"
Assert-FileExists "backend/src/ccore/tasks/task_routes.py"
Assert-FileExists "backend/src/ccore/tasks/task_service.py"
Assert-FileExists "backend/src/ccore/tasks/task_execution.py"
Assert-FileExists "backend/src/ccore/tasks/task_execution_constants.py"
Assert-FileExists "backend/src/ccore/tasks/task_execution_mapper.py"
Assert-FileExists "backend/src/ccore/tasks/task_execution_repository.py"
Assert-FileExists "backend/src/ccore/tasks/task_execution_repository_contract.py"
Assert-FileExists "backend/src/ccore/tasks/task_execution_runner.py"
Assert-FileExists "backend/tests/test_ccore_task_execution_framework_contract.py"
Assert-FileExists "scripts/db/postgres/config/entities.json"
Assert-FileExists "scripts/db/postgres/config/postgres_create_schema.json"
Assert-FileExists "scripts/db/postgres/config/postgres_seed_data.json"

Write-Step "Compiling Automation Factory Python files"
try {
    $PythonFiles = @(
        "backend/src/api/route_registry.py",
        "backend/src/ccore/application/service_factory.py",
        "backend/src/ccore/tasks/task_routes.py",
        "backend/src/ccore/tasks/task_service.py",
        "backend/src/ccore/tasks/task_execution.py",
        "backend/src/ccore/tasks/task_execution_constants.py",
        "backend/src/ccore/tasks/task_execution_mapper.py",
        "backend/src/ccore/tasks/task_execution_repository.py",
        "backend/src/ccore/tasks/task_execution_repository_contract.py",
        "backend/src/ccore/tasks/task_execution_runner.py",
        "backend/tests/test_ccore_task_execution_framework_contract.py"
    )

    python -m py_compile @PythonFiles
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "Automation Factory Python files compiled"
    }
    else {
        Write-Fail "Python compilation failed with exit code $LASTEXITCODE"
    }
}
catch {
    Write-Fail "Could not compile Automation Factory Python files: $($_.Exception.Message)"
}

Write-Step "Checking CCore task API"
try {
    $tasksResponse = Invoke-JsonRequest -Method "GET" -Url "$BaseUrl/api/ccore/tasks"
    if (-not $tasksResponse.success) {
        Write-Fail "CCore task API returned success=false"
    }
    else {
        Write-Pass "CCore task API responded"
        Invoke-TaskExecutionValidation -Tasks $tasksResponse.tasks -TaskName "Validate Project" -ExpectedSections @(
            "configuration",
            "python_compilation",
            "javascript_syntax",
            "unit_tests"
        )
        Invoke-TaskExecutionValidation -Tasks $tasksResponse.tasks -TaskName "Inspect Project" -ExpectedSections @(
            "project_structure",
            "naming_conventions",
            "hardcoded_paths",
            "automation_factory_contracts"
        )
    }
}
catch {
    Write-Fail "Backend/API validation failed: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "========================================"
if ($Failures.Count -eq 0) {
    Write-Host "AUTOMATION FACTORY VALIDATION PASSED" -ForegroundColor Green
    exit 0
}

Write-Host "AUTOMATION FACTORY VALIDATION FAILED" -ForegroundColor Red
foreach ($Failure in $Failures) {
    Write-Host "- $Failure" -ForegroundColor Red
}
exit 1
