$ErrorActionPreference = 'Stop'
try {
    $health = Invoke-RestMethod 'http://127.0.0.1:8000/health' -TimeoutSec 3
    if ($health.service -ne 'deepagent-search') { throw 'Unexpected service' }
    Write-Host 'DeepSearch is running: http://127.0.0.1:8000'
} catch {
    Write-Host 'DeepSearch is not running. Use Start-DeepSearch.cmd.'
    exit 1
}
