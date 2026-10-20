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

if (-not (Test-Path -LiteralPath $pythonPath)) { throw '还没有安装运行环境，请先双击“安装.cmd”。' }
if (-not (Test-Path -LiteralPath (Join-Path $deployRoot 'frontend\dist\index.html'))) { throw '网页还没有生成，请先双击“安装.cmd”。' }
if (-not (Test-Path -LiteralPath (Join-Path $backend '.env'))) { throw '还没有配置文件，请双击“配置.cmd”，填写密钥并保存。' }


$configFile = Join-Path $backend '.env'
& $pythonPath -c "from dotenv import dotenv_values; import sys; sys.exit(0 if (dotenv_values(sys.argv[1]).get('TAVILY_API_KEY') or '').strip() else 1)" $configFile
if ($LASTEXITCODE -ne 0) {
    throw '还没有填写 Tavily 密钥。请双击“配置.cmd”，在 TAVILY_API_KEY 等号后填入自己的密钥，保存后重新启动。'
}

if (Test-Ready) {
    Write-Host "DeepSearch 已经在运行，打开这个地址即可：$url"
    if ($OpenBrowser) { Start-Process $url }
    exit 0
}
if (Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue) {
    throw '8000 端口被其他程序占用了。请先关闭占用该端口的程序，再启动 DeepSearch。'
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
        Write-Host "DeepSearch 已启动：$url"
        Write-Host "运行日志保存在：$deployRoot\logs"
        if ($OpenBrowser) { Start-Process $url }
        exit 0
    }
    if ($proc.HasExited) { throw '启动失败。请打开 logs/server.err.log 查看具体原因。' }
    Start-Sleep -Seconds 1
}
Stop-Process -Id $proc.Id -ErrorAction SilentlyContinue
throw '等待启动超时。请打开 logs/server.err.log 查看具体原因。'
