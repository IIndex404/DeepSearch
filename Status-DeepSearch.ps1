$ErrorActionPreference = 'Stop'
try {
    $health = Invoke-RestMethod 'http://127.0.0.1:8000/health' -TimeoutSec 3
    if ($health.service -ne 'deepagent-search') { throw '这个地址运行的是其他程序' }
    Write-Host 'DeepSearch 正在运行，浏览器打开 http://127.0.0.1:8000 即可。'
} catch {
    Write-Host 'DeepSearch 还没有启动，请双击“启动.cmd”。'
    exit 1
}
