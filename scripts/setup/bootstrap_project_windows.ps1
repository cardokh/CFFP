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
$ConfigurationResolution = @()
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
        $OutputTail = ""

        if (-not [string]::IsNullOrWhiteSpace($StderrContent)) {
            $OutputTail = $StderrContent.Trim()
        }
        elseif (-not [string]::IsNullOrWhiteSpace($StdoutContent)) {
            $OutputTail = $StdoutContent.Trim()
        }

        if ($OutputTail.Length -gt 1200) {
            $OutputTail = $OutputTail.Substring($OutputTail.Length - 1200)
        }

        $Message = "Command failed with exit code $ExitCode."

        if (-not [string]::IsNullOrWhiteSpace($OutputTail)) {
            $Message = "$Message $OutputTail"
        }

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


function Test-SensitiveConfigKey {
    param ([string]$Key)

    if ([string]::IsNullOrWhiteSpace($Key)) {
        return $false
    }

    return ($Key -match "(?i)(password|secret|token|key)")
}

function Get-MaskedConfigValue {
    param (
        [string]$Key,
        [object]$Value
    )

    if (Test-SensitiveConfigKey $Key) {
        if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) {
            return ""
        }

        return "********"
    }

    return [string]$Value
}

function Resolve-ConfigurationValue {
    param (
        [string]$GroupName,
        [string]$Key,
        [string]$EnvironmentVariableName,
        [object]$ConfiguredValue
    )

    if ([string]::IsNullOrWhiteSpace($EnvironmentVariableName)) {
        $ResolvedValue = $ConfiguredValue
        $Source = "database.json"
    }
    else {
        $EnvironmentValue = [Environment]::GetEnvironmentVariable($EnvironmentVariableName, "Process")

        if (-not [string]::IsNullOrWhiteSpace($EnvironmentValue)) {
            $ResolvedValue = $EnvironmentValue
            $Source = "environment"
        }
        else {
            $ResolvedValue = $ConfiguredValue
            $Source = "database.json"
        }
    }

    $script:ConfigurationResolution += [PSCustomObject]@{
        group               = $GroupName
        key                 = $Key
        value               = Get-MaskedConfigValue -Key $Key -Value $ResolvedValue
        source              = $Source
        environmentVariable = $EnvironmentVariableName
        sensitive           = (Test-SensitiveConfigKey $Key)
    }

    $MaskedValue = Get-MaskedConfigValue -Key $Key -Value $ResolvedValue
    $EnvironmentNote = ""

    if (-not [string]::IsNullOrWhiteSpace($EnvironmentVariableName)) {
        $EnvironmentNote = ": $EnvironmentVariableName"
    }

    Add-Log "CONFIG - $GroupName.$Key - $MaskedValue ($Source$EnvironmentNote)"

    return $ResolvedValue
}

function Set-ResolvedEnvironmentValue {
    param (
        [string]$GroupName,
        [string]$Key,
        [string]$VariableName,
        [object]$ConfiguredValue
    )

    $ResolvedValue = Resolve-ConfigurationValue `
        -GroupName $GroupName `
        -Key $Key `
        -EnvironmentVariableName $VariableName `
        -ConfiguredValue $ConfiguredValue

    if (-not [string]::IsNullOrWhiteSpace($VariableName) -and $null -ne $ResolvedValue) {
        [Environment]::SetEnvironmentVariable($VariableName, [string]$ResolvedValue, "Process")
    }
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

    Add-Log "PostgreSQL configuration resolution started."

    Set-ResolvedEnvironmentValue -GroupName "postgres.admin" -Key "host" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.host -ConfiguredValue $PostgreSqlDatabaseConfig.adminConnection.host
    Set-ResolvedEnvironmentValue -GroupName "postgres.admin" -Key "port" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.port -ConfiguredValue $PostgreSqlDatabaseConfig.adminConnection.port
    Set-ResolvedEnvironmentValue -GroupName "postgres.admin" -Key "databaseName" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.databaseName -ConfiguredValue $PostgreSqlDatabaseConfig.adminConnection.databaseName
    Set-ResolvedEnvironmentValue -GroupName "postgres.admin" -Key "username" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.username -ConfiguredValue $PostgreSqlDatabaseConfig.adminConnection.username
    Set-ResolvedEnvironmentValue -GroupName "postgres.admin" -Key "password" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.admin.password -ConfiguredValue $PostgreSqlDatabaseConfig.adminConnection.password

    Set-ResolvedEnvironmentValue -GroupName "postgres.application" -Key "host" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.host -ConfiguredValue $PostgreSqlDatabaseConfig.applicationConnection.host
    Set-ResolvedEnvironmentValue -GroupName "postgres.application" -Key "port" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.port -ConfiguredValue $PostgreSqlDatabaseConfig.applicationConnection.port
    Set-ResolvedEnvironmentValue -GroupName "postgres.application" -Key "databaseName" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.databaseName -ConfiguredValue $PostgreSqlDatabaseConfig.applicationConnection.databaseName
    Set-ResolvedEnvironmentValue -GroupName "postgres.application" -Key "username" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.username -ConfiguredValue $PostgreSqlDatabaseConfig.applicationConnection.username
    Set-ResolvedEnvironmentValue -GroupName "postgres.application" -Key "password" -VariableName $PostgreSqlDatabaseConfig.environmentVariables.application.password -ConfiguredValue $PostgreSqlDatabaseConfig.applicationConnection.password

    Add-Log "PostgreSQL configuration resolution completed."
    Flush-Log
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
        steps                   = $Steps
        configurationResolution = $ConfigurationResolution
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
        steps                   = $Steps
        configurationResolution = $ConfigurationResolution
        error                   = $ErrorMessage
    }

    $Summary |
        ConvertTo-Json -Depth 10 |
        Set-Content -Path $SummaryFilePath -Encoding UTF8

    Flush-Log
    Write-Host "FAILED Project bootstrap failed. Summary: scripts/setup/output/$($Config.summaryFileName)"
    exit 1
}
