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
$LogCache = New-Object System.Collections.Generic.List[string]

function Add-Log {
    param ([string]$Message)

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $script:LogCache.Add("[$Timestamp] $Message") | Out-Null
}

function Flush-Log {
    if ($script:LogCache.Count -gt 0) {
        $script:LogCache | Add-Content -Path $LogFilePath -Encoding UTF8
        $script:LogCache.Clear()
    }
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
        [string]$Executable,
        [string[]]$ArgList
    )

    Add-Log "STARTED - $Name - $Executable $($ArgList -join ' ')"

    $Output = & $Executable @ArgList 2>&1
    $ExitCode = $LASTEXITCODE

    foreach ($Line in $Output) {
        Add-Log $Line.ToString()
    }

    if ($ExitCode -ne 0) {
        $Message = "Command failed with exit code $ExitCode."
        Add-Step $Name "FAILED" $Message
        Flush-Log
        throw $Message
    }

    Add-Step $Name "PASSED" "Command completed successfully."
    Flush-Log
}

function Get-FileMd5Hash {
    param ([string]$Path)

    if (-not (Test-Path $Path)) {
        return $null
    }

    return (Get-FileHash -Path $Path -Algorithm MD5).Hash
}

function Install-DependenciesIfNeeded {
    $RequirementsPath = Join-Path $ProjectRoot "requirements.txt"
    $VirtualEnvironmentPath = Join-Path $ProjectRoot ".venv"
    $HashFilePath = Join-Path $VirtualEnvironmentPath ".requirements.hash"

    if (-not (Test-Path $RequirementsPath)) {
        Add-Step "Install dependencies" "SKIPPED" "requirements.txt not found."
        return
    }

    $CurrentHash = Get-FileMd5Hash $RequirementsPath
    $PreviousHash = $null

    if (Test-Path $HashFilePath) {
        $PreviousHash = (Get-Content $HashFilePath -Raw).Trim()
    }

    if ($CurrentHash -eq $PreviousHash) {
        Add-Step "Install dependencies" "SKIPPED" "requirements.txt unchanged."
        return
    }

    Invoke-BootstrapCommand `
        -Name "Install dependencies" `
        -Executable "python" `
        -ArgList @("-m", "pip", "install", "-r", "requirements.txt")

    Set-Content -Path $HashFilePath -Value $CurrentHash -Encoding UTF8
    Add-Log "UPDATED - requirements hash cache - .venv/.requirements.hash"
    Flush-Log
}

try {
    Set-Content -Path $LogFilePath -Value "" -Encoding UTF8

    Add-Log "Project bootstrap started."
    Add-Log "Project root: ."
    Flush-Log

    if ($Config.steps.createVirtualEnvironment -eq $true) {
        $VirtualEnvironmentPath = Join-Path $ProjectRoot ".venv"

        if (-not (Test-Path $VirtualEnvironmentPath)) {
            Invoke-BootstrapCommand `
                -Name "Create virtual environment" `
                -Executable "python" `
                -ArgList @("-m", "venv", ".venv")
        }
        else {
            Add-Step "Create virtual environment" "SKIPPED" "Existing .venv found."
            Flush-Log
        }
    }

    $ActivateScriptPath = Join-Path $ProjectRoot ".venv/Scripts/Activate.ps1"

    if (-not (Test-Path $ActivateScriptPath)) {
        throw "Virtual environment activation script not found: .venv/Scripts/Activate.ps1"
    }

    . $ActivateScriptPath
    Add-Step "Activate virtual environment" "PASSED" "Virtual environment activated."
    Flush-Log

    $env:PYTHONPATH = $ProjectRoot
    Add-Step "Set PYTHONPATH" "PASSED" "PYTHONPATH set to project root."
    Flush-Log

    if ($Config.steps.installDependencies -eq $true) {
        Install-DependenciesIfNeeded
    }

    if ($Config.steps.createDatabaseSchema -eq $true) {
        Invoke-BootstrapCommand `
            -Name "Create SQLite database schema" `
            -Executable "python" `
            -ArgList @("-m", "scripts.db.sqlite_create_schema")
    }

    if ($Config.steps.seedDatabase -eq $true) {
        Invoke-BootstrapCommand `
            -Name "Seed SQLite database" `
            -Executable "python" `
            -ArgList @("-m", "scripts.db.sqlite_seed_data")
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

    Add-Log "Project bootstrap completed successfully."
    Flush-Log

    Write-Host "PASSED Project bootstrap completed. Summary: scripts/setup/output/$($Config.summaryFileName)"
    exit 0
}
catch {
    $ErrorMessage = $_.Exception.Message

    if (-not $ErrorMessage) {
        $ErrorMessage = "Unknown bootstrap error. Check log file."
    }

    Add-Log "FAILED - Project bootstrap failed - $ErrorMessage"
    Flush-Log

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