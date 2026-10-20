$ErrorActionPreference = 'Stop'
$serviceRoot = Join-Path $PSScriptRoot 'services/ragflow'
if (-not (Test-Path -LiteralPath (Join-Path $serviceRoot '.env'))) {
    throw '请先把 services/ragflow/.env.example 复制为同目录的 .env，并填写密码。具体步骤见 docs/data-services.md。'
}
Push-Location -LiteralPath $serviceRoot
try {
    docker compose -f compose.yaml up -d
    if ($LASTEXITCODE -ne 0) { throw '知识库服务启动失败。请确认 Docker Desktop 已打开，再查看上方报错。' }
    Write-Host '知识库管理页面：http://127.0.0.1:8080。第一次需要下载镜像和模型，请等待服务准备好。'
} finally { Pop-Location }
