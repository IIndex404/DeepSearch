$ErrorActionPreference = 'Stop'
$pidFile = Join-Path $PSScriptRoot 'logs\service.json'
if (-not (Test-Path -LiteralPath $pidFile)) {
    Write-Host '没有找到由此目录启动的程序，无需停止。'
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
            throw "进程 $serviceId 不属于这个目录启动的 DeepSearch，已保留它，请确认是不是打开了另一份项目。"
        }
        Stop-Process -Id $serviceId -Force
    }
}
Remove-Item -LiteralPath $pidFile
Write-Host 'DeepSearch 已停止，可以关闭这个窗口。'
