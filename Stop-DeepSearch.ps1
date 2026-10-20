$ErrorActionPreference = 'Stop'
$pidFile = Join-Path $PSScriptRoot 'logs\service.json'
if (-not (Test-Path -LiteralPath $pidFile)) {
    Write-Host 'No managed DeepSearch service is recorded.'
    exit 0
}
$state = Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json
$launcher = Get-CimInstance Win32_Process -Filter "ProcessId = $($state.launcherId)"
$launcherValid = $launcher -and $launcher.CommandLine -match 'uvicorn\s+deploy_server:app' -and
    $launcher.CommandLine -match [regex]::Escape($state.pythonPath)
foreach ($serviceId in @($state.processId, $state.launcherId) | Select-Object -Unique) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $serviceId"
    if ($process) {
        $belongsToLauncher = $launcherValid -and $process.ParentProcessId -eq $state.launcherId
        $usesEnvironment = $process.CommandLine -match [regex]::Escape($state.pythonPath)
        if ($process.CommandLine -notmatch 'uvicorn\s+deploy_server:app' -or
            (-not $usesEnvironment -and -not $belongsToLauncher)) {
            throw "Process $serviceId does not match this deployment; it was left running."
        }
        Stop-Process -Id $serviceId -Force
    }
}
Remove-Item -LiteralPath $pidFile
Write-Host 'DeepSearch stopped.'
