<#
Validates CFFP Automation Factory Story 2 task execution with one command.
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

Write-Host "CFFP Story 2 validation: CCore task execution framework"
Write-Host "Repository: $(Get-Location)"
Write-Host "Backend URL: $BaseUrl"

Write-Step "Checking Story 2 files"
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

Write-Step "Compiling Story 2 Python files"
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
        Write-Pass "Story 2 Python files compiled"
    }
    else {
        Write-Fail "Python compilation failed with exit code $LASTEXITCODE"
    }
}
catch {
    Write-Fail "Could not compile Story 2 Python files: $($_.Exception.Message)"
}

Write-Step "Checking CCore task API"
try {
    $tasksResponse = Invoke-JsonRequest -Method "GET" -Url "$BaseUrl/api/ccore/tasks"
    if (-not $tasksResponse.success) {
        Write-Fail "CCore task API returned success=false"
    }
    else {
        Write-Pass "CCore task API responded"
    }

    $validateTask = $tasksResponse.tasks | Where-Object { (Get-TaskName $_) -eq "Validate Project" } | Select-Object -First 1
    if ($null -eq $validateTask) {
        Write-Fail "Validate Project task was not found in CCore task registry"
    }
    else {
        $validateTaskId = Get-TaskId $validateTask
        if ([string]::IsNullOrWhiteSpace($validateTaskId)) {
            Write-Fail "Validate Project task did not include a task id"
        }
        else {
            Write-Pass "Validate Project task found: $validateTaskId"

            Write-Step "Executing Validate Project task through CCore"
            $encodedTaskId = [System.Uri]::EscapeDataString($validateTaskId)
            $executeResponse = Invoke-JsonRequest -Method "POST" -Url "$BaseUrl/api/ccore/tasks/$encodedTaskId/execute"
            if (-not $executeResponse.success) {
                Write-Fail "CCore execute endpoint returned success=false"
            }
            elseif ($null -eq $executeResponse.execution) {
                Write-Fail "CCore execute endpoint did not return an execution object"
            }
            else {
                $executionId = Get-ExecutionId $executeResponse.execution
                Write-Pass "Execution completed with status: $($executeResponse.execution.status)"
                Write-Pass "Execution id: $executionId"

                if ($null -eq $executeResponse.execution.report) {
                    Write-Fail "Execution did not include a report"
                }
                else {
                    Write-Pass "Execution report returned"
                }
            }

            Write-Step "Checking CCore execution history"
            $historyResponse = Invoke-JsonRequest -Method "GET" -Url "$BaseUrl/api/ccore/tasks/$encodedTaskId/executions"
            if (-not $historyResponse.success) {
                Write-Fail "CCore execution history endpoint returned success=false"
            }
            elseif ($null -eq $historyResponse.executions -or $historyResponse.executions.Count -lt 1) {
                Write-Fail "CCore execution history did not contain any executions"
            }
            else {
                Write-Pass "CCore execution history contains $($historyResponse.executions.Count) execution(s)"
            }
        }
    }
}
catch {
    Write-Fail "Backend/API validation failed: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "========================================"
if ($Failures.Count -eq 0) {
    Write-Host "STORY 2 VALIDATION PASSED" -ForegroundColor Green
    exit 0
}

Write-Host "STORY 2 VALIDATION FAILED" -ForegroundColor Red
foreach ($Failure in $Failures) {
    Write-Host "- $Failure" -ForegroundColor Red
}
exit 1
