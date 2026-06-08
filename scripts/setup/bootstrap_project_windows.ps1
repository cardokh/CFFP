$ErrorActionPreference = "Stop"

$ProjectRoot = (Get-Location).Path
$ConfigFilePath = Join-Path $ProjectRoot "scripts/setup/config/bootstrap_project.json"

if (-not (Test-Path $ConfigFilePath)) {
    Write-Host "FAILED Project bootstrap failed. Missing config: scripts/setup/config/bootstrap_project.json"
    exit 1
}

$Config = Get-Content $ConfigFilePath -Raw | ConvertFrom-Json

$OutputDirectory = Join-Path $ProjectRoot $Config.outputDirectory
$SummaryFilePath = Join-Path $OutputDirectory $Config.summaryFileName
$LogFilePath = Join-Path $OutputDirectory $Config.logFileName

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$Steps = @()

function Add-Log {
    param ([string]$Message)

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFilePath -Value "[$Timestamp] $Message"
}

function Add-Step {
    param (
        [string]$Name,
        [string]$Status,
        [string]$Message
    )

    $script:Steps += [PSCustomObject]@{
        name    = $Name
        status  = $Status
        message = $Message
    }

    Add-Log "$Status - $Name - $Message"
}

function Invoke-BootstrapCommand {
    param (
        [string]$Name,
        [string]$Command
    )

    Add-Log "STARTED - $Name - $Command"

    cmd.exe /c "$Command >> `"$LogFilePath`" 2>&1"

    if ($LASTEXITCODE -ne 0) {
        $Message = "Command failed with exit code $LASTEXITCODE."
        Add-Step $Name "FAILED" $Message
        throw $Message
    }

    Add-Step $Name "PASSED" "Command completed successfully."
}

try {
    Set-Content -Path $LogFilePath -Value ""

    Add-Log "Project bootstrap started."
    Add-Log "Project root: ."

    if ($Config.steps.createVirtualEnvironment -eq $true) {
        $VirtualEnvironmentPath = Join-Path $ProjectRoot ".venv"

        if (-not (Test-Path $VirtualEnvironmentPath)) {
            Invoke-BootstrapCommand "Create virtual environment" "python -m venv .venv"
        }
        else {
            Add-Step "Create virtual environment" "SKIPPED" "Existing .venv found."
        }
    }

    $ActivateScriptPath = Join-Path $ProjectRoot ".venv/Scripts/Activate.ps1"

    if (-not (Test-Path $ActivateScriptPath)) {
        throw "Virtual environment activation script not found: .venv/Scripts/Activate.ps1"
    }

    . $ActivateScriptPath
    Add-Step "Activate virtual environment" "PASSED" "Virtual environment activated."

    $env:PYTHONPATH = $ProjectRoot
    Add-Step "Set PYTHONPATH" "PASSED" "PYTHONPATH set to project root."

    if ($Config.steps.installDependencies -eq $true) {
        Invoke-BootstrapCommand "Install dependencies" "python -m pip install -r requirements.txt"
    }

    if ($Config.steps.createDatabaseSchema -eq $true) {
        Invoke-BootstrapCommand "Create SQLite database schema" "python -m scripts.db.sqlite_create_schema"
    }

    if ($Config.steps.seedDatabase -eq $true) {
        Invoke-BootstrapCommand "Seed SQLite database" "python -m scripts.db.sqlite_seed_data"
    }

    $Summary = [PSCustomObject]@{
        status      = "PASSED"
        projectRoot = "."
        summaryFile = "scripts/setup/output/$($Config.summaryFileName)"
        logFile     = "scripts/setup/output/$($Config.logFileName)"
        steps       = $Steps
    }

    $Summary |
    ConvertTo-Json -Depth 10 |
    Set-Content -Path $SummaryFilePath -Encoding UTF8

    Write-Host "PASSED Project bootstrap completed. Summary: scripts/setup/output/$($Config.summaryFileName)"
    exit 0
}
catch {
    $ErrorMessage = $_.Exception.Message

    if (-not $ErrorMessage) {
        $ErrorMessage = "Unknown bootstrap error. Check log file."
    }

    Add-Log "FAILED - Project bootstrap failed - $ErrorMessage"

    $Summary = [PSCustomObject]@{
        status      = "FAILED"
        projectRoot = "."
        summaryFile = "scripts/setup/output/$($Config.summaryFileName)"
        logFile     = "scripts/setup/output/$($Config.logFileName)"
        error       = $ErrorMessage
        steps       = $Steps
    }

    $Summary |
    ConvertTo-Json -Depth 10 |
    Set-Content -Path $SummaryFilePath -Encoding UTF8

    Write-Host "FAILED Project bootstrap failed. Summary: scripts/setup/output/$($Config.summaryFileName)"
    exit 1
}