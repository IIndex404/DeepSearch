$ErrorActionPreference = 'Stop'
$serviceRoot = Join-Path $PSScriptRoot 'services/ragflow'
if (-not (Test-Path -LiteralPath (Join-Path $serviceRoot '.env'))) {
    throw 'Copy services/ragflow/.env.example to .env and fill the credentials first.'
}
Push-Location -LiteralPath $serviceRoot
try {
    docker compose -f compose.yaml up -d
    if ($LASTEXITCODE -ne 0) { throw 'Data service startup failed.' }
    Write-Host 'RAGFlow: http://127.0.0.1:8080; first startup downloads images and the embedding model.'
} finally { Pop-Location }
