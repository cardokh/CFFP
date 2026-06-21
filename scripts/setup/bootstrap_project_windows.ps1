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
$RequirementsHashFilePath = Join-Path $ProjectRoot ".venv/.requirements.hash"

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$Steps = @()
$LogCache = New-Object System.Collections.Generic.List[string]

function Add-Log {
    param ([string]$Message)

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $script:LogCache.Add("[$Timestamp] $Message") | Out-Null
}

function Flush-Log {
    $LogDirectory = Split-Path -Parent $LogFilePath
    New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null
    Set-Content -Path $LogFilePath -Value $script:LogCache -Encoding UTF8
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
    Flush-Log
}

function Test-StepEnabled {
    param (
        [string]$StepName,
        [bool]$DefaultValue = $false
    )

    if ($null -eq $Config.steps) {
        return $DefaultValue
    }

    $StepProperty = $Config.steps.PSObject.Properties[$StepName]

    if ($null -eq $StepProperty) {
        return $DefaultValue
    }

    return ($StepProperty.Value -eq $true)
}

function Invoke-BootstrapCommand {
    param (
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments
    )

    $RenderedCommand = "$Executable $($Arguments -join ' ')"
    Add-Log "STARTED - $Name - $RenderedCommand"

    $StdoutFilePath = Join-Path $OutputDirectory "bootstrap_command_stdout.tmp"
    $StderrFilePath = Join-Path $OutputDirectory "bootstrap_command_stderr.tmp"

    if (Test-Path $StdoutFilePath) {
        Remove-Item $StdoutFilePath -Force
    }

    if (Test-Path $StderrFilePath) {
        Remove-Item $StderrFilePath -Force
    }

    $PreviousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        & $Executable @Arguments 1> $StdoutFilePath 2> $StderrFilePath
        $ExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    if (Test-Path $StdoutFilePath) {
        $StdoutContent = Get-Content $StdoutFilePath -Raw

        if (-not [string]::IsNullOrWhiteSpace($StdoutContent)) {
            Add-Log $StdoutContent.TrimEnd()
        }

        Remove-Item $StdoutFilePath -Force
    }

    if (Test-Path $StderrFilePath) {
        $StderrContent = Get-Content $StderrFilePath -Raw

        if (-not [string]::IsNullOrWhiteSpace($StderrContent)) {
            Add-Log $StderrContent.TrimEnd()
        }

        Remove-Item $StderrFilePath -Force
    }

    if ($ExitCode -ne 0) {
        $Message = "Command failed with exit code $ExitCode."
        Add-Step $Name "FAILED" $Message
        throw $Message
    }

    Add-Step $Name "PASSED" "Command completed successfully."
}

function Get-FileMd5Hash {
    param ([string]$Path)

    return (Get-FileHash -Path $Path -Algorithm MD5).Hash
}

function Invoke-DependencyInstallation {
    $RequirementsPath = Join-Path $ProjectRoot "requirements.txt"

    if (-not (Test-Path $RequirementsPath)) {
        Add-Step "Install dependencies" "SKIPPED" "requirements.txt not found."
        return
    }

    $CurrentRequirementsHash = Get-FileMd5Hash $RequirementsPath
    $PreviousRequirementsHash = $null

    if (Test-Path $RequirementsHashFilePath) {
        $PreviousRequirementsHash = (Get-Content $RequirementsHashFilePath -Raw).Trim()
    }

    if ($CurrentRequirementsHash -eq $PreviousRequirementsHash) {
        Add-Step "Install dependencies" "SKIPPED" "requirements.txt unchanged."
        return
    }

    Invoke-BootstrapCommand `
        -Name "Install dependencies" `
        -Executable "python" `
        -Arguments @("-m", "pip", "install", "-r", "requirements.txt")

    Set-Content -Path $RequirementsHashFilePath -Value $CurrentRequirementsHash -Encoding UTF8
}

function Test-PostgreSqlBootstrapEnabled {
    $PostgreSqlDatabaseConfigPath = Join-Path $ProjectRoot "scripts/db/postgres/config/database.json"

    if (-not (Test-Path $PostgreSqlDatabaseConfigPath)) {
        return $false
    }

    $PostgreSqlDatabaseConfig = Get-Content $PostgreSqlDatabaseConfigPath -Raw | ConvertFrom-Json

    if ($null -eq $PostgreSqlDatabaseConfig.bootstrap) {
        return $true
    }

    if ($null -eq $PostgreSqlDatabaseConfig.bootstrap.enabled) {
        return $true
    }

    return ($PostgreSqlDatabaseConfig.bootstrap.enabled -eq $true)
}

function Set-PostgreSqlEnvironmentDefaults {
    $PostgreSqlDatabaseConfigPath = Join-Path $ProjectRoot "scripts/db/postgres/config/database.json"

    if (-not (Test-Path $PostgreSqlDatabaseConfigPath)) {
        throw "PostgreSQL database config not found: scripts/db/postgres/config/database.json"
    }

    $PostgreSqlDatabaseConfig = Get-Content $PostgreSqlDatabaseConfigPath -Raw | ConvertFrom-Json

    if ($PostgreSqlDatabaseConfig.databaseType -ne "postgres") {
        throw "PostgreSQL database config must use databaseType 'postgres'."
    }

    if ($null -eq $PostgreSqlDatabaseConfig.adminConnection) {
        throw "PostgreSQL database config must contain adminConnection settings."
    }

    if ($null -eq $PostgreSqlDatabaseConfig.applicationConnection) {
        throw "PostgreSQL database config must contain applicationConnection settings."
    }

    if ($null -eq $PostgreSqlDatabaseConfig.environmentVariables) {
        throw "PostgreSQL database config must contain environment variable mappings."
    }

    if ($null -eq $PostgreSqlDatabaseConfig.environmentVariables.admin) {
        throw "PostgreSQL database config must contain admin environment variable mappings."
    }

    if ($null -eq $PostgreSqlDatabaseConfig.environmentVariables.application) {
        throw "PostgreSQL database config must contain application environment variable mappings."
    }

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.host `
        -Value $PostgreSqlDatabaseConfig.adminConnection.host

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.port `
        -Value $PostgreSqlDatabaseConfig.adminConnection.port

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.databaseName `
        -Value $PostgreSqlDatabaseConfig.adminConnection.databaseName

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.username `
        -Value $PostgreSqlDatabaseConfig.adminConnection.username

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.password `
        -Value $PostgreSqlDatabaseConfig.adminConnection.password

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.host `
        -Value $PostgreSqlDatabaseConfig.applicationConnection.host

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.port `
        -Value $PostgreSqlDatabaseConfig.applicationConnection.port

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.databaseName `
        -Value $PostgreSqlDatabaseConfig.applicationConnection.databaseName

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.username `
        -Value $PostgreSqlDatabaseConfig.applicationConnection.username

    Set-EnvironmentDefault `
        -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.password `
        -Value $PostgreSqlDatabaseConfig.applicationConnection.password
}

