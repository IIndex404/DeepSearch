param([switch]$OpenBrowser)
$ErrorActionPreference = 'Stop'
$deployRoot = $PSScriptRoot
$backend = Join-Path $deployRoot 'backend'
$pythonPath = Join-Path $backend '.venv\Scripts\python.exe'
$pidFile = Join-Path $deployRoot 'logs\service.json'
$url = 'http://127.0.0.1:8000'

function Test-Ready {
    try {
        $health = Invoke-RestMethod "$url/health" -TimeoutSec 2
        return ($health.service -eq 'deepagent-search' -and $health.status -eq 'ok')
    } catch { return $false }
}

if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Python environment missing: backend\.venv' }
if (-not (Test-Path -LiteralPath (Join-Path $deployRoot 'frontend\dist\index.html'))) { throw 'Frontend build missing: frontend\dist' }
if (-not (Test-Path -LiteralPath (Join-Path $backend '.env'))) { throw 'Configuration missing: backend\.env' }

if (Test-Ready) {
    Write-Host "DeepSearch is already running: $url"
    if ($OpenBrowser) { Start-Process $url }
    exit 0
}
if (Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue) {
    throw 'Port 8000 is occupied by another service.'
}
New-Item -ItemType Directory -Path (Join-Path $deployRoot 'logs') -Force | Out-Null
$env:PYTHONUTF8 = '1'
$env:PYTHONUNBUFFERED = '1'
$proc = Start-Process -FilePath $pythonPath -WorkingDirectory $backend `
    -ArgumentList '-m','uvicorn','deploy_server:app','--host','127.0.0.1','--port','8000','--log-level','info' `
    -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $deployRoot 'logs\server.out.log') `
    -RedirectStandardError (Join-Path $deployRoot 'logs\server.err.log')

for ($attempt = 0; $attempt -lt 45; $attempt++) {
    if (Test-Ready) {
        $listener = Get-NetTCPConnection -State Listen -LocalPort 8000 | Select-Object -First 1
        @{ processId = $listener.OwningProcess; launcherId = $proc.Id; pythonPath = $pythonPath; url = $url } |
            ConvertTo-Json | Set-Content -LiteralPath $pidFile -Encoding UTF8
        Write-Host "DeepSearch started: $url"
        Write-Host "Logs: $deployRoot\logs"
        if ($OpenBrowser) { Start-Process $url }
        exit 0
    }
    if ($proc.HasExited) { throw 'Service exited. See logs\server.err.log.' }
    Start-Sleep -Seconds 1
}
Stop-Process -Id $proc.Id -ErrorAction SilentlyContinue
throw 'Startup timed out. See logs\server.err.log.'