function Set-EnvironmentDefault {
    param (
        [string]$VariableName,
        [object]$Value
    )

    if ([string]::IsNullOrWhiteSpace($VariableName)) {
        return
    }

    if ($null -eq $Value) {
        return
    }

    $ExistingValue = [Environment]::GetEnvironmentVariable($VariableName, "Process")

    if (-not [string]::IsNullOrWhiteSpace($ExistingValue)) {
        return
    }

    [Environment]::SetEnvironmentVariable($VariableName, [string]$Value, "Process")
}

try {
    Set-Content -Path $LogFilePath -Value "" -Encoding UTF8

    Add-Log "Project bootstrap started."
    Add-Log "Project root: ."
    Flush-Log

    if (Test-StepEnabled "createVirtualEnvironment" $true) {
        $VirtualEnvironmentPath = Join-Path $ProjectRoot ".venv"

        if (-not (Test-Path $VirtualEnvironmentPath)) {
            Invoke-BootstrapCommand `
                -Name "Create virtual environment" `
                -Executable "python" `
                -Arguments @("-m", "venv", ".venv")
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

    if (Test-StepEnabled "installDependencies" $true) {
        Invoke-DependencyInstallation
    }

    if (Test-StepEnabled "createDatabaseSchema" $true) {
        Invoke-BootstrapCommand `
            -Name "Create SQLite database schema" `
            -Executable "python" `
            -Arguments @("-m", "scripts.db.sqlite_create_schema")
    }

    if (Test-StepEnabled "seedDatabase" $true) {
        Invoke-BootstrapCommand `
            -Name "Seed SQLite database" `
            -Executable "python" `
            -Arguments @("-m", "scripts.db.sqlite_seed_data")
    }

    if (Test-PostgreSqlBootstrapEnabled) {
        Set-PostgreSqlEnvironmentDefaults

        Invoke-BootstrapCommand `
            -Name "Create PostgreSQL database schema" `
            -Executable "python" `
            -Arguments @("-m", "scripts.db.postgres.postgres_create_schema")

        Invoke-BootstrapCommand `
            -Name "Seed PostgreSQL database" `
            -Executable "python" `
            -Arguments @("-m", "scripts.db.postgres.postgres_seed_data")
    }
    else {
        Add-Step "Create PostgreSQL database schema" "SKIPPED" "PostgreSQL bootstrap is disabled in database config."
        Add-Step "Seed PostgreSQL database" "SKIPPED" "PostgreSQL bootstrap is disabled in database config."
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

    $Summary = [PSCustomObject]@{
        status      = "FAILED"
        projectRoot = "."
        summaryFile = "scripts/setup/output/$($Config.summaryFileName)"
        logFile     = "scripts/setup/output/$($Config.logFileName)"
        steps       = $Steps
        error       = $ErrorMessage
    }

    $Summary |
        ConvertTo-Json -Depth 10 |
        Set-Content -Path $SummaryFilePath -Encoding UTF8

    Flush-Log
    Write-Host "FAILED Project bootstrap failed. Summary: scripts/setup/output/$($Config.summaryFileName)"
    exit 1
}
